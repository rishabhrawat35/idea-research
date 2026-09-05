---
name: idea-research
description: 'Adversarial multi-agent research system that pressure-tests a startup idea for the Indian market. Builds its own specialist agent roster for the domain, runs researcher-versus-challenger pairs that write evidence to disk, and returns a BUILD / RESHAPE / KILL decision memo. Use when someone wants an idea validated, a market or competitor scan, gap and threat analysis, community and investor sentiment, or a go/no-go on a venture bet.'
license: MIT
metadata:
  tags: "Startup Research, Market Analysis, Multi-Agent, India, Idea Validation"
  category: "research"
---

# Idea Research

Pressure-test a startup idea by making agents argue with each other **on paper**, not in context.

- Default market: **India**. Amounts in ₹. Indian sources preferred.
- Default reader: a founder with **no money, no team, no network**.
- Default posture: the system tries to **kill** the idea. Survival is the signal.

## When to use

| Use it for | Do not use it for |
|---|---|
| "Validate this idea" | Writing a pitch deck |
| "Should I build X" | Building a financial model |
| "Is there a gap in Y market" | Diligence on a company that already exists |
| "Would anyone fund this in India" | Generic market-size lookups |
| "Who else is doing this and why haven't they won" | Copywriting or naming |

## Non-negotiables

Breaking any one of these is what makes multi-agent research hallucinate and drift. They hold for every run.

1. **Agents write files. The orchestrator reads summaries.** Never pull a full research payload back into the main thread. A subagent returns at most 5 lines: file path, strongest finding, weakest claim, claim counts, verdict.
2. **Every factual claim carries a tag.**
   - `[HIGH|url1, url2]` — two or more independent sources
   - `[MED|url]` — one source
   - `[LOW]` — inference from other findings, no direct source
   - `[ASSUMPTION]` — the agent made it up to keep moving
3. **Scope is a contract.** Every agent reads the scope block first and works only inside it. Anything interesting but outside goes in a `DRIFT_REQUEST` line — never into the findings.
4. **Budgets are hard.** An agent that hits its search or word cap stops and reports what it has. Partial and honest beats complete and invented.
5. **One rebuttal round per lane.** A lane resolves after at most one researcher counter-attack. No second challenge, ever. This is the loop breaker.
6. **Founder lens on every lane.** Each lane file ends with `SO WHAT FOR A ₹0 FOUNDER` in one or two lines. A finding with no founder consequence gets cut.
7. **Invented numbers are tagged, not hidden.** A market size with no source is `[ASSUMPTION]`, and the CFO challenger will kill it. That is the system working, not failing.

## Modes

| Mode | Lanes | Agents | Wall time | Use for |
|---|---|---|---|---|
| `lite` | 3 — Demand Signal, Competitors, Wedge | ~7 | 8-12 min | Triage. Killing weak ideas cheaply. |
| `full` | 5 core + 0-3 adaptive | 12-18 | 25-40 min | An idea that survived lite, or one the founder is serious about. |

Default to `full`. Use `lite` when the user says quick, triage, lite, or is comparing several ideas in one go.

---

# Phase 0 — SCOPE

**Orchestrator only. No subagents. This phase is where drift is prevented, so do not rush it.**

## 0.1 Clarify only if you must

Ask **at most 3** questions, and only when the idea cannot be scoped without them. Typical gaps: who the user is, whether it is B2B or B2C, and whether the founder has an unfair advantage here. If the idea is scopeable, skip straight to 0.2.

## 0.2 Write the scope contract

Create the run folder `runs/<idea-slug>/` and write `00_scope.md`:

