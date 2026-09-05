---
name: idea-research
description: 'Checks whether a startup idea is worth building, using research agents that argue against each other and write everything to files. India-first, written for a founder with no money. Returns a plain-English answer, not a report. Use when someone wants an idea checked, a market or competitor scan, a look at gaps and threats, community and investor sentiment, or a go/no-go on a new bet.'
license: MIT
metadata:
  tags: "Startup Research, Market Analysis, Multi-Agent, India, Idea Validation"
  category: "research"
---

# Idea Research

Check whether an idea is worth building by making research agents argue with each other in files, then answer the founder in plain English.

- Market: India by default. Money in ₹.
- Reader: a founder with no money, no team, no network.
- Job: try to kill the idea. If it survives, that means something.

## When to use

| Use it for | Don't use it for |
|---|---|
| "Is this idea worth building" | Writing a pitch deck |
| "Should I build X" | Building a financial model |
| "Is there a gap in this market" | Research on a company that already exists |
| "Would anyone fund this in India" | Looking up a market size |

---

# HOW TO WRITE (read this before anything else)

Most of what goes wrong with this skill is the writing, not the research. The founder is reading on a phone, at night, tired. Write like a smart friend explaining something over chai, not like a consultant billing by the word.

## Banned outright

| Never write | Write instead |
|---|---|
| artefact, offering, solution, proposition | the thing, the PDF, the report, the app |
| keepable, actionable, learnings, surface | Say what it actually is |
| load-bearing, resolves to, converts into | rests on, is really, becomes |
| leverage (as a verb), unlock, enable | use, let, allow |
| "Buy the traffic" | "Run Meta ads, ₹12,000" |
| "VERDICT: KILL" | "Should you build this? No." |
| "The killer assumption" | "What has to be true" |
| "Three lanes resolved DEAD" | "Three of the seven checks failed" |

**Never use the system's internal words in what the founder reads.** No lane, no verdict, no SURVIVES/WOUNDED/DEAD, no kill criteria, no confidence tags, no ASSUMPTION, no down-weighting. Those are scaffolding. The founder sees the building, not the scaffolding.

## Sentence rules

1. **Say the action, not a saying about the action.** "Run Meta ads targeting women 22-38 for ₹12,000" — not "buy the traffic, because there is no network to borrow."
2. **No aphorisms.** If a sentence sounds like it belongs on a poster, delete it. A line that states a fact then restates it as wisdom is one line too long.
3. **Three sentences maximum per paragraph.** Longer means it should be a list or a table.
4. **Name real things.** Real company names, real prices in ₹, real websites, real tools. "A funded competitor" is useless; "Pinky Promise, ₹99 a consult, 400,000 users" is the finding.
5. **No em-dash stacking.** One per paragraph at most.
6. **Numbers beat adjectives.** Not "expensive" — "₹40,000 a month."
7. **If you are guessing, say "we're guessing."** In those words.

## Table rules

Tables are for comparing things, not for hiding prose in a grid.

- Every cell: 15 words maximum. Preferably 5.
- No cell may contain a hedge on its own ("Partly.", "It depends.")
- Column headers are short and concrete: "Company", "Price", "Users", "What it means" — never "Why that reason is beatable now"
- If a column would be full of paragraphs, it is not a column. Make it a list below the table.

## The read-aloud test

Before writing any section, read the previous one aloud in your head. If you sound like a McKinsey deck or a LinkedIn post, rewrite it. If you sound like a person telling a friend what they found, ship it.

---

# THE PIPELINE

Five stages. Stage 1 often ends the run cheaply, which is the point.

| Stage | Agents | Time | What happens |
|---|---|---|---|
| 0 Scope | 0 | 2 min | Orchestrator writes the brief, picks the roster |
| 1 Scout | 1 | 4 min | One agent checks: does this already exist, and does anyone pay for it |
| 2 Research | 3-6 | 10 min | Parallel researchers, one file each |
| 3 Attack | 1-2 | 5 min | One agent attacks everything at once |
| 4 Answer | 1 | 4 min | One agent writes the founder-facing answer |

Total: 6-10 agents, 20-25 minutes. Never more than 12 agents.

---

## Stage 0 — Scope

Orchestrator only. No agents yet.

Ask **at most 3** questions, only if the idea can't be scoped without them. Then write `runs/<slug>/00_brief.md`:

```markdown
# Brief — <idea>

- WHAT IT IS: one sentence a stranger understands
- WHO HAS THE PROBLEM: a specific person, not a segment
- WHAT THEY DO NOW: including "nothing"
- WHAT THEY PAY NOW: ₹, and how often
- WHERE: India / specific cities / tier
- WHAT THE FOUNDER HAS: skills, access, money, or none
- NOT RESEARCHING: 3-5 things nobody should chase
- WHAT WOULD KILL THIS: 2-3 findings that end it
```

