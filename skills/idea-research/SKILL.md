---
name: idea-research
description: 'Checks whether a startup idea is worth building. Research agents dig, one sceptic tries to kill it, one builder tries to find the way in, and the answer says which. Asks what changed recently that makes this newly possible, so genuinely new ideas are not rejected for having no track record. India-first, plain English. Use when someone wants an idea checked, a market or competitor scan, gaps and threats, community or investor sentiment, or a go/no-go on a new bet.'
license: MIT
metadata:
  tags: "Startup Research, Market Analysis, Multi-Agent, India, Idea Validation"
  category: "research"
---

# Idea Research

Check whether an idea is worth building. One set of agents digs, one tries to kill it, one tries to find the way in, and the answer tells the founder which won.

- Market: India by default. Money in ₹.
- Reader: a founder with no money, no team, no network.
- Job: find the truth, not a verdict. A "no" with no way in is only half a job done.

## When to use

| Use it for | Don't use it for |
|---|---|
| "Is this idea worth building" | Writing a pitch deck |
| "Should I build X" | Building a financial model |
| "Is there a gap in this market" | Research on a company that already exists |
| "Would anyone fund this in India" | Looking up a market size |

## The two mistakes this system must not make

1. **Saying yes to a corpse.** Most ideas that nobody pays for are ideas people have already refused. Softening that helps nobody.
2. **Saying no to something new.** Nobody paid to summon a car from a phone before GPS phones existed. Nobody paid for web search before the web got big. An idea with no track record is not the same as an idea that has been refused.

Telling those apart is the whole job. Everything below exists to do it.

---

# HOW TO WRITE (read this before anything else)

The founder is reading on a phone, at night, tired. Write like a smart friend explaining something over chai, not like a consultant billing by the word.

## Banned outright

| Never write | Write instead |
|---|---|
| artefact, offering, solution, proposition | the thing, the PDF, the report, the app |
| keepable, actionable, learnings, surface | Say what it actually is |
| load-bearing, resolves to, converts into | rests on, is really, becomes |
| leverage (as a verb), unlock, enable | use, let, allow |
| ecosystem, landscape, moat, thesis, posture | name the actual thing |
| "Buy the traffic" | "Run Meta ads, ₹12,000" |
| "VERDICT: KILL" | "Should you build this? No." |
| "The killer assumption" | "What has to be true" |
| "Three lanes resolved DEAD" | "Three of the seven checks failed" |

**Never use the system's internal words in what the founder reads.** No lane, no verdict, no kill criteria, no confidence tags, no down-weighting. That is scaffolding. The founder sees the building.

## Sentence rules

1. **Say the action, not a saying about the action.** "Run Meta ads targeting women 22-38 for ₹12,000" — not "buy the traffic, because there is no network to borrow."
2. **No aphorisms.** If a sentence sounds like it belongs on a poster, delete it. Never state a fact then restate it as wisdom.
3. **Three sentences maximum per paragraph.** Longer means it should be a list or a table.
4. **Nothing over 25 words in a sentence.**
5. **Name real things.** Real companies, real prices in ₹, real websites. "A funded competitor" is useless; "Mylo, $24.25M raised, ₹63.4 Cr revenue, ₹19 Cr loss" is the finding.
6. **Numbers beat adjectives.** Not "expensive" — "₹40,000 a month."
7. **If you are guessing, write "we're guessing here."** In those words.

## Table rules

- Every cell: 15 words maximum. Preferably 5.
- No cell that is only a hedge ("Partly.", "It depends.")
- Headers are short and concrete: "Company", "Price", "Users", "What it means".
- If a column would be full of paragraphs, it is not a column. Make it a list below.

## The read-aloud test

Read each section back in your head. If it sounds like a McKinsey deck or a LinkedIn post, rewrite it.

---

# NEVER STOP AT A BLOCKED SOURCE

Every researcher follows this. "Reddit was blocked" is not a finding. It is a researcher giving up.

When a site will not load, work down this ladder and say in the file which rungs you tried:

