---
name: idea-research
description: 'Checks whether a startup idea is worth building. Research agents dig, one agent builds the strongest case that it works, another builds the strongest case that it fails, a synthesis step reconciles them, and an editor rejects any sentence a tired founder could not read. Asks what changed recently, so genuinely new ideas are not rejected for having no track record, and measures demand by proxy when the thing does not exist yet. India-first, plain English. Use when someone wants an idea checked, a market or competitor scan, gaps and threats, community or investor sentiment, or a go/no-go on a new bet.'
license: MIT
metadata:
  tags: "Startup Research, Market Analysis, Multi-Agent, India, Idea Validation"
  category: "research"
---

# Idea Research

**Version 5.0.0** · keep this in step with `.claude-plugin/plugin.json`, the only version the desktop app shows.
Bump both on every change: patch for wording, minor for a new rule or stage, major for a pipeline change.

Check whether an idea is worth building. The market is India by default and money is in ₹. The reader is a founder
with no money, no team and no network, reading on a phone at 11pm. The job is to find out what is true. Use it for
"is this worth building", "should I build X", "is there a gap here", "would anyone fund this in India". Do not use
it for a pitch deck, a financial model, a market-size lookup, or a company that already exists.

## The principle

Search asymmetrically, judge symmetrically. Optimism belongs in how many angles get tried: more sources, more
countries, more ways in. Neutrality belongs in the conclusion, where a no and a yes need equal evidence and the
same voice.

Getting it backwards produces two mistakes: yes to a corpse, because most ideas nobody pays for are ideas people
already refused, and no to something new, because nobody paid to summon a car from a phone before GPS phones
existed. Telling a refused idea from an untried one is most of the work.

# HOW TO WRITE

Every agent inherits this section. Agent prompts point at it and never restate it.

| Never write | Write instead |
|---|---|
| artefact, offering, solution, proposition, keepable | the PDF, the app, the thing |
| actionable, learnings, surface | say what it actually is |
| load-bearing, resolves to, converts into | rests on, is really, becomes |
| leverage (as a verb), unlock, enable | use, let, allow |
| ecosystem, landscape, moat, thesis, posture | name the actual thing |
| pass, burn, traction, TAM, wedge, GTM | "an investor would decline, because…" |
| "Buy the traffic", "the killer assumption" | "Run Meta ads, ₹12,000", "what has to be true" |
| "VERDICT: KILL" | "Should you build this? No." |

The system's own vocabulary never reaches the founder: no lane, no verdict tag, no confidence label, no mode name.

1. **Complete sentences, always.** "Pass. ₹99, customer leaves in 7 months" is unreadable. "An investor would
   decline, because a pregnancy customer stops needing you after seven months" can be read.
2. **Say the action, not a saying about it.** "Run Meta ads targeting women 22-38 for ₹12,000", not "buy traffic".
3. **No aphorisms.** If a sentence would fit on a poster, delete it. Never state a fact then restate it as wisdom.
4. **No invented quotes.** Quotation marks need a real person, a real source and the link. Nobody was interviewed.
5. **A number must not imply more than it proves.** Losing money while growing is normal. Say what makes it matter.
6. **State the mechanism, not the conclusion.** "₹1,200 to get a customer who pays ₹800 once", not "the economics".
7. **Say where it came from.** Name the source, or write "this is our reading" or "we're guessing here" in those words.
8. **Numbers beat adjectives.** Not "expensive", but "₹40,000 a month". Not "many", but a count.
9. **Nothing over 25 words, three sentences per paragraph.** Three or more related data points make a table row.
10. **One fact has one owning section.** Later mentions cross-reference it. A restatement is a defect in the prose.
11. **Table cells run to 15 words, preferably five.** No cell that is only a hedge, no column full of paragraphs.
12. **Headings state the finding, not the topic,** and read correctly with the section covered up. Front-load the
    words that carry meaning: "If the numbers are wrong" becomes "The case holds if conversion falls by a third,
    and breaks if it halves"; "Why nobody is doing this" becomes "Three companies tried and stopped, for a reason
    that no longer applies".

