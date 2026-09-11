#!/usr/bin/env python3
"""Check an idea-research answer against the writing rules.

Usage:  python3 tools/lint.py <ANSWER.md> [--strict] [--json]
Standard library only, Python 3.8. --strict exits 1 when any problem is found, except
BUDGET and TOTAL, which are counted and printed and never fail a run. The default is
advisory and exits 0. What a script cannot judge is the editor's job.

There is NO word cap on an answer any more. SKILL.md deleted the per-part budget it
used to state, so the two length numbers this script still prints, the per-part BUDGET
and the whole-document TOTAL, are an advisory fallback and nothing else: they are
counted, printed, labelled advisory, and can never fail --strict. Length is controlled
by FILLER, which cuts a paragraph that carries nothing and keeps a long one that
carries figures.

A section's ROLE comes from its POSITION, never from the words in its heading. Every h2
before the first heading that starts "Appendix" is a part, in order; that heading and
every h2 after it is an appendix; and the action section, where imperative fragments and
unlinked quotes are allowed, is the last part before the appendices. Keying any of this
on the literal words "PART <n>" was the old bug: SKILL.md forbids the writer from typing
them, so HEADING_NUMBER fired on the three mandated headings, PROSE_WALL went inert, and
the appendices lost the suppression that keeps FRAGMENT and PARA off their prose.

The checks gate composition as well as prose: HEADING_NUMBER, CALLOUT_RUN and PROSE_WALL
read the shape of the page, and FILLER decides what gets cut now that length does not.
"""
import argparse, difflib, json, re, sys
from pathlib import Path

# Advisory length fallback, keyed by the part's POSITION, because no heading text says
# which part it is any more. SKILL.md no longer states a per-part word count, so these
# numbers gate nothing: they exist only so a founder who wants a length figure gets one.
# Parts beyond the third, and every section of an older answer that numbers its sections
# two digits at a time, fall back to PART_BUDGET_OTHER. Appendices are never capped.
PART_BUDGETS = {1: 350, 2: 800, 3: 800}
PART_BUDGET_OTHER = 250
# Whole-document advisory fallback on visible words: every section but the appendices,
# with code fences and block tags removed. Nothing measured this number, and no document
# the founder reads claims a ceiling, so it is printed as a fallback and never enforced.
TOTAL_BUDGET = 2000
# Both numbers above are REPORTED, never fatal. The founder decided there is no word cap
# on content that carries data, so length is controlled by FILLER instead: a paragraph
# that carries nothing is cut, and a long section that carries figures stays.
ADVISORY = {"BUDGET", "TOTAL"}
# Every check this script can emit, so --json names them all whether or not one fired.
CHECKS = ("BANNED", "BUDGET", "CALLOUT_RUN", "CELL", "FILLER", "FRAGMENT", "HEADING",
          "HEADING_NUMBER", "HEDGE", "INTERNAL", "JARGON", "LONG", "PARA", "PROSE_WALL",
          "QUOTE", "REPEAT", "TAG_ORPHAN", "TOTAL", "UNSOURCED")

