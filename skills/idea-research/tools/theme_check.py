#!/usr/bin/env python3
"""theme_check.py, the contrast gate for one run's theme.

    python3 tools/theme_check.py runs/<slug>/theme.json [--strict] [--tokens FILE]

It checks a theme.json for the keys render.py needs, resolves the theme's token
set, and computes WCAG 2.1 contrast ratios for text on bg, muted on bg, accent
on bg, the section number on bg, and every callout foreground on its own tint
over the background. A tint is composited over the background before it is
measured, whether it is written as rgba() or stored already composited.

Standard library only. No colour library, and render/themes.py is read rather
than imported, so this script never depends on that module loading.

Exit codes: 0 clean, 1 a schema error or, with --strict, a failing ratio.
"""

import argparse
import ast
import json
import os
import re
import sys

# Keys theme.json must carry. Unknown extra keys are ignored, never failed,
# because render.py ignores them too.
REQUIRED_KEYS = ["theme", "accent", "reason", "type", "density"]
REQUIRED_TYPE_KEYS = ["display", "body"]
THEME_NAMES = ["clinical", "warm", "industrial", "financial"]
DENSITIES = ["compact", "regular"]

HUES = ["note", "tip", "important", "warning", "caution"]

# Tokens this script measures. A token set missing one of these cannot be checked.
MEASURED_TOKENS = ["bg", "text", "muted", "dim", "accent", "accent-tint"] + \
    HUES + [h + "-tint" for h in HUES]
# Tokens render/report.css also needs. Absence is reported, not failed, because
# it is the stylesheet that breaks, not the contrast.
STRUCTURAL_TOKENS = ["surface", "surface-2", "line", "line-soft"]

BODY_MIN = 4.5
LARGE_MIN = 3.0
LARGE_PX = 24.0  # WCAG 2.1 large text: 24px, or 18.66px bold


# ------------------------------------------------------------------ colour math

def norm_key(key):
    return str(key).strip().lower().replace("_", "-").replace(" ", "-")


class ColourError(ValueError):
    pass


def parse_colour(value, where="colour"):
    """Return (r, g, b, alpha) with r,g,b as 0-255 ints and alpha 0.0-1.0.

    Accepts #rgb, #rrggbb, #rrggbbaa, rgb(), rgba(), and [colour, alpha].
    """
    if isinstance(value, (list, tuple)):
        if len(value) == 2:
            r, g, b, _ = parse_colour(value[0], where)
            return (r, g, b, clamp_alpha(value[1], where))
        if len(value) in (3, 4):
            nums = [as_channel(v, where) for v in value[:3]]
            alpha = clamp_alpha(value[3], where) if len(value) == 4 else 1.0
            return (nums[0], nums[1], nums[2], alpha)
        raise ColourError("%s: cannot read colour %r" % (where, value))
    if not isinstance(value, str):
        raise ColourError("%s: cannot read colour %r" % (where, value))
    text = value.strip().lower()
    if text.startswith("#"):
        digits = text[1:]
        if len(digits) == 3:
            digits = "".join(ch * 2 for ch in digits)
        if len(digits) == 8:
            alpha = int(digits[6:8], 16) / 255.0
            digits = digits[:6]
        elif len(digits) == 6:
            alpha = 1.0
        else:
            raise ColourError("%s: %r is not a 3, 6 or 8 digit hex colour" % (where, value))
        try:
            return (int(digits[0:2], 16), int(digits[2:4], 16),
                    int(digits[4:6], 16), alpha)
        except ValueError:
            raise ColourError("%s: %r has non hex digits" % (where, value))
    match = re.match(r"^rgba?\(([^)]*)\)$", text)
    if match:
        parts = [p.strip() for p in re.split(r"[,/\s]+", match.group(1)) if p.strip()]
        if len(parts) not in (3, 4):
            raise ColourError("%s: %r needs 3 or 4 components" % (where, value))
        nums = [as_channel(p, where) for p in parts[:3]]
        alpha = clamp_alpha(parts[3], where) if len(parts) == 4 else 1.0
        return (nums[0], nums[1], nums[2], alpha)
    raise ColourError("%s: %r is not a hex, rgb() or rgba() colour" % (where, value))