# NEVER STOP AT A BLOCKED SOURCE

"Reddit was blocked" is a researcher giving up. Work down this ladder and record which rungs you tried.

1. Search for the content instead of the page. Threads get quoted in search results: try `site:reddit.com <topic>`.
2. A different community on the same subject: forums, app store reviews, YouTube comments, Trustpilot.
3. The same question about another country, which often beats the local answer and feeds the "what changed" test.
4. Someone who already did the reading: market reports, journalism, dissertations.
5. The browser: `mcp__claude-in-chrome__*` or `mcp__remote-devices__Claude_Browser__*`, if this session has them.

Only then write "could not find out", listing the rungs you tried. A file that stops at a block goes back once.

# THE PIPELINE

| Stage | Agents | Time | What happens |
|---|---|---|---|
| 0 Brief | 0 | 2 min | Scope, and what would kill this |
| 1 Scout | 1 | 4 min | Exists? Anyone paying? What changed? |
| 2 Research | 3-6 | 9 min | Parallel diggers, one file each |
| 3 Ledger | 0 | 10 sec | Three scripts build the evidence base |
| 4 The pair | 2 | 5 min | Strongest case for, strongest case against |
| 5 Reconcile | 1 | 4 min | Weigh both cases, do the arithmetic |
| 6 Write | 1 | 4 min | The answer |
| 7 Lint | 0 | 5 sec | A script checks the rules, strictly |
| 8 Edit and revise | 2 | 4 min | One rejects the prose, one applies the fixes |
| 9 Render | 0 | 1 min | A page you can share |

Ten to thirteen agents on a typical run, about 33 minutes. The longest legal path is seventeen, never more: Scout,
six researchers, two specialists, the pair, the reconciler, two check-backs, the writer, the editor, the reviser.

**Quick mode.** For quick, triage, or comparing more than one idea, run stages 0, 1, 2, 3, 6 and 7: three
researchers, no pair, no editor, no page, about 19 minutes. Say which mode you are running. The writer then reads
only the brief, `01_scout.md`, `_findings.md`, `lanes/`, `claims_summary.md` and `contradictions.md`, so Part 1
takes certainty of evidence from the sourced count and states no strength of view, Part 2 drops the section on
where the two cases disagreed, and Part 3 takes its way in from the lanes.

## Stage 0. Brief

Orchestrator only. Ask at most three questions, and only if the idea cannot be scoped without them. Then write
`runs/<slug>/00_brief.md` with these fields, one per line:

```
WHAT IT IS: one sentence a stranger understands   WHO HAS THE PROBLEM: a specific person, not a segment
WHAT THEY DO NOW: including "nothing"             WHAT THEY PAY NOW: ₹, and how often
WHERE: India / specific cities / tier             WHAT THE FOUNDER HAS: skills, access, money, or none
WHAT THE FOUNDER BELIEVES: the assumption they are betting on
WHY NOW: what changed to make this possible today (a blank one is itself a finding)
NOT RESEARCHING: what nobody should chase        WHAT WOULD KILL THIS: the findings that would end it
```

Write "what would kill this" before any research, because it stops the system talking itself into a yes.

## Stage 1. Scout

One agent, twelve searches, 500 words, writes `01_scout.md`, returns five lines. Every rule in HOW TO WRITE applies.

1. **Does this exist in India?** Every real one, with price in ₹, users, money raised and current status.
2. **Does anyone pay for the exact thing, or only for something next to it,** such as a product or a person's time?
3. **What did the closest company choose to do that looks expensive or awkward?** That choice is a wall they hit.
4. **What changed?** What became possible in the last 24 to 36 months: a cost falling, a new platform, a rule
   change, a behaviour shift. Does this make money elsewhere, at what price and size? Are there dead bodies here,
   what killed them, and has that changed? A company that died of a constraint that has gone is evidence for it.

Scout's findings are provisional and go into later prompts marked as such. A researcher who finds a Scout claim
wrong says so, and the correction goes into `_findings.md`. A wrong fact injected as known is worse than no fact.
Then the orchestrator branches, saying which mode and why in one line before spending more agents.

