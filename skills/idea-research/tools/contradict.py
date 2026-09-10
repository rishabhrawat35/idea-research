#!/usr/bin/env python3
"""Flag claims in a run that disagree with each other.

Usage:  python3 tools/contradict.py runs/<slug>/

Reads claims.jsonl (written by claims.py) and writes contradictions.md.
Deliberately narrow. Three cases only:
  a) one entity carrying two different figures of the same kind and measure
  b) one entity with two different years attached to the same event
  c) one line asserting what another negates, on a shared subject

Precision beats recall. Every rule below would rather miss a disagreement than
invent one, because a checker that cries wolf gets switched off.

Exit 0 on success, 1 on a real failure, 2 on bad usage. Standard library only.
"""
import json
import re
import sys
from itertools import combinations
from pathlib import Path

USAGE = "usage: python3 contradict.py runs/<slug>/"

URL_RE = re.compile(r"https?://[^\s<>)\]\"'|]+")
NUM = r"\d+(?:,\d{3})*(?:\.\d+)?"
SCALE_WORDS = {"crore": 1e7, "cr": 1e7, "lakh": 1e5, "lakhs": 1e5,
               "million": 1e6, "mn": 1e6, "m": 1e6, "k": 1e3,
               "billion": 1e9, "bn": 1e9}
FIGURE_RE = re.compile(
    r"(?<![\w.,-])(?P<cur>₹|(?:US)?\$)?\s?(?P<num>" + NUM + r")"
    r"\s*(?P<scale>crore|cr|lakhs|lakh|million|billion|mn|bn|[mk])?"
    r"(?P<pct>\s?(?:%|per cent|percent))?(?![\w.])", re.I)

YEAR_RE = re.compile(r"(?<![\d,.])(?:19|20)\d{2}(?!\d)")

# Words that say what a figure measures. A figure with none of these beside it
# is compared with nothing, which is most of what keeps this checker quiet.
MEASURES = {
    "raised": "funding", "raise": "funding", "raises": "funding",
    "raising": "funding", "funding": "funding", "funded": "funding",
    "round": "funding", "seed": "funding", "series": "funding",
    "price": "price", "prices": "price", "priced": "price",
    "pricing": "price", "cost": "price", "costs": "price",
    "charges": "price", "charge": "price", "charging": "price",
    "sells": "price", "sold": "price", "fee": "price", "fees": "price",
    "revenue": "revenue", "revenues": "revenue", "sales": "revenue",
    "turnover": "revenue",
    "users": "users", "user": "users", "actives": "users", "mau": "users",
    "installs": "installs", "install": "installs",
    "downloads": "downloads", "download": "downloads",
    "customers": "customers", "subscribers": "customers",
    "orders": "orders", "retention": "retention", "retained": "retention",
    "threads": "threads", "prevalence": "prevalence",
}

# Event words for the date check, mapped onto one canonical event each.
EVENTS = {
    "started": "started", "start": "started", "starts": "started",
    "began": "started", "begin": "started", "founded": "started",
    "launched": "started", "launch": "started", "launches": "started",
    "raised": "funding", "raises": "funding", "raising": "funding",
    "added": "added", "adds": "added",
    "shut": "shut", "closed": "shut",
}

STOP = set("""a an the this that these those it its he she they we i you their our
his her my your there here and or but so if then than as at by for from in into of
on to with without over under about after before per both each all any some no not
nor only just also still yet now today when where which who whom whose why how what
is are was were be been being has have had do does did will would can could should
may might must shall says said say stated states nobody nothing none one two three
four five six seven eight nine ten first second third last next same other another
more most less least very roughly around nearly up down out own real actual thing
things number numbers figure figures line lines source sources January February March
April May June July August September October November December company companies name
names item items thing what much size status price cost total row rows table
eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty
thirty forty fifty sixty seventy eighty ninety hundred thousand half twice
""".split())

# Words dropped from the tail of a name so "Arva Health" and "Arva" are one
# entity, while "Arva Duo", a product, stays separate.
GENERIC_TAIL = {"health", "healthtech", "care", "fertility", "labs", "lab",
                "clinic", "clinics", "inc", "ltd", "limited", "app", "india",
                "technologies", "pvt"}

# Only the four plain negators, plus contractions. "cannot" was tried and
# removed: "the founder cannot charge much" negates the founder, not the
# subject the two sentences share.
NEGATIONS = ("not", "no", "never", "none", "n't")

