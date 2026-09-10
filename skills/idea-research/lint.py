#!/usr/bin/env python3
"""Check an idea-research answer against the writing rules.

Usage:  python3 tools/lint.py <ANSWER.md> [--strict] [--json]
Standard library only, Python 3.8. --strict exits 1 when any problem is found;
the default is advisory and exits 0. What a script cannot judge is the editor's job.
"""
import argparse, difflib, json, re, sys
from pathlib import Path

# Word budget per section. The template mandates three "## PART n." sections of about
# 300, 700 and 700 words, so each part carries its own cap; appendices are not capped.
# "part" is the fallback for older answers whose sections are two-digit numbered.
BUDGETS = {"PART1": 350, "PART2": 800, "PART3": 800, "part": 250, "appendix": None}
# Whole-document ceiling on visible words: every section but the appendices, with code
# fences and block tags removed. SKILL.md states this budget; nothing measured it.
TOTAL_BUDGET = 2000

MAX_SENTENCE_WORDS, MAX_PARA_SENTENCES, MAX_CELL_WORDS = 25, 3, 15
MIN_HEADING_WORDS, REPEAT_MIN_WORDS, REPEAT_RATIO = 4, 12, 0.90
# Fragment check skips longer sentences (the lexicon's gap, not the writer's), but
# is high enough to catch the verbless data fragments the old 14-word cap let through.
FRAGMENT_MAX_WORDS = 18

# Rows 1-4 of the "Never write" table in SKILL.md's HOW TO WRITE section, verbatim.
# Row 5 (pass, burn, traction, TAM, wedge, GTM) is JARGON below; row 7 is INTERNAL.
BANNED = """artefact offering solution proposition keepable actionable learnings surface
load-bearing ecosystem landscape moat thesis posture leverage unlock unlocks""".split() + ["resolves to", "converts into"]
# Not in the table, kept on judgement: "artifact" is the US spelling of a banned word,
# and the rest are the generic slop the table's own instruction ("say what it actually
# is") exists to stop. Delete this line to make the list the table and nothing else.
BANNED += """artifact synergy holistic paradigm best-in-class seamless robust cutting-edge game-changer
disrupt supercharge delve""".split()
JARGON = {
    "pass": 'VC jargon. Write "an investor would decline, because..."',
    "burn": 'Write "money spent per month".', "traction": "Say the actual number instead.",
    "TAM": "Write out the market size and where it came from.",
    "SAM": "Write out the market size and where it came from.",
    "wedge": 'Write "the narrow first version".', "GTM": 'Write "how you reach customers".',
    "ARR": 'Write "yearly revenue".',
    "CAC": 'First use should read "cost to get one customer (CAC)".',
    "LTV": 'First use should read "what a customer is worth (LTV)".',
}
# The compliant form the CAC and LTV messages ask for must not itself be flagged.
JARGON_OK = re.compile(r"\((?:CAC|LTV)\)")
INTERNAL = ["lane", "kill criteria", "confidence tag", "down-weight", "SURVIVES", "WOUNDED", "VERDICT:", "DRIFT_REQUEST"]