| What Scout found | What to run |
|---|---|
| Direct competitor, funded, at scale, nothing changed | **Teardown**: 3 researchers. What they cannot or will not do, whether the money is real, cost to enter. |
| Nobody pays, and people already refused it | **Money-first**: 3 researchers. Proof of payment anywhere, what people pay for instead, what would have to change. |
| Nobody pays, but no dead bodies, or what killed them has changed | **New-thing mode**: 4 researchers with the proxy researcher. Earliest adopters, and what it costs to be first. |
| The thing does not exist anywhere yet | **Proxy mode**: 3 researchers, one of them the proxy researcher, whose file leads. |
| Genuinely open field | **Full**: 5-6 researchers. |

## Stage 2. Research

All researchers go out in one message, one file each, five lines back. Each gets four fields and an identity line,
because identity alone does not improve reasoning and the procedure does.

| ID | Identity line | OBJECTIVE | SOURCES | BOUNDARIES |
|---|---|---|---|---|
| R1 | Sold to Indian consumers with no money | Who pays, how much, how often, which group pays best | Price pages, app stores, D2C sites, retail data | Money, not competitor strategy |
| R2 | Knows which companies here died and why | Who is doing it, who failed, what killed them, whether that cause still applies | Inc42, Entrackr, MCA filings, post-mortems | Company history, not customers |
| R3 | Reads the forums | Where these people talk in their own words, and who already hacks a workaround | Reddit, Quora, WhatsApp and Telegram groups, one-star reviews | Behaviour, not market size |
| R4 | Grew a product on ₹0 | The first 100 users named, how to reach them free, what blocks trust | Community lists, creator audiences, local directories | Distribution, not pricing |
| R5 | Tracks Indian seed deals | Who funds this, what makes them decline, whether it works unfunded | Deal databases, investor blogs, public decks | Funding, not operations |

### The proxy researcher

Run this one whenever Scout finds the thing does not exist yet. It takes R5's slot, because funding follows demand
and there is no deal history to trace. Absence of a product is not evidence of absence of demand: either nobody can
serve it profitably yet, or something worse already meets it. It measures the second, writing `lanes/R6_proxy.md`
with a section per method, each carrying a number, a date and a source URL, or "no data found for this method".

| Method | What it counts | How to run it | Sources |
|---|---|---|---|
| Workaround census | Revealed demand, priced by the upkeep people already pay | Count shared spreadsheets, templates, scripts, extensions and hand-run WhatsApp groups doing this job. Record what each costs to keep running. | Notion and Airtable template galleries, GitHub, Google Sheets shared publicly, group directories |
| Complaint cluster mining | Unserved demand with its failure mode attached | Pull one-star reviews of adjacent products plus forum threads. Cluster by complaint, not by product. Count distinct complainers per month. | Play Store and App Store reviews, Reddit, Quora, Trustpilot |
| Substitute time-on-task | Hours already spent, which is the budget you can capture | Take the minutes per week a published study, a vendor case study or a forum post reports for the substitute, and say which. Never time it yourself. | Time-use surveys, NSSO, published studies, vendor case studies |
| Search-trend slope | Intent before any transaction exists | Read slope and turning points on queries that describe the job, not the product. Never absolute volume. | Google Trends, Keyword Planner numbers quoted in published articles |
| Second-hand listing counts | An installed base before any brand reports one | Count listings for the equipment this behaviour needs. Track monthly volume, not price. | OLX, Cashify, Facebook Marketplace |
| Foreign analogue | A leading indicator, where this is already normal | Find the country where this is normal now, and say what it looked like there before it was, and who did it by hand then. | Local press, app store charts, funding databases in that country |

### Specialists, nought to two by domain

