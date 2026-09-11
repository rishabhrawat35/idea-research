#!/usr/bin/env python3
"""Render a tagged markdown answer into one self-contained HTML report.

Usage:  python3 render.py runs/<slug>/ANSWER.md [--theme runs/<slug>/theme.json]

Writes two files next to the input:
  report.html       CSS inlined, no external request except a Google Fonts link
                    when theme.json names a font family
  ANSWER_clean.md   the same content with every block tag and badge stripped,
                    which is the markdown a person is handed

Without --theme the `clinical` theme is used, which is the palette report.css
already carries. With it, the named theme from themes.py is substituted into the
stylesheet's single :root block and theme.json's accent overrides the default
accent. With no --theme flag at all the clinical theme is used and the run
exits 0, because a run with no design stage never had a theme.json. A --theme
that IS passed and cannot be read, holds invalid JSON, or names a theme that is
not one of the four is a failure and exits 1, because a page whose accent no
gate validated must not ship.

Block tags are written in the markdown as HTML comments -- `<!--::verdict-->`
-- so the markdown stays readable and valid anywhere else. A tag applies to the
block that follows it. An untagged document renders as plain prose.

Standard library only. If the third-party `markdown` package happens to be
installed it is used; if it is not, a built-in converter covering the answer's
own markdown -- headings, bold, italic, inline code, links, lists, tables, code
fences -- takes over, so the script runs on a laptop with nothing installed.
No JavaScript is emitted.
"""

import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes  # noqa: E402  the four curated token sets

try:
    import markdown
except ImportError:  # nothing installed: MiniMarkdown below stands in
    markdown = None

HERE = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(HERE, "report.css")

# ---------------------------------------------------------------- tag grammar

# <!--::tag-->  or  <!--::tag|extra-->   (extra = a label, title or summary text)
TAG_RE = re.compile(r"^<!--::\s*([A-Za-z][\w-]*)\s*(?:\|\s*(.*?))?\s*-->\s*$")
ANY_COMMENT_RE = re.compile(r"^<!--.*-->\s*$")

CALLOUTS = {
    "note": "Note",
    "tip": "Tip",
    "important": "Important",
    "warn": "Warning",
    "warning": "Warning",
    "caution": "Caution",
}
CALLOUT_CLASS = {"warn": "warning"}

# stat item:  "18,000 :: what a couple spends"   (em dash and " - " also accepted)
# "\u2014" is written as an escape on purpose: no file in this build carries a
# literal em dash, and the character is still accepted as a separator.
STAT_SPLIT_RE = re.compile("\\s*(?:::|\u2014|\\s-\\s)\\s*")
# metadata strip inside a finding:  "COST: 2,000 | EFFORT: 2 days"
STRIP_RE = re.compile(r"^[A-Z][A-Za-z ]{1,18}:\s*[^|]+(\|\s*[A-Z][A-Za-z ]{1,18}:\s*[^|]+)*$")
LIST_RE = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s)")
# field separator inside ::ranked, ::timeline and ::asks. Only "::", so a claim
# may contain a hyphen or a dash without being cut in half.
FIELD_RE = re.compile(r"\s*::\s*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
# a heading that already carries its own number: "00 . Title", "6. Title", "3 - Title"
HEADNUM_RE = re.compile("^(\\d+)\\s*(?:[.)\u00b7\u2013\u2014:-]\\s*)+")
BADGE_RE = re.compile(r"\[\[(?:(ok|warn|bad|flat):)?([^\]\n|]{1,40})\]\]")


def shown_path(path):
    """The path as the caller would type it, so the printed line is portable.

    Printing the absolute path made the renderer name the checkout it ran in,
    which nobody reading that output in a README or a chat can reproduce.
    """
    try:
        rel = os.path.relpath(path, os.getcwd())
    except ValueError:
        return path
    return path if rel.startswith(os.pardir) else rel


def slug(text):
    s = re.sub(r"<[^>]+>", "", text).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "section"


def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text).strip()


# ---------------------------------------------------------------- block reader