Write "what would kill this" **before** any research. It is what stops the system talking itself into a yes.

---

## Stage 1 — Scout (one agent, always, before anything else)

This stage exists because the last version of this skill burned 14 agents re-discovering something one agent found in five minutes.

One agent, 10 searches, 400 words. It answers only:

1. Does this product already exist in India? Name it, its price, its size, its funding.
2. Does anyone in this market pay for the exact thing being sold here, or do they pay for something adjacent (a product, a person's time)?
3. What did the closest existing player choose to do that looks expensive or awkward? That choice is usually them hitting a wall the founder hasn't hit yet.

It writes `01_scout.md` and returns 5 lines.

**Then the orchestrator branches:**

| What Scout found | What to run |
|---|---|
| A direct competitor doing the same thing, funded, at scale | **Teardown mode**: 3 researchers only — what the competitor can't or won't do, whether the money is real, what it costs to enter. Skip the rest. |
| Nobody pays for the core thing anywhere in this market | **Money-first mode**: 3 researchers only — is there any proof of payment, what do people pay for instead, what would have to change. Skip the rest. |
| Genuinely open field | **Full mode**: 5-6 researchers as below. |

Say which mode was picked and why, in one line, before spending more agents.

---

## Stage 2 — Research

Spawn all researchers in one message. Each writes one file and returns 5 lines.

### Core researchers

| ID | Who they are | What they find out |
|---|---|---|
| R1 | Someone who has sold to Indian consumers with no money | Who pays, how much, how often, which sub-group pays best. Real ₹, real sources. |
| R2 | Someone who knows which companies in this space died and why | Who is doing it now, who tried and failed, what killed them, who could enter tomorrow |
| R3 | Someone who reads the forums | Where these people complain, in their own words. Whether anyone is already hacking a workaround. |
| R4 | Someone who has grown a product on ₹0 | The first 100 users, named. How to reach them free. What blocks trust. |
| R5 | Someone who tracks Indian seed deals | Who funds this, what makes them pass, whether it works without funding |

### Specialist researchers (add 0-2, based on the domain)

| Domain | Add this specialist |
|---|---|
| Health, pharma, medtech | Someone who reads the actual regulation (NMC, CDSCO, ABDM) and prices what compliance costs |
| Fintech, lending, insurance | Someone who reads RBI, IRDAI, SEBI, DPDP rules and prices compliance |
| Manufacturing, hardware, D2C | Someone who knows customs, BIS and landed cost |
| Sports, education, agri | The person doing the job today — the coach, the teacher, the farmer |
| B2B, enterprise | The channel partner and the procurement head who signs |
| Consumer social, creator | A community moderator who knows platform risk |
| Nothing fits | Invent one. Name a real job title and what that person would know. |

Cap at 2 specialists. Needing more means the idea is scoped too wide.

### What each researcher gets

```
You are {WHO}: {ONE LINE ON WHY THEY KNOW THIS}.

FIRST ACTION: read runs/<slug>/00_brief.md and 01_scout.md. Work only inside the brief.

ALREADY KNOWN — do not re-research, build on it:
{3-5 bullet findings from Scout and any earlier wave}

YOUR JOB: {4-5 specific questions}

RULES
- Max {N} searches, max 700 words. Stop at the cap.
- Every fact gets a source URL. If you have no source, write "no source — this is a guess."
- Indian sources, Indian prices, ₹.
- Report what argues AGAINST the idea. If you found none, you did not look.
- Off-topic goes in NOT MY JOB at the bottom. Don't chase it.
- Don't recommend anything. Find things out.
- Write plainly. No jargon, no aphorisms, three sentences per paragraph.

WRITE to {PATH}:
# {NAME}
## WHAT I FOUND        (bullets, most important first)
## THE NUMBERS         (table: what | how much | source)
## WHAT ARGUES AGAINST IT
## WHAT I COULDN'T FIND OUT
## WHAT THIS MEANS FOR A FOUNDER WITH NO MONEY
## NOT MY JOB

RETURN only: file path, biggest finding (1 line), shakiest thing you relied on (1 line), how many facts had sources vs were guesses. Max 5 lines.
```

Budgets: 12 searches and 700 words in full mode, 8 and 500 in teardown or money-first mode.

**Duplicate rule:** each researcher appends its headline findings to `_findings.md`. Before writing, a researcher reads that file. If its main finding is already there, it says "already known" and spends its remaining budget on something not yet covered. This is what stops six agents reaching one conclusion.

---

## Stage 3 — Attack

**One agent, not one per researcher.** The old version ran seven attackers who all said the same thing.

```
You are the sharpest sceptic this idea will ever meet. Your job is to kill it.

READ every file in lanes/ and the brief. Max 5 new searches, only to land a specific hit.

For EACH research file, find:
1. The claim the conclusion depends on that has no source behind it. If the argument dies without it, say so.
2. The Indian reality it ignored: price sensitivity, who controls the money in the household, trust, language, regulation, cost to serve.
3. The best argument that this fails.

Then, across all of them:
4. What a big company does the day this starts working.
5. Which of these files are all saying the same thing? Name the duplication.

WRITE runs/<slug>/02_attack.md:
## WHAT KILLS IT          (ranked, worst first)
## WHAT NEEDS AN ANSWER   (ranked)
## SURVIVES THE ATTACK    (what held up)
## WHAT ONE FACT WOULD CHANGE THE ANSWER

Plain English. No scoring, no verdict labels, no jargon.
```

**Then one round of checking back, and only where research can settle it.** If the attack turns on a fact that can be looked up — a rule, a policy, a price, a disclosed number — send one agent with 5 searches to check it. If it turns on something only a live test can answer, don't send an agent. Write it down as a thing to test and move on. Never more than 2 check-back agents.

---

## Stage 4 — The answer

One agent. It reads the research files and the attack. It does no research.

This is the only thing the founder reads carefully. It follows the writing rules at the top of this file, strictly.

```
You are writing the answer for a founder with no money, reading on their phone, tired.

READ: 00_brief.md, 01_scout.md, everything in lanes/, 02_attack.md.

WRITE runs/<slug>/ANSWER.md in this exact structure:

# <Idea> — should you build it?

## The answer
"Yes" / "No" / "Not this version, but here's the one that might work".
Then 3 bullets on why. Each bullet: one fact, one sentence.

## Who's already doing this
Table: Company | What they do | Price | How big | What it tells you
If nobody is, say so and say what that probably means.

## Would people actually pay
- What people in this market pay for today, with real ₹ figures
- What they have never been shown to pay for
- One line on which group would pay most, and why

## What has to be true
One sentence. The single belief the whole idea rests on.

## How to find out
A test costing under ₹20,000 and taking under two weeks.
Numbered steps. Each step: what to do, what it costs, how long.
Last step: the number that means yes and the number that means no.

## Do this first
One thing, doable today, under two hours. Say exactly what to open and what to do.

## What we couldn't find out
Table: Question | Why it matters | Cheapest way to answer it
Include anything the research was blocked from reaching.

RULES
- No jargon. No words from the list of banned words. No aphorisms.
- Three sentences per paragraph, maximum.
- Table cells: 15 words maximum.
- Real names, real prices, real websites.
- If a finding rests on a guess, write "we're guessing here" in plain words.
- If most of the research failed, say "don't build this" plainly. Don't soften it, don't dress it up.
- If there is a smaller version worth testing, describe it in five plain sentences. Don't oversell it.
- No summary of the research. The files exist. Answer the question.
```

## Delivering it

Show the founder the answer file. Then one line naming where the detailed files are. Do not re-explain the research in chat.

---

# Files

```
runs/<slug>/
├── 00_brief.md        the brief, read by every agent
├── 01_scout.md        does this exist, does anyone pay
├── _findings.md       running list, stops duplicate work
├── _state.md          what has run
├── lanes/             one file per researcher
├── 02_attack.md       everything the sceptic found
└── ANSWER.md          what the founder reads
```

# Keeping it fast

| Rule | Why |
|---|---|
| Scout runs first, alone | One agent often ends the run in 5 minutes |
| Mode is picked after Scout | Stops a 7-lane run on a question already answered |
| One attacker, not one per researcher | Seven attackers produced one conclusion last time |
| Check back only on lookup-able facts | "Needs a live test" doesn't need an agent to say it |
| `_findings.md` before writing | Stops researchers re-deriving each other |
| Never more than 12 agents | If it needs more, the idea is scoped too wide |

# When it goes wrong

| What you see | Why | Fix |
|---|---|---|
| Everything says the same thing | Idea scoped too broadly | Narrow the brief, rerun |
| The answer sounds like a consultant | Writing rules ignored | Rewrite Stage 4 only, point at the banned list |
| Nothing was found to argue against it | Attacker was too polite | Rerun Stage 3, tell it it is being judged on kills |
| The run took 30+ minutes | Scout branch was skipped | Always run Scout first |
| Answer is vague | Stage 4 read raw research | It must read the research files and attack file only |
| No Indian sources | Brief didn't name a place | Put the city or state in the brief |