# Composition limits. Two callouts in a row read as emphasis; three read as a wall of
# boxes with no page between them. Three plain paragraphs read as prose; four read as an
# essay, and the template exists to stop the answer becoming one.
MAX_CALLOUT_RUN, MAX_PROSE_RUN = 2, 3
# FILLER only reads a paragraph at the template's maximum length. SKILL.md caps a
# paragraph at three sentences, so a one or two sentence paragraph is a definition, a
# distinction, a verdict label or a hinge. That was not a guess: at a two-sentence
# threshold the only two hits on the answers on disk were "Refused. The transaction you
# want is a recurring payment for guidance..." and "Do not sell the plan. Sell the
# decision about what not to buy...", and both are the paragraph their section is built
# on. Cutting either would have removed the point of the section.
FILLER_MIN_SENTENCES = 3
# The five callout tags. Every other tag is a component with its own shape.
CALLOUT_TAGS = {"note", "tip", "important", "warn", "caution"}

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
rate block overstate understate float stand hide sit read write draw round divide multiply
renew disagree
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
# "paid" and "used" left this set: both are the ordinary past tense of a verb this writing
# leans on, so "The nearest real customer here paid Uvi 999" read as a verbless fragment.
# The rest were read one at a time and stay. "given" and "mixed" are past PARTICIPLES,
# which need an auxiliary to be finite, and the lexicon already finds the auxiliary;
# alone they are adjectives. "limited", "advanced", "related" and "detailed" are past
# tenses nobody writes in the past tense here, and are adjectives in every line of the
# three real answers, so freeing them would cost FRAGMENT more than it would buy.
NOUN_ING_ED = set("""funding marketing testing spending pricing reporting onboarding branding screening tracking coaching wording heading
holding briefing offering meeting reading finding findings beginning ending outstanding advanced limited unpaid
mixed given related detailed""".split())
CONTRACTED = ("'re", "'ve", "'ll", "'d", "'m")
# "It's" carries a verb; "the couple's plan" does not. Only these stems take bare "'s".
SUBJECTS = set("""it that there he she who what here this i you we they everything nothing someone""".split())

# Lines that open with one of these labels are citations or data, not prose.
LABEL_LINE = re.compile(r"^(sources?|note|notes|evidence|caveat|citation|from|see|budget|verdict|certainty|confidence|status|owner|next|risk|assumption)s?\s*:", re.I)
# 09-12 are the action sections of older two-digit answers, still recognised so those
# answers still lint. The current template has no numbered sections at all: its action
# section is found by POSITION, as the last part before the appendices. See section_roles.
ACTION_SECTIONS = ("09", "10", "11", "12")
NUM_HEADING = re.compile(r"^#+\s*(\d{2})\s*[·.\-]")
# Block tags are HTML comments on their own line: <!--::verdict|The call-->. They are
# instructions to the renderer, not prose, so they are stripped before every check.
BLOCK_TAG = re.compile(r"<!--\s*::.*?-->")
HTML_COMMENT = re.compile(r"<!--.*?-->")
# TAG_ORPHAN reads a tag exactly the way render.py's read_blocks does, so these four
# patterns are copies of render.py's TAG_RE, ANY_COMMENT_RE, its fence test and
# HEADING_RE. A tag render.py will not see is a tag this check must not report.
TAG_LINE = re.compile(r"^<!--::\s*([A-Za-z][\w-]*)\s*(?:\|\s*(.*?))?\s*-->\s*$")
COMMENT_LINE = re.compile(r"^<!--.*-->\s*$")
FENCE_LINE = re.compile(r"^\s*(```|~~~)")
HEADING_LINE = re.compile(r"^#{1,6}\s+")
# COMPONENTS.md says ::appendix is placed before an "##" heading and collapses that
# section, and render.py binds it there on purpose. It is the one tag a heading does
# not orphan. ::meta needs no exemption: COMPONENTS.md gives it its own "Key: value"
# block above the H1, so the documented shape is a tag followed by its own content.
HEADING_BINDING_TAGS = ("appendix",)
# Fallback for older answers, whose action section sits in the middle of the file rather
# than last. Imperatives and the founder's own budget are fine in these.
ACTION_HEADING = re.compile(r"^(how to find out|how to test|do this first|what to do|ask \d+|the next \d+|track (these|the)|the way in)", re.I)
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
HTML_LINE = re.compile(r"^</?(?:img|div|table|tr|td|th|br|p|a|b|i|h[1-6]|sub|sup|details|summary|picture|source|span|em|strong|code|pre|ul|ol|li|hr|center|font)\b", re.I)
APPENDIX = re.compile(r"^appendix\b", re.I)
HEADING_TOPIC_OPENER = re.compile(r"^(who|what|why|how|where|when|which|whether|would|should|could|can|do|does|did|is|are|was|were|if|about|on|notes?\s+on|the\s+\w+\s+thing)\b", re.I)
DATA_ROW = re.compile(r"^[^:]{1,70}:\s*[₹$\d]")
FIGURE = re.compile(r"[₹$]\s?[\d,]+|\b\d+(\.\d+)?%")
QUOTE_CHARS = re.compile(u"[\"\u201c\u201d]")
# A URL, a bare domain, or a named store or journal the run cites by name.
SOURCE_ON_LINE = re.compile(
    r"https?://"
    r"|\b[a-z0-9][a-z0-9-]*\.(?:com|in|org|net|io|co|health|gov|edu|app|dev)\b"
    r"|\b(?:1mg|Play Store|App Store|Google Play|Flipkart|PubMed|Reddit|Quora)\b", re.I)
