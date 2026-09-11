#!/usr/bin/env python3
"""Pull every factual claim out of a run's research files into a ledger.

Usage:  python3 tools/claims.py runs/<slug>/

Reads every .md file in the run directory and its lanes/ subdirectory, minus
the files this pipeline generates itself. Nothing is hardcoded, so a renamed
or added stage file is audited without editing this script, and the stage
files of older runs still audit exactly as before.

Writes three files into the run directory. claims.jsonl holds one claim per
line, claims_summary.md holds every row, and claims_brief.md holds the counts
and one compact line per shaky row that carries a figure. This replaces the
analyst writing the evidence ledger by hand. A stage that only needs to know
which figures are shaky reads the brief, so it does not re-read the ledger.

Exit 0 on success, 1 on a real failure, 2 on bad usage. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

USAGE = "usage: python3 claims.py runs/<slug>/"

# Files this pipeline writes into the run directory. Auditing them would make
# the script read its own output: claims_summary.md would re-import every claim
# as a table row, and ANSWER.md would re-import the ones already counted from
# the files it was written from. Compared lowercase, so ANSWER.md and answer.md
# are both recognised.
GENERATED_NAMES = ("claims_summary.md", "claims_brief.md", "contradictions.md",
                   "verify_queue.md", "ANSWER.md", "ANSWER_clean.md", "_state.md",
                   "layout.md", "07_ux.md", "06_edit.md")
GENERATED = {name.lower() for name in GENERATED_NAMES}

URL_RE = re.compile(r"https?://[^\s<>)\]\"'|]+")

NUM = r"\d+(?:,\d{3})*(?:\.\d+)?"
SCALE = r"(?:\s*(?:crore|cr|lakhs|lakh|million|billion|mn|bn|[mk])\b)?"

# Ordered alternatives: currency and percent beat a bare number, so the first
# figure reported for a line is the most informative one on it. The lookbehind
# keeps the match off digits and letters inside identifiers such as "Inc42",
# "Ferty9" or "n=293".
FIGURE_RE = re.compile(
    r"(?<![\w.,-])(?:"
    r"₹\s?" + NUM + SCALE +
    r"|(?:US)?\$\s?" + NUM + SCALE +
    r"|" + NUM + r"\s?(?:%|per cent|percent)"
    r"|" + NUM + r"\s*(?:crore|lakhs|lakh|million|billion|mn|bn|[mk])\b"
    r"|" + NUM +
    r")",
    re.I,
)

YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")

# Phrases a researcher uses when they are telling you the number is not solid.
GUESS_MARKERS = [
    "no source", "no sources", "we're guessing", "we are guessing", "guessing",
    "not found", "could not find", "couldn't find", "cannot find",
    "unverified", "not verified", "never verified", "not re-verified",
    "did not re-verify", "not published", "treat as unknown", "my own arithmetic",
    "my own calculation", "this arithmetic is mine", "assumption", "estimate",
]

LIST_MARKER_RE = re.compile(r"^(?:[-*+]\s+|\d+[.)]\s+|>\s*)")
SKIP_RE = re.compile(r"^(?:#|```|\|?\s*:?-{3,}|\*{3,}|_{3,})")
TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|?$")

HEADING_RE = re.compile(r"^#+\s*(.+)$")

# A SOURCES section repeats, as citations, claims already made in the body.
# Reading it would double-count them and fill the verify sample with URLs.
SKIP_SECTION_RE = re.compile(r"source", re.I)

MIN_WORDS = 4


def first_url(lines, i):
    """First URL on this line or the next two, since citations often trail a
    bullet on their own line. Stops at the next claim line, so a claim never
    borrows the citation belonging to the claim below it."""
    for j in range(i, min(i + 3, len(lines))):
        if j > i and is_claim(clean(lines[j])):
            break
        m = URL_RE.search(lines[j])
        if m:
            return m.group(0).rstrip(".,;:)")
    return ""


def first_figure(text):
    """First figure worth recording. A bare year or a lone digit is not one."""
    for m in FIGURE_RE.finditer(text):
        fig = re.sub(r"\s+", " ", m.group(0)).strip()
        if YEAR_RE.match(fig) or re.match(r"^\d$", fig):
            continue
        return fig
    return ""


def status_of(text, url):
    if url:
        return "sourced"
    low = text.lower()
    if any(mark in low for mark in GUESS_MARKERS):
        return "guess"
    return "unsourced"


def clean(line):
    """Strip the list marker and collapse whitespace; keep the wording intact."""
    return re.sub(r"\s+", " ", LIST_MARKER_RE.sub("", line.strip())).strip()


def is_claim(text):
    """A claim is a content line with real prose in it, not a heading or rule."""
    if not text or SKIP_RE.match(text) or TABLE_SEP_RE.match(text):
        return False
    bare = URL_RE.sub(" ", text).replace("|", " ")
    bare = re.sub(r"[^\w\s%₹$.,-]", " ", bare)
    return len(bare.split()) >= MIN_WORDS


def read_lines(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print("skipped %s: %s" % (path.name, exc))
        return []


def discover(run_dir):
    """Every stage file in the run: *.md in the run directory and in lanes/.

    Sorted by path relative to the run directory, so the ledger comes out in
    the same order every time and reads in stage order: 00_brief.md, 01_scout.md,
    the case files, 05_reconcile.md, then lanes/. Whatever a stage file is
    called, it is audited; the pipeline's own outputs are not.
    """
    candidates = list(run_dir.glob("*.md"))
    lanes_dir = run_dir / "lanes"
    if lanes_dir.is_dir():
        candidates += lanes_dir.glob("*.md")
    paths = [p for p in candidates
             if p.is_file() and p.name.lower() not in GENERATED]
    return sorted(paths, key=lambda p: p.relative_to(run_dir).as_posix())


def collect(run_dir):
    paths = discover(run_dir)

    claims = []
    for path in paths:
        lines = read_lines(path)
        in_fence = False
        in_sources = False
        for i, raw in enumerate(lines):
            if raw.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            heading = HEADING_RE.match(raw.strip())
            if heading:
                in_sources = bool(SKIP_SECTION_RE.search(heading.group(1)))
                continue
            if in_sources:
                continue
            # A row followed by |---|---| is a table heading, not a claim.
            if i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1].strip()):
                continue
            text = clean(raw)
            if not is_claim(text):
                continue
            url = first_url(lines, i)
            claims.append({
                "file": str(path.relative_to(run_dir)),
                "line": i + 1,
                "text": text,
                "figure": first_figure(URL_RE.sub(" ", text)),
                "url": url,
                "status": status_of(text, url),
            })
    return paths, claims


# The full ledger's table. The brief uses a shorter one-line shape instead.
# A five-column row spends more words on separators than on the claim, and a
# reader who only wants the figure gains nothing from those separators.
TABLE_HEAD = ["| File | Line | Figure | Status | Claim |", "|---|---|---|---|---|"]

# The statuses the brief keeps. A sourced row carries its own URL, so a stage
# checking which figures are shaky has no reason to read it.
SHAKY = ("unsourced", "guess")

# The brief cuts each claim to this many words. Twelve is enough to recognise
# the sentence, and the file and line number lead to the rest of it.
BRIEF_CLAIM_WORDS = 12

# Ceilings on the padding that lines the brief's columns up in a terminal. The
# widths are measured from the rows actually written and then capped, so one
# very long figure cannot push every claim halfway across the screen. Markdown
# collapses the runs of spaces, which costs the alignment there and nothing else.
FIGURE_CAP = 14
LOCATION_CAP = 28
STATUS_WIDTH = 9


def count_statuses(claims):
    counts = {"sourced": 0, "guess": 0, "unsourced": 0}
    for c in claims:
        counts[c["status"]] += 1
    return counts


def table_row(c):
    """One ledger row. Long claim text is cut, because the file and line
    number are enough to find the original."""
    text = c["text"].replace("|", "/")
    if len(text) > 110:
        text = text[:107] + "..."
    return "| %s | %d | %s | %s | %s |" % (
        c["file"], c["line"], c["figure"].replace("|", "/") or "-",
        c["status"], text)


def write_summary(run_dir, paths, claims):
    counts = count_statuses(claims)

    rows = list(TABLE_HEAD)
    for c in claims:
        rows.append(table_row(c))

    out = ["# Claim ledger", "",
           "Built by tools/claims.py from %d file(s). One row per claim line."
           % len(paths), ""]
    out += rows
    out += ["",
            "Sourced %d / guess %d / unsourced %d, out of %d claims."
            % (counts["sourced"], counts["guess"], counts["unsourced"], len(claims)),
            ""]
    (run_dir / "claims_summary.md").write_text("\n".join(out), encoding="utf-8")
    return counts


def location(c):
    """Where the claim is, as one word a reader can paste into a search."""
    return "%s:%d" % (c["file"], c["line"])


def brief_line(c, figure_pad, location_pad):
    """One brief line: the figure, its status, where it is, and the opening of
    the claim. A guess is marked in capitals, so the figures a researcher
    already doubted stand out from the ones that simply carry no URL."""
    words = c["text"].split()
    text = " ".join(words[:BRIEF_CLAIM_WORDS])
    if len(words) > BRIEF_CLAIM_WORDS:
        text += "..."
    status = "GUESS" if c["status"] == "guess" else c["status"]
    return "- %s %s %s %s" % (
        c["figure"].ljust(figure_pad), status.ljust(STATUS_WIDTH),
        location(c).ljust(location_pad), text)


def write_brief(run_dir, paths, claims, counts):
    """The short ledger: the counts, then the shaky rows that carry a figure.

    Five stages need to know which figures are shaky, and none of them needs
    the sourced rows to find that out. A shaky row with no figure in it is not
    a number a writer can check. Such a row stays in the full ledger and out
    of here. The closing line names that ledger and its row count.
    """
    shaky = [c for c in claims if c["status"] in SHAKY]
    figured = [c for c in shaky if c["figure"]]

    out = ["# Claim ledger, shaky figures only", "",
           "Built by tools/claims.py. It lists every figure that carries no "
           "source, one line each.", "",
           "- claims: %d" % len(claims),
           "- sourced: %d" % counts["sourced"],
           "- guess: %d" % counts["guess"],
           "- unsourced: %d" % counts["unsourced"],
           "- shaky rows carrying a figure: %d" % len(figured),
           "- files audited: %d" % len(paths),
           ""]

    if figured:
        out += ["Each line below is the figure, then its status, then the file "
                "and line, then the first %d words of the claim. A figure "
                "marked GUESS was flagged by a researcher; the rest are only "
                "unsourced." % BRIEF_CLAIM_WORDS,
                ""]
        figure_pad = min(max(len(c["figure"]) for c in figured), FIGURE_CAP)
        location_pad = min(max(len(location(c)) for c in figured), LOCATION_CAP)
        for c in figured:
            out.append(brief_line(c, figure_pad, location_pad))
    else:
        out.append("No unsourced or guessed claim in this run carries a figure.")

    out += ["",
            "The full ledger is claims_summary.md, with all %d rows: the "
            "sourced ones, and the %d shaky rows that carry no figure."
            % (len(claims), len(shaky) - len(figured)),
            ""]
    (run_dir / "claims_brief.md").write_text("\n".join(out), encoding="utf-8")
    return len(shaky), len(figured)


def main(argv):
    args = [a for a in argv if not a.startswith("-")]
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__.strip())
        return 0
    if len(args) != 1:
        print(USAGE)
        return 2

    run_dir = Path(args[0])
    if not run_dir.is_dir():
        print("no such run directory: %s" % run_dir)
        return 1

    paths, claims = collect(run_dir)
    if not paths:
        print("no research files found in %s (looked for *.md there and in "
              "lanes/, ignoring %s)"
              % (run_dir, ", ".join(GENERATED_NAMES)))
        return 1

    with (run_dir / "claims.jsonl").open("w", encoding="utf-8") as fh:
        for c in claims:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    counts = write_summary(run_dir, paths, claims)
    shaky, figured = write_brief(run_dir, paths, claims, counts)
    print("%d claims from %d files -> %s" % (len(claims), len(paths), run_dir / "claims.jsonl"))
    print("sourced %d, guess %d, unsourced %d"
          % (counts["sourced"], counts["guess"], counts["unsourced"]))
    print("%d shaky row(s), %d of them carrying a figure -> %s"
          % (shaky, figured, run_dir / "claims_brief.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