# A sentence is a sentence when it holds a finite verb from an explicit lexicon.
# Guessing from suffixes was the old bug: "\w+ing" read "funding" as a verb and hid
# real fragments; "\w+s" read "startups" as one. Set membership cannot do either.
AUX = """is are was were be been being am has have had do does did will would can could should may might must shall ought
need needs cannot isnt arent wasnt werent hasnt havent hadnt dont doesnt didnt wont wouldnt cant couldnt shouldnt
mustnt lets""".split()
BASE_VERBS = """accept add admit advise agree aim allow answer appear apply argue arrive ask assume attend avoid back beat become
begin believe belong break bring build buy call cancel carry cause change charge check choose claim clear climb
close collect come compare complain complete compute conclude confirm consider contain continue convert cook copy
correct cost count cover create cross cut deal decide decline deliver depend describe design die disclose discover
discuss double doubt drive drop earn eat enable end enter exist expand expect explain fail fall feel fight fill find
finish fit fix flag fly focus follow forget form gain get give go grow guess hand handle happen hear help hide hire
hit hold hope ignore imply improve include increase indicate insist intend introduce invest invite join judge keep
kill know land last launch lead learn leave lend let lie like limit link list live look lose love make manage mark
match matter mean measure meet mention miss move name need note notice offer open operate order own pay pick plan
play point post prefer prepare present press prevent price print produce promise prove provide publish pull push put
raise reach read realise realize receive recommend record reduce refer reflect refuse remain remember remove repeat
replace reply report represent require rest result retain return reveal ride rise run say scale see seek seem sell
send serve set settle share shift ship show shut sign sit skip solve sound speak spend spot stand start state stay
step stop study submit suggest supply support suppose survive switch take talk teach tell test think throw tie touch
track trade train treat try turn understand use validate value verify visit wait walk want warn wash watch wear win
travel govern carry apply argue audit badge bind cap collapse detect enforce feed inherit lint number obey rank
render restate sample score search skip split strip tag weigh
wish wonder work worry write book phone ring email text draft sketch map rank log chart plot budget cap trim pitch
quote bill refund pause split merge batch queue file tag sort filter scan screen survey poll interview recruit hang
stick sample swap trial pilot bundle chase nudge remind chat message dial tour host cite paste install update
download upload click type restart enable disable select save edit delete rename toggle export import sync""".split()
# Irregular and otherwise unguessable forms, listed rather than derived.
IRREGULAR = """began begun beaten became bet bid bound bought broke broken brought built burnt caught chose chosen came dealt done
drew drawn drove driven ate eaten fell fallen fed felt fought found flew flown forgot forgotten got gotten gave
given went gone grew grown heard held hid hidden kept knew known laid led left lent lay lost made meant met paid
quit ran rang rose said saw seen sold sent shot showed shown sang sat slept spent spoke spoken spread stood stuck
taught tore told took taken thought threw thrown understood woke wore won wrote written""".split()
# Nouns ending -ing/-ed, listed so a later BASE_VERBS edit cannot revive them as verbs.
NOUN_ING_ED = set("""funding marketing testing spending pricing reporting onboarding branding screening tracking coaching wording heading
holding briefing offering meeting reading finding findings beginning ending outstanding advanced limited paid unpaid
mixed given used related detailed""".split())
CONTRACTED = ("'re", "'ve", "'ll", "'d", "'m")
# "It's" carries a verb; "the couple's plan" does not. Only these stems take bare "'s".
SUBJECTS = set("""it that there he she who what here this i you we they everything nothing someone""".split())

# Lines that open with one of these labels are citations or data, not prose.
LABEL_LINE = re.compile(r"^(sources?|note|notes|evidence|caveat|citation|from|see|budget|verdict|certainty|confidence|status|owner|next|risk|assumption)s?\s*:", re.I)
# "PART3" is `## PART 3. WHAT TO DO` in the current template; 09-12 are the action
# sections of older two-digit answers, still recognised so those answers still lint.
ACTION_SECTIONS = ("09", "10", "11", "12", "PART3")
NUM_HEADING = re.compile(r"^#+\s*(\d{2})\s*[·.\-]")
PART_HEADING = re.compile(r"^#*\s*part\s+(\d+)\s*[·.\-:)]?\s*", re.I)
# Block tags are HTML comments on their own line: <!--::verdict|The call-->. They are
# instructions to the renderer, not prose, so they are stripped before every check.
BLOCK_TAG = re.compile(r"<!--\s*::.*?-->")
HTML_COMMENT = re.compile(r"<!--.*?-->")
# For answers that do not number their sections. Imperatives and the founder's own budget are fine in these.
ACTION_HEADING = re.compile(r"^(how to find out|how to test|do this first|what to do|ask \d+|the next \d+|track (these|the)|the way in)", re.I)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
HTML_LINE = re.compile(r"^</?(?:img|div|table|tr|td|th|br|p|a|b|i|h[1-6]|sub|sup|details|summary|picture|source|span|em|strong|code|pre|ul|ol|li|hr|center|font)\b", re.I)
APPENDIX = re.compile(r"^appendix\b", re.I)
HEADING_TOPIC_OPENER = re.compile(r"^(who|what|why|how|where|when|which|whether|would|should|could|can|do|does|did|is|are|was|were|if|about|on|notes?\s+on|the\s+\w+\s+thing)\b", re.I)
DATA_ROW = re.compile(r"^[^:]{1,70}:\s*[₹$\d]")
FIGURE = re.compile(r"[₹$]\s?[\d,]+|\b\d+(\.\d+)?%")
QUOTE_CHARS = re.compile(u"[\"\u201c\u201d]")
SOURCEISH = re.compile(r"\b[a-z0-9_-]+\.(com|in|org|net|health|app|io|co|md)\b")