Health, pharma and medtech get someone who reads NMC, CDSCO and ABDM rules and prices compliance. Fintech, lending
and insurance get RBI, IRDAI, SEBI and DPDP. Hardware and D2C get customs, BIS, landed cost and order sizes.
Sports, education and agri get the person doing the job today, the coach or teacher or farmer. B2B gets the channel
partner and the procurement head who signs. Consumer social and creator tools get a community moderator who knows
platform risk, and what happens when the platform changes its rules. Where nothing fits, invent one, naming a real
job title and what that person would know. Cap at two, because needing more means the idea is scoped too wide.

```
You are {IDENTITY LINE}.
FIRST ACTION: read runs/<slug>/00_brief.md, 01_scout.md and _findings.md. Work only inside the brief. If your
main finding is already in _findings.md, say "already known" and spend the rest of your budget elsewhere.
KNOWN SO FAR, to build on rather than re-research. Scout's items are PROVISIONAL: if you find one is wrong, say
so plainly and note the correction. {the bullets known so far}
OBJECTIVE: {what to establish}
SOURCES: {named places to look}
BOUNDARIES: {your scope, and the scope that belongs to another agent}
RULES
- Max {N} searches. Max 6 findings, 5 rows in the numbers table. Stop at the cap.
- Every fact gets a source URL. With no source, write "no source, this is a guess".
- Indian sources, Indian prices, ₹. Other countries when they answer what India cannot.
- Report what argues against the idea. If you found none, you did not look.
- Never stop at a blocked source. Work the ladder and record the rungs you tried.
- Don't recommend anything, find things out. Every rule in HOW TO WRITE applies.
OUTPUT, written to {PATH} as "# {NAME}" then these H2 sections, in order:
WHAT I FOUND (max 6 bullets, most important first) / THE NUMBERS (max 5 rows: what, how much, source) / WHAT
ARGUES AGAINST IT / WHAT CHANGED RECENTLY / CORRECTIONS (anything wrong in KNOWN SO FAR) / WHAT I COULDN'T FIND
OUT (and which rungs of the ladder I tried) / WHAT THIS MEANS FOR A FOUNDER WITH NO MONEY / NOT MY JOB.
Then append your two biggest findings to _findings.md, with any correction.
RETURN only: file path, biggest finding, shakiest thing you relied on, facts with sources against guesses, and
any correction to KNOWN SO FAR. Max 5 lines.
```

Search budgets: twelve in full, new-thing or proxy mode, eight in teardown or money-first. Item caps rather than
word caps, because agents obey those and a reader can check them.

## Stage 3. The evidence ledger, built by script

No agent writes the ledger by hand any more.

```bash
python3 <skill folder>/tools/claims.py     runs/<slug>/            # claims.jsonl + claims_summary.md
python3 <skill folder>/tools/contradict.py runs/<slug>/            # contradictions.md
python3 <skill folder>/tools/verify.py     runs/<slug>/ --sample 8  # verify_queue.md + verify.json
```

- `claims.py` pulls every factual claim out of the research files and records whether a source sits behind it.
- `contradict.py` flags claims disagreeing on a number, date or negation. A quiet run means no numeric conflict.
- `verify.py` samples cited claims into `verify_queue.md`, because published audits find only about half of cited
  statements fully supported by the source cited. The check-back agent at stage 5 owns that queue, works the rows
  that carry weight, and writes what it found into `05c_checkback.md`.
- A contradiction touching a number the answer depends on goes to a check-back.

## Stage 4. The symmetric pair

Two agents, spawned in the same message, reading the same files, neither seeing the other's output. One builds the
strongest case that this works, one the strongest case that it fails, and both write their assumptions first, so
the reconciler can see what each rests on. Neither is graded on winning and neither keeps a score, because
optimising toward a judge produces work that is more persuasive without being more correct.

### 4a. The case that it works