# A range or a list, not a disagreement: "₹300 to ₹800", "$6M, $29M".
CONNECTIVE_RE = re.compile(r"\b(?:to|and|or|vs|versus|from|between|through)\b|[-–—,/]")

NAME_RE = re.compile(
    r"\b[A-Z][A-Za-z0-9&.'’\-]*(?:\s+(?:of|and|for|the))?"
    r"(?:\s+[A-Z][A-Za-z0-9&.'’\-]*)*")

PROCESS_RE = re.compile(
    r"\b(?:i|we)\b.{0,40}\b(?:found|find|reach|reached|search|searched|verify|"
    r"verified|check|checked|fetch|fetched|tried|try|read|could|couldn)", re.I)

VERB_RE = re.compile(
    r"\b(?:is|are|was|were|has|have|had|does|do|did|can|cannot|could|will|would|"
    r"sells|sold|charges|charged|pays|paid|discloses|disclosed|publishes|published|"
    r"shows|showed|found|finds|reports|reported|started|raised|reached|makes|works|"
    r"costs|offers|includes|says|said|exists|remains|gives|gave|took|takes|went|"
    r"goes|treats|adds|added|keeps|kept|means|moved|chose|decided)\b", re.I)

QUAL_WORDS = 4       # attribute phrase: the few words just before a figure
MAX_QUOTE = 170
MIN_SHARED = 2       # shared content words needed for the negation check


def clean_text(text):
    """Blank out URLs so their digits and path words are never read as claims."""
    return URL_RE.sub(lambda m: " " * len(m.group(0)), text)


def norm_word(word):
    return word.strip("(),.;:!?\"'’“”*[]|").lower()


def stem(word):
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    return word.rstrip("s").rstrip("e")


def entity_key(name):
    words = [norm_word(w) for w in name.split()]
    while len(words) > 1 and words[-1] in GENERIC_TAIL:
        words.pop()
    return " ".join(words)


def value_of(match):
    """Normalised value and figure kind, so ₹5 crore == ₹50,000,000."""
    num = float(match.group("num").replace(",", ""))
    scale = (match.group("scale") or "").lower()
    if scale:
        num *= SCALE_WORDS.get(scale, 1)
    if match.group("pct"):
        kind = "%"
    elif match.group("cur"):
        kind = "₹" if "₹" in match.group("cur") else "$"
    else:
        kind = "n"
    return num, kind


def sentence_spans(text):
    spans, start = [], 0
    # A bold lead-in ("**Inito, Bold Care and every lab.** None of them...")
    # ends a sentence too, so the closing ** counts as a boundary.
    for m in re.finditer(
            r"(?:(?<=[.!?])|(?<=[.!?]\*\*))\s+(?=\*{0,2}[A-Z(\"“₹$])", text):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(text)))
    return spans


def span_at(spans, pos, text):
    for start, end in spans:
        if start <= pos <= end:
            return start, end
    return 0, len(text)


def cell_spans(text):
    """Spans of the cells of a markdown table row, or None for prose."""
    if not text.startswith("|"):
        return None
    spans, pos = [], 0
    for part in text.split("|"):
        spans.append((pos, pos + len(part)))
        pos += len(part) + 1
    return spans


def table_headers(lines):
    """Line number -> header cells, for every data row of every table.

    A table figure often sits alone in its cell ("$22.5M"), so the column
    heading is the only thing on the page saying what it measures.
    """
    headers = {}
    for i, line in enumerate(lines):
        if i == 0 or not re.match(r"^\|[\s:|-]+\|?$", line.strip()):
            continue
        cells = [c.strip().lower() for c in lines[i - 1].strip().split("|")]
        for j in range(i + 1, len(lines)):
            if not lines[j].strip().startswith("|"):
                break
            headers[j + 1] = cells
    return headers


def names_in(text):
    """Accepted proper names, in order of appearance."""
    out = []
    for m in NAME_RE.finditer(text):
        words = m.group(0).split()
        if words and norm_word(words[0]) in STOP:
            words = words[1:]
        while words and norm_word(words[-1]) in ("of", "and", "for", "the"):
            words.pop()
        if not words:
            continue
        name = " ".join(words)
        key = entity_key(name)
        if len(key) < 3 or key in STOP:
            continue
        out.append((m.start(), name, key))
    return out