1. **Search for the content instead of the page.** Reddit and Quora threads are quoted all over search results. Try `site:reddit.com <topic>` and the topic plus "reddit" as plain search.
2. **Go to a different community on the same subject.** Forums, Discord write-ups, Facebook group coverage, niche Indian sites, app store review pages, YouTube comment round-ups, Trustpilot, Play Store reviews.
3. **Ask the same question about another country.** This is often better evidence than the local answer, and it feeds the "what changed" test below. If couples in Indonesia or Brazil pay for this, the Indian question becomes *when*, not *whether*.
4. **Look for someone who already did the reading.** Market reports, dissertations, journalism, a Substack, a YC company's blog post.
5. **Use the browser, if this session has browser tools.** Claude in Chrome (`mcp__claude-in-chrome__*`) or the built-in browser (`mcp__remote-devices__Claude_Browser__*`) can open pages the fetch tool cannot. Ask the orchestrator to run it if a subagent cannot.
6. **Only then** write "could not find out", and list the five things you tried.

The orchestrator must check this. If a research file says a source was blocked and does not list what was tried instead, send it back once.

---

# THE PIPELINE

| Stage | Agents | Time | What happens |
|---|---|---|---|
| 0 Scope | 0 | 2 min | Write the brief |
| 1 Scout | 1 | 4 min | Does it exist, does anyone pay, **and what changed recently** |
| 2 Research | 3-6 | 10 min | Parallel researchers, one file each |
| 3 Attack + Build | 2 | 5 min | One tries to kill it, one tries to find the way in. Same time, same files. |
| 4 Answer | 1 | 4 min | Reads both sides, writes the answer |

Total: 7-11 agents, 20-25 minutes. Never more than 12.

---

## Stage 0 — Scope

Orchestrator only. No agents.

Ask **at most 3** questions, only if the idea cannot be scoped without them. Then write `runs/<slug>/00_brief.md`:

```markdown
# Brief — <idea>

- WHAT IT IS: one sentence a stranger understands
- WHO HAS THE PROBLEM: a specific person, not a segment
- WHAT THEY DO NOW: including "nothing"
- WHAT THEY PAY NOW: ₹, and how often
- WHERE: India / specific cities / tier
- WHAT THE FOUNDER HAS: skills, access, money, or none
- WHY NOW: what the founder thinks changed that makes this possible today
- NOT RESEARCHING: 3-5 things nobody should chase
- WHAT WOULD KILL THIS: 2-3 findings that end it
```

Write "what would kill this" **before** any research. It is what stops the system talking itself into a yes.

`WHY NOW` may be blank if the founder has no answer. A blank one is itself a finding, and Scout will try to fill it.

---

## Stage 1 — Scout

One agent, 12 searches, 500 words. Before anything expensive.

It answers four things:

