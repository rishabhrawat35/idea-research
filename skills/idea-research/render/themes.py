#!/usr/bin/env python3
"""The four curated themes. render.py substitutes one of these into report.css.

There are four and only four. A design agent picks one by domain and tunes the
accent, and nothing else. No palette is generated at run time.

Interface, which tools/theme_check.py and render/render.py both read:

    THEMES          dict name -> dict of CSS token name (no leading "--") to a
                    solid "#rrggbb" string. Every value is opaque hex, so a
                    contrast check needs no alpha compositing.
    THEME_NAMES     the four names, in the order they are documented.
    DEFAULT_THEME   "clinical", which is also what report.css carries inline.
    GROUND          name -> "light" or "dark".
    REQUIRED_TOKENS the token names every theme must carry.
    get_theme(name, accent=None)   a copy of one token set, with the accent and
                    its two derived tokens recomputed when an accent is given.
    token_map(name, accent=None, font=None, display=None, mono=None)
                    the same tokens keyed "--bg" style, with the three font
                    stacks added, ready to write into :root.
    css_root(...)   those declarations as CSS text.
    contrast_ratio(a, b)           WCAG 2.1 contrast of two hex colours.
    audit(name, accent=None)       list of (label, ratio, floor, passed).

Standard library only.  `python3 themes.py` prints every ratio for all four.
"""

# ---------------------------------------------------------------- colour maths


def _rgb(colour):
    """"#rrggbb" or "#rgb" -> (r, g, b) as ints 0-255."""
    text = colour.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError("not a hex colour: %r" % colour)
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))


def _hex(triple):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in triple)


def _channel(value):
    v = value / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def relative_luminance(colour):
    """WCAG 2.1 relative luminance of a hex colour."""
    r, g, b = _rgb(colour)
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(one, two):
    """WCAG 2.1 contrast ratio between two hex colours. 1.0 to 21.0."""
    a, b = relative_luminance(one), relative_luminance(two)
    high, low = max(a, b), min(a, b)
    return (high + 0.05) / (low + 0.05)


def blend(front, back, alpha):
    """Composite `front` over `back` at `alpha` and return opaque hex.

    Tints in these themes are stored already composited, so a checker never has
    to parse rgba(). This is the function that produced them.
    """
    f, b = _rgb(front), _rgb(back)
    return _hex(tuple(f[i] * alpha + b[i] * (1.0 - alpha) for i in range(3)))


# ---------------------------------------------------------------- token names

REQUIRED_TOKENS = (
    "bg", "surface", "surface-2", "line", "line-soft",
    "text", "strong", "muted", "dim", "accent",
    "accent-tint", "accent-line", "zebra",
    "note", "tip", "important", "warning", "caution",
    "note-tint", "tip-tint", "important-tint", "warning-tint", "caution-tint",
)

# How much of a hue is mixed into the ground to make its callout tint. Light
# grounds need less, because a tint that is too strong on paper reads as dirt.
TINT_ALPHA = {"clinical": 0.10, "warm": 0.11, "industrial": 0.14, "financial": 0.14}

FALLBACK_SANS = (
    'system-ui, -apple-system, "Segoe UI", Roboto, "DejaVu Sans", '
    "Helvetica, Arial, sans-serif"
)
FALLBACK_MONO = (
    'ui-monospace, "SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace'
)

# ---------------------------------------------------------------- the four