def attribute(window):
    """The few significant words right before a figure: what it is a figure of."""
    words = [norm_word(w) for w in window.split()]
    words = [w for w in words if w and not w[0].isdigit()]
    keep = []
    for w in reversed(words[-QUAL_WORDS - 2:]):
        if w in STOP or w in MEASURES or len(w) < 3:
            continue
        keep.append(w)
        if len(keep) >= QUAL_WORDS:
            break
    return {stem(w) for w in keep}


def figure_facts(claim, headers):
    """Every (entity, measure, kind, value) a claim states, with its context."""
    text = clean_text(claim["text"])
    cells = cell_spans(text)
    sents = sentence_spans(text)
    header_cells = headers.get(claim["line"])
    facts = []

    for m in FIGURE_RE.finditer(text):
        # Only money and percentages. A bare number ("2,190 reviews", "4.9
        # stars") attaches to its subject too loosely to compare safely.
        if not (m.group("cur") or m.group("pct")):
            continue
        pos = m.start()

        if cells:
            start, end = span_at(cells, pos, text)
            window = text[start:pos]
            context = text[cells[0][0]:cells[0][1]] + " " + text[cells[1][0]:cells[1][1]]
            if header_cells:
                idx = next((k for k, (s, e) in enumerate(cells) if s <= pos <= e), 0)
                if idx < len(header_cells):
                    context += " " + header_cells[idx]
        else:
            s_start, _ = span_at(sents, pos, text)
            window = text[max(s_start, pos - 90):pos]
            context = window

        words = [norm_word(w) for w in (window + " " + context).split()]
        measures = {MEASURES[w] for w in words if w in MEASURES}
        if not measures:
            continue

        # Entity: the nearest name before the figure, plus one fallback. In a
        # table that fallback is the row label; in prose it is the name the
        # sentence opens with, which catches "Healofy ... was $17.54M; Outlook
        # Business reports $22.5M" where the nearest name is the publisher.
        near = names_in(text[max(0, pos - 120):pos] if not cells else window)
        cands = [near[-1]] if near else []
        if cells:
            label = text[cells[1][0]:cells[1][1]].strip(" *")
            if label and not FIGURE_RE.match(label):
                cands.append((0, label, entity_key(label)))
        else:
            first = names_in(text[span_at(sents, pos, text)[0]:pos])
            if first:
                cands.append(first[0])

        value, kind = value_of(m)
        quals = attribute(window)
        seen = set()
        for _, name, key in cands:
            if key in seen:
                continue
            seen.add(key)
            for measure in measures:
                facts.append({"claim": claim, "pos": pos, "entity": name,
                              "key": key, "measure": measure, "kind": kind,
                              "value": value, "figure": m.group(0).strip(),
                              "quals": quals})
    return facts


def same_place(a, b):
    return (a["claim"]["file"] == b["claim"]["file"]
            and a["claim"]["line"] == b["claim"]["line"])


def joined_as_list(claim, pos_a, pos_b):
    """True when two figures are the ends of a range or items of a list."""
    text = clean_text(claim["text"])
    lo, hi = sorted((pos_a, pos_b))
    return bool(CONNECTIVE_RE.search(text[lo:hi]))


def comparable(a, b):
    """Same attribute, or one figure with no attribute at all (a table cell).

    Intersection was tried first and was the main source of false positives:
    "couples check ₹1,999" and "egg-freezing check ₹999" share the word check
    and are not a contradiction.
    """
    if not a["quals"] and not b["quals"]:
        return False
    if a["quals"] == b["quals"]:
        return True
    return (not a["quals"] or not b["quals"]) and a["entity"] == b["entity"]


def listed_pairs(claims):
    """Value pairs some claim writes as a range or a list: "$6M, $29M"."""
    listed = set()
    for c in claims:
        facts = []
        for m in FIGURE_RE.finditer(clean_text(c["text"])):
            if m.group("cur") or m.group("pct"):
                value, kind = value_of(m)
                facts.append((m.start(), value, kind))
        for (pa, va, ka), (pb, vb, kb) in combinations(facts, 2):
            if ka == kb and va != vb and joined_as_list(c, pa, pb):
                listed.add((ka, min(va, vb), max(va, vb)))
    return listed