def _inflect(base):
    yield base
    yield base + ("es" if re.search(r"(s|x|z|ch|sh|o)$", base) else "s")
    if base.endswith("e"):
        yield base + "d"
        yield base[:-1] + "ing"
    elif re.search(r"[^aeiou]y$", base):
        # A consonant before the y takes -ies, not -ys: carry/carries, try/tries,
        # study/studies. Without this line the third-person form yielded above is
        # "carrys", so "The ledger carries every figure" read as a verbless fragment.
        yield base[:-1] + "ies"
        yield base[:-1] + "ied"
        yield base + "ing"
    else:
        yield base + "ed"
        yield base + "ing"
        if re.search(r"[aeiou][bdgklmnprt]$", base) and len(base) <= 5:
            yield base + base[-1] + "ed"
            yield base + base[-1] + "ing"

VERB_FORMS = set(AUX) | set(IRREGULAR)
for _b in BASE_VERBS:  VERB_FORMS.update(_inflect(_b))
VERB_FORMS -= NOUN_ING_ED

def has_verb(sentence):
    """True when the sentence holds a finite verb from the lexicon."""
    for w in re.findall(r"[A-Za-z']+", sentence.lower()):
        if w.endswith("'s") and w[:-2] in SUBJECTS:
            return True
        if any(w.endswith(c) and len(w) > len(c) for c in CONTRACTED):
            return True
        bare = w.replace("'", "")
        if bare in NOUN_ING_ED:
            continue
        if bare in VERB_FORMS:
            return True
    return False

def section_of(stack):
    """Id of the innermost numbered heading: "09" for v4 answers, "PART3" for current."""
    for h in reversed(stack):
        m = NUM_HEADING.match(h)
        if m:
            return m.group(1)
        m = PART_HEADING.match(h)
        if m:
            return "PART" + m.group(1)
    return None

def heading_text(stripped):
    t = re.sub(r"^#+\s*", "", stripped)
    t = PART_HEADING.sub("", t)
    return re.sub(r"^\d{2}\s*[·.\-]\s*", "", t).strip()

def sentences(text):  return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def _repeats(seen, add):
    """REPEAT: the same sentence, or a long sentence 90% similar to another."""
    def norm(s):  return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
    flagged = set()
    for a in range(len(seen)):
        for b in range(a + 1, len(seen)):
            la, sa = seen[a]
            lb, sb = seen[b]
            if la == lb or b in flagged: continue
            na, nb = norm(sa), norm(sb)
            if not na or not nb: continue
            if na == nb:
                add(lb, "REPEAT", "sentence already appears at line %d: %s..." % (la, sa[:60]))
                flagged.add(b)
            elif (len(na.split()) > REPEAT_MIN_WORDS and len(nb.split()) > REPEAT_MIN_WORDS
                    and difflib.SequenceMatcher(None, na, nb).quick_ratio() >= REPEAT_RATIO
                    and difflib.SequenceMatcher(None, na, nb).ratio() >= REPEAT_RATIO):
                add(lb, "REPEAT", "sentence is near-identical to line %d: %s..." % (la, sa[:60]))
                flagged.add(b)