SOURCEISH = re.compile(r"\b[a-z0-9_-]+\.(com|in|org|net|health|app|io|co|md)\b")
# A block tag on its own line names the component under it: <!--::warn|Title-->.
# The name runs to the "|" or to the closing "-->", so the trailing dashes of the
# comment must not be eaten into it: render.py's own TAG_RE ends the same way.
TAG_NAME = re.compile(r"<!--\s*::\s*([A-Za-z][\w-]*?)\s*(?:\||-->)")
# A line holding nothing but inline badges is the writer's honest marking, not a
# component, so it neither breaks a callout run nor counts as a paragraph.
BADGE_LINE = re.compile(r"^(?:\[\[[a-z]+:[^\]]*\]\]\s*)+$", re.I)
# HEADING_NUMBER. report.css numbers every h2 and h3 with a counter, so a number in the
# heading's own text renders twice: "## PART 1. THE ANSWER" comes out "1. PART 1. THE
# ANSWER". Two shapes are caught: a word then a number ("PART 1.", "Section 4"), and a
# bare ordinal then a separator ("3.", "IV)"). "Appendix A" is not caught, because
# appendices are lettered by hand and that lettering is intended.
HEADING_ORDINAL = re.compile(
    r"^(?:part|section|chapter|stage|step|phase|round)\s+(?:\d+|[IVX]{1,4})\b"
    r"|^(?:\d+|[IVX]{1,4})\s*[.:)\u00b7\u2013\u2014-]", re.I)
# FILLER. What makes a paragraph carry something the reader could not get elsewhere.
# Every entry below is a reason to stay silent, because a false positive here deletes a
# sentence the reader needed, and only silence is recoverable.
FILLER_DIGIT = re.compile(r"\d")
FILLER_MONEY = re.compile(u"[\u20b9$]")
FILLER_URL = re.compile(r"https?://|\bwww\.")
# A number written as a word is still a figure: "twenty paid audits", "seventy-two hours".
NUMBER_WORDS = set("""one two three four five six seven eight nine ten eleven twelve thirteen
fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy
eighty ninety hundred thousand lakh lakhs crore crores million billion dozen half twice single
double triple first second third fourth fifth sixth seventh eighth ninth tenth
zero none once""".split())
# A capitalised word that is not the first word of its sentence, and not a function word,
# is a named entity: "Redcliffe Labs", "in India", "an IVF clinic", "PCOS". At the start
# of a sentence only an internal capital or an acronym is safe to read that way, because
# "Certainty" and "Deliver" open sentences too and neither names anything.
CAP_STOP = set("""the this that these those a an and or but so if then it its we you they he she
his her their our your no not do does did there here what which who whom when where why how
for from with without on in at to of by as after before per each every both all only even
because nothing nobody everything someone anyone something anything untried today now still
about into over under again more most less least other another same such than while whether
also just very much many few enough between during within against upon since until though
although unless however therefore thus hence yes maybe never always often sometimes""".split())
# The honest markings SKILL.md asks for, plus the honest absences. A paragraph that says
# the research came back empty is doing its job, and carries something with no figure.
FILLER_HONEST = re.compile(
    r"this is our reading|we(?:'| a)re guessing|we are guessing"
    r"|research (?:did not|didn't|does not|doesn't|could not|couldn't)"
    r"|(?:did not|does not|could not|cannot|will not|never) (?:find|know|published|publish|invent)"
    r"|found nothing|nothing published|never published|has (?:ever )?published"
    r"|no company|nobody measured|is an absence|nobody in this research"
    r"|certainty is (?:low|medium|high)", re.I)