def read_blocks(text):
    """Split source into [(tag, extra, lines)]. A block is contiguous non-blank lines."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").expandtabs(4).split("\n")
    blocks, buf, tag, extra, pending = [], [], None, None, None
    fence = None

    def flush():
        nonlocal buf, tag, extra
        if buf:
            blocks.append((tag, extra, buf))
        buf, tag, extra = [], None, None

    for line in lines:
        fence_hit = re.match(r"^\s*(```|~~~)", line)
        if fence:
            buf.append(line)
            if fence_hit:
                fence = None
                flush()
            continue
        if fence_hit:
            flush()
            fence = fence_hit.group(1)
            buf.append(line)
            continue
        m = TAG_RE.match(line)
        if m:
            flush()
            pending = (m.group(1).lower(), m.group(2))
            continue
        if not line.strip():
            flush()
            continue
        if ANY_COMMENT_RE.match(line) and not buf:
            continue  # an unrelated HTML comment, dropped
        if HEADING_RE.match(line):
            # a heading is always its own block, even with no blank line under it
            keep = pending
            flush()
            if keep:
                tag, extra = keep
                pending = None
            buf.append(line)
            flush()
            continue
        if not buf and pending:
            tag, extra = pending
            pending = None
        buf.append(line)
    flush()

    # merge adjacent untagged list blocks so a loose list stays one list
    merged = []
    for blk in blocks:
        if (
            merged
            and blk[0] is None
            and merged[-1][0] is None
            and LIST_RE.match(blk[2][0])
            and LIST_RE.match(merged[-1][2][0])
        ):
            merged[-1][2].extend([""] + blk[2])
        else:
            merged.append((blk[0], blk[1], list(blk[2])))
    return merged


# ---------------------------------------------------------------- table fixups


def label_table(table_html):
    """Add data-label to every td from the header row, and mark a winning row."""
    heads = [strip_tags(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", table_html, re.S)]
    if not heads:
        return table_html

    def fix_row(match):
        row = match.group(0)
        idx = [0]

        def fix_cell(cm):
            i = idx[0]
            idx[0] += 1
            label = heads[i] if i < len(heads) else ""
            attrs, inner = cm.group(1), cm.group(2)
            if "data-label" in attrs:
                return cm.group(0)
            return '<td%s data-label="%s">%s</td>' % (attrs, html.escape(label, quote=True), inner)

        row = re.sub(r"<td([^>]*)>(.*?)</td>", fix_cell, row, flags=re.S)
        # a row whose first cell is bold is the winning option; tint the whole row
        if re.match(r"<tr>\s*<td[^>]*>\s*<strong>", row):
            row = row.replace("<tr>", '<tr class="win">', 1)
        return row

    body = re.search(r"<tbody>(.*?)</tbody>", table_html, re.S)
    if not body:
        return re.sub(r"<tr>.*?</tr>", fix_row, table_html, flags=re.S)
    fixed = re.sub(r"<tr>.*?</tr>", fix_row, body.group(1), flags=re.S)
    return table_html.replace(body.group(1), fixed)


def wrap_tables(chunk, compare=False):
    cls = "tablewrap compare" if compare else "tablewrap"
    out = []
    pos = 0
    for m in re.finditer(r"<table>.*?</table>", chunk, re.S):
        out.append(chunk[pos : m.start()])
        out.append('<div class="%s">%s</div>' % (cls, label_table(m.group(0))))
        pos = m.end()
    out.append(chunk[pos:])
    return "".join(out)


# ------------------------------------------------------------- fallback markdown

# The block tags are consumed by read_blocks before any of this runs, so the
# converter only ever sees the inside of one block: prose, a list, a table, a
# fence or a heading line. That is the whole subset an ANSWER.md contains, which
# is why a converter this small is enough when the markdown package is missing.
# It emits the same shapes python-markdown does -- bare <table>/<thead>/<tbody>,
# one <p> around a lone paragraph -- because label_table, wrap_tables and
# md_inline read that HTML back.

MINI_FENCE_RE = re.compile(r"^\s*(```|~~~)\s*([\w.+#-]*)\s*$")
MINI_TABLE_SEP_RE = re.compile(r"^\s*\|?(?:\s*:?-{2,}:?\s*\|)+\s*:?-{2,}:?\s*\|?\s*$")
MINI_ITEM_RE = re.compile(r"^(\s*)(?:([-*+])|(\d+)[.)])\s+(.*)$")
MINI_RULE_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
MINI_CODESPAN_RE = re.compile(r"(`+)([^\n]+?)\1")
MINI_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+.!|>~-])")
MINI_LINK_RE = re.compile(r"\[([^\]\n]*)\]\(\s*<?([^\s<>)]*)>?(?:\s+\"[^\"]*\")?\s*\)")
MINI_BOLD_RE = re.compile(r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1", re.S)
MINI_ITAL_STAR_RE = re.compile(r"\*(?=\S)([^*\n]+?)(?<=\S)\*")
MINI_ITAL_US_RE = re.compile(r"(?<![A-Za-z0-9_])_(?=\S)([^_\n]+?)(?<=\S)_(?![A-Za-z0-9_])")
MINI_AMP_RE = re.compile(r"&(?!#?\w{1,32};)")
MINI_BREAK_RE = re.compile(r"  +\n")
MINI_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")
MINI_HOLD = "\x00%d\x00"
MINI_HOLD_RE = re.compile(r"\x00(\d+)\x00")


def mini_escape(text):
    """Escape what HTML needs escaping, leaving existing entities alone."""
    return MINI_AMP_RE.sub("&amp;", text).replace("<", "&lt;").replace(">", "&gt;")


def mini_inline(text):
    """`code`, **bold**, *italic*, [links](url) and backslash escapes."""
    held = []

    def hold(value):
        held.append(value)
        return MINI_HOLD % (len(held) - 1)

    text = MINI_ESCAPE_RE.sub(lambda m: hold(mini_escape(m.group(1))), text)
    text = MINI_CODESPAN_RE.sub(
        lambda m: hold("<code>%s</code>" % mini_escape(m.group(2).strip())), text)
    text = MINI_BREAK_RE.sub("<br />\n", mini_escape(text))
    text = MINI_LINK_RE.sub(
        lambda m: '<a href="%s">%s</a>' % (m.group(2).replace('"', "%22"), m.group(1)),
        text)
    text = MINI_BOLD_RE.sub(lambda m: "<strong>%s</strong>" % m.group(2), text)
    text = MINI_ITAL_STAR_RE.sub(lambda m: "<em>%s</em>" % m.group(1), text)
    text = MINI_ITAL_US_RE.sub(lambda m: "<em>%s</em>" % m.group(1), text)
    return MINI_HOLD_RE.sub(lambda m: held[int(m.group(1))], text)


def mini_cells(row, width=None):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not row.endswith("\\|"):
        row = row[:-1]
    cells = [c.strip() for c in MINI_CELL_SPLIT_RE.split(row)]
    if width is not None:
        cells = (cells + [""] * width)[:width]
    return cells


def mini_table(lines, i):
    """One pipe table starting at lines[i], header row then separator."""
    heads = mini_cells(lines[i])
    out = ["<table>", "<thead>", "<tr>"]
    out += ["<th>%s</th>" % mini_inline(h) for h in heads]
    out += ["</tr>", "</thead>", "<tbody>"]
    j = i + 2
    while j < len(lines) and lines[j].strip() and "|" in lines[j]:
        out.append("<tr>")
        out += ["<td>%s</td>" % mini_inline(c)
                for c in mini_cells(lines[j], len(heads))]
        out.append("</tr>")
        j += 1
    out += ["</tbody>", "</table>"]
    return "\n".join(out), j


def mini_list(entries, at, indent, loose):
    """Emit one <ul>/<ol> from flat (indent, ordered, body) entries."""
    tag = "ol" if entries[at][1] else "ul"
    items, i = [], at
    while i < len(entries):
        ind, _ordered, body = entries[i]
        if ind < indent:
            break
        if ind > indent:  # a deeper marker: a list inside the item above it
            child, i = mini_list(entries, i, ind, loose)
            if items:
                items[-1] += child + "\n"
            continue
        items.append("\n<p>%s</p>\n" % mini_inline(body) if loose
                     else mini_inline(body))
        i += 1
    return ("<%s>\n%s\n</%s>"
            % (tag, "\n".join("<li>%s</li>" % it for it in items), tag), i)


def mini_convert(text):
    lines = text.replace("\r\n", "\n").replace("\r", "\n").expandtabs(4).split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        fence = MINI_FENCE_RE.match(line)
        if fence:
            body, i = [], i + 1
            while i < len(lines) and not MINI_FENCE_RE.match(lines[i]):
                body.append(lines[i])
                i += 1
            i += 1  # closing fence, or the end of the block
            cls = ' class="language-%s"' % fence.group(2) if fence.group(2) else ""
            out.append("<pre><code%s>%s\n</code></pre>"
                       % (cls, mini_escape("\n".join(body))))
            continue

        head = HEADING_RE.match(line)
        if head:
            level = len(head.group(1))
            out.append("<h%d>%s</h%d>"
                       % (level, mini_inline(head.group(2).strip()), level))
            i += 1
            continue

        if MINI_RULE_RE.match(line):
            out.append("<hr>")
            i += 1
            continue

        if (i + 1 < len(lines) and "|" in line
                and MINI_TABLE_SEP_RE.match(lines[i + 1])):
            chunk, i = mini_table(lines, i)
            out.append(chunk)
            continue

        if line.lstrip().startswith(">"):
            quoted = []
            while i < len(lines) and lines[i].strip():
                quoted.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>\n%s\n</blockquote>" % mini_convert("\n".join(quoted)))
            continue

        first = MINI_ITEM_RE.match(line)
        if first:
            base, ordered = len(first.group(1)), first.group(3) is not None

            def other_kind(m):
                """A bullet list under a numbered one is a list of its own."""
                return len(m.group(1)) == base and (m.group(3) is not None) != ordered

            entries, loose, blank = [], False, False
            while i < len(lines):
                if not lines[i].strip():
                    # a blank line ends the list unless another item of the
                    # same kind follows, which makes the list a loose one
                    nxt = (MINI_ITEM_RE.match(lines[i + 1])
                           if i + 1 < len(lines) else None)
                    if nxt and not other_kind(nxt):
                        blank = True
                        i += 1
                        continue
                    break
                m = MINI_ITEM_RE.match(lines[i])
                if m:
                    if other_kind(m):
                        break
                    entries.append((len(m.group(1)), m.group(3) is not None,
                                    m.group(4).strip()))
                    if blank:
                        loose = True
                elif entries:  # a wrapped continuation line
                    ind, was_ordered, body = entries[-1]
                    entries[-1] = (ind, was_ordered, body + " " + lines[i].strip())
                else:
                    break
                i += 1
            if entries:
                chunk, _ = mini_list(entries, 0, entries[0][0], loose)
                out.append(chunk)
            continue

        # A paragraph runs to the blank line. List markers hanging off the end
        # of a paragraph with no blank line above them stay part of the
        # paragraph, which is what a list needing a blank line before it means.
        para = []
        while i < len(lines) and lines[i].strip():
            if para and (HEADING_RE.match(lines[i]) or MINI_FENCE_RE.match(lines[i])
                         or MINI_RULE_RE.match(lines[i])):
                break
            if (para and "|" in lines[i] and i + 1 < len(lines)
                    and MINI_TABLE_SEP_RE.match(lines[i + 1])):
                break
            # two trailing spaces are a hard line break, so they survive
            hard = "  " if lines[i].endswith("  ") else ""
            para.append(lines[i].strip() + hard)
            i += 1
        out.append("<p>%s</p>" % mini_inline("\n".join(para)))
    return "\n".join(out)


class MiniMarkdown(object):
    """Stands in for markdown.Markdown: same reset().convert() shape."""

    def reset(self):
        return self

    def convert(self, text):
        return mini_convert(text)


# ---------------------------------------------------------------- markdown glue

if markdown is None:
    MD = MiniMarkdown()
else:
    MD = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"])


def md_inline(text):
    """Inline markdown only: no wrapping <p>."""
    out = MD.reset().convert(text.strip())
    out = out.strip()
    if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return badges(out)


def md_block(text, compare=False):
    return wrap_tables(badges(MD.reset().convert(text)), compare=compare)


def badges(chunk):
    def one(m):
        tone, label = m.group(1), m.group(2)
        cls = "badge " + tone if tone else "badge"
        return '<span class="%s">%s</span>' % (cls, html.escape(label.strip()))

    return BADGE_RE.sub(one, chunk)


# ---------------------------------------------------------------- components


def c_verdict(lines, extra):
    label = extra or "Recommendation"
    body = md_block("\n".join(lines))
    return '<section class="verdict"><span class="label">%s</span>%s</section>' % (
        html.escape(label),
        body,
    )


def c_stat(lines, extra):
    items = []
    for raw in lines:
        line = re.sub(LIST_RE, "", raw).strip()
        if not line:
            continue
        parts = STAT_SPLIT_RE.split(line, maxsplit=1)
        if len(parts) == 2:
            value, label = parts
        else:
            bits = line.split(None, 1)
            value, label = bits[0], (bits[1] if len(bits) > 1 else "")
        items.append(
            "<div class=\"stat\"><b>%s</b><span>%s</span></div>"
            % (md_inline(value), md_inline(label))
        )
    if not items:
        return ""
    return '<div class="stats">%s</div>' % "".join(items)


def c_finding(lines, extra):
    claim, evidence, strip, nxt = None, [], None, None
    for raw in lines:
        line = re.sub(LIST_RE, "", raw).strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("next:"):
            nxt = line.split(":", 1)[1].strip()
        elif STRIP_RE.match(line) and strip is None:
            strip = line
        elif claim is None:
            claim = line
        else:
            evidence.append(line)
    parts = []
    if claim:
        parts.append('<p class="claim">%s</p>' % md_inline(claim))
    if evidence:
        parts.append('<p class="evidence">%s</p>' % md_inline(" ".join(evidence)))
    if strip:
        pairs = []
        for pair in strip.split("|"):
            if ":" not in pair:
                continue
            k, v = pair.split(":", 1)
            pairs.append(
                '<span class="pair"><span class="k">%s</span><span class="v">%s</span></span>'
                % (md_inline(k.strip()), md_inline(v.strip()))
            )
        if pairs:
            parts.append('<div class="strip">%s</div>' % "".join(pairs))
    if nxt:
        parts.append('<p class="next"><b>Next:</b> %s</p>' % md_inline(nxt))
    if not parts:
        return ""
    return '<div class="finding">%s</div>' % "".join(parts)


def c_callout(lines, extra, kind):
    cls = CALLOUT_CLASS.get(kind, kind)
    title = extra or CALLOUTS.get(kind, kind.title())
    return '<div class="callout %s"><div class="title">%s</div>%s</div>' % (
        cls,
        html.escape(title),
        md_block("\n".join(lines)),
    )


def c_quote(lines, extra):
    body, attrib = [], extra
    for raw in lines:
        line = raw.strip()
        if line.startswith(("\u2014", "--", "-- ")) and len(body) > 0:
            attrib = line.lstrip("\u2014- ").strip()
        else:
            body.append(line)
    out = md_block("\n".join(body))
    if attrib:
        out += '<span class="attrib">%s</span>' % md_inline(attrib)
    return "<blockquote>%s</blockquote>" % out


def c_steps(lines, extra):
    items = [re.sub(LIST_RE, "", l).strip() for l in lines if l.strip()]
    return '<ol class="steps">%s</ol>' % "".join(
        "<li>%s</li>" % md_inline(i) for i in items
    )


def c_cards(lines, extra):
    cards = []
    for raw in lines:
        line = re.sub(LIST_RE, "", raw).strip()
        if not line:
            continue
        parts = STAT_SPLIT_RE.split(line, maxsplit=1)
        name = parts[0]
        desc = parts[1] if len(parts) == 2 else ""
        cards.append(
            "<div class=\"card\"><b>%s</b><span>%s</span></div>"
            % (md_inline(name), md_inline(desc))
        )
    return '<div class="cards">%s</div>' % "".join(cards)


def c_figure(lines, extra):
    title = extra or ""
    src = ""
    body = []
    for raw in lines:
        line = raw.strip()
        if line.lower().startswith("source:"):
            src = line.split(":", 1)[1].strip()
        else:
            body.append(line)
    out = "<figure>"
    if title:
        out += '<div class="fig-title">%s</div>' % md_inline(title)
    out += '<div class="fig-body">%s</div>' % md_block("\n".join(body))
    if src:
        out += "<figcaption>Source: %s</figcaption>" % md_inline(src)
    return out + "</figure>"


def _items(lines):
    """Split a block into [(first_line_fields, [continuation lines])].

    A line that opens with a list marker starts an item. Any other line belongs
    to the item above it, so a writer may put the long half on its own line.
    """
    out = []
    for raw in lines:
        if not raw.strip():
            continue
        if LIST_RE.match(raw) or not out:
            body = re.sub(LIST_RE, "", raw).strip()
            out.append([FIELD_RE.split(body), []])
        else:
            out[-1][1].append(raw.strip())
    return out


def c_ranked(lines, extra):
    """::ranked  an ordered list where the order is the argument.

    `claim :: why it ranks there`, or the why on the next line. The number is a
    CSS counter reset at the PART heading, so a second ::ranked block in the
    same part carries on from where the first one stopped.
    """
    items = []
    for fields, extra_lines in _items(lines):
        claim = fields[0].strip()
        why = " ".join([f.strip() for f in fields[1:] if f.strip()] + extra_lines)
        if not claim:
            continue
        row = '<p class="rank-claim">%s</p>' % md_inline(claim)
        if why.strip():
            row += '<p class="rank-why">%s</p>' % md_inline(why.strip())
        items.append("<li>%s</li>" % row)
    if not items:
        return ""
    return '<ol class="ranked">%s</ol>' % "".join(items)


def c_timeline(lines, extra):
    """::timeline  a phased plan.

    `phase :: the item :: the number that means it worked`. Rows sharing a phase
    label collapse into one node on the rule, so a horizon with two items reads
    as one horizon rather than two.
    """
    rows = []
    for fields, extra_lines in _items(lines):
        fields = [f.strip() for f in fields] + ["", ""]
        phase, item, metric = fields[0], fields[1], fields[2]
        if extra_lines and not metric:
            metric = " ".join(extra_lines)
        elif extra_lines:
            item = (item + " " + " ".join(extra_lines)).strip()
        if not item and phase:  # a single field is the item, under the phase above
            item, phase = phase, ""
        if not item:
            continue
        if phase and rows and rows[-1][0] == phase:
            phase = ""
        rows.append((phase, item, metric))

    phases, out = [], []
    for phase, item, metric in rows:
        if phase or not phases:
            phases.append([phase, []])
        phases[-1][1].append((item, metric))
    for label, entries in phases:
        cells = []
        for item, metric in entries:
            cell = '<span class="item">%s</span>' % md_inline(item)
            if metric:
                cell += '<span class="metric">%s</span>' % md_inline(metric)
            cells.append("<li>%s</li>" % cell)
        out.append(
            '<div class="phase"><p class="phase-label">%s</p>'
            '<ul class="phase-items">%s</ul></div>'
            % (md_inline(label) if label else "", "".join(cells))
        )
    if not out:
        return ""
    return '<div class="timeline">%s</div>' % "".join(out)


def c_asks(lines, extra):
    """::asks  the people to approach.

    `name :: why them :: question | question`, or one question per following
    line. Each question becomes its own ruled row, which is what stops a card
    of three questions from reading as a paragraph.
    """
    cards = []
    for fields, extra_lines in _items(lines):
        fields = [f.strip() for f in fields]
        who = fields[0]
        why = fields[1] if len(fields) > 1 else ""
        questions = []
        for chunk in fields[2:] + extra_lines:
            for part in chunk.split("|"):
                part = part.strip()
                if part:
                    questions.append(part)
        if not who:
            continue
        card = '<div class="who">%s</div>' % md_inline(who)
        if why:
            card += '<div class="why">%s</div>' % md_inline(why)
        if questions:
            card += '<ul class="qs">%s</ul>' % "".join(
                "<li>%s</li>" % md_inline(q) for q in questions)
        cards.append('<div class="ask">%s</div>' % card)
    if not cards:
        return ""
    return '<div class="asks">%s</div>' % "".join(cards)


def c_meta(lines, extra):
    bits = []
    fields = []
    for raw in lines:
        fields.extend(re.sub(LIST_RE, "", raw).split("|"))
    for line in fields:
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            bits.append("<span><b>%s</b> %s</span>" % (md_inline(k.strip()), md_inline(v.strip())))
        else:
            bits.append("<span>%s</span>" % md_inline(line))
    return '<div class="meta-header">%s</div>' % "".join(bits)


# ---------------------------------------------------------------- theme

def wrong_shape(path, want="file"):
    """Return one line naming a path of the wrong shape, or "" when it is fine.

    Every other script in this pipeline takes runs/<slug>/, so handing this one
    the run directory is the ordinary typo. os.path.exists is true for a
    directory, which is how that typo used to reach open() and raise
    IsADirectoryError with a traceback.
    """
    if want == "file":
        if os.path.isdir(path):
            return ("%s is a directory, not a file. render takes the markdown "
                    "file inside the run: %s"
                    % (path, os.path.join(path, "ANSWER.md")))
        if not os.path.isfile(path):
            return "no such file: %s" % path
        return ""
    if os.path.isfile(path):
        return ("%s is a file, not a directory. Pass the directory that holds "
                "it: %s" % (path, os.path.dirname(os.path.abspath(path)) or "."))
    if not os.path.isdir(path):
        return "no such directory: %s" % path
    return ""


HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
ROOT_RE = re.compile(r":root\s*\{.*?\n\}", re.S)


def load_theme(path):
    """Read theme.json. Return (spec, notes, fatal). Never raises, never crashes.

    spec keys: theme, accent, display, body, density. notes are lines for stdout
    explaining any fallback that is still safe, because a silent fallback is how
    a page ships in the wrong palette. Unknown keys in the file are ignored
    rather than failing.

    fatal is None, or one line saying why the theme could not be trusted. It is
    only ever set when a --theme path was passed, and the caller turns it into
    exit 1: a theme.json that was asked for and could not be read is a mistyped
    path, and falling back to clinical there ships an accent no gate measured.
    No --theme at all is not an error, it is the documented default.
    """
    spec = {"theme": themes.DEFAULT_THEME, "accent": None,
            "display": None, "body": None, "density": "regular"}
    notes = []
    if not path:
        return spec, notes, None
    shape = wrong_shape(path, "file")
    if shape:
        if os.path.isdir(path):
            return spec, notes, ("--theme %s is a directory, not a file. Pass "
                                 "the theme.json inside it: %s"
                                 % (path, os.path.join(path, "theme.json")))
        return spec, notes, ("--theme %s does not exist, so no theme was "
                             "validated" % path)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (IOError, OSError) as err:
        return spec, notes, ("--theme %s could not be read (%s), so no theme "
                             "was validated" % (path, err))
    except ValueError as err:
        return spec, notes, ("--theme %s is not valid JSON (%s), so no theme "
                             "was validated" % (path, err))
    if not isinstance(data, dict):
        return spec, notes, ("--theme %s must hold a JSON object, so no theme "
                             "was validated" % path)

    name = str(data.get("theme", "") or "").strip().lower()
    if name in themes.THEMES:
        spec["theme"] = name
    elif name:
        return spec, notes, ('--theme %s names "%s", which is not one of: %s'
                             % (path, name, ", ".join(sorted(themes.THEMES))))
    else:
        return spec, notes, ("--theme %s names no theme. It needs a \"theme\" "
                             "key holding one of: %s"
                             % (path, ", ".join(sorted(themes.THEMES))))

    accent = str(data.get("accent", "") or "").strip()
    if accent and HEX_RE.match(accent):
        spec["accent"] = accent
    elif accent:
        notes.append('theme.json accent "%s" is not a hex colour, '
                     "using the theme's own accent" % accent)

    typ = data.get("type")
    if isinstance(typ, dict):
        spec["display"] = str(typ.get("display", "") or "").strip() or None
        spec["body"] = str(typ.get("body", "") or "").strip() or None
    density = str(data.get("density", "") or "").strip().lower()
    if density in ("compact", "regular"):
        spec["density"] = density
    return spec, notes, None


def apply_theme(css, spec):
    """Substitute one token set into the stylesheet's single :root block.

    There is one stylesheet, not four. report.css ships with the clinical set
    inline so it is readable and testable on its own, and this replaces those
    declarations at build time.
    """
    root = ROOT_RE.search(css)
    if not root:
        return css
    block = ":root {\n%s\n}" % themes.css_root(
        spec["theme"], spec.get("accent"), spec.get("body"), spec.get("display"))
    return css[:root.start()] + block + css[root.end():]


def font_link(spec):
    """The one external reference the page is allowed, and only when asked for."""
    families = []
    for key in ("body", "display"):
        family = (spec.get(key) or "").strip()
        if (family and family.lower() != "system"
                and re.fullmatch(r"[A-Za-z0-9 ]{2,40}", family)
                and family not in families):
            families.append(family)
    if not families:
        return ""
    query = "&amp;".join(
        "family=%s:ital,wght@0,400;0,600;0,700;1,400" % f.replace(" ", "+")
        for f in families)
    return ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
            '%s&amp;display=swap">\n' % query)


# ---------------------------------------------------------------- main render


def render_block(tag, extra, lines, state):
    """Return (html, kind). kind is 'heading2' when the block opens a new section."""
    text = "\n".join(lines)

    hm = HEADING_RE.match(lines[0]) if lines else None
    if hm and len(lines) == 1:
        level, body = len(hm.group(1)), hm.group(2).strip()
        if level == 1:
            state["title"] = strip_tags(body)
            return "<h1>%s</h1>" % md_inline(body), "h1"
        cls = ""
        num = HEADNUM_RE.match(body)
        if level == 2 and num:
            if state["first_h2_num"] is None:
                state["first_h2_num"] = int(num.group(1))
            body = body[num.end():].strip()
        elif level == 2 and state["first_h2_num"] is None:
            state["first_h2_num"] = 1
        sid = slug(body)
        return '<h%d id="%s"%s>%s</h%d>' % (level, sid, cls, md_inline(body), level), (
            "h2" if level == 2 else "h%d" % level
        )

    # a lone italic line straight after a heading is the section subtitle
    if (
        tag is None
        and state.get("after_heading")
        and len(lines) == 1
        and re.fullmatch(r"\*[^*].*\*|_[^_].*_", lines[0].strip())
    ):
        return '<p class="dek">%s</p>' % md_inline(lines[0].strip()[1:-1]), "dek"

    if tag == "verdict":
        return c_verdict(lines, extra), "block"
    if tag == "stat" or tag == "stats":
        return c_stat(lines, extra), "block"
    if tag == "finding":
        return c_finding(lines, extra), "finding"
    if tag in CALLOUTS:
        return c_callout(lines, extra, tag), "block"
    if tag == "quote":
        return c_quote(lines, extra), "block"
    if tag in ("steps", "step"):
        return c_steps(lines, extra), "block"
    if tag == "cards":
        return c_cards(lines, extra), "block"
    if tag == "ranked":
        return c_ranked(lines, extra), "block"
    if tag == "timeline":
        return c_timeline(lines, extra), "block"
    if tag == "asks":
        return c_asks(lines, extra), "block"
    if tag == "figure":
        return c_figure(lines, extra), "block"
    if tag == "meta":
        return c_meta(lines, extra), "meta"
    if tag == "compare":
        return md_block(text, compare=True), "block"

    if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", lines[0].strip()) and len(lines) == 1:
        return "<hr>", "hr"
    return md_block(text), "block"


def wrap_findings(parts):
    """Group runs of consecutive .finding cards into one counter scope."""
    out, run = [], []
    for kind, chunk in parts:
        if kind == "finding":
            run.append(chunk)
            continue
        if run:
            out.append('<div class="findings">%s</div>' % "".join(run))
            run = []
        out.append(chunk)
    if run:
        out.append('<div class="findings">%s</div>' % "".join(run))
    return out


def render(src_text, spec=None):
    spec = spec or {"theme": themes.DEFAULT_THEME}
    state = {"title": "Report", "first_h2_num": None, "after_heading": False}
    blocks = read_blocks(src_text)

    rendered = []  # (kind, html, tag, extra, raw_heading_text)
    for tag, extra, lines in blocks:
        chunk, kind = render_block(tag, extra, lines, state)
        state["after_heading"] = kind in ("h1", "h2", "h3", "h4")
        if not chunk:
            continue
        heading_text = strip_tags(chunk) if kind.startswith("h") else ""
        rendered.append({"kind": kind, "html": chunk, "tag": tag, "extra": extra,
                         "head": heading_text})

    # appendix sections: an explicit ::appendix tag on a heading, or any "## Appendix ..."
    body_parts = []
    i = 0
    while i < len(rendered):
        item = rendered[i]
        is_h2 = item["kind"] == "h2"
        appendix = is_h2 and (
            item["tag"] == "appendix"
            or re.match(r"^\s*(?:\d+[.)·-]*\s*)?appendix\b", item["head"], re.I)
        )
        if appendix:
            summary = item["head"]
            inner = []
            j = i + 1
            while j < len(rendered) and rendered[j]["kind"] not in ("h1", "h2"):
                if rendered[j]["kind"] != "hr":
                    inner.append((rendered[j]["kind"], rendered[j]["html"]))
                j += 1
            count = item["extra"] or ""
            body_parts.append(
                (
                    "block",
                    "<details><summary><span>%s</span>%s</summary>%s</details>"
                    % (
                        html.escape(summary),
                        '<span class="count">%s</span>' % html.escape(count) if count else "",
                        "".join(wrap_findings(inner)),
                    ),
                )
            )
            i = j
            continue
        if item["tag"] == "appendix" and not is_h2:
            body_parts.append(
                (
                    "block",
                    "<details><summary><span>%s</span></summary>%s</details>"
                    % (html.escape(item["extra"] or "Appendix"), item["html"]),
                )
            )
            i += 1
            continue
        body_parts.append((item["kind"], item["html"]))
        i += 1

    body = "".join(wrap_findings(body_parts))

    css = ""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, encoding="utf-8") as fh:
            css = fh.read()
    css = apply_theme(css, spec)

    classes = "report"
    if state["first_h2_num"] == 0:
        classes += " zero-based"
    if spec.get("density") == "compact":
        classes += " compact"
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n%s<style>\n%s</style>\n</head>\n<body>\n"
        '<main class="%s">\n%s\n</main>\n</body>\n</html>\n'
        % (html.escape(state["title"]), font_link(spec), css, classes, body)
    )


# ------------------------------------------------------------- clean markdown

# A badge carries meaning, so it must not vanish. `[[warn:Thin]]` becomes
# "(status: Thin)": the writer's own word survives, nothing is invented, and a
# reader who never saw the engine still understands it is a marker on the claim.
def clean_badge(match):
    return "(status: %s)" % match.group(2).strip()


def clean_markdown(src_text):
    """The same answer with every block tag and badge gone.

    This is the file a person is handed, so it must contain no engine syntax at
    all: no `<!--` comment, no `[[badge]]`, and no `::` field separator. A tag's
    label after the pipe does carry meaning, so it is promoted to a bold lead-in
    line rather than dropped, except on a tag that sits above a heading.
    """
    lines = src_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = TAG_RE.match(line)
        if m:
            tag = m.group(1).lower()
            label = (m.group(2) or "").strip()
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            follows_heading = bool(j < len(lines) and HEADING_RE.match(lines[j]))
            if label and tag != "appendix" and not follows_heading:
                out.append("**%s**" % label)
                out.append("")
            i += 1
            continue
        if ANY_COMMENT_RE.match(line):
            i += 1
            continue
        out.append(line)
        i += 1

    text = "\n".join(out)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)     # any inline comment
    text = BADGE_RE.sub(clean_badge, text)                  # [[warn:Thin]]
    text = re.sub(r"[ \t]*::[ \t]*", " - ", text)           # component fields
    text = re.sub(r"^ +- ", "- ", text, flags=re.M)
    # inside a list item a pipe separated two questions, and the question marks
    # already separate them. A table row starts with "|", so it is untouched.
    text = re.sub(r"^(\s*[-*+] .*)$",
                  lambda m: re.sub(r"[ \t]*\|[ \t]*", " ", m.group(1)),
                  text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def count_tags(src_text):
    found = {}
    for line in src_text.split("\n"):
        m = TAG_RE.match(line)
        if m:
            found[m.group(1).lower()] = found.get(m.group(1).lower(), 0) + 1
    return found


def main(argv):
    args, src, theme_path = argv[1:], None, None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--theme":
            i += 1
            if i >= len(args):
                sys.stderr.write("--theme needs a path to theme.json\n")
                return 2
            theme_path = args[i]
        elif arg.startswith("--theme="):
            theme_path = arg.split("=", 1)[1]
        elif arg in ("-h", "--help"):
            print(__doc__.strip())
            return 0
        elif arg.startswith("-"):
            sys.stderr.write("unknown option: %s\n" % arg)
            return 2
        elif src is None:
            src = arg
        else:
            sys.stderr.write("too many arguments: %s\n" % arg)
            return 2
        i += 1
    if src is None:
        print(__doc__.strip())
        return 2

    src = os.path.abspath(src)
    shape = wrong_shape(src, "file")
    if shape:
        sys.stderr.write("render: " + shape + "\n")
        return 1
    with open(src, encoding="utf-8") as fh:
        text = fh.read()

    spec, notes, fatal = load_theme(theme_path)
    if fatal:
        sys.stderr.write("render: " + fatal + "\n")
        sys.stderr.write("render: nothing was written. Fix the path or drop "
                         "--theme to render on the %s theme.\n"
                         % themes.DEFAULT_THEME)
        return 1
    for note in notes:
        print(note)

    out_dir = os.path.dirname(src)
    html_path = os.path.join(out_dir, "report.html")
    clean_path = os.path.join(out_dir, "ANSWER_clean.md")
    page = render(text, spec)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    clean = clean_markdown(text)
    with open(clean_path, "w", encoding="utf-8") as fh:
        fh.write(clean)

    tokens = themes.get_theme(spec["theme"], spec.get("accent"))
    print("theme: %s (%s ground), accent %s, density %s"
          % (spec["theme"], themes.GROUND[spec["theme"]], tokens["accent"],
             spec.get("density", "regular")))
    fonts = [f for f in (spec.get("body"), spec.get("display")) if f]
    print("fonts: %s" % (", ".join(fonts) if fonts else "system stack only"))
    print("wrote %s (%d bytes)" % (shown_path(html_path), len(page.encode("utf-8"))))
    print("wrote %s (%d bytes)" % (shown_path(clean_path), len(clean.encode("utf-8"))))
    if markdown is None:
        print("note: the markdown package is not installed, so the built-in "
              "converter was used (headings, bold, italic, code, links, lists, "
              "tables, fences). For the full parser: python3 -m pip install markdown")
    tags = count_tags(text)
    if tags:
        print("tags found: " + ", ".join("%s x%d" % (k, v) for k, v in sorted(tags.items())))
    else:
        print("tags found: none (rendered as plain prose)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