```markdown
# Scope contract — <idea>

- ONE LINER: <what it is, in a sentence a stranger understands>
- WHO HURTS: <the specific person, not a segment>
- WHAT THEY DO TODAY: <the status quo it replaces, including "nothing">
- WHAT THEY PAY TODAY: <₹ or time, for the status quo>
- GEOGRAPHY: <India / metro / tier-2-3 / specific state>
- CATEGORY: <the shelf it sits on>
- DOMAIN ARCHETYPE: <see roster table below>
- FOUNDER POSITION: <what they already have — skills, access, capital, none>
- OUT OF SCOPE: <3-5 things nobody should research>
- KILL CRITERIA: <2-3 findings that would end this outright>
```

`KILL CRITERIA` matters most. Writing down what would end the idea *before* researching it is what stops the system from rationalising a yes.

## 0.3 Build the roster

Every run gets these **5 core lanes** (3 in lite mode — marked ★):

| ID | Lane | Researcher persona | Must answer | Challenger persona |
|---|---|---|---|---|
| L1 | Market & Money | Bootstrapped India operator | Who pays, how much, how often, in ₹. Realistic reachable market, not TAM theatre. | **The CFO** — has seen 100 decks, kills fantasy arithmetic |
| L2 ★ | Competitors & Incumbents | Category historian | Who tried, who is funded, who died and why. Why has the obvious player not shipped this. Adjacent industries that could enter. | **Incumbent's Head of Product** — "we ship this in a quarter and crush you" |
| L3 ★ | Demand Signal | Community lurker | Reddit, Quora, YouTube comments, X, niche forums, plus news for directional movement. Real complaints in real words. | **The Churned User** — tried something like this, stopped paying, explains why |
| L4 ★ | Wedge & Distribution | Zero-budget growth operator | First 100 users with ₹0. WhatsApp, regional language, tier-2/3, offline, community-led. | **Growth Lead with no budget** — "your CAC is unpayable" |
| L5 | Capital & Survival | India seed scout | Would anyone fund this. Comparable Indian deals. Or is it bootstrap-only, and is that acceptable. | **Seed Partner who passes on 99%** — writes the actual pass email |

Then add **0-3 adaptive lanes** by matching the domain archetype:

| Domain archetype | Adaptive researcher | Its challenger |
|---|---|---|
| Pharma, health, medtech | Regulatory analyst (CDSCO, NMC, ABDM, clinical claims) | Hospital compliance head |
| Fintech, lending, insurance | Regulatory analyst (RBI, IRDAI, SEBI, DPDP) | Risk & compliance officer |
| Manufacturing, hardware, D2C physical | Supply chain & import-export analyst (BIS, customs, landed cost) | Freight and customs veteran |
| Sports, fitness | The practitioner — athlete or coach | Practitioner who has watched 10 apps come and go |
| Education | The practitioner — teacher or parent paying fees | School procurement decision maker |
| Agri, rural | The practitioner — farmer or FPO operator | Rural distribution veteran |
| B2B, enterprise SaaS | Channel partner and systems integrator | Enterprise procurement head |
| Consumer social, creator | Community moderator or creator | Platform policy and dependency risk analyst |
| Logistics, mobility | Fleet and last-mile operator | Unit-economics operator from a delivery company |
| Nothing fits | **Invent one.** Name the role a real insider would hold, write its one-line brief, and pair it with the skeptic who would most want it to fail. | |

Cap at 3 adaptive lanes. If more than 3 seem necessary, the scope is too wide — narrow the scope instead.

## 0.4 Show the roster and get a go-ahead

Write `01_roster.md`, then show the user a compact table: lane, persona, challenger, why this lane was added. Ask for a one-line go-ahead. Do not spend agents before that.

---

# Phase 1 — GROUND

Spawn **every researcher in a single message** so they run in parallel. Each gets this prompt, filled in:

```
You are {PERSONA}: {PERSONA_ONE_LINER}.

SCOPE CONTRACT — do not research outside this:
{paste 00_scope.md verbatim}

YOUR LANE: {LANE_NAME}
Answer these, in order:
{LANE_QUESTIONS}

RULES
- Budget: max {SEARCHES} web searches, max {WORDS} words written. Stop at the cap and report what you have.
- Tag every factual claim: [HIGH|url,url] [MED|url] [LOW] [ASSUMPTION].
- Indian sources and Indian pricing first. Amounts in ₹.
- You must report disconfirming evidence. A lane with no counter-evidence is a lane that did not look.
- Interesting but out of scope goes under DRIFT_REQUEST. Do not chase it.
- Do not recommend anything. You gather; someone else decides.

WRITE to {PATH} with exactly these sections:
# {LANE_NAME}
## FINDINGS
## EVIDENCE TABLE      (claim | tag | source | why it matters)
## DISCONFIRMING EVIDENCE
## OPEN QUESTIONS
## SO WHAT FOR A ₹0 FOUNDER
## DRIFT_REQUEST

RETURN to the orchestrator ONLY: file path, strongest finding (1 line), weakest load-bearing claim (1 line), claim counts by tag. Max 5 lines.
```

Budgets:

| Mode | Searches per researcher | Words per lane file |
|---|---|---|
| `lite` | 6-8 | 500 |
| `full` | 12-18 | 900 |

## Lane questions

**L1 Market & Money**
- Who writes the cheque, and is that the same person who feels the pain?
- What do they pay today for the status quo, in ₹, and how often?
- What is the realistically reachable set of buyers in year one — a number you can defend, not a TAM slide?
- What does the same job cost in a market where it is already solved, and does that price survive Indian willingness to pay?
- What breaks the unit economics: payment collection, support cost, churn, GST, returns?

**L2 Competitors & Incumbents**
- Who is doing this in India now — funded, bootstrapped, or as a side feature?
- Who tried and died, and what actually killed them?
- Why has the obvious incumbent not shipped this? Distinguish *cannot* from *will not* — "will not" is a real opening, "cannot" is usually temporary.
- Which adjacent industry could enter this and win on distribution alone?
- Which global player is one India-launch away from owning this?

**L3 Demand Signal**
- Where do these people complain in public? Name the specific subreddits, Quora topics, YouTube channels, forums, communities.
- Quote the actual language they use for the pain. Their words, not yours.
- Is anyone hacking together a workaround today? A workaround is stronger evidence than a wishlist.
- What is the directional movement in news over the last 18 months — into this space or out of it?
- Where is the silence? A category with no complaints often has no demand.

**L4 Wedge & Distribution**
- Name the first 100 users specifically enough to list them.
- Reach them with ₹0: which community, which WhatsApp group, which offline gathering, which existing audience?
- What is the one narrow use case that gets a yes fastest, even if it is a fraction of the vision?
- What is the trust barrier in India for this, and who lends credibility cheaply?
- Language, device and payment reality: does this work on a ₹8,000 Android on patchy data, in the buyer's language, paid by UPI?

**L5 Capital & Survival**
- Which Indian funds have written cheques in or next to this category in the last 8 quarters? Name them and the deals.
- What do those deals suggest about what a fundable version of this looks like?
- What would make an investor pass in 30 seconds?
- Is a bootstrapped version viable, and what does it need to reach ₹1 lakh a month?
- Does this need capital to work at all, or only to grow faster?

**Adaptive lanes** — write 4-5 questions in the same shape: specific, answerable, India-anchored, and ending in a founder consequence.

---

# Phase 2 — CHALLENGE

Spawn **every challenger in a single message**. Each reads only its own lane file.

```
You are {CHALLENGER}: {CHALLENGER_ONE_LINER}.
Your job is to kill this lane, not to be fair to it.

READ ONLY: {PATH}
Run new searches only to land a specific attack. Max {C} searches ({C} = 3 full, 2 lite).

ATTACK IN THIS ORDER
1. Every [LOW] and [ASSUMPTION] claim the conclusion rests on. If the argument dies without it, say so plainly.
2. The Indian-market reality the lane ignored: price sensitivity, cash flow timing, tier-2/3 behaviour, regulation, language, trust, cost to serve.
3. The strongest version of the counter-case. Steelman why this fails.
4. What a well-resourced incumbent does the day this starts working.

APPEND to the same file:
## CHALLENGE — {CHALLENGER}
### Fatal      (kills the lane)
### Serious    (needs an answer before proceeding)
### Noted      (survivable, logged)
### VERDICT: SURVIVES | WOUNDED | DEAD
### The one question that would save this lane:

RETURN only: verdict, and the one question. Max 3 lines.
```