# A definition or a distinction is content even with no figure in it: "Untried is not a yes
# and not a no. It means nobody has bought this." The template asks for these on purpose.
# TIGHTENED, because this signal was carrying four fifths of a challenger's planted padding.
# Gone: "rather than" and "instead of", ordinary connectives that join any two nouns; and
# the bare negated copula and bare "means", which any padding paragraph produces ("What
# this means in practice is..."). A connective alone no longer exempts anything, and what
# is left names the act of defining and cannot be read as a connective. Two things make
# that safe. FILLER never reads a paragraph under FILLER_MIN_SENTENCES, and a real
# definition here is one or two sentences ("Untried is not a yes and not a no. It means
# nobody has bought this."), so the sentence gate already exempts it. And it was measured:
# on the three real answers no paragraph FILLER reads depends on this signal at all.
FILLER_DEFINE = re.compile(r"\bthe difference between\b|\bcounts as\b"
                           r"|\bnot the same (?:as|thing|question)\b|\b(?:is|are) defined as\b", re.I)

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

def carries_something(text, sents):
    """True when a paragraph carries a figure, a source, a named entity or a rupee amount.

    FILLER is the founder's replacement for the word budget, so it decides what gets cut.
    Any one signal below is enough to keep the paragraph, and the list is deliberately
    generous: silence costs a founder nothing, and a wrong cut costs them a sentence.
    """
    low = text.lower()
    if FILLER_DIGIT.search(text) or FILLER_MONEY.search(text):
        return True                       # any figure, any rupee or dollar amount
    if FILLER_URL.search(low) or SOURCEISH.search(low):
        return True                       # a URL or a bare domain is a source
    if "source" in low or "according to" in low:
        return True
    if FILLER_HONEST.search(text) or FILLER_DEFINE.search(text):
        return True                       # honest marking, or a definition, is content
    if any(len(q.split()) >= 4 for q in QUOTE_CHARS.split(text)[1::2]):
        return True                       # a quoted phrase is evidence
    for s in sents:
        words = re.findall(r"[A-Za-z][A-Za-z0-9&'\u2019.-]*", s)
        for idx, w in enumerate(words):
            for part in re.split(r"[^a-z]+", w.lower()):
                if part in NUMBER_WORDS:
                    return True           # a number written as a word
            if len(w) > 1 and w.isupper():
                return True               # an acronym: PCOS, IVF, GST
            if idx == 0:
                if re.search(r"[a-z][A-Z]", w):
                    return True           # HealthifyMe, StepSetGo, WhatsApp
                continue                  # a capital here is only the sentence opening
            if w[0].isupper() and w.lower().strip(".") not in CAP_STOP:
                return True               # a named entity
    return False

def section_of(stack):
    """Id of the innermost two-digit heading: "09" in an older answer, else None."""
    for h in reversed(stack):
        m = NUM_HEADING.match(h)
        if m:
            return m.group(1)
    return None

def heading_text(stripped):
    t = re.sub(r"^#+\s*", "", stripped)
    return re.sub(r"^\d{2}\s*[·.\-]\s*", "", t).strip()

def section_roles(lines):
    """Decide every h2 section's role by POSITION, and return {line: (role, part_no)}.

    Every h2 before the first heading whose text starts "Appendix" is a part, numbered in
    the order they appear. That heading and every h2 after it is an appendix. The second
    return value is the number of the LAST part, which is the action section: the place
    imperative fragments and unlinked quotes belong. Heading words decide nothing here,
    because SKILL.md forbids the writer from typing "PART <n>" and asks for a heading that
    states the part's finding instead, so no fixed string is left to match.
    """
    h2, in_code = [], False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("## "):
            h2.append((i, heading_text(stripped)))
    first_appendix = None
    for i, text in h2:
        if APPENDIX.match(text):
            first_appendix = i
            break
    roles, part_no = {}, 0
    for i, text in h2:
        if first_appendix is not None and i >= first_appendix:
            roles[i] = ("appendix", None)
        else:
            part_no += 1
            roles[i] = ("part", part_no)
    return roles, part_no

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