def as_channel(part, where):
    text = str(part).strip()
    try:
        if text.endswith("%"):
            val = float(text[:-1]) * 255.0 / 100.0
        else:
            val = float(text)
    except ValueError:
        raise ColourError("%s: %r is not a number" % (where, part))
    return int(round(max(0.0, min(255.0, val))))


def clamp_alpha(part, where):
    text = str(part).strip()
    try:
        val = float(text[:-1]) / 100.0 if text.endswith("%") else float(text)
    except ValueError:
        raise ColourError("%s: alpha %r is not a number" % (where, part))
    return max(0.0, min(1.0, val))


def composite(fg_rgba, bg_rgb):
    """Source over compositing in gamma encoded sRGB, the way a browser paints.

    out = alpha * tint + (1 - alpha) * background, per 0-255 channel.
    Doing this in linear light instead is the classic bug: it lightens the
    result and reports a contrast the eye does not get.
    """
    alpha = fg_rgba[3]
    return tuple(int(round(alpha * fg_rgba[i] + (1.0 - alpha) * bg_rgb[i]))
                 for i in range(3))


def tint_alpha(tint_rgba, hue_rgba, bg_rgba):
    """The alpha a tint was mixed at, so a re-tuned accent can be re-composited.

    A tint written as rgba() states its own alpha. A tint stored already
    composited states nothing, so solve it per channel from
    tint = alpha * hue + (1 - alpha) * bg, and average the channels where the
    hue and the background actually differ.
    """
    if tint_rgba[3] < 0.999:
        return tint_rgba[3], "alpha taken from the rgba value"
    solved = []
    for i in range(3):
        span = hue_rgba[i] - bg_rgba[i]
        if abs(span) < 12:
            continue
        solved.append((tint_rgba[i] - bg_rgba[i]) / float(span))
    if not solved:
        return None, ""
    alpha = sum(solved) / len(solved)
    if not 0.02 <= alpha <= 0.6:
        return None, ""
    return alpha, ("recovered from the stored tint, the default accent and bg")


