---
name: idea-research
description: 'Checks whether a startup idea is worth building. Research agents dig, one sceptic tries to kill it, one builder tries to find the way in, one analyst counts, and an editor rejects any sentence a tired founder could not read. Asks what changed recently, so genuinely new ideas are not rejected for having no track record. India-first, plain English. Use when someone wants an idea checked, a market or competitor scan, gaps and threats, community or investor sentiment, or a go/no-go on a new bet.'
license: MIT
metadata:
  tags: "Startup Research, Market Analysis, Multi-Agent, India, Idea Validation"
  category: "research"
---

# Idea Research

Check whether an idea is worth building. Agents dig, one tries to kill it, one tries to find the way in, one counts, and an editor throws back anything that reads like a consultant wrote it.

- Market: India by default. Money in ₹.
- Reader: a founder with no money, no team, no network, reading on a phone at 11pm.
- Job: find the truth, not a verdict. A "no" with no way in is half a job.

## When to use

| Use it for | Don't use it for |
|---|---|
| "Is this idea worth building" | Writing a pitch deck |
| "Should I build X" | Building a financial model |
| "Is there a gap in this market" | Research on a company that already exists |
| "Would anyone fund this in India" | Looking up a market size |

## The two mistakes this system must not make

1. **Saying yes to a corpse.** Most ideas nobody pays for are ideas people already refused.
2. **Saying no to something new.** Nobody paid to summon a car from a phone before GPS phones existed. An idea with no track record is not the same as an idea that has been refused.

Telling those apart is the whole job.

---

# HOW TO WRITE

Every agent follows this. The research was never the weak part.

## Banned outright

| Never write | Write instead |
|---|---|
| artefact, offering, solution, proposition | the PDF, the app, the thing |
| keepable, actionable, learnings, surface | say what it actually is |
| load-bearing, resolves to, converts into | rests on, is really, becomes |
| leverage (as a verb), unlock, enable | use, let, allow |
| ecosystem, landscape, moat, thesis, posture | name the actual thing |
| pass, burn, traction, TAM, wedge, GTM | write it out: "an investor would decline, because…" |
| "Buy the traffic" | "Run Meta ads, ₹12,000" |
| "VERDICT: KILL" | "Should you build this? No." |
| "The killer assumption" | "What has to be true" |

**Never use the system's own words in what the founder reads.** No lane, no verdict, no confidence tag, no DEAD or WOUNDED. That is scaffolding, not the building.

## The rules

1. **Say the action, not a saying about the action.** "Run Meta ads targeting women 22-38 for ₹12,000" — not "buy the traffic, because there is no network to borrow."
2. **No aphorisms.** If a sentence sounds like it belongs on a poster, delete it.
3. **Complete sentences, always.** Fragments read as style and carry no information. "Pass. ₹99, customer leaves in 7 months" is unreadable. "An investor would decline, because a pregnancy customer stops needing you after seven months, so you buy your whole customer base again every year" is the same point and can be read.
4. **No invented quotes.** Nobody was interviewed. Nothing goes in quotation marks unless a real person said it in a real source, with the link.
5. **A number must not imply more than it proves.** A company losing money while growing is normal. If a loss matters, say what makes it matter — no new funding, falling revenue, a discounted sale. If you cannot say, leave the number out.
6. **State the mechanism, not the conclusion.** "It costs ₹1,200 to get a customer who pays ₹800 once" beats "the unit economics don't work."
7. **Say where it comes from.** Name the source, or write "this is our reading, nobody was interviewed."
8. **Three sentences per paragraph. Nothing over 25 words per sentence.**
9. **Name real things.** Real companies, real prices in ₹, real websites.
10. **Numbers beat adjectives.** Not "expensive" — "₹40,000 a month."
11. **If you are guessing, write "we're guessing here."** In those words.
12. **No insider jargon.** A founder reading at 11pm should not have to look anything up.

## Tables

- Every cell: 15 words maximum. Preferably 5.
- No cell that is only a hedge ("Partly.", "It depends.")
- Headers short and concrete: "Company", "Price", "Where they are now".
- A column full of paragraphs is not a column. Make it a list below.

---