def tag_orphans(lines):
    """Block tags with no block of their own, read the way render.py binds one.

    render.py holds a tag pending until a block of content arrives, so a tag that
    loses its content does not vanish: it lands on the next unrelated block. That
    is how a deleted line turned a plain paragraph into a legal Caution callout,
    and the tag census still counted the tag, so the zero-tags backstop passed.

    Four shapes leave a tag with nothing of its own, each read off read_blocks:
      1. another block tag comes next, which overwrites the pending tag
      2. a heading comes next, which takes the tag and then renders without it,
         except ::appendix, which render.py does bind to a heading on purpose
      3. the file ends with the tag still pending
      4. a code fence comes next, which render.py never binds a tag to, so the
         tag falls past the fenced block onto whatever follows it

    A blank line and a plain HTML comment do not break a binding, because
    read_blocks keeps the tag pending across both. So a tag above a blank line and
    then its paragraph, its table or its list is correct and is never reported.
    """
    found, fence = [], None
    for idx, line in enumerate(lines):
        hit = FENCE_LINE.match(line)
        if fence is not None:
            # Inside a fence every line is content, including a tag comment.
            if hit: fence = None
            continue
        if hit:
            fence = hit.group(1); continue
        tag = TAG_LINE.match(line)
        if not tag: continue
        name = tag.group(1).lower()
        j = idx + 1
        while j < len(lines):
            nxt = lines[j]
            if not nxt.strip():
                j += 1; continue
            if COMMENT_LINE.match(nxt) and not TAG_LINE.match(nxt):
                j += 1; continue   # render.py drops a plain comment, tag still pending
            break
        why = None
        if j >= len(lines):
            why = "the file ends before any block follows it"
        elif TAG_LINE.match(lines[j]):
            why = ("the next block tag, on line %d, replaces it before it binds anything"
                   % (j + 1))
        elif FENCE_LINE.match(lines[j]):
            why = ("a code fence follows on line %d, and render.py leaves a fenced block "
                   "untagged, so the tag lands on the block after it" % (j + 1))
        elif HEADING_LINE.match(lines[j]) and name not in HEADING_BINDING_TAGS:
            why = ("a heading follows on line %d, and render.py drops a ::%s tag that "
                   "lands on a heading" % (j + 1, name))
        if why:
            found.append((idx + 1,
                          "::%s has no block of its own: %s. Delete the tag, or give it "
                          "back the content it lost" % (name, why)))
    return found