def lint(path):
    lines, problems = Path(path).read_text(encoding="utf-8").split("\n"), []
    # The UNSOURCED window reads neighbouring lines, so it reads them tag-free too:
    # a <!--::figure|Source--> tag must not pass as the source of the figure below it.
    clean = [HTML_COMMENT.sub("", l) for l in lines]
    def add(n, kind, msg):  problems.append((n, kind, msg))
    in_code, headings, action = False, [], False
    para, para_start, para_action = [], 0, False
    sec_head, sec_line, sec_words, sec_appendix, sec_action = None, 0, 0, False, False
    sec_part = None      # "PART1".."PART3" when the section is one of the three parts
    doc_words, block_tags = 0, 0   # visible words outside appendices; block tags seen
    body_started = False  # SKILL.md puts the meta line and the check-back line above the
                          # H1 and calls them outside the word count, so honour that
    sec_src, sec_figs = False, []   # does this section cite anything, and its figure lines
    seen = []  # (line, sentence) for the REPEAT check
    def flush_para():
        # Split sentences only after joining physical lines, or a hard-wrapped
        # sentence reads as two and its tail as a fragment.
        if not para: return
        text = " ".join(para).strip()
        label = bool(LABEL_LINE.match(text))
        sents = sentences(text)
        if len(sents) > MAX_PARA_SENTENCES and not para_action:
            add(para_start, "PARA", "paragraph is %d sentences (max %d)" % (len(sents), MAX_PARA_SENTENCES))
        for s in sents:
            n = len(s.split())
            if n > MAX_SENTENCE_WORDS:
                add(para_start, "LONG", "sentence is %d words (max %d): %s..." % (n, MAX_SENTENCE_WORDS, s[:60]))
            if n >= 5 and not label: seen.append((para_start, s))
            # "Trimacare 2, 60 tablets: 3,263" is a data row, not prose.
            if (4 <= n <= FRAGMENT_MAX_WORDS and not para_action and not label
                    and not DATA_ROW.match(s) and not s.endswith(":") and not has_verb(s)):
                add(para_start, "FRAGMENT", "no verb - write a complete sentence: %s..." % s[:60])
        del para[:]
    def close_section():
        # A section-level "Sources:" line sources the whole section; a 3-line window
        # alone called section 02 unsourced 4 times.
        if not sec_src:
            for n in sec_figs:
                add(n, "UNSOURCED", "figure with no source, and no \"we are guessing\" nearby")
        del sec_figs[:]
        if sec_head is None: return
        if sec_appendix:
            cap = BUDGETS["appendix"]
        else:
            cap = BUDGETS.get(sec_part, BUDGETS["part"])
        if cap and sec_words > cap:
            add(sec_line, "BUDGET", "section is %d words (budget %d): %s" % (sec_words, cap, sec_head))
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code; continue
        if in_code: continue
        # Block tags are counted, then removed, before anything reads the line: left in,
        # they inflated the word counts and their text tripped the prose checks.
        if "<!--" in line:
            block_tags += len(BLOCK_TAG.findall(line))
            raw, line = line, HTML_COMMENT.sub("", line)
            if raw.strip() and not line.strip():
                flush_para(); continue
        low, stripped = line.lower(), line.strip()
        # Headings first, so `action` is set before any check reads it. The old order
        # read it before assignment: UnboundLocalError on a first line with a quote.
        if stripped.startswith("#"):
            headings.append(stripped)
            if stripped.startswith("# "): body_started = True
            if stripped.startswith("## "):
                close_section()
                text = heading_text(stripped)
                sec_head, sec_line, sec_words, sec_src = text, i, 0, False
                m = PART_HEADING.match(stripped)
                sec_part = "PART" + m.group(1) if m else None
                sec_action = bool(ACTION_HEADING.match(text)) or sec_part == "PART3"
                sec_appendix = bool(APPENDIX.match(text))
                n = len(text.split())
                if sec_appendix or sec_part:
                    pass          # "## Appendix A - ..." and the three mandated
                                  # "## PART n." titles are exempt by contract
                elif n < MIN_HEADING_WORDS:
                    add(i, "HEADING", "heading is %d words (min %d), no finding: %s" % (n, MIN_HEADING_WORDS, text))
                elif HEADING_TOPIC_OPENER.match(text) or not has_verb(text):
                    add(i, "HEADING", "heading names a topic, not a finding: %s" % text)
            action = section_of(headings) in ACTION_SECTIONS or sec_action
        for w in BANNED:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                add(i, "BANNED", '"%s" - see the banned list' % w)
        for w, why in JARGON.items():
            if re.search(r"\b" + re.escape(w) + r"\b", line):
                if not (w in ("CAC", "LTV") and JARGON_OK.search(line)):
                    add(i, "JARGON", '"%s" - %s' % (w, why))
        # Boundaries, or "lane" fires on plane; caps match case, or "SURVIVES" on survives.
        for w in INTERNAL:
            cased = w.isupper() or w.endswith(":")
            if re.search(r"\b" + re.escape(w) + r"\b", line if cased else low,
                         0 if cased else re.I):
                add(i, "INTERNAL", '"%s" is the system\'s own vocabulary, not the reader\'s' % w)
        if stripped.startswith("|") and stripped.endswith("|") and "---" not in stripped:
            # Count the cells, not the pipes. "| a | b |" split() gives 5 for 2 words,
            # which charged a mandated table 64 phantom words in the acceptance test.
            row_words = sum(len(c.split()) for c in stripped.strip("|").split("|"))
            sec_words += row_words
            if body_started and not sec_appendix: doc_words += row_words
            for cell in [c.strip() for c in stripped.strip("|").split("|")]:
                n = len(cell.split())
                if n > MAX_CELL_WORDS:
                    add(i, "CELL", "table cell is %d words (max %d): %s..." % (n, MAX_CELL_WORDS, cell[:60]))
                if cell.lower().rstrip(".") in {"partly", "it depends", "maybe", "unclear", "n/a"}:
                    add(i, "HEDGE", 'cell is only a hedge: "%s"' % cell)
            continue
        # Only a sentence-length quote implies a person was quoted. "Not Available"
        # and a defined term in quotes are labels, and were 4 of 5 hits before.
        if not action and not re.search(r"https?://", line):
            # Odd segments of a split on quote marks are the quoted spans themselves.
            if any(len(q.split()) >= 5 for q in QUOTE_CHARS.split(line)[1::2]):
                add(i, "QUOTE", "quotation marks with no source link - nobody was interviewed")
        if stripped.startswith("#") or not stripped:
            flush_para(); continue
        # A fully bold or italic line is a mandated subtitle or a label, so it is exempt
        # from the prose checks. It still counts: the template mandates a bold claim in
        # every finding and an italic subtitle under every heading, and skipping both hid
        # 246 words of one 700-word part from its own budget.
        if re.fullmatch(r"\*{1,2}[^*]+\*{1,2}", stripped) or HTML_LINE.match(stripped):
            plain = len(stripped.strip("*").split())
            sec_words += plain
            if body_started and not sec_appendix: doc_words += plain
            continue
        # Each list item is its own paragraph; merging made section 09 read as one.
        if LIST_ITEM.match(line): flush_para()
        body = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", stripped)
        if not body: continue
        sec_words += len(body.split())
        if body_started and not sec_appendix: doc_words += len(body.split())
        if not para: para_start, para_action = i, action
        para.append(body)
        # A lane file is a source: "From R1_money.md" was 18 of the 39 first-run hits.
        if "source" in low or "http" in low or SOURCEISH.search(low): sec_src = True
        if not action and FIGURE.search(line):
            window = " ".join(clean[max(0, i - 3):i + 2]).lower()
            # A number the writer marked [[warn:Thin]] or [[bad:Not found]] is doing
            # exactly what SKILL.md asks. Honest marking is not a violation.
            if ("http" not in window and "guess" not in window
                    and "source" not in window and "[[warn:" not in window
                    and "[[bad:" not in window and not SOURCEISH.search(window)):
                sec_figs.append(i)
    flush_para()
    close_section()
    _repeats(seen, add)
    if doc_words > TOTAL_BUDGET:
        add(1, "TOTAL", "answer is %d visible words (ceiling %d), appendices excluded"
            % (doc_words, TOTAL_BUDGET))
    return sorted(set(problems)), {"visible_words": doc_words, "block_tags": block_tags}