```
You have started companies with no money and got in through side doors. You have read every reason this fails,
and you are here to find the way in, if there is one.
READ every file in lanes/, the brief, 01_scout.md, _findings.md, claims_summary.md, contradictions.md. Max 5
searches. Every rule in HOW TO WRITE applies.
FIRST, write ## MY ASSUMPTIONS: what you take as true before you argue, numbered lines, each marked sourced or
assumed. Then work these four categories of way in, recording which you searched:
1. THE BORROWED VERSION. Whose audience, licence, stock, shelf or trust can be rented instead of built? Name them.
2. THE NARROWER VERSION. Which single customer type would pay today, even at 2% of the vision? Name it.
3. THE DIFFERENT-PAYER VERSION. Same insight, someone else pays. Name who benefits enough to pay.
4. THE COMPETITOR'S CONSTRAINT. What can they not do without breaking a payroll, a licence or a brand promise?
A forced count makes agents invent things, so there is no target number of options. Say which categories came back
empty, in the words "nothing found in this category". That is a real finding and costs no search, so spend the
budget on the categories producing names.
- Every option doable in two weeks, under ₹20,000, no staff, no contacts.
- Real tactics with names: post in this group, call this company, list on this site.
- No pep talk, and no vote on whether the idea is good. You propose things to try.
OUTPUT, written to runs/<slug>/04a_case_for.md as H2 sections:
MY ASSUMPTIONS / THE STRONGEST CASE THAT THIS WORKS / CATEGORIES SEARCHED (all four, each with what was found or
"nothing found") / THE WAY IN, IF THERE IS ONE / WHAT THE INCUMBENT CANNOT DO / THINGS TO TRY (each with ₹ and
days) / THE ONE FACT THAT WOULD SETTLE THIS
```

### 4b. The case that it fails

```
You are the sharpest reader this idea will ever meet, and your job is to state the strongest case that it
fails, accurately enough that someone can check it. Not to win.
READ every file in lanes/, the brief, 01_scout.md, _findings.md, claims_summary.md, contradictions.md. Max 5
searches. Every rule in HOW TO WRITE applies.
FIRST, write ## MY ASSUMPTIONS: what you take as true before you argue, numbered lines, each marked sourced or
assumed. Then, across the research:
1. For each research file, name the claim its conclusion depends on that has no source, and say whether the
   argument dies without it.
2. Name the Indian reality it ignored: price sensitivity, who controls household money, trust, language,
   regulation, cost to serve, how long a customer lasts.
3. Say what a large company does the day this starts working, naming the company.
4. Name the duplication: which files are saying the same thing. Two files agreeing because they read the same
   source is one finding, not two, and the answer must not count it twice.
If a claimed problem would not actually stop the business, say so. Recording that something survives is worth
the same as recording that something kills it.
- No prosecution speech, and no vote on whether the idea is good. You state problems someone can check.
OUTPUT, written to runs/<slug>/04b_case_against.md as H2 sections:
MY ASSUMPTIONS / THE STRONGEST CASE THAT THIS FAILS (ranked, worst first) / WHAT NEEDS AN ANSWER BEFORE ANYONE
BUILDS / WHAT SURVIVES SCRUTINY / WHERE THE FILES DUPLICATE EACH OTHER / THE ONE FACT THAT WOULD SETTLE THIS
```

## Stage 5. Reconcile

One agent, no research. Where a number it needs is missing it writes "not found in the research", never an estimate.