def figure_conflicts(claims, headers_by_file):
    listed = listed_pairs(claims)
    groups = {}
    for c in claims:
        for f in figure_facts(c, headers_by_file.get(c["file"], {})):
            groups.setdefault((f["key"], f["measure"], f["kind"]), []).append(f)

    found = {}
    for (key, measure, kind), facts in groups.items():
        for a, b in combinations(facts, 2):
            if a["value"] == b["value"] or not comparable(a, b):
                continue
            pair = (kind, min(a["value"], b["value"]), max(a["value"], b["value"]))
            if pair in listed:
                continue
            same_line = same_place(a, b)
            if same_line and joined_as_list(a["claim"], a["pos"], b["pos"]):
                continue
            dedupe = (key, measure, kind, tuple(sorted((a["value"], b["value"]))))
            row = {"type": "figure", "subject": "%s (%s)" % (a["entity"], measure),
                   "a": a, "b": b, "same_line": same_line}
            if dedupe not in found or (found[dedupe]["same_line"] and not same_line):
                found[dedupe] = row
    return list(found.values())


def date_facts(claim):
    text = clean_text(claim["text"])
    sents = sentence_spans(text)
    facts = []
    for m in YEAR_RE.finditer(text):
        pos = m.start()
        s_start, s_end = span_at(sents, pos, text)
        sent = text[s_start:s_end]
        # A sentence listing several years is a history, not a claim about one
        # date, so nothing in it is compared.
        if len(YEAR_RE.findall(sent)) > 1:
            continue
        window = text[max(s_start, pos - 70):pos]
        words = [norm_word(w) for w in window.split()]
        events = {EVENTS[w] for w in words if w in EVENTS}
        if not events:
            continue
        near = names_in(text[max(0, pos - 120):pos])
        first = names_in(text[s_start:pos])
        cands = ([near[-1]] if near else []) + ([first[0]] if first else [])
        seen = set()
        for _, name, key in cands:
            if key in seen:
                continue
            seen.add(key)
            for event in events:
                facts.append({"claim": claim, "entity": name, "key": key,
                              "measure": event, "value": m.group(0),
                              "figure": m.group(0), "pos": pos})
    return facts


def date_conflicts(claims):
    groups = {}
    for c in claims:
        for f in date_facts(c):
            groups.setdefault((f["key"], f["measure"]), []).append(f)

    found = {}
    for (key, event), facts in groups.items():
        for a, b in combinations(facts, 2):
            if a["value"] == b["value"] or same_place(a, b):
                continue
            dedupe = (key, event, tuple(sorted((a["value"], b["value"]))))
            found.setdefault(dedupe, {
                "type": "date", "subject": "%s (%s)" % (a["entity"], event),
                "a": a, "b": b, "same_line": False})
    return list(found.values())


def content_words(sentence):
    out = set()
    for word in sentence.split():
        w = norm_word(word)
        if len(w) >= 4 and w not in STOP and not w[0].isdigit():
            out.add(stem(w))
    return out


def negation_index(words):
    for i, word in enumerate(words):
        w = norm_word(word)
        if w in NEGATIONS or w.endswith("n't"):
            return i
    return -1


def assertion_units(claims):
    units = []
    for c in claims:
        text = clean_text(c["text"])
        if text.startswith("|"):
            continue  # table rows carry no assertion to negate
        for start, end in sentence_spans(text):
            sent = text[start:end].strip()
            words = sent.split()
            if not 5 <= len(words) <= 30:
                continue
            if PROCESS_RE.search(sent) or not VERB_RE.search(sent):
                continue  # a note about the search, or no assertion at all
            # The subject has to be named in the sentence itself. Taking it from
            # anywhere in the claim let unrelated sentences pair up.
            found_names = names_in(sent)
            sent_keys = {k for _, _, k in found_names}
            if not sent_keys:
                continue
            # The shared subject does not count as shared predicate. Two
            # sentences about Arva that share only the words "Arva Health" are
            # not arguing with each other.
            name_words = {stem(norm_word(w)) for _, name, _ in found_names
                          for w in name.split()}
            units.append({"claim": c, "sent": sent, "keys": sent_keys,
                          "name": found_names[0][1], "words": words,
                          "neg": negation_index(words),
                          "content": content_words(sent) - name_words})
    return units