def relative_luminance(rgb):
    """WCAG 2.1 relative luminance: linearise each sRGB channel, then weight."""
    chan = []
    for value in rgb[:3]:
        srgb = value / 255.0
        if srgb <= 0.03928:
            chan.append(srgb / 12.92)
        else:
            chan.append(((srgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]


def contrast_ratio(rgb_a, rgb_b):
    lum_a = relative_luminance(rgb_a)
    lum_b = relative_luminance(rgb_b)
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


def hexof(rgb):
    return "#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])


# ------------------------------------------------------------- token resolution

def themes_py_path(theme_json_path):
    """render/themes.py, found relative to this script and to the theme.json."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.path.dirname(here), "render", "themes.py"),
        os.path.join(here, "themes.py"),
        os.path.join(os.path.dirname(os.path.abspath(theme_json_path)),
                     "render", "themes.py"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def literal_dicts_from_module(path):
    """Every module level dict literal in a .py file, without importing it.

    ast.literal_eval only evaluates literals, so nothing in the file runs.
    """
    with open(path, "r") as fh:
        source = fh.read()
    found = {}
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ColourError("%s does not parse (%s)" % (path, exc))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError, TypeError):
                continue
            if isinstance(value, dict):
                found[target.id] = value
    return found


def tokens_from_mapping(mapping, theme_name):
    """Pull one theme's token dict out of whatever shape the mapping has."""
    lowered = dict((norm_key(k), v) for k, v in mapping.items())
    entry = lowered.get(norm_key(theme_name))
    if entry is None:
        return None
    if isinstance(entry, dict):
        for inner in ("tokens", "vars", "palette", "colors", "colours"):
            if isinstance(entry.get(inner), dict):
                return flatten_tokens(entry[inner])
        return flatten_tokens(entry)
    return None


def flatten_tokens(raw):
    """Normalise keys and fold a nested tints/hues block up to the top level."""
    out = {}
    for key, value in raw.items():
        nkey = norm_key(key)
        if isinstance(value, dict):
            if nkey in ("tints", "tint"):
                for hue, tint in value.items():
                    out[norm_key(hue) + "-tint"] = tint
            elif nkey in ("hues", "semantic", "callouts"):
                for hue, hval in value.items():
                    if isinstance(hval, dict):
                        for sub, sval in hval.items():
                            nsub = norm_key(sub)
                            if nsub in ("tint",):
                                out[norm_key(hue) + "-tint"] = sval
                            elif nsub in ("fg", "color", "colour", "hue", "base"):
                                out[norm_key(hue)] = sval
                    else:
                        out[norm_key(hue)] = hval
            else:
                continue
        else:
            out[nkey] = value
    return out


def resolve_tokens(theme_json_path, theme, theme_json, tokens_arg):
    """Return (tokens, source_description, error). Tokens is None on error."""
    if tokens_arg:
        if os.path.isdir(tokens_arg):
            return None, "", ("--tokens %s is a directory, not a file. Pass the "
                              "JSON file of token sets." % tokens_arg)
        if not os.path.isfile(tokens_arg):
            return None, "", "--tokens %s does not exist" % tokens_arg
        try:
            with open(tokens_arg, "r") as fh:
                data = json.load(fh)
        except ValueError as exc:
            return None, "", "--tokens %s is not valid JSON (%s)" % (tokens_arg, exc)
        if isinstance(data, dict):
            picked = tokens_from_mapping(data, theme)
            if picked:
                return picked, "%s, theme %s" % (tokens_arg, theme), None
            return flatten_tokens(data), "%s" % tokens_arg, None
        return None, "", "--tokens %s must hold a JSON object" % tokens_arg

    inline = theme_json.get("tokens")
    if isinstance(inline, dict):
        return flatten_tokens(inline), \
            "%s, inline \"tokens\" key" % os.path.basename(theme_json_path), None

    module = themes_py_path(theme_json_path)
    if module:
        try:
            dicts = literal_dicts_from_module(module)
        except ColourError as exc:
            return None, "", str(exc)
        for name in ("THEMES", "THEME_TOKENS", "PALETTES", "THEME", "TOKENS"):
            if name in dicts:
                picked = tokens_from_mapping(dicts[name], theme)
                if picked:
                    return picked, "%s, %s[%r]" % (module, name, theme), None
        for name, value in sorted(dicts.items()):
            picked = tokens_from_mapping(value, theme)
            if picked:
                return picked, "%s, %s[%r]" % (module, name, theme), None
            if norm_key(name) == norm_key(theme):
                return flatten_tokens(value), "%s, %s" % (module, name), None
        return None, "", ("%s has no token set for theme %r. Supply one with "
                          "--tokens FILE or a \"tokens\" key in theme.json."
                          % (module, theme))
    return None, "", ("no token source. render/themes.py was not found, so pass "
                      "--tokens FILE or put a \"tokens\" object in theme.json.")


# ------------------------------------------------------------- schema and checks

def wrong_shape(path, want="file"):
    """Return one line naming a path of the wrong shape, or "" when it is fine.

    Every other script in this pipeline takes runs/<slug>/, so handing this one
    the run directory is the ordinary typo. os.path.exists is true for a
    directory, which is how that typo used to reach open() and raise
    IsADirectoryError with a traceback.
    """
    if want == "file":
        if os.path.isdir(path):
            return ("%s is a directory, not a file. theme_check takes the "
                    "theme.json inside the run: %s"
                    % (path, os.path.join(path, "theme.json")))
        if not os.path.isfile(path):
            return "no such file: %s" % path
        return ""
    if os.path.isfile(path):
        return ("%s is a file, not a directory. Pass the directory that holds "
                "it: %s" % (path, os.path.dirname(os.path.abspath(path)) or "."))
    if not os.path.isdir(path):
        return "no such directory: %s" % path
    return ""


def check_schema(theme_json_path):
    """Return (theme_json, errors)."""
    shape = wrong_shape(theme_json_path)
    if shape:
        return None, [shape]
    try:
        with open(theme_json_path, "r") as fh:
            data = json.load(fh)
    except ValueError as exc:
        return None, ["%s is not valid JSON (%s)" % (theme_json_path, exc)]
    if not isinstance(data, dict):
        return None, ["%s must hold a JSON object" % theme_json_path]

    errors = []
    for key in REQUIRED_KEYS:
        if key not in data:
            errors.append("theme.json is missing the required key \"%s\"" % key)
    if "theme" in data and data["theme"] not in THEME_NAMES:
        errors.append("key \"theme\" is %r, which is not one of: %s"
                      % (data["theme"], "|".join(THEME_NAMES)))
    if "accent" in data:
        if not re.match(r"^#[0-9a-fA-F]{6}$", str(data["accent"]).strip()):
            errors.append("key \"accent\" is %r, which is not #RRGGBB"
                          % data["accent"])
    if "reason" in data and not str(data.get("reason") or "").strip():
        errors.append("key \"reason\" is empty, and it must name what in this "
                      "idea's world chose the theme")
    if "type" in data:
        if not isinstance(data["type"], dict):
            errors.append("key \"type\" must be an object with \"display\" and \"body\"")
        else:
            for key in REQUIRED_TYPE_KEYS:
                if not str(data["type"].get(key) or "").strip():
                    errors.append("key \"type.%s\" is missing or empty" % key)
    if "density" in data and data["density"] not in DENSITIES:
        errors.append("key \"density\" is %r, which is not one of: %s"
                      % (data["density"], "|".join(DENSITIES)))
    return data, errors


def build_checks(tokens, accent_override):
    """Return (rows, errors). Each row is one measured pair."""
    errors = []
    missing = [t for t in MEASURED_TOKENS if t not in tokens]
    resolved = {}
    for name, value in tokens.items():
        try:
            resolved[name] = parse_colour(value, "token %s" % name)
        except ColourError as exc:
            errors.append(str(exc))
    if missing:
        errors.append("token set is missing: %s" % ", ".join(missing))
    if errors:
        return [], errors, []

    notes = []
    tint_notes = {}
    if accent_override:
        new_accent = parse_colour(accent_override, "theme.json accent")
        old_accent = resolved["accent"]
        old_tint = resolved["accent-tint"]
        resolved["accent"] = new_accent
        # The accent tint has to follow the accent, or the check measures the
        # old hue's ground. A tint given as rgba keeps its alpha. A tint stored
        # already composited has its alpha recovered from the old accent first.
        alpha, how = tint_alpha(old_tint, old_accent, resolved["bg"])
        if alpha is None:
            notes.append("accent-tint kept as the theme stores it, because its "
                         "alpha could not be recovered from the default accent")
        else:
            ground = composite((new_accent[0], new_accent[1], new_accent[2], alpha),
                               resolved["bg"][:3])
            resolved["accent-tint"] = (ground[0], ground[1], ground[2], 1.0)
            tint_notes["accent-tint"] = ("accent-tint re-derived at alpha %.3f "
                                         "over bg" % alpha)
            notes.append("accent-tint re-derived for the new accent at alpha "
                         "%.3f, %s" % (alpha, how))

    bg = resolved["bg"][:3]
    rows = []

    def plain(label, token, px):
        fg = resolved[token][:3]
        rows.append({"label": label, "fg_token": token, "fg": hexof(fg),
                     "bg_token": "bg", "bg": hexof(bg), "bg_note": "",
                     "px": px, "ratio": contrast_ratio(fg, bg)})

    def over_tint(label, token, tint_token, px):
        tint = resolved[tint_token]
        ground = composite(tint, bg)
        fg = resolved[token][:3]
        if tint_token in tint_notes:
            note = tint_notes[tint_token]
        elif tint[3] < 0.999:
            note = "%s at %.0f%% over bg" % (tint_token, tint[3] * 100)
        else:
            note = "%s, stored already composited" % tint_token
        rows.append({"label": label, "fg_token": token, "fg": hexof(fg),
                     "bg_token": tint_token, "bg": hexof(ground),
                     "bg_note": note,
                     "px": px, "ratio": contrast_ratio(fg, ground)})

    plain("text on bg", "text", 17)
    plain("muted on bg", "muted", 16)
    plain("accent on bg, link text", "accent", 17)
    plain("dim on bg, section number", "dim", 29)
    for hue in HUES:
        over_tint("%s title on %s-tint over bg" % (hue, hue), hue, hue + "-tint", 14)
    over_tint("accent label on accent-tint over bg", "accent", "accent-tint", 12)

    for row in rows:
        row["need"] = LARGE_MIN if row["px"] >= LARGE_PX else BODY_MIN
        row["size"] = "large" if row["px"] >= LARGE_PX else "body"
        row["pass"] = row["ratio"] + 1e-9 >= row["need"]
    return rows, [], notes


def render_rows(rows):
    headers = ["pair", "fg", "ground", "composited from", "size", "ratio",
               "needs", "verdict"]
    body = []
    for row in rows:
        body.append([
            row["label"], row["fg"], row["bg"],
            row["bg_note"] or "-",
            "%dpx %s" % (row["px"], row["size"]),
            "%.2f:1" % row["ratio"],
            "%.1f:1" % row["need"],
            "pass" if row["pass"] else "FAIL",
        ])
    widths = [len(h) for h in headers]
    for line in body:
        for i, cell in enumerate(line):
            widths[i] = max(widths[i], len(cell))
    fmt = lambda cells: "  " + "  ".join(
        cells[i].ljust(widths[i]) for i in range(len(cells))).rstrip()
    out = [fmt(headers), fmt(["-" * w for w in widths])]
    for line in body:
        out.append(fmt(line))
    return out


def main(argv):
    parser = argparse.ArgumentParser(
        prog="theme_check.py",
        description="WCAG 2.1 contrast gate for a run's theme.json.",
        epilog=("Body text needs %.1f:1. Text at %dpx or larger needs %.1f:1.\n"
                "A tint is composited over the background before it is measured."
                % (BODY_MIN, int(LARGE_PX), LARGE_MIN)),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("theme_json", help="runs/<slug>/theme.json")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when any pair fails its threshold")
    parser.add_argument("--tokens", default="",
                        help="JSON file of token sets, when render/themes.py "
                             "is not the source of truth")
    args = parser.parse_args(argv)

    shape = wrong_shape(args.theme_json)
    if shape:
        sys.stderr.write("theme_check: " + shape + "\n")
        return 1

    data, errors = check_schema(args.theme_json)
    print("theme.json : %s" % os.path.abspath(args.theme_json))
    if errors:
        for err in errors:
            print("SCHEMA FAIL : %s" % err)
        print("")
        print("%d schema error%s. Nothing was measured."
              % (len(errors), "" if len(errors) == 1 else "s"))
        return 1

    theme = data["theme"]
    accent = str(data["accent"]).strip()
    tokens, source, err = resolve_tokens(args.theme_json, theme, data, args.tokens)
    if tokens is None:
        print("TOKEN FAIL : %s" % err)
        return 1

    print("theme      : %s" % theme)
    default_accent = str(tokens.get("accent", "not set"))
    if default_accent.lower() == accent.lower():
        print("accent     : %s, the theme default" % accent)
    else:
        print("accent     : %s, tuned from the theme default %s"
              % (accent, default_accent))
    print("type       : display %r, body %r"
          % (data["type"]["display"], data["type"]["body"]))
    print("density    : %s" % data["density"])
    print("tokens     : %s" % source)
    absent = [t for t in STRUCTURAL_TOKENS if t not in tokens]
    if absent:
        print("note       : token set has no %s. report.css needs them, contrast "
              "does not." % ", ".join(absent))
    unknown = sorted(k for k in data.keys()
                     if k not in REQUIRED_KEYS and k != "tokens")
    if unknown:
        print("ignored    : extra key%s %s, which render.py ignores too"
              % ("" if len(unknown) == 1 else "s", ", ".join(unknown)))
    print("")

    try:
        rows, errors, notes = build_checks(tokens, accent)
    except ColourError as exc:
        print("TOKEN FAIL : %s" % exc)
        return 1
    if errors:
        for err in errors:
            print("TOKEN FAIL : %s" % err)
        print("")
        print("%d token error%s. Nothing was measured."
              % (len(errors), "" if len(errors) == 1 else "s"))
        return 1

    for line in render_rows(rows):
        print(line)
    print("")
    for note in notes:
        print("derived   : %s" % note)
    print("composite : out = alpha * tint + (1 - alpha) * bg, per sRGB byte "
          "channel, before luminance")
    print("luminance : sRGB linearised, then 0.2126R + 0.7152G + 0.0722B; "
          "ratio (L1 + 0.05) / (L2 + 0.05)")
    failed = [r for r in rows if not r["pass"]]
    if not failed:
        print("OK. %d of %d pairs pass." % (len(rows), len(rows)))
        return 0
    print("FAIL %d of %d pairs:" % (len(failed), len(rows)))
    for row in failed:
        print("  %s is %.2f:1 and needs %.1f:1. Change %s or %s."
              % (row["label"], row["ratio"], row["need"],
                 row["fg_token"], row["bg_token"]))
    if not args.strict:
        print("Not strict, so this exits 0. Add --strict to make it a gate.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