THEMES = {
    # Cool light paper, deep teal accent, near-black slate text. Highest
    # legibility of the four. For health, medtech, diagnostics and pharma.
    "clinical": {
        "bg": "#edf1f3", "surface": "#f8fafb", "surface-2": "#e2e8ec",
        "line": "#c1ccd2", "line-soft": "#d7e0e5",
        "text": "#15242b", "strong": "#06131a", "muted": "#465a63", "dim": "#55686f",
        "accent": "#0a656f", "accent-tint": "#dbe6e8", "accent-line": "#87b2b8",
        "zebra": "#e5e9ea",
        "note": "#0f5c8c", "tip": "#166a3b", "important": "#5b3ea8",
        "warning": "#815307", "caution": "#a3221c",
        "note-tint": "#d7e2e9", "tip-tint": "#d8e4e1", "important-tint": "#dedfec",
        "warning-tint": "#e2e1db", "caution-tint": "#e6dcde",
    },
    # Warm stone paper, softer lines, deep rose-plum accent. Deliberately not
    # cream and terracotta. For consumer, family, wellness, education and food.
    "warm": {
        "bg": "#f2efe9", "surface": "#fbf9f5", "surface-2": "#e8e3d9",
        "line": "#cdc5b6", "line-soft": "#dfd9cc",
        "text": "#292520", "strong": "#151210", "muted": "#5a5248", "dim": "#6e6558",
        "accent": "#8c3f56", "accent-tint": "#e9e0dc", "accent-line": "#c4a0a7",
        "zebra": "#eae7e1",
        "note": "#12578a", "tip": "#1a6438", "important": "#5c3f9e",
        "warning": "#7d5306", "caution": "#a02a1f",
        "note-tint": "#d9dedf", "tip-tint": "#dae0d6", "important-tint": "#e2dce1",
        "warning-tint": "#e5ded0", "caution-tint": "#e9d9d3",
    },
    # Warm graphite ground, tight lines, safety-orange accent. Reads like a
    # shop-floor panel. For hardware, manufacturing, logistics and B2B.
    "industrial": {
        "bg": "#1a1a17", "surface": "#232320", "surface-2": "#2c2c28",
        "line": "#474741", "line-soft": "#33332e",
        "text": "#eeece4", "strong": "#ffffff", "muted": "#aba89c", "dim": "#918e83",
        "accent": "#e07a2f", "accent-tint": "#30251a", "accent-line": "#734522",
        "zebra": "#22221f",
        "note": "#63a8f0", "tip": "#54c274", "important": "#b492f5",
        "warning": "#d8a52a", "caution": "#f58275",
        "note-tint": "#242e35", "tip-tint": "#223224", "important-tint": "#302b36",
        "warning-tint": "#352d1a", "caution-tint": "#392924",
    },
    # Cool ink ground, terminal teal accent, tabular numbers everywhere. For
    # fintech, lending, insurance and markets.
    "financial": {
        "bg": "#0e1520", "surface": "#16202e", "surface-2": "#1d2938",
        "line": "#35465c", "line-soft": "#243040",
        "text": "#e3eaf3", "strong": "#ffffff", "muted": "#a2b3c6", "dim": "#8798ad",
        "accent": "#2fb0a6", "accent-tint": "#12262f", "accent-line": "#1d5b5c",
        "zebra": "#161d28",
        "note": "#5ba4f2", "tip": "#3ac07c", "important": "#ab8cf6",
        "warning": "#d9a52a", "caution": "#f2685c",
        "note-tint": "#19293d", "tip-tint": "#142d2d", "important-tint": "#24263e",
        "warning-tint": "#2a2921", "caution-tint": "#2e2128",
    },
}

THEME_NAMES = ("clinical", "warm", "industrial", "financial")
DEFAULT_THEME = "clinical"
GROUND = {"clinical": "light", "warm": "light", "industrial": "dark", "financial": "dark"}

# What each theme is for, one line each, so an agent can pick without guessing.
PURPOSE = {
    "clinical": "Health, medtech, diagnostics, pharma. Cool light paper, highest legibility.",
    "warm": "Consumer, family, wellness, education, food. Warm stone paper, softer lines.",
    "industrial": "Hardware, manufacturing, logistics, B2B. Dark graphite, tight and dense.",
    "financial": "Fintech, lending, insurance, markets. Dark ink, cool, tabular emphasis.",
}


# ---------------------------------------------------------------- accessors