def assertion_conflicts(claims):
    """One sentence asserts what another negates, on a shared subject."""
    units = assertion_units(claims)
    found = {}
    for a, b in combinations(units, 2):
        if (a["neg"] >= 0) == (b["neg"] >= 0) or a["claim"] is b["claim"]:
            continue
        if not (a["keys"] & b["keys"]):
            continue
        shared = a["content"] & b["content"]
        smaller = min(len(a["content"]), len(b["content"])) or 1
        if len(shared) < MIN_SHARED or len(shared) / float(smaller) < 0.5:
            continue
        neg, plain = (a, b) if a["neg"] >= 0 else (b, a)
        # The negation has to bite on the shared wording rather than sit
        # somewhere else in the sentence.
        near = {stem(norm_word(w))
                for w in neg["words"][max(0, neg["neg"] - 2):neg["neg"] + 5]}
        if not (near & shared):
            continue
        # One row per pair of lines, not per pair of sentences.
        dedupe = tuple(sorted([(neg["claim"]["file"], neg["claim"]["line"]),
                               (plain["claim"]["file"], plain["claim"]["line"])]))
        found.setdefault(dedupe, {
            "type": "assertion",
            "subject": "%s (%s)" % (neg["name"], ", ".join(sorted(shared)[:3])),
            "a": {"claim": neg["claim"], "figure": "negated", "quote": neg["sent"]},
            "b": {"claim": plain["claim"], "figure": "asserted", "quote": plain["sent"]},
            "same_line": False})
    return list(found.values())


def quote(side):
    text = side.get("quote") or side["claim"]["text"]
    text = re.sub(r"\s+", " ", text).replace("|", "/")
    if len(text) > MAX_QUOTE:
        text = text[:MAX_QUOTE - 3] + "..."
    return text


def write_report(run_dir, rows):
    out = ["# Contradictions", "",
           "Built by tools/contradict.py from claims.jsonl. Narrow by design:",
           "one entity with clashing figures, clashing years, or an assertion",
           "against its negation. These are pairs to check, not verdicts.", ""]
    if not rows:
        out += ["No contradictions found.", ""]
    else:
        out += ["| Type | Subject | Claim A | Claim B |", "|---|---|---|---|"]
        for r in rows:
            a, b = r["a"], r["b"]
            out.append("| %s | %s | **%s** %s:%d -- \"%s\" | **%s** %s:%d -- \"%s\" |" % (
                r["type"], r["subject"].replace("|", "/"),
                a.get("figure", ""), a["claim"]["file"], a["claim"]["line"], quote(a),
                b.get("figure", ""), b["claim"]["file"], b["claim"]["line"], quote(b)))
        out += ["", "%d pair(s) flagged." % len(rows), ""]
    (run_dir / "contradictions.md").write_text("\n".join(out), encoding="utf-8")


def load_claims(path):
    claims = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
        if not line.strip():
            continue
        try:
            c = json.loads(line)
        except ValueError:
            print("skipped malformed claims.jsonl line %d" % (i + 1))
            continue
        if isinstance(c, dict) and c.get("text"):
            c.setdefault("file", "?")
            c.setdefault("line", 0)
            claims.append(c)
    return claims


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
    claims_path = run_dir / "claims.jsonl"
    if not claims_path.is_file():
        print("no claims.jsonl in %s -- run claims.py first" % run_dir)
        return 1

    claims = load_claims(claims_path)
    if not claims:
        print("claims.jsonl holds no usable claims")
        write_report(run_dir, [])
        return 0

    headers_by_file = {}
    for name in sorted({c["file"] for c in claims}):
        path = run_dir / name
        if path.is_file():
            headers_by_file[name] = table_headers(
                path.read_text(encoding="utf-8", errors="replace").splitlines())

    rows = (figure_conflicts(claims, headers_by_file)
            + date_conflicts(claims)
            + assertion_conflicts(claims))
    rows.sort(key=lambda r: (r["type"], r["subject"]))
    write_report(run_dir, rows)

    if rows:
        print("%d contradiction pair(s) across %d claims -> %s"
              % (len(rows), len(claims), run_dir / "contradictions.md"))
        for r in rows:
            print("  [%s] %s: %s:%d vs %s:%d" % (
                r["type"], r["subject"], r["a"]["claim"]["file"], r["a"]["claim"]["line"],
                r["b"]["claim"]["file"], r["b"]["claim"]["line"]))
    else:
        print("No contradictions found across %d claims." % len(claims))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