1. **Does this exist in India?** Name every real one. Price in ₹, users, money raised, current status.
2. **Does anyone pay for the exact thing, or only for something next to it** (a product, a person's time)?
3. **What did the closest company choose to do that looks expensive or awkward?** That choice is usually them hitting a wall.
4. **What changed?** This is the question that stops good new ideas being rejected. Specifically:
   - What became possible in the last 24 to 36 months that was not before? Cost falling, a new platform, a rule change, a behaviour shift, infrastructure arriving.
   - Does this work and make money in another country? Which, at what price, how big?
   - Are there dead bodies here? If yes, **what killed them, and has that thing since changed?** A company that died of a constraint that no longer exists is evidence *for* the idea, not against it.

It writes `01_scout.md` and returns 5 lines.

### Then the orchestrator branches

| What Scout found | What to run |
|---|---|
| Direct competitor, funded, at scale, and nothing has changed since | **Teardown**: 3 researchers. What that competitor cannot or will not do, whether the money is real, cost to enter. |
| Nobody pays for the core thing, and people have already refused it | **Money-first**: 3 researchers. Any proof of payment anywhere, what people pay for instead, what would have to change. |
| Nobody pays, **but no dead bodies, or the thing that killed them has changed** | **New-thing mode**: 4 researchers. Do not ask "who pays today". Ask what would have to be true, who the earliest adopters are, whether the new behaviour is visible anywhere yet, and what it costs to be first. |
| Genuinely open field | **Full**: 5-6 researchers. |

Say which mode was picked and why, in one line, before spending more agents.

**New-thing mode matters.** Most systems like this only have the first two rows, which is why they would reject anything genuinely new. If Scout finds that the ground moved recently, "nobody pays today" stops being evidence of anything.

---

## Stage 2 — Research

Spawn all researchers in one message. Each writes one file and returns 5 lines.

### Core researchers

| ID | Who they are | What they find out |
|---|---|---|
| R1 | Someone who has sold to Indian consumers with no money | Who pays, how much, how often, which group pays best. Real ₹, real sources. |
| R2 | Someone who knows which companies here died and why | Who is doing it now, who failed, what killed them, whether that cause still applies, who could enter tomorrow |
| R3 | Someone who reads the forums | Where these people talk, in their own words. Who is already hacking a workaround. |
| R4 | Someone who has grown a product on ₹0 | The first 100 users, named. How to reach them free. What blocks trust. |
| R5 | Someone who tracks Indian seed deals | Who funds this, what makes them pass, whether it works unfunded |

In **new-thing mode**, swap R5 for:

| R6 | Someone who studies how new behaviours start | Where this behaviour is visible in early form. Who is doing it manually today. What it looked like in another country 2-4 years before it became normal. |

### Specialists (add 0-2, by domain)

| Domain | Add this specialist |
|---|---|
| Health, pharma, medtech | Reads NMC, CDSCO, ABDM rules, prices what compliance costs |
| Fintech, lending, insurance | Reads RBI, IRDAI, SEBI, DPDP rules, prices compliance |
| Manufacturing, hardware, D2C | Knows customs, BIS, landed cost, minimum orders |
| Sports, education, agri | The person doing the job today — the coach, the teacher, the farmer |
| B2B, enterprise | The channel partner, and the procurement head who signs |
| Consumer social, creator | A community moderator who knows platform risk |
| Nothing fits | Invent one. Name a real job title and what that person would know. |

Cap at 2. Needing more means the idea is scoped too wide.

### What each researcher gets

```
You are {WHO}: {ONE LINE ON WHY THEY KNOW THIS}.

FIRST ACTION: read runs/<slug>/00_brief.md, 01_scout.md and _findings.md. Work only inside the brief.

ALREADY KNOWN — do not re-research, build on it:
{3-5 bullets from Scout and earlier waves}

YOUR JOB: {4-5 specific questions}

RULES
- Max {N} searches, max 700 words. Stop at the cap.
- Every fact gets a source URL. No source, write "no source — this is a guess."
- Indian sources, Indian prices, ₹. Other countries when they answer a question India cannot.
- Report what argues AGAINST the idea. If you found none, you did not look.
- BLOCKED SOURCES: never stop. Search for the content, try other communities, try another
  country, try app store reviews, ask the orchestrator to use browser tools. Write down which
  of these you tried. "It was blocked" on its own is not acceptable.
- Off-topic goes under NOT MY JOB. Don't chase it.
- Don't recommend anything. Find things out.
- Write plainly. No jargon, no aphorisms, three sentences per paragraph.

WRITE to {PATH}:
# {NAME}
## WHAT I FOUND        (bullets, most important first)
## THE NUMBERS         (table: what | how much | source)
## WHAT ARGUES AGAINST IT
## WHAT CHANGED RECENTLY  (anything that makes this newly possible, or newly impossible)
## WHAT I COULDN'T FIND OUT  (and the five things I tried first)
## WHAT THIS MEANS FOR A FOUNDER WITH NO MONEY
## NOT MY JOB

Then append your two biggest findings to _findings.md.

RETURN only: file path, biggest finding, shakiest thing you relied on, facts with sources vs guesses. Max 5 lines.
```

Budgets: 12 searches and 700 words in full or new-thing mode, 8 and 500 in teardown or money-first.

**Duplicate rule:** each researcher reads `_findings.md` before writing. If its main finding is already there, it says "already known" and spends the rest of its budget on something uncovered.

---

## Stage 3 — Attack and Build, at the same time

Two agents, spawned together, reading the same files. Neither sees the other's output. This is the argument the founder needs to watch.

### 3a — The sceptic

```
You are the sharpest sceptic this idea will ever meet. Your job is to kill it.

READ every file in lanes/, the brief and 01_scout.md. Max 5 new searches, only to land a hit.

For EACH research file:
1. The claim its conclusion depends on that has no source. If the argument dies without it, say so.
2. The Indian reality it ignored: price sensitivity, who controls household money, trust,
   language, regulation, cost to serve, how long a customer lasts.
3. The best argument that this fails.

Across all of them:
4. What a big company does the day this starts working. Name the company.
5. Which files are saying the same thing? Name the duplication.
6. Be precise about WHY nobody pays: have people refused this, or has it not been possible
   until now? These are different and the difference decides the answer.

WRITE runs/<slug>/02_attack.md:
## WHAT KILLS IT          (ranked, worst first)
## WHAT NEEDS AN ANSWER   (ranked)
## SURVIVES THE ATTACK
## REFUSED, OR NOT YET POSSIBLE?   (pick one, and say why)
## WHAT ONE FACT WOULD CHANGE THE ANSWER

Plain English. No scoring, no verdict labels, no jargon.
```

### 3b — The builder

This agent exists because a research system with no builder rejects everything that has no track record. Uber had no evidence anyone would summon a car by phone. Airbnb had no evidence anyone would sleep in a stranger's spare room. Those companies were not found by research. They were found by someone doing something manual and unreasonable for the first fifty customers.

```
You are someone who has started companies with no money and got in through side doors.
You have read every reason this fails. You are not here to argue with them.
You are here to find the way in, if there is one.

READ every file in lanes/, the brief and 01_scout.md. Max 5 searches.

For each reason this fails, find:
1. THE MANUAL VERSION. What does this look like done by hand, badly, for 20 people, this week?
   No product, no app, no company. What would you personally do?
2. THE BORROWED VERSION. Whose audience, licence, inventory, stock, trust or shelf can be
   rented instead of built? Name real ones.
3. THE NARROWER VERSION. Which single type of customer would pay today, even if that is 2%
   of the vision? Name them specifically enough to find this week.
4. THE DIFFERENT-MONEY VERSION. Same insight, different way of charging. Who else benefits
   enough to pay — and would they pay instead of the user?
5. THE THING THAT DOESN'T SCALE. What would you do for the first 50 customers that a funded
   company would never do, and that nobody could copy quickly?
6. THE COMPETITOR'S CONSTRAINT. Every incumbent has something it cannot do without breaking
   itself: a payroll, a licence, a brand promise, an investor. Name theirs, exactly.

HARD RULES
- Every idea must be doable in two weeks, under ₹20,000, no staff, no contacts.
- Name real tactics. "Post in this group", "call this company", "list on this site".
  Never "build a community" or "engage users".
- No pep talk. No "the opportunity is huge". You are a mechanic, not a coach.
- You do not get a vote on whether the idea is good. You propose things to try.
- If you genuinely cannot find a way in, say so in one line. That is a real finding and it
  is far more useful than a weak idea dressed up.

WRITE runs/<slug>/03_build.md:
## THE WAY IN, IF THERE IS ONE     (or one line saying there isn't)
## THE MANUAL VERSION              (what you'd do by hand this week)
## WHAT CAN BE BORROWED            (real names)
## THE NARROWEST CUSTOMER WHO PAYS TODAY
## WHAT THE INCUMBENT CANNOT DO
## FIVE THINGS TO TRY              (each with ₹ and days)

Plain English. Three sentences per paragraph. No jargon, no aphorisms.
```

### Checking back — only where research can settle it

If the sceptic or the builder turns on a fact that can be looked up (a rule, a policy, a price, a disclosed number), send one agent with 5 searches to check it. If it can only be settled by a live test, do not send an agent. Write it into the test and move on. Never more than 2 check-back agents.

---

## Stage 4 — The answer

One agent. Reads the research files, the attack and the build. Does no research.

```
You are writing the answer for a founder with no money, reading on their phone, tired.

READ: 00_brief.md, 01_scout.md, everything in lanes/, 02_attack.md, 03_build.md.

WRITE runs/<slug>/ANSWER.md in this exact structure:

# <Idea> — should you build it?

## The answer
"Yes" / "No" / "Not this version, but here's the one that might work".
Then three bullets. Each: one fact, one sentence.

## Why nobody is doing this
Pick one and say which, plainly:
- People have already refused it. Here are the companies that died trying.
- It has not been possible until recently. Here is what changed.
- Nobody has tried. Here is why that is suspicious, or why it is not.
This section decides everything else. Do not skip it and do not hedge it.

## Who's already tried this
Table: Company | What they did | Money raised | Revenue | Where they are now
If nobody has, say so, and say what that probably means.

## Would people actually pay
- What this market pays for today, with real ₹ prices
- What nobody has ever been shown to pay for
- One line on who would pay most, and why

## The way in
From the builder's file. The cheapest, most manual version of this that could exist by next
Friday. What to do by hand, whose audience to borrow, which single customer to start with.
If the builder found no way in, say that plainly in one line and do not invent one.

## What has to be true
One sentence. The single thing that, if false, ends this.

## How to find out
A test under ₹20,000 and under two weeks. Numbered steps, each with cost in ₹ and time.
Last step: the number that means yes, and the number that means no.

## Do this first
One thing, today, under two hours. Name exactly what to open and what to do.

## What we couldn't find out
Table: Question | Why it matters | Cheapest way to answer it
Say which sources were blocked AND what was tried instead.

RULES
- No jargon, no banned words, no aphorisms.
- Three sentences per paragraph. Nothing over 25 words. Table cells under 15 words.
- Real names, real prices, real websites.
- If a finding rests on a guess, write "we're guessing here".
- If people have already refused this, say "don't build this" plainly. Do not soften it.
- But never end on a no with no way in. If the builder found one, it goes in. If it did not,
  say so, and say what would have to change for there to be one.
- No summary of the research. The files exist. Answer the question.
```

## Delivering it

Show the founder the answer. Then one line naming where the detailed files are. Do not re-explain the research in chat.

---

# Files

```
runs/<slug>/
├── 00_brief.md        the brief, read by every agent
├── 01_scout.md        does it exist, does anyone pay, what changed
├── _findings.md       running list, stops duplicate work
├── _state.md          what has run
├── lanes/             one file per researcher
├── 02_attack.md       the sceptic
├── 03_build.md        the builder
└── ANSWER.md          what the founder reads
```

# Keeping it fast

| Rule | Why |
|---|---|
| Scout runs first, alone | One agent often ends the run in 5 minutes |
| Mode picked after Scout | Stops six researchers working a settled question |
| One sceptic, not one per researcher | Seven sceptics once produced one conclusion |
| Sceptic and builder run together | Same wall-clock as running one |
| Check back only on lookup-able facts | "Needs a live test" does not need an agent to say it |
| `_findings.md` before writing | Stops researchers re-deriving each other |
| 12 agents, hard ceiling | More than that means the idea is scoped too wide |

# When it goes wrong

| What you see | Why | Fix |
|---|---|---|
| Every idea comes back as no | Builder was skipped, or Scout never asked what changed | Rerun stage 3b, and check Scout answered question 4 |
| A research file says a source was blocked and stops there | The ladder was ignored | Send it back once, name the ladder |
| Everything says the same thing | Idea scoped too broadly | Narrow the brief, rerun |
| It reads like a consultant wrote it | Writing rules ignored | Rewrite stage 4 only, point at the banned list |
| Nothing argues against the idea | Sceptic too polite | Rerun stage 3a, tell it it is judged on kills |
| The builder wrote a pep talk | It thinks it is a coach | Rerun it, remind it: real tactics, ₹ and days, no encouragement |
| Took over 30 minutes | Scout branch skipped | Scout always runs first |
| No Indian sources | No place in the brief | Put the city or state in the brief |
