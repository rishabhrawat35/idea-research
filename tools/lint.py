#!/usr/bin/env python3
"""Check an idea-research answer against the writing rules.

Usage:  python3 tools/lint.py runs/<slug>/ANSWER.md

Rules that a script can check, checked by a script. Everything a script cannot
judge is the editor agent's job. Standard library only.
"""
import re
import sys
from pathlib import Path

BANNED = [
    "artefact", "artifact", "offering", "proposition", "keepable", "actionable",
    "learnings", "load-bearing", "resolves to", "converts into", "leverage",
    "unlock", "unlocks", "ecosystem", "landscape", "moat", "thesis", "posture",
    "synergy", "holistic", "paradigm", "best-in-class", "seamless", "robust",
    "cutting-edge", "game-changer", "disrupt", "supercharge", "delve",
]
JARGON = {
    "pass": 'VC jargon. Write "an investor would decline, because..."',
    "burn": 'Write "money spent per month".',
    "traction": "Say the actual number instead.",
    "TAM": "Write out the market size and where it came from.",
    "SAM": "Write out the market size and where it came from.",
    "wedge": 'Write "the narrow first version".',
    "GTM": 'Write "how you reach customers".',
    "ARR": 'Write "yearly revenue".',
    "CAC": 'First use should read "cost to get one customer (CAC)".',
    "LTV": 'First use should read "what a customer is worth (LTV)".',
}
INTERNAL = ["lane", "kill criteria", "confidence tag", "down-weight",
            "SURVIVES", "WOUNDED", "VERDICT:", "DRIFT_REQUEST"]

MAX_SENTENCE_WORDS = 25
MAX_PARA_SENTENCES = 3
MAX_CELL_WORDS = 15

VERBS = re.compile(
    r"\b(is|are|was|were|be|been|has|have|had|do|does|did|will|would|can|could|"
    r"should|may|might|must|costs?|pays?|paid|sells?|sold|makes?|made|took|takes?|"
    r"needs?|means?|shows?|found|find|raised|lost|charges?|runs?|ran|gets?|got|"
    r"go|goes|went|says?|said|built|build|leaves?|left|spends?|spent|wants?|"
    r"asks?|tells?|told|gives?|gave|keeps?|kept|puts?|comes?|came|works?|looks?|"
    r"seems?|stays?|starts?|stops?|reaches?|adds?|opens?|reads?|writes?|"
    r"exists?|remains?|carries|carry|counts?|holds?|falls?|rises?)\b",
    re.I)

# Sections where the text is instructions to the founder. Imperatives, scripted
# questions and the founder's own budget are correct there, so three checks are
# switched off rather than firing on every line.
ACTION_SECTIONS = ("09", "10", "11", "12")


def section_of(heading_stack):
    """Return the two-digit section number the linter is currently inside."""
    for h in reversed(heading_stack):
        m = re.match(r"#+\s*(\d{2})\s*[·.\-]", h)
        if m:
            return m.group(1)
    return None


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def lint(path):
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    problems = []

    def add(n, kind, msg):
        problems.append((n, kind, msg))

    in_code = False
    para, para_start = [], 0
    headings = []

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        low = line.lower()
        stripped = line.strip()

        for w in BANNED:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                add(i, "BANNED", f'"{w}" — see the banned list')

        for w, why in JARGON.items():
            if re.search(r"\b" + re.escape(w) + r"\b", line):
                add(i, "JARGON", f'"{w}" — {why}')

        for w in INTERNAL:
            if w.lower() in low:
                add(i, "INTERNAL", f'"{w}" is the system\'s own vocabulary, not the reader\'s')

        if ('"' in line or "\u201c" in line) and not action:
            if not re.search(r"https?://", line):
                add(i, "QUOTE", "quotation marks with no source link — nobody was interviewed")

        # table rows
        if stripped.startswith("|") and stripped.endswith("|") and "---" not in stripped:
            for cell in [c.strip() for c in stripped.strip("|").split("|")]:
                n_words = len(cell.split())
                if n_words > MAX_CELL_WORDS:
                    add(i, "CELL", f"table cell is {n_words} words (max {MAX_CELL_WORDS}): {cell[:60]}…")
                if cell.lower().rstrip(".") in {"partly", "it depends", "maybe", "unclear", "n/a"}:
                    add(i, "HEDGE", f'cell is only a hedge: "{cell}"')
            continue

        if stripped.startswith("#"):
            headings.append(stripped)
        section = section_of(headings)
        action = section in ACTION_SECTIONS

        if stripped.startswith("#") or not stripped:
            if para:
                if len(para) > MAX_PARA_SENTENCES:
                    add(para_start, "PARA", f"paragraph is {len(para)} sentences (max {MAX_PARA_SENTENCES})")
                para = []
            continue

        body = re.sub(r"^[-*\d.\s]+", "", stripped)
        if not body:
            continue
        if not para:
            para_start = i
        for s in sentences(body):
            para.append(s)
            n_words = len(s.split())
            if n_words > MAX_SENTENCE_WORDS:
                add(i, "LONG", f"sentence is {n_words} words (max {MAX_SENTENCE_WORDS}): {s[:60]}…")
            # "Trimacare 2, 60 tablets: ₹3,263" is a data row, not prose.
            data_row = bool(re.match(r"^[^:]{1,70}:\s*[₹$\d]", s))
            if (n_words >= 4 and not action and not data_row
                    and not VERBS.search(s) and not s.endswith(":")):
                add(i, "FRAGMENT", f"no verb — write a complete sentence: {s[:60]}…")

        if not action and re.search(r"[₹$]\s?[\d,]+|\b\d+(\.\d+)?%", line):
            window = " ".join(lines[max(0, i - 3):i + 2]).lower()
            if "http" not in window and "guess" not in window and "source" not in window:
                add(i, "UNSOURCED", "figure with no source and no \"we're guessing here\" nearby")

    if para and len(para) > MAX_PARA_SENTENCES:
        add(para_start, "PARA", f"paragraph is {len(para)} sentences (max {MAX_PARA_SENTENCES})")

    return sorted(set(problems))


def main():
    if len(sys.argv) < 2:
        print("usage: lint.py <ANSWER.md>")
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"no such file: {p}")
        return 2
    problems = lint(p)
    if not problems:
        print(f"{p}: clean — 0 problems")
        return 0
    counts = {}
    for _, kind, _ in problems:
        counts[kind] = counts.get(kind, 0) + 1
    for n, kind, msg in problems:
        print(f"{p}:{n}: {kind}: {msg}")
    print()
    print(f"{len(problems)} problems: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 1


if __name__ == "__main__":
    sys.exit(main())