def lint(path):
    lines, problems = Path(path).read_text(encoding="utf-8").split("\n"), []
    # The UNSOURCED window reads neighbouring lines, so it reads them tag-free too:
    # a <!--::figure|Source--> tag must not pass as the source of the figure below it.
    clean = [HTML_COMMENT.sub("", l) for l in lines]
    # Roles first, in their own pass, because the action section is the LAST part and no
    # single line can tell you that: the reader has to have seen the appendices already.
    roles, last_part = section_roles(lines)
    def add(n, kind, msg):  problems.append((n, kind, msg))
    # Its own pass, because it reads forward from a tag and the main loop reads one
    # line at a time. A tag that binds nothing is a composition fault, not prose.
    for orphan_line, orphan_msg in tag_orphans(lines):
        add(orphan_line, "TAG_ORPHAN", orphan_msg)
    in_code, headings, action = False, [], False
    para, para_start, para_action, para_plain = [], 0, False, True
    # Block structure. `in_tag` is true while a block tag's own contiguous lines are being
    # read, which is how render.py groups them: a blank line ends the block.
    in_tag, tag_name = False, None
    crun, crun_line, crun_tags = 0, 0, []   # the callout run: length, first line, tags
    prun, prun_line = 0, 0                  # the plain-paragraph run: length, first line
    sec_head, sec_line, sec_words, sec_appendix, sec_action = None, 0, 0, False, False
    sec_part = None      # 1, 2, 3... when the section is a part; None inside an appendix
    allow_frag = False   # FRAGMENT and PARA are off in the action section and in every
                         # appendix: one is imperative steps, the others are data.
    doc_words, block_tags = 0, 0   # visible words outside appendices; block tags seen
    body_started = False  # SKILL.md puts the meta line and the check-back line above the
                          # H1 and calls them outside the word count, so honour that
    sec_src, sec_figs = False, []   # does this section cite anything, and its figure lines
    seen = []  # (line, sentence) for the REPEAT check
    def close_callout_run():
        nonlocal crun
        if crun > MAX_CALLOUT_RUN:
            add(crun_line, "CALLOUT_RUN",
                "%d callout blocks in a row (%s), max %d: break them with a heading, a "
                "table or a paragraph" % (crun, ", ".join(crun_tags), MAX_CALLOUT_RUN))
        crun = 0
        del crun_tags[:]
    def close_prose_run():
        nonlocal prun
        if prun > MAX_PROSE_RUN:
            add(prun_line, "PROSE_WALL",
                "%d plain paragraphs in a row (max %d): this part needs a component, not "
                "more prose" % (prun, MAX_PROSE_RUN))
        prun = 0
    def flush_para():
        # Split sentences only after joining physical lines, or a hard-wrapped
        # sentence reads as two and its tail as a fragment.
        nonlocal prun, prun_line
        if not para: return
        text = " ".join(para).strip()
        label = bool(LABEL_LINE.match(text))
        sents = sentences(text)
        # PROSE_WALL counts only plain paragraphs, and only inside a part, which is now
        # any h2 section before the first appendix. An appendix is allowed to be prose.
        if para_plain and not label:
            if sec_part is not None:
                if prun == 0: prun_line = para_start
                prun += 1
            # FILLER. Only a full-length paragraph that carries nothing is worth
            # cutting; a shorter one is a definition or a hinge the reader needs.
            if len(sents) >= FILLER_MIN_SENTENCES and not carries_something(text, sents):
                add(para_start, "FILLER",
                    "paragraph carries no figure, no source, no named entity and no "
                    "rupee amount: %s..." % text[:60])
        else:
            close_prose_run()
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
        # Appendices are never capped. A part's cap comes from its position, and every
        # BUDGET hit is advisory: it is printed for a founder who wants the number and
        # it cannot fail --strict.
        cap = None if sec_appendix else PART_BUDGETS.get(sec_part, PART_BUDGET_OTHER)
        if cap and sec_words > cap:
            add(sec_line, "BUDGET", "section is %d words (advisory fallback %d, not a cap): %s"
                % (sec_words, cap, sec_head))
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
                # A tag on its own line opens a block. CALLOUT_RUN counts the tag rather
                # than its text, so a run survives a tag comment between two callouts.
                flush_para(); close_prose_run()
                names = TAG_NAME.findall(raw)
                if names:
                    in_tag, tag_name = True, names[-1].lower()
                    if tag_name in CALLOUT_TAGS:
                        if crun == 0: crun_line = i
                        crun += 1
                        crun_tags.append(tag_name)
                continue
        low, stripped = line.lower(), line.strip()
        # Any line of real content ends the run, unless it is the open callout's own text.
        # A badge line is the writer's marking, so it is neither content nor a break.
        if stripped and not BADGE_LINE.match(stripped):
            if not (in_tag and tag_name in CALLOUT_TAGS):
                close_callout_run()
        # Headings first, so `action` is set before any check reads it. The old order
        # read it before assignment: UnboundLocalError on a first line with a quote.
        if stripped.startswith("#"):
            flush_para(); close_prose_run(); close_callout_run()
            in_tag, tag_name = False, None
            headings.append(stripped)
            raw_text = re.sub(r"^#+\s*", "", stripped).strip()
            # render.py strips a bare leading number from an h2 itself and offsets the CSS
            # counter, so the legacy "## 09 - ..." id is not a double number and is exempt.
            legacy = stripped.startswith("## ") and NUM_HEADING.match(stripped)
            if HEADING_ORDINAL.match(raw_text) and not legacy:
                add(i, "HEADING_NUMBER",
                    "heading text carries its own number and the stylesheet numbers the "
                    "section too, so it renders twice: %s" % raw_text)
            if stripped.startswith("# "): body_started = True
            if stripped.startswith("## "):
                close_section()
                text = heading_text(stripped)
                sec_head, sec_line, sec_words, sec_src = text, i, 0, False
                # Position decides the role. Nothing here reads the heading's words
                # except the one anchor D1 names, the first "Appendix", which
                # section_roles has already found.
                role, part_no = roles.get(i, ("part", None))
                sec_appendix = role == "appendix"
                sec_part = part_no if role == "part" else None
                # The action section is the last part before the appendices, so an
                # imperative step list passes there without any heading text saying so.
                # ACTION_HEADING stays as a fallback for older answers, whose action
                # section sits in the middle of the file rather than at the end of it.
                sec_action = (sec_part is not None and last_part > 0 and sec_part == last_part) \
                    or bool(ACTION_HEADING.match(text))
                # Exempt by ROLE, never by wording. An appendix heading is a label on a
                # pile of source rows, so "Appendix A. Sources for every figure" is doing
                # its job. Parts get no exemption: rule 12 wants their finding stated, and
                # keying that exemption on the words "PART n." is what broke three checks.
                n = len(text.split())
                if sec_appendix:
                    pass
                elif n < MIN_HEADING_WORDS:
                    add(i, "HEADING", "heading is %d words (min %d), no finding: %s" % (n, MIN_HEADING_WORDS, text))
                elif HEADING_TOPIC_OPENER.match(text) or not has_verb(text):
                    add(i, "HEADING", "heading names a topic, not a finding: %s" % text)
            action = section_of(headings) in ACTION_SECTIONS or sec_action
            allow_frag = action or sec_appendix
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
            flush_para(); close_prose_run()
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
        # A bare domain is what rule 7 asks for, "name the source", so redcliffelabs.com
        # on the line is a source even with no scheme. Demanding https:// flagged four
        # correctly attributed quotations in one real answer.
        if not action and not SOURCE_ON_LINE.search(line):
            # Odd segments of a split on quote marks are the quoted spans themselves.
            if any(len(q.split()) >= 5 for q in QUOTE_CHARS.split(line)[1::2]):
                add(i, "QUOTE", "quotation marks with no source link - nobody was interviewed")
        if not stripped:
            # A blank line ends a block, which is exactly how render.py reads one.
            in_tag, tag_name = False, None
            flush_para(); continue
        if stripped.startswith("#"):
            flush_para(); continue
        # A fully bold or italic line is a mandated subtitle or a label, so it is exempt
        # from the prose checks. It still counts: the template mandates a bold claim in
        # every finding and an italic subtitle under every heading, and skipping both hid
        # 246 words of one 700-word part from its own budget.
        if re.fullmatch(r"\*{1,2}[^*]+\*{1,2}", stripped) or HTML_LINE.match(stripped):
            flush_para(); close_prose_run()
            plain = len(stripped.strip("*").split())
            sec_words += plain
            if body_started and not sec_appendix: doc_words += plain
            continue
        # Each list item is its own paragraph; merging made section 09 read as one.
        if LIST_ITEM.match(line): flush_para(); close_prose_run()
        body = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", stripped)
        if not body: continue
        sec_words += len(body.split())
        if body_started and not sec_appendix: doc_words += len(body.split())
        if not para:
            # A list item, a table row and a tagged block are components, not prose, so
            # neither PROSE_WALL nor FILLER may read them as paragraphs.
            para_start, para_action = i, allow_frag
            para_plain = not in_tag and not LIST_ITEM.match(line)
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
    close_prose_run(); close_callout_run()
    close_section()
    _repeats(seen, add)
    if doc_words > TOTAL_BUDGET:
        add(1, "TOTAL", "answer is %d visible words (ceiling %d), appendices excluded"
            % (doc_words, TOTAL_BUDGET))
    return sorted(set(problems)), {"visible_words": doc_words, "block_tags": block_tags}