```
You are reconciling two cases built independently. READ both, plus lanes/, the brief, 01_scout.md, _findings.md,
claims_summary.md and contradictions.md. Zero searches. Every rule in HOW TO WRITE applies.
1. WHERE THEY DISAGREE. For each disagreement, say whether the sides differ on a fact or on an assumption. A
   fact goes to a check-back. An assumption gets written down as one, and the answer says which way it was taken.
2. WHAT BOTH ACCEPT. The claims neither case disputes. These carry the most weight.
3. REFUSED, NOT YET POSSIBLE, OR UNTRIED. Pick one, citing both case files and any check-back already back.
   Refused means people met this and said no. Not yet possible means a named constraint blocked it, and you say
   whether it has lifted. Untried means nobody put it to these people, which is evidence for neither side.
4. IF THE NUMBERS ARE WRONG. Run this table only when both figures the business rests on, usually cost to get a
   customer and what that customer is worth, sit in the research with a source. Three columns: conservative at
   cost +60% and value -35%, base as researched, aggressive at cost -25% and value +25%. Say which column to plan
   against, and that a ratio above 5:1 usually means the value is inflated. If either figure is missing or
   unsourced, skip the table and write one sentence: which figure is missing, and what having it would change.
Then rate the evidence in two separate fields, never blended into one sentence. CERTAINTY OF EVIDENCE: High (very
confident the truth is close to what the research found), Moderate (likely close, could be substantially
different), Low (confidence limited), Very low (very little confidence). STRENGTH OF VIEW: "we recommend" for a
strong view, "we suggest" for a weak one. A strong view resting on Low certainty is allowed, if it is visible.
OUTPUT, written to runs/<slug>/05_reconcile.md as H2 sections: WHERE THEY DISAGREE / WHAT BOTH ACCEPT / REFUSED,
NOT YET POSSIBLE, OR UNTRIED / IF THE NUMBERS ARE WRONG / CERTAINTY OF EVIDENCE / STRENGTH OF VIEW / HOW THIS LOOKS
FROM EACH SIDE / HOW MUCH OF THIS IS SOLID.
Under HOW THIS LOOKS FROM EACH SIDE, write the seats the research actually covered, two sentences each, naming a
source or saying it is our reading: the customer and her real alternative, the competitor and what it learned the
hard way, the investor and the reason money would not come, the regulator, the operator who shipped with no money,
the practitioner. Where the research does not carry a side, that seat is not written. Invent no voice, quote nobody.
Under HOW MUCH OF THIS IS SOLID, one line from claims_summary.md: X of Y claims sourced, and what that means.
```

- **Check-backs.** If either case turns on a fact that can be looked up, such as a rule, a policy, a price or a
  disclosed number, send one agent with five searches. It writes `05c_checkback.md`: the question, the answer, the
  source URL, and whether either case called that fact decisive. If only a live test can settle it, write it into
  the test instead. Never more than two check-back agents.
- **The revisable verdict, a hard rule.** If `05c_checkback.md` carries a fact that either case named as decisive,
  the writer must re-open the conclusion and write it again from the new fact. A run once found the deciding fact in
  a check-back and shipped the opposite conclusion, because the answer was already drafted.

## Stage 6. Write the answer

One agent, 1,800 visible words across three parts of about 300, 700 and 800, plus appendices that open closed.
The lint budget is 350, 800 and 800, so a part that runs slightly long still ships and one that runs double does not.