def main():
    ap = argparse.ArgumentParser(description="Lint an idea-research answer.")
    ap.add_argument("path")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any problem is found")
    ap.add_argument("--json", action="store_true", dest="as_json", help="emit results as JSON")
    args = ap.parse_args()
    p = Path(args.path)
    if not p.exists():
        print(json.dumps({"file": str(p), "error": "not found"}) if args.as_json
              else "no such file: %s" % p)
        return 2
    (problems, stats), counts = lint(p), {}
    for _, kind, _ in problems:
        counts[kind] = counts.get(kind, 0) + 1
    # The block-tag count is reported, not judged: the render stage checks the number.
    tally = "%d visible words, %d block tags" % (stats["visible_words"], stats["block_tags"])
    if args.as_json:
        print(json.dumps({"file": str(p), "problems": len(problems), "counts": counts,
                          "strict": args.strict,
                          "visible_words": stats["visible_words"],
                          "word_ceiling": TOTAL_BUDGET,
                          "block_tags": stats["block_tags"],
                          "findings": [{"line": n, "kind": k, "message": m}
                                       for n, k, m in problems]}, indent=2))
    elif not problems:
        print("%s: clean - 0 problems (%s)" % (p, tally))
    else:
        for n, kind, msg in problems:
            print("%s:%d: %s: %s" % (p, n, kind, msg))
        print("\n%d problems: " % len(problems)
              + ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items()))
              + "\n" + tally)
    return 1 if (args.strict and problems) else 0

if __name__ == "__main__":
    sys.exit(main())