def main():
    ap = argparse.ArgumentParser(description="Lint an idea-research answer.")
    ap.add_argument("path")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any problem is found, except BUDGET and TOTAL")
    ap.add_argument("--json", action="store_true", dest="as_json", help="emit results as JSON")
    args = ap.parse_args()
    p = Path(args.path)
    if not p.exists():
        print(json.dumps({"file": str(p), "error": "not found"}) if args.as_json
              else "no such file: %s" % p)
        return 2
    # os.path.exists is true for a directory, and every other script in this pipeline
    # takes the run directory, so this is the argument a tired founder will type. One
    # line naming the mistake beats an IsADirectoryError traceback.
    if p.is_dir():
        msg = "%s is a directory: pass the answer file, for example %s" % (p, p / "ANSWER.md")
        print(json.dumps({"file": str(p), "error": "is a directory",
                          "hint": str(p / "ANSWER.md")}) if args.as_json else msg)
        return 2
    (problems, stats), counts = lint(p), {}
    for _, kind, _ in problems:
        counts[kind] = counts.get(kind, 0) + 1
    # BUDGET and TOTAL are still counted and still printed, and they no longer fail a run.
    # Length is FILLER's job now, so only a non-advisory problem can exit 1.
    advisory = [t for t in problems if t[1] in ADVISORY]
    fatal = [t for t in problems if t[1] not in ADVISORY]
    over = sum(1 for t in advisory if t[1] == "BUDGET")
    # The block-tag count is reported, not judged: the render stage checks the number.
    # There is no word cap, so the two length numbers are labelled for what they are.
    tally = ("%d visible words (no cap; advisory fallback %d), %d sections over their "
             "advisory fallback, %d block tags"
             % (stats["visible_words"], TOTAL_BUDGET, over, stats["block_tags"]))
    budgets = dict(("part_%d" % k, v) for k, v in sorted(PART_BUDGETS.items()))
    budgets["other_parts"] = PART_BUDGET_OTHER
    budgets["appendix"] = None
    if args.as_json:
        print(json.dumps({"file": str(p), "problems": len(problems), "counts": counts,
                          "strict": args.strict,
                          "checks": list(CHECKS),
                          "visible_words": stats["visible_words"],
                          "word_ceiling_advisory": TOTAL_BUDGET,
                          "word_cap": None,
                          "over_word_ceiling": stats["visible_words"] > TOTAL_BUDGET,
                          "over_budget_sections": over,
                          "section_budgets_advisory": budgets,
                          "advisory_kinds": sorted(ADVISORY),
                          "advisory_problems": len(advisory),
                          "strict_problems": len(fatal),
                          "block_tags": stats["block_tags"],
                          "findings": [{"line": n, "kind": k, "message": m,
                                        "advisory": k in ADVISORY}
                                       for n, k, m in problems]}, indent=2))
    elif not problems:
        print("%s: clean - 0 problems (%s)" % (p, tally))
    else:
        for n, kind, msg in problems:
            print("%s:%d: %s%s: %s" % (p, n, kind, " (advisory)" if kind in ADVISORY else "", msg))
        print("\n%d problems: " % len(problems)
              + ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items()))
              + "\n" + tally)
        if advisory:
            print("%d of those are advisory (%s) and do not fail --strict"
                  % (len(advisory), ", ".join(sorted(ADVISORY))))
        if not fatal:
            print("nothing that fails --strict")
    return 1 if (args.strict and fatal) else 0

if __name__ == "__main__":
    sys.exit(main())