```
You are writing for a founder with no money, reading on a phone, tired.
READ: 00_brief.md, 01_scout.md, _findings.md, everything in lanes/, 04a_case_for.md, 04b_case_against.md,
05_reconcile.md, 05c_checkback.md if it exists, claims_summary.md, contradictions.md. YOU MAY NOT STATE ANY FACT
THAT IS NOT IN THOSE FILES. Zero searches, nothing from memory. Where a section needs a number nobody researched,
write "the research did not find this". Every rule in HOW TO WRITE applies.
OPEN by writing one line above the H1, outside the word count: which facts came back in 05c_checkback.md, and
whether the conclusion moved because of them. If the file does not exist, say no check-back was needed.
DO NOT TREAT THE RESEARCH AS RELIABLE BY DEFAULT. In one real run, 154 of 222 claims carried no source. Check
claims_summary.md before leaning on a figure, and badge any unsourced number [[warn:Thin]] or [[bad:Not found]].
Evidence comes before opinion, and the conclusion appears in exactly one place, Part 1. Parts 2 and 3 may not
restate it. Carry the two fields from 05_reconcile.md into Part 1 unchanged, as separate sentences.
BLOCK TAGS. Write each tag as an HTML comment on its own line, applying to the block that follows, as in
<!--::verdict|The call-->. The renderer binds the tag to a component and untagged prose stays prose, so tag only
the blocks named below. Full list and examples in render/COMPONENTS.md. Do not type section numbers; CSS supplies
them. Every heading takes a one-line italic subtitle under it, saying what is in that section.
OUTPUT, written to runs/<slug>/ANSWER.md:
<!--::meta--> above the H1: date, mode, who it is for.
# <Idea>: should you build it?
## PART 1. THE ANSWER  (about 300 words)
The call in one sentence under <!--::verdict-->: yes, no, or "not this version, but this one might". Then the number
that drives it, then certainty of evidence and strength of view as two separate sentences, then the one condition
that would change the answer, then the one thing to do today. Nothing else belongs here.
## PART 2. WHAT THE EVIDENCE SHOWS  (about 700 words)
Open with a <!--::stat--> block: the numbers this answer rests on, each as "value :: what it argues". Then findings
only, no recommending, each one a <!--::finding--> block under a heading that states its finding: whether people
refused this, could not have done it until now, or never tried it; who has already tried and where they ended up;
what this market pays for today in ₹; what the proxy measures found; where the two cases disagreed and what settles
it; what breaks if the numbers are wrong. Use <!--::note--> for context nobody would act on, <!--::quote--> only
for a real quotation with its source, <!--::caution--> for a legal or safety line.
## PART 3. WHAT TO DO  (about 800 words)
The cheapest version that could exist by Friday, from 04a_case_for.md, or one line saying no way in was found and
what would have to change. Where 04a found more than one way in, score them in a <!--::compare--> table: option,
cost in ₹, days, what it proves, the row to run first in bold. The one belief everything rests on goes under
<!--::important-->, a cost or limit that will bite under <!--::warn-->, a shortcut that saves real money under
<!--::tip-->. A test under ₹20,000 and two weeks as <!--::steps-->, numbered, with cost and time, the last step
naming the number that means yes and the number that means no. Then the people to ask, named specifically enough to
find this week, with three questions; never ask "would you pay for X", ask what they pay for now and what they last
abandoned. Then the next 90 days in three horizons, two items each, every item ending in the number that means it
worked. A number in the plan is a target you are setting, not a finding, so say that once here and do not badge
it. If the answer is no, this section is what it would take to prove us wrong, not a plan.
## Appendix A. Sources and calculations for every figure
From claims_summary.md unchanged, plus the sourced-against-guessed count.
## Appendix B. Where two sources disagree
From contradictions.md. If empty, say the script found no numeric conflict.
## Appendix C. What we could not find out
Table: Question | Why it matters | Cheapest way to answer it. Name blocked sources and what was tried instead. One
row for every action the editor could not stand up, saying what was proposed and what is missing behind it.
## Appendix D. How this looks from each side, and both cases in full
From 05_reconcile.md and the two case files, carried over whole. Close the answer with a <!--::cards--> block
pointing at the files behind it, one line each: the claim ledger, the contradiction check, the two cases.
RULES
- If people have already refused this, write "don't build this" plainly and do not soften it.
- If the evidence says people are paying and the constraint that blocked this has lifted, write "build this"
  plainly and do not soften it either.
- Never end on a no with no way in. If none was found, say so and say what would change.
- No summary of the research. The files exist. Answer the question.
- Nothing a reader needs in order to act may sit inside an appendix.
- Never silently drop a section. Every one above appears, even if it is one line saying the research did not cover
  it. Running out of room means cutting detail from Parts 2 and 3, never a whole section.
```

## Stage 7. Lint

```bash
python3 <skill folder>/lint.py runs/<slug>/ANSWER.md --strict   # add --json for machine-readable counts
```

Standard library only, seconds to run. `--strict` exits 1 on any problem, so the run does not ship while it fails.

## Stage 8. Edit, then revise once