## Rebuttal — once, then stop

For each lane returning `WOUNDED` or `DEAD`, spawn **one** researcher with the challenger's single question and a budget of 5 searches. It appends:

```
## REBUTTAL
## RESOLVED VERDICT: SURVIVES | WOUNDED | DEAD
```

Then the lane is closed. No second challenge round under any circumstance. If a lane is still DEAD, that is a finding, not a failure.

---

# Phase 3 — ASSESS

**One agent.** It reads the lane files and the scope contract. It does no research of its own.

```
You are the Assessor. You did not do this research and you will not do any now.

READ: 00_scope.md and every file in lanes/.

WRITE 99_verdict.md:

## VERDICT: BUILD | RESHAPE | KILL
Two lines of why. Nothing hedged.

## THE THREE REAL GAPS
Table: gap | why it is still open | why that reason is beatable now
A gap with no explanation of why nobody has filled it is not a finding — it is a hole in the research. Say so if that is the case.

## THREE THREATS AS LEVERAGE
Table: threat | how it converts into an advantage | what flipping it costs

## THE KILLER ASSUMPTION
The single belief that, if wrong, ends this. One line.

## THE ₹20K TEST
A two-week experiment that falsifies the killer assumption. Numbered steps, each with cost in ₹ and time. Total under ₹20,000.

## MONDAY MORNING
One action, doable in under 2 hours, starting today.

## WHAT WE STILL DO NOT KNOW
Ranked, each with the cheapest way to find out.

RULES
- Down-weight every conclusion resting on [LOW] or [ASSUMPTION] claims, and name them.
- If 3 or more lanes resolved DEAD, the verdict is KILL. Do not soften it.
- Recommend nothing that needs money, headcount or a network the founder does not have.
- No summary of the research. The lane files already exist. Decide.
```

## Deliver

Show the user `99_verdict.md` in full, then a one-line index of the lane files. Do not restate the research in chat.

---

# Run state

Maintain `_state.md` in the run folder so a crashed or resumed run picks up cleanly:

| Lane | Researcher | Challenger | Rebuttal | Verdict |
|---|---|---|---|---|
| L1 | done | done | n/a | SURVIVES |
| L2 | done | done | done | WOUNDED |

Update it after each phase. It is the only state the orchestrator needs to hold.

# File layout

```
runs/<idea-slug>/
├── 00_scope.md          scope contract, read by every agent
├── 01_roster.md         which lanes ran and why
├── _state.md            phase and lane status
├── lanes/
│   ├── L1_market.md     findings + CHALLENGE + REBUTTAL + verdict, one file
│   ├── L2_competitors.md
│   ├── L3_demand.md
│   ├── L4_wedge.md
│   ├── L5_capital.md
│   └── A1_<adaptive>.md
└── 99_verdict.md        the decision memo
```

One lane, one file, start to finish. The argument and its resolution live together, so nothing has to be reassembled later.

# Failure modes and what to do

| Symptom | Cause | Fix |
|---|---|---|
| Lanes all say the same thing | Scope too broad | Rewrite `00_scope.md` narrower, rerun |
| Every lane SURVIVES | Challengers were too polite | Rerun Phase 2 with the instruction "you are being graded on kills" |
| Verdict reads generic | Assessor got raw research instead of lane files | It must read `lanes/` only |
| Agent went off-topic | Scope contract not pasted into its prompt | Paste it verbatim, every time |
| Run stalls midway | Too many agents at once | Cap parallel spawns at 6, run in two waves |