def get_theme(name, accent=None):
    """A copy of one token set. A given accent replaces the default accent and
    its two derived tokens, so a tuned accent stays consistent with its tint."""
    key = (name or DEFAULT_THEME).strip().lower()
    if key not in THEMES:
        raise KeyError(key)
    tokens = dict(THEMES[key])
    if accent:
        accent = accent.strip()
        _rgb(accent)  # raises on anything that is not a hex colour
        tokens["accent"] = accent
        tokens["accent-tint"] = blend(accent, tokens["bg"], TINT_ALPHA[key] * 0.8)
        tokens["accent-line"] = blend(accent, tokens["bg"], 0.45)
    return tokens


def font_stack(family=None, mono=False):
    """A Google family followed by a real system fallback, or the fallback alone.

    'DejaVu Sans' is in every stack on purpose: on a bare Linux box with no
    network, a missing family otherwise falls all the way back to a serif.
    """
    base = FALLBACK_MONO if mono else FALLBACK_SANS
    family = (family or "").strip()
    if not family or family.lower() == "system":
        return base
    return '"%s", %s' % (family.replace('"', ""), base)


def token_map(name, accent=None, font=None, display=None, mono=None):
    """Tokens keyed the way :root wants them, the three font stacks included."""
    tokens = get_theme(name, accent)
    out = {
        "--font": font_stack(font),
        "--display": font_stack(display or font),
        "--mono": font_stack(mono, mono=True),
    }
    for key in REQUIRED_TOKENS:
        out["--" + key] = tokens[key]
    return out


def css_root(name, accent=None, font=None, display=None, mono=None):
    """The declarations that go inside report.css's single :root block."""
    values = token_map(name, accent, font, display, mono)
    lines = ["  --font: %s;" % values["--font"],
             "  --display: %s;" % values["--display"],
             "  --mono: %s;" % values["--mono"]]
    for key in REQUIRED_TOKENS:
        lines.append("  --%s: %s;" % (key, values["--" + key]))
    return "\n".join(lines)


# ---------------------------------------------------------------- self-check


def audit(name, accent=None):
    """[(label, ratio, floor, passed)] for the checks that matter on a page."""
    t = get_theme(name, accent)
    rows = [
        ("text on bg", t["text"], t["bg"], 4.5),
        ("strong on bg", t["strong"], t["bg"], 4.5),
        ("muted on bg", t["muted"], t["bg"], 4.5),
        ("dim on bg", t["dim"], t["bg"], 4.5),
        ("accent on bg", t["accent"], t["bg"], 4.5),
        ("text on surface", t["text"], t["surface"], 4.5),
        ("muted on surface", t["muted"], t["surface"], 4.5),
        ("muted on surface-2", t["muted"], t["surface-2"], 4.5),
        ("accent on accent-tint", t["accent"], t["accent-tint"], 4.5),
        ("strong on accent-tint", t["strong"], t["accent-tint"], 4.5),
    ]
    for hue in ("note", "tip", "important", "warning", "caution"):
        rows.append(("%s on %s-tint" % (hue, hue), t[hue], t[hue + "-tint"], 4.5))
    out = []
    for label, fg, bg, floor in rows:
        ratio = contrast_ratio(fg, bg)
        out.append((label, ratio, floor, ratio >= floor))
    return out


def main():
    worst_all = 99.0
    for name in THEME_NAMES:
        tokens = THEMES[name]
        print("%s  (%s ground, bg %s, accent %s)"
              % (name, GROUND[name], tokens["bg"], tokens["accent"]))
        print("  %s" % PURPOSE[name])
        missing = [k for k in REQUIRED_TOKENS if k not in tokens]
        if missing:
            print("  MISSING TOKENS: %s" % ", ".join(missing))
        worst = 99.0
        for label, ratio, floor, ok in audit(name):
            worst = min(worst, ratio)
            print("    %-24s %5.2f:1  %s" % (label, ratio, "pass" if ok else "FAIL"))
        print("    worst ratio in this theme: %.2f:1" % worst)
        worst_all = min(worst_all, worst)
        print("")
    print("worst ratio across all four themes: %.2f:1 (floor 4.50:1)" % worst_all)
    return 0 if worst_all >= 4.5 else 1


if __name__ == "__main__":
    raise SystemExit(main())