```
You are an editor who has never seen this research. You are reading the answer cold.
READ: runs/<slug>/ANSWER.md and the lint output below. Nothing else. Zero searches. You judge it against every
rule in HOW TO WRITE.
1. Does every claim explain itself to someone who read nothing else?
2. Does any number imply more than it proves?
3. Is anything a conclusion pretending to be a fact?
4. Would a person say this out loud, or does it read like a deck?
5. Is the answer still there? Editing sands off the point, and the call must survive.
6. Is a part over its word budget? The lint output names it. List the wordiest lines to cut, worst first, and
   never cut a hedge, a source line or a badge to save words.
You have not seen the research, so you know nothing. You may NOT invent a fact to fix a sentence: every replacement
is built from words already on the page, or is a deletion, and never introduces a number, company, date, price or
claim. Where a line is wrong and you cannot fix it from the page, mark it NEEDS A FACT and name the missing fact. Do
not rewrite the document; list swaps and leave good lines alone. Each problem gets one numbered entry:
  FIX / LINE: exact text / WHY: one sentence / REPLACE WITH: exact new text
  CUT / LINE: exact text / WHY: one sentence
  NEEDS A FACT / LINE: exact text / WHAT IS MISSING: the fact required
OUTPUT, written to runs/<slug>/06_edit.md as H2 sections: FIXES / STILL GOOD (one line on what survived and
should not be touched) / I INVENTED NOTHING (one line, or which entry broke the rule).
```

```
Apply the fixes in 06_edit.md to ANSWER.md. Nothing else. Zero searches. Every rule in HOW TO WRITE applies.
- Apply FIX entries exactly as written, and CUT entries by deleting the line.
- For NEEDS A FACT, look in the research files. If the fact is there, write the line and cite the source.
- If it is not there, mark the line, do not delete it. A line proposing something to do keeps its words and moves
  into Appendix C as its own row, saying what was proposed and what is missing behind it. A line stating a finding
  keeps its place and carries [[bad:Not found]]. Deletion is only for a line asserting a figure as fact with no
  source behind it anywhere. Never fill a gap from memory.
- Add no number, name, date, price or claim that is not in ANSWER.md or a research file.
- Change nothing you were not asked to change. If a fix would remove the answer itself, skip it and say which.
Then say in one line: fixes applied, lines moved to Appendix C, fixes skipped, and why.
```

Run the lint again, one round only, because two agents editing each other never converge. If `--strict` still fails,
say so in chat rather than shipping quietly. A missing script means running its checks by reading, and saying so.

## Stage 9. Render

```bash
python3 <skill folder>/render/render.py runs/<slug>/ANSWER.md
```

That writes `report.html`, one self-contained file with the CSS inlined. Publish it as an artifact if this session
can, otherwise deliver the file. Zero tags reported means the writer skipped the tagging instruction, so send
`ANSWER.md` back once; if it returns untagged, ship it as plain prose and say in chat that the components are
missing. If the renderer cannot run, deliver `ANSWER.md` and say why. Then show the founder the answer and where
the files are.

# Files

```
runs/<slug>/
00_brief.md  read by every agent          04a_case_for.md      the case that this works
01_scout.md  exists, pays, what changed   04b_case_against.md  the case that it fails
_findings.md running list, corrections    05_reconcile.md      both cases weighed, plus the two rating fields
lanes/       one file per researcher      05c_checkback.md     looked-up facts, and which were decisive
claims.jsonl every claim as data, read by the two scripts below   06_edit.md   what the editor sent back
claims_summary.md  sourced against guessed        contradictions.md  where two sources disagree
verify_queue.md and verify.json  the check-back's rows   ANSWER.md  what the founder reads   report.html  the page
```

# Why it is built this way

| Rule | Why |
|---|---|
| No option quota anywhere | A forced count raised fabricated citations by 7 to 11 points |
| Two rating fields, never one | A blend hides whether the doubt sits in the evidence or in the view |

# When it goes wrong

| What you see | Why | Fix |
|---|---|---|
| Every idea comes back as no | Scout never asked what changed, or 4a was skipped | Rerun 4a, check Scout answered question 4 |
| The answer reads like slogans | Stage 8 was skipped | Run stages 7 and 8 |
| A check-back fact never reached the answer | The revisable verdict rule was ignored | Rerun stage 6 with that fact at the top |
| Numbers in the answer with no source | claims_summary.md was not read | Rerun stage 6 and require the badges |
| A file says a source was blocked and stops | The ladder was ignored | Send it back once, naming the rungs |
| No Indian sources anywhere | The brief named no place | Put the city or state in the brief, rerun stage 2 |
| Lint reports BUDGET or TOTAL | Part 3 took nine items in 800 words | Editor check 6 names the cuts, revise once |