# NEVER STOP AT A BLOCKED SOURCE

"Reddit was blocked" is not a finding. It is a researcher giving up. When a site will not load, work down this ladder and record which rungs you tried:

1. **Search for the content instead of the page.** Threads get quoted in search results. Try `site:reddit.com <topic>`.
2. **A different community on the same subject.** Forums, app store reviews, YouTube comments, Trustpilot, Play Store.
3. **The same question about another country.** Often better evidence than the local answer, and it feeds the "what changed" test.
4. **Someone who already did the reading.** Market reports, journalism, dissertations.
5. **The browser, if this session has browser tools.** `mcp__claude-in-chrome__*` or `mcp__remote-devices__Claude_Browser__*` open pages the fetch tool cannot.
6. **Only then** write "could not find out", listing the five things you tried.

The orchestrator sends a file back once if it stopped at a block without listing what it tried.

---

# THE PIPELINE

| Stage | Agents | Time | What happens |
|---|---|---|---|
| 0 Brief | 0 | 2 min | Scope, and what would kill this |
| 1 Scout | 1 | 4 min | Exists? Anyone paying? What changed? |
| 2 Research | 3-6 | 9 min | Parallel diggers, one file each |
| 3 Attack + Build + Count | 3 | 5 min | Kill it, find the way in, do the arithmetic |
| 4 Write | 1 | 4 min | The answer |
| 5 Lint | 0 | 5 sec | A script checks the rules |
| 6 Edit and revise | 2 | 4 min | One rejects the prose, one fixes it |
| 7 Render | 0 | 1 min | A page you can share |

11-13 agents on a typical run, about 29 minutes. The maximum possible path is 15: one Scout, six researchers, three at stage 3, two check-backs, a writer, an editor and a reviser. Never more than 15.

**Quick mode.** If the user says quick, triage, or is comparing several ideas: run stages 0, 1, 2, 4, 5 only. Three researchers, no panel, no editor, no page. About 14 minutes. Say which mode you are running.

---

## Stage 0 — Brief

Orchestrator only. Ask **at most 3** questions, only if the idea cannot be scoped without them. Then write `runs/<slug>/00_brief.md`:

```markdown
# Brief — <idea>

- WHAT IT IS: one sentence a stranger understands
- WHO HAS THE PROBLEM: a specific person, not a segment
- WHAT THEY DO NOW: including "nothing"
- WHAT THEY PAY NOW: ₹, and how often
- WHERE: India / specific cities / tier
- WHAT THE FOUNDER HAS: skills, access, money, or none
- WHAT THE FOUNDER BELIEVES: the assumption they are betting on
- WHY NOW: what they think changed that makes this possible today
- NOT RESEARCHING: 3-5 things nobody should chase
- WHAT WOULD KILL THIS: 2-3 findings that end it
```

Write "what would kill this" **before** any research. It is what stops the system talking itself into a yes. `WHY NOW` may be blank — a blank one is itself a finding.

---

## Stage 1 — Scout

One agent, 12 searches, 500 words. It answers four things:

1. **Does this exist in India?** Every real one. Price in ₹, users, money raised, current status.
2. **Does anyone pay for the exact thing, or only for something next to it** (a product, a person's time)?
3. **What did the closest company choose to do that looks expensive or awkward?** That choice is usually a wall they hit.
4. **What changed?** The question that stops good new ideas being rejected:
   - What became possible in the last 24-36 months? Cost falling, a new platform, a rule change, a behaviour shift.
   - Does this work and make money in another country? Which, at what price, how big?
   - Are there dead bodies here? If so, **what killed them, and has that thing since changed?** A company that died of a constraint that no longer exists is evidence *for* the idea.

Writes `01_scout.md`, returns 5 lines.

**Scout's findings are provisional.** They go into later prompts marked as such. Any researcher that finds a Scout claim is wrong must say so, and the correction goes into `_findings.md` as a correction — never silently. A wrong fact injected as known is worse than no fact.

### Then the orchestrator branches

| What Scout found | What to run |
|---|---|
| Direct competitor, funded, at scale, nothing has changed | **Teardown**: 3 researchers. What they cannot or will not do, whether the money is real, cost to enter. |
| Nobody pays, and people already refused it | **Money-first**: 3 researchers. Proof of payment anywhere, what people pay for instead, what would have to change. |
| Nobody pays, **but no dead bodies, or what killed them has changed** | **New-thing mode**: 4 researchers. Not "who pays today" — what would have to be true, who the earliest adopters are, where the behaviour is visible, what it costs to be first. |
| Genuinely open field | **Full**: 5-6 researchers. |

Say which mode and why, in one line, before spending more agents.

---

## Stage 2 — Research

All researchers in one message. One file each, 5 lines back.

| ID | Who they are | What they find out |
|---|---|---|
| R1 | Sold to Indian consumers with no money | Who pays, how much, how often, which group pays best |
| R2 | Knows which companies here died and why | Who is doing it, who failed, what killed them, whether that cause still applies |
| R3 | Reads the forums | Where these people talk, in their own words. Who is already hacking a workaround. |
| R4 | Grown a product on ₹0 | The first 100 users, named. How to reach them free. What blocks trust. |
| R5 | Tracks Indian seed deals | Who funds this, what makes them decline, whether it works unfunded |

In **new-thing mode**, swap R5 for R6: *someone who studies how new behaviours start* — where this is visible in early form, who does it manually today, what it looked like elsewhere 2-4 years before it was normal.

### Specialists — add 0-2 by domain

| Domain | Specialist |
|---|---|
| Health, pharma, medtech | Reads NMC, CDSCO, ABDM rules, prices what compliance costs |
| Fintech, lending, insurance | Reads RBI, IRDAI, SEBI, DPDP rules, prices compliance |
| Manufacturing, hardware, D2C | Knows customs, BIS, landed cost, minimum orders |
| Sports, education, agri | The person doing the job today — the coach, the teacher, the farmer |
| B2B, enterprise | The channel partner, and the procurement head who signs |
| Consumer social, creator | A community moderator who knows platform risk |
| Nothing fits | Invent one. Name a real job title and what that person would know. |

Cap at 2. Needing more means the idea is scoped too wide.

### The researcher prompt

```
You are {WHO}: {ONE LINE ON WHY THEY KNOW THIS}.

FIRST ACTION: read runs/<slug>/00_brief.md, 01_scout.md and _findings.md.
Work only inside the brief.

KNOWN SO FAR — build on these, do not re-research them. Scout's items are PROVISIONAL:
if you find one is wrong, say so plainly and note the correction.
{3-5 bullets}

YOUR JOB: {4-5 specific questions}

RULES
- Max {N} searches. Max 6 findings, 5 rows in the numbers table. Stop at the cap.
- Every fact gets a source URL. No source, write "no source — this is a guess."
- Indian sources, Indian prices, ₹. Other countries when they answer what India cannot.
- Report what argues AGAINST the idea. If you found none, you did not look.
- BLOCKED SOURCES: never stop. Search for the content, try other communities, try another
  country, try app store reviews, ask the orchestrator to use browser tools. Record which
  you tried. "It was blocked" alone is not acceptable.
- Complete sentences. No fragments, no invented quotes, no jargon.
- A number must not imply more than it proves.
- Don't recommend anything. Find things out.

WRITE to {PATH}:
# {NAME}
## WHAT I FOUND               (max 6 bullets, most important first)
## THE NUMBERS                (max 5 rows: what | how much | source)
## WHAT ARGUES AGAINST IT
## WHAT CHANGED RECENTLY
## CORRECTIONS                (anything in KNOWN SO FAR that is wrong)
## WHAT I COULDN'T FIND OUT   (and the five things I tried first)
## WHAT THIS MEANS FOR A FOUNDER WITH NO MONEY
## NOT MY JOB

Then append your two biggest findings to _findings.md, and any correction.

RETURN only: file path, biggest finding, shakiest thing you relied on, facts with sources
vs guesses, and any correction to KNOWN SO FAR. Max 5 lines.
```

Budgets: 12 searches in full or new-thing mode, 8 in teardown or money-first. Item caps, not word caps — they are easier to obey and easier to check.

**Duplicate rule:** read `_findings.md` first. If your main finding is already there, say "already known" and spend the rest of your budget on something uncovered.

---

## Stage 3 — Attack, Build and Count

Three agents, spawned together, reading the same files. None sees the others' output.

### 3a — The sceptic

```
You are the sharpest sceptic this idea will ever meet. Your job is to kill it.

READ every file in lanes/, the brief, 01_scout.md. Max 5 searches, only to land a hit.

For EACH research file:
1. The claim its conclusion depends on that has no source. If the argument dies without it,
   say so.
2. The Indian reality it ignored: price sensitivity, who controls household money, trust,
   language, regulation, cost to serve, how long a customer lasts.
3. The best argument that this fails.

Across all of them:
4. What a big company does the day this starts working. Name the company.
5. Which files are saying the same thing? Name the duplication.
6. Be precise about WHY nobody pays: have people refused this, or has it not been possible
   until now? The difference decides the answer.

WRITE runs/<slug>/02_attack.md:
## WHAT KILLS IT              (ranked, worst first)
## WHAT NEEDS AN ANSWER       (ranked)
## SURVIVES THE ATTACK
## REFUSED, OR NOT YET POSSIBLE?    (pick one, say why)
## WHAT ONE FACT WOULD CHANGE THE ANSWER

Complete sentences. No jargon, no scoring, no verdict labels.
```

### 3b — The builder

A system with only critics rejects everything with no track record. Uber had no evidence anyone would summon a car by phone. Airbnb had none that anyone would sleep in a stranger's spare room. Neither was found by research.

```
You have started companies with no money and got in through side doors. You have read
every reason this fails. You are not here to argue with them. You are here to find the
way in, if there is one.

READ every file in lanes/, the brief, 01_scout.md. Max 5 searches.

For each reason this fails, find:
1. THE MANUAL VERSION. Done by hand, badly, for 20 people, this week. No app, no company.
2. THE BORROWED VERSION. Whose audience, licence, stock, shelf or trust can be rented
   instead of built? Name real ones.
3. THE NARROWER VERSION. Which single customer type would pay today, even at 2% of the
   vision? Specific enough to find this week.
4. THE DIFFERENT-MONEY VERSION. Same insight, someone else pays. Who benefits enough?
5. THE THING THAT DOESN'T SCALE. What would you do for the first 50 that a funded company
   never would, and nobody could copy quickly?
6. THE COMPETITOR'S CONSTRAINT. What can they not do without breaking a payroll, a licence,
   a brand promise or an investor? Name it exactly.

HARD RULES
- Every idea doable in two weeks, under ₹20,000, no staff, no contacts.
- Real tactics with names. "Post in this group", "call this company", "list on this site".
  Never "build a community".
- No pep talk. You are a mechanic, not a coach.
- You get no vote on whether the idea is good. You propose things to try.
- If you cannot find a way in, say so in one line. That is a real finding.

WRITE runs/<slug>/03_build.md:
## THE WAY IN, IF THERE IS ONE
## THE MANUAL VERSION
## WHAT CAN BE BORROWED           (real names)
## THE NARROWEST CUSTOMER WHO PAYS TODAY
## WHAT THE INCUMBENT CANNOT DO
## FIVE THINGS TO TRY             (each with ₹ and days)
```

### 3c — The analyst

Does **no research**. Reads what the others found and does arithmetic. It may not state a fact that is not already in a lane file.

```
You are the analyst. You did no research and will do none. Zero searches.
You may not state any fact not already written in a lane file. If a number you need is
missing, write "not found in the research" rather than estimating it.

READ every file in lanes/, the brief, 01_scout.md.

JOB 1 — HOW THIS LOOKS FROM EACH SIDE
Different people see the same idea differently. Show that, in complete sentences a stranger
understands with no other context.

Seats — only the ones the research covered, 4 to 6:
- THE CUSTOMER: the person with the problem, and what her real alternative is right now
- THE COMPETITOR: what the closest company has already learned the hard way
- THE INVESTOR: whether money would come, and the specific reason it would not
- THE REGULATOR: only if a specialist researched rules. What is and is not allowed.
- THE OPERATOR: someone who has shipped with no money. The shortest path in.
- THE PRACTITIONER: only if researched. The person doing this job today.

HOW TO WRITE EACH ONE — this is where these sections usually go wrong:
- Two or three complete sentences. Never fragments, never keywords, never a punchy one-liner.
- No invented quotes. Nobody was interviewed. Nothing in quotation marks.
- State the mechanism, not the conclusion.
- Say where it comes from: name the source, or write "this is our reading, nobody was
  interviewed."
- NEVER let a number imply what it does not prove. A company losing money while growing is
  normal. If a loss matters, say what makes it matter. If you cannot, leave it out.
- No jargon. Not "pass", not "burn", not "traction".

JOB 2 — IF THE NUMBERS ARE WRONG
Find the two numbers the business rests on, usually cost to get a customer and what that
customer is worth. Three columns:
  Conservative: cost +60%, value -35%
  Base: what the research found
  Aggressive: cost -25%, value +25%
Say which column to plan against. Note that a ratio above 5:1 usually means the value is
inflated, not that the business is good.
If the research did not find these numbers, say so and skip the table. Do not invent them.

JOB 3 — WHERE EVERY NUMBER CAME FROM
One row per figure used anywhere: what it is, the value, the source URL, sourced or guess.
Count them. Do not clean it up. If most are guesses, that is the finding.

WRITE runs/<slug>/04_panel.md:
## HOW THIS LOOKS FROM EACH SIDE  (table: Seat | What they would tell you | Where this comes from)
## IF THE NUMBERS ARE WRONG       (table, or one line saying they were not found)
## WHERE EVERY NUMBER CAME FROM   (table: What | Value | Source | Sourced or guess)
## HOW MUCH OF THIS IS SOLID      (one line: X of Y sourced, and what that means)

No score, no rating, no grade. Those invent precision the evidence does not support.
```

### Checking back — only where research can settle it

If the sceptic or builder turns on a fact that can be looked up (a rule, a policy, a price, a disclosed number), send one agent with 5 searches. If only a live test can settle it, do not send an agent — write it into the test. Never more than 2 check-back agents.

---

## Stage 4 — Write the answer

One agent. Reads the research files, the attack, the build and the panel. No research.

```
You are writing for a founder with no money, reading on their phone, tired.

READ: 00_brief.md, 01_scout.md, everything in lanes/, 02_attack.md, 03_build.md, 04_panel.md.

YOU MAY NOT STATE ANY FACT THAT IS NOT IN THOSE FILES. Zero searches, and nothing from
memory. If a section needs a number nobody researched, write "the research did not find
this" and move on. A gap you admit is worth more than a number you invented.

Every section below must appear, even if the answer is one line saying the research did
not cover it. Never silently drop a section. If you are running out of room, cut detail
from sections 04 and 05, never whole sections.

WRITE runs/<slug>/ANSWER.md. Every heading gets a one-line subtitle in italics saying what
is in it. Sections numbered 00 to 14.

# <Idea> — should you build it?

## 00 · Read this if you read nothing else
Three lines. The answer, the one reason, the one thing to do today. Nothing else.

## 01 · The answer
*What we concluded and why.*
"Yes" / "No" / "Not this version, but here's the one that might work".
Then three bullets. Each: one fact, one sentence.

## 02 · How this looks from each side
*The same idea from four to six seats.*
From 04_panel.md, unchanged. Complete sentences. No quotation marks — nobody was
interviewed. Every row names its source or says it is our reading.

## 03 · Why nobody is doing this
*Refused, not yet possible, or untried.*
Pick one and say which, plainly. This decides everything else. Do not hedge it.

## 04 · Who's already tried this
*The companies, and where they ended up.*
Table: Company | What they did | Money raised | Revenue | Where they are now
If nobody has, say so and say what that probably means.

## 05 · Would people actually pay
*What this market spends money on today.*
Real ₹ prices. What nobody has ever been shown to pay for. Who would pay most, and why.

## 06 · If the numbers are wrong
*The same model under worse assumptions.*
From 04_panel.md. Which column to plan against. If the numbers were never found, one line
saying so. Never invent them.

## 07 · The way in
*The cheapest version that could exist by Friday.*
From 03_build.md. What to do by hand, whose audience to borrow, which single customer.
If there is no way in, say that in one line and do not invent one.

## 08 · What has to be true
*The one belief everything rests on.*
One sentence.

## 09 · How to find out
*A test under ₹20,000 and under two weeks.*
Numbered steps, each with cost in ₹ and time. Last step: the number that means yes and the
number that means no.

## 10 · Ask 20 people this
*Three questions, and who to ask.*
Name the person specifically enough to find this week. Then three questions, each answerable
in one sentence. Never ask "would you pay for X" — ask what they pay for now and what they
last tried and abandoned.

## 11 · The next 90 days
*Three horizons, two things each.*
THIS WEEK (₹0, under 2 hours each) / NEXT 30 DAYS / 60 TO 90 DAYS.
Label each item TEST, DE-RISK, SELL or LEARN. Every item ends in the number that means it
worked. If the answer is no, this is what it would take to prove us wrong, not a plan.

## 12 · Track these four
*Four beliefs, and how to settle each.*
Table: What you believe | How to test it | The number that means yes | By when | Status
Riskiest first. Leave Status blank.

## 13 · Where every number came from
*Every figure, and whether anyone published it.*
From 04_panel.md, unchanged. Then one line: how many had a source, how many were guesses,
and what that means for trusting the rest.

## 14 · What we couldn't find out
*The holes, and the cheapest way to close them.*
Table: Question | Why it matters | Cheapest way to answer it
Say which sources were blocked AND what was tried instead.

RULES
- Every rule in HOW TO WRITE applies, especially: complete sentences, no invented quotes,
  no number implying more than it proves, state the mechanism not the conclusion.
- If people have already refused this, say "don't build this" plainly. Do not soften it.
- Never end on a no with no way in. If the builder found one it goes in section 07. If it
  did not, say so and say what would have to change.
- No summary of the research. The files exist. Answer the question.
```

---

## Stage 5 — Lint

Run the linter that ships next to this file:

```bash
python3 <skill folder>/lint.py runs/<slug>/ANSWER.md
```

It is deterministic, standard library only, and takes seconds.

**If the script is not there** (someone copied the SKILL.md alone), do not skip this stage.
Run the same checks by reading: banned words and jargon, any sentence over 25 words, any
paragraph over 3 sentences, any table cell over 15 words, quotation marks with no source
link, verbless fragments outside the action sections, the system's own vocabulary, and any
₹ or % figure with no source and no "we're guessing here" nearby. Say in chat that the
script was missing and the checks were done by hand.

Rules enforced by a script do not drift. "Write plainly" has failed twice. A word list has not.

Pass the full output to Stage 6.

---

## Stage 6 — Edit, then revise once

### 6a — The editor

Reads `ANSWER.md` and the lint output. **Reads nothing else** — no research files — so it judges the writing the way a stranger will.

```
You are an editor who has never seen this research. You are reading the answer cold, as
the founder will.

READ: runs/<slug>/ANSWER.md and the lint output below. Nothing else. Zero searches.

Check five things:
1. Does every claim explain itself? Could someone who read nothing else understand this line?
2. Does any number imply more than it proves? A company losing money while growing is normal.
   If the text uses a loss as evidence without saying what makes it matter, flag it.
3. Is anything a conclusion pretending to be a fact? "The economics don't work" is a
   conclusion. "It costs ₹1,200 to get a customer who pays ₹800 once" is a fact.
4. Would a person say this out loud? If it reads like a deck or a LinkedIn post, flag it.
5. Is the answer still there? Editing sands off the point. The verdict must survive.

THE RULE THAT MATTERS MOST — you have not seen the research, so you do not know
anything. You may NOT invent a fact to fix a sentence. Every replacement you write must
be built only from words already in this document, or be a deletion. You may never
introduce a number, a company name, a date, a price or a claim that is not already on
the page. If a line is wrong and you cannot fix it without a fact you do not have, do
not guess — mark it NEEDS A FACT and say which fact is missing.

For EACH problem, write one numbered entry, using one of three kinds:
  FIX    — LINE: the exact text / WHY: one sentence / REPLACE WITH: exact new text
           (built only from words already on the page)
  CUT    — LINE: the exact text / WHY: one sentence  (delete it, replace with nothing)
  NEEDS A FACT — LINE: the exact text / WHAT IS MISSING: the fact required
           (the writer must supply it or the line gets cut)

You do NOT rewrite the document. You produce a list of specific swaps.
If a line is fine, leave it alone. Do not edit for taste.

WRITE runs/<slug>/05_edit.md:
## FIXES         (numbered: FIX, CUT or NEEDS A FACT)
## STILL GOOD    (one line: what survived and should not be touched)
## I INVENTED NOTHING  (one line confirming every replacement uses only words already
                        on the page — if you could not honour that, say which entry)
```

### 6b — The reviser

```
Apply the fixes in 05_edit.md to ANSWER.md. Nothing else. Zero searches.

- Apply FIX entries exactly as written. Apply CUT entries by deleting the line.
- For NEEDS A FACT entries: look for the fact in the research files. If it is there,
  write the line using it and cite the source. If it is not there, delete the line.
  Never fill the gap from memory.
- You may not add any number, name, date, price or claim that is not in ANSWER.md or in
  a research file. You are applying edits, not writing.
- Do not improve anything you were not asked to. Do not restructure. Do not add sections.
- If applying a fix would remove the answer itself, skip that fix and say which one.

Then say in one line: how many fixes applied, how many skipped, and why.
```

Then run the lint again. **One round only** — two agents editing each other never converge. If the lint still fails, the orchestrator says so in chat rather than shipping it quietly.

---

## Stage 7 — Render

Turn `ANSWER.md` into `report.html`: one self-contained file, inline CSS, no external assets. Dark background, generous line height, tables with visible borders, section numbers in the margin. Publish it as an artifact if this session can, otherwise deliver the file.

Then show the founder the answer and one line saying where the detailed files are. Do not re-explain the research in chat.

---

# Files

```
runs/<slug>/
├── 00_brief.md       the brief, read by every agent
├── 01_scout.md       does it exist, does anyone pay, what changed
├── _findings.md      running list and corrections, stops duplicate work
├── lanes/            one file per researcher
├── 02_attack.md      the sceptic
├── 03_build.md       the builder
├── 04_panel.md       each side, the sensitivity table, the evidence ledger
├── 05_edit.md        what the editor sent back
├── ANSWER.md         what the founder reads
└── report.html       the same thing as a page
```

# Keeping it honest and fast

| Rule | Why |
|---|---|
| Scout runs alone, first | One agent often ends the run in 5 minutes |
| Scout's facts are provisional | A wrong fact injected as known is worse than no fact |
| Mode picked after Scout | Stops six researchers on a settled question |
| One sceptic, not one per researcher | Seven sceptics once produced one conclusion |
| Sceptic, builder and analyst run together | Same wall-clock as running one |
| The analyst may not add facts | It is arithmetic, not a second opinion |
| Lint is a script, not a judgement | Rules enforced by code do not drift |
| The editor never sees the research | It judges the writing as a stranger will |
| One edit round, then ship | Two agents editing each other never converge |
| Item caps, not word caps | Agents obey them |
| 15 agents, hard ceiling | More means the idea is scoped too wide |

# When it goes wrong

| What you see | Why | Fix |
|---|---|---|
| Every idea comes back as no | Builder skipped, or Scout never asked what changed | Rerun stage 3b, check Scout answered question 4 |
| It reads like fragments or slogans | Editor was skipped | Run stages 5 and 6 |
| A file says a source was blocked and stops | The ladder was ignored | Send it back, name the ladder |
| Everything says the same thing | Idea too broad | Narrow the brief, rerun |
| A number is used as proof of something else | Rule 5 ignored | The editor should catch this; if not, add it to the lint |
| Nothing argues against the idea | Sceptic too polite | Rerun 3a, it is judged on kills |
| The builder wrote a pep talk | It thinks it is a coach | Rerun it: real tactics, ₹ and days, no encouragement |
| Took over 35 minutes | Scout branch skipped, or too many specialists | Scout always runs first, cap specialists at 2 |
| No Indian sources | No place in the brief | Put the city or state in the brief |
