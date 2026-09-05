# Idea Research

**Checks whether a startup idea is worth building, by making research agents argue with each other.**

Ask any AI "is this a good startup idea?" and you get a confident yes. This does the opposite: it tries to kill the idea, and tells you plainly what survived.

- Runs inside Claude — desktop app or Claude Code terminal
- No servers, no API keys, no database
- Agents write to files, so a long run doesn't drift or make things up
- Ends with a decision in plain English, not a report

---

## Contents

- [What it fixes](#what-it-fixes)
- [How it runs](#how-it-runs)
- [The agents](#the-agents)
- [How it stays honest](#how-it-stays-honest)
- [How it stays fast](#how-it-stays-fast)
- [How it writes](#how-it-writes)
- [What you get](#what-you-get)
- [Install](#install)
- [Using it](#using-it)
- [Files it creates](#files-it-creates)
- [When it goes wrong](#when-it-goes-wrong)
- [Why it's built this way](#why-its-built-this-way)

---

## What it fixes

| Problem | What it looks like | What this does |
|---|---|---|
| AI agrees with you | Every idea comes back promising | An agent is paid to kill it |
| Long runs drift | The research forgets the question | Findings go in files, not the chat |
| Made-up numbers | Market sizes with no source | Every fact needs a URL or gets marked a guess |
| Reports nobody reads | 3,000 words of hedging | Plain English, tables, a yes or no |

Written for a founder with no money, no team and no network. Every finding has to matter to that person or it gets cut.

---

## How it runs

Five stages. Stage 1 often ends the run in five minutes, which is the point.

```
   your idea
       │
       ▼
 ┌─────────────┐
 │ 0  BRIEF    │  no agents · 2 min
 │             │  who has the problem, what would kill this
 └──────┬──────┘
        ▼
 ┌─────────────┐
 │ 1  SCOUT    │  1 agent · 4 min
 │             │  does this exist already? does anyone pay for it?
 └──────┬──────┘
        │
        ├── competitor found ──▶ teardown mode  (3 researchers)
        ├── nobody pays ───────▶ money-first mode (3 researchers)
        └── open field ────────▶ full mode (5-6 researchers)
        │
        ▼
 ┌─────────────┐
 │ 2  RESEARCH │  3-6 agents in parallel · 10 min
 │             │  one file each, sources on everything
 └──────┬──────┘
        ▼
 ┌─────────────┐
 │ 3  ATTACK   │  1 agent · 5 min
 │             │  reads everything, tries to kill all of it at once
 └──────┬──────┘
        ▼
 ┌─────────────┐
 │ 4  ANSWER   │  1 agent · 4 min
 │             │  reads the files, not the raw research
 └──────┬──────┘
        ▼
   yes / no / not this version
```

**Total: 6-10 agents, 20-25 minutes.** Never more than 12.

### Stage 0 — Brief

No agents, so it's free. Up to 3 questions, only if the idea can't be pinned down without them. Then it writes down who has the problem, what they pay today, and — most importantly — **what would kill this idea**, before any research happens. Deciding what counts as failure afterwards is how a system talks itself into a yes.

### Stage 1 — Scout

One agent. Ten searches. It answers three things:

1. Does this already exist in India? Name, price, size, funding.
2. Does anyone here pay for this exact thing, or only for something next to it?
3. What did the closest existing company choose to do that looks expensive? That's usually a wall they hit.

Then the run branches. If a funded competitor is already doing it, there's no point running a full open-field investigation — it switches to taking that competitor apart instead.

### Stage 2 — Research

Researchers run in parallel, one file each. Each one:

- Reads the brief first
- Needs a URL for every fact, or has to write "no source — this is a guess"
- Must report what argues **against** the idea
- Checks a shared findings list first, so agents don't re-derive each other's work

### Stage 3 — Attack

**One sceptic reads everything at once.** It looks for claims with nothing behind them, Indian realities the research skipped, and the best argument that this fails. It also names which files are just repeating each other.

Then facts get checked — but only facts that can actually be looked up. If something can only be settled by a live test, that gets written down as a test, not handed to another agent.

### Stage 4 — Answer

One agent that did none of the research. It reads the files and the attack, and writes the thing you actually read.

---

## The agents

Five core researchers. Not all run every time — Scout decides.

| Who | What they find out |
|---|---|
| **Someone who has sold to Indian consumers with no money** | Who pays, how much, how often. Which group pays best. |
| **Someone who knows who died in this space** | Who's doing it now, who failed, what killed them, who could enter tomorrow |
| **Someone who reads the forums** | Where these people complain, in their own words. Who's already hacking a workaround. |
| **Someone who has grown on ₹0** | The first 100 users by name. How to reach them free. What blocks trust. |
| **Someone who tracks Indian seed deals** | Who funds this, what makes them pass, whether it works unfunded |

### It picks specialists for the domain

A pharma idea and a manufacturing idea don't need the same people.

| Domain | Specialist added |
|---|---|
| Health, pharma, medtech | Someone who reads NMC, CDSCO and ABDM rules and prices what compliance costs |
| Fintech, lending, insurance | Someone who reads RBI, IRDAI, SEBI and DPDP rules |
| Manufacturing, hardware, D2C | Someone who knows customs, BIS and landed cost |
| Sports, education, agri | The person doing the job today — coach, teacher, farmer |
| B2B, enterprise | The channel partner, and the procurement head who signs |
| Consumer social, creator | A community moderator who knows platform risk |
| Nothing fits | It invents one — a real job title and what that person would know |

Two specialists maximum. Needing more means the idea is too broad.

---

## How it stays honest

| Mechanism | What it stops |
|---|---|
| Agents write files, the orchestrator reads 5-line summaries | The chat filling up and the run forgetting the question |
| Every fact needs a URL, or gets marked "this is a guess" | Invented numbers passing as facts |
| The brief goes into every agent's instructions | Agents wandering into next-door topics |
| Off-topic findings go in a "not my job" section | Tangents quietly becoming the research |
| Hard limits on searches and words | Padding instead of prioritising |
| One attack round, then it's settled | Agents arguing with each other forever |
| "What would kill this" written before research starts | The system rationalising a yes afterwards |

Two more rules that shape quality:

- **Finding nothing against the idea is treated as not having looked.**
- **Every finding must matter to someone with no money**, or it gets cut.

---

## How it stays fast

An earlier version of this took 30+ minutes and 14 agents to produce five findings, two of which arrived in the first five minutes. These rules are the fix.

| Rule | Why |
|---|---|
| Scout runs alone, first | One agent often ends the run before the expensive part |
| Mode chosen after Scout | No point running six researchers on a settled question |
| One attacker, not one per researcher | Seven attackers previously reached one conclusion |
| Check back only on facts you can look up | "Needs a live test" doesn't need an agent to say it |
| Shared findings list, read before writing | Stops researchers re-deriving each other |
| 12 agents, hard ceiling | More than that means the idea is scoped too wide |

---

## How it writes

The research was never the weak part. The writing was. So the skill carries hard rules about it.

**Banned:**

| Never | Instead |
|---|---|
| artefact, offering, solution, proposition | the PDF, the app, the thing |
| keepable, actionable, learnings, surface | say what it actually is |
| leverage, unlock, enable | use, let, allow |
| "Buy the traffic" | "Run Meta ads, ₹12,000" |
| "VERDICT: KILL" | "Should you build this? No." |
| "Three lanes resolved DEAD" | "Three of the seven checks failed" |

Also banned: the system's own vocabulary. You never see the words lane, verdict, kill criteria, or confidence tag. That's scaffolding, not the building.

**Required:**

- Three sentences per paragraph, maximum. Longer becomes a list.
- Table cells: 15 words maximum, and no cell that's just a hedge.
- Real names, real prices in ₹, real websites.
- Say the action, not a saying about the action.
- If it's a guess, the words "we're guessing" appear.

---

## What you get

`ANSWER.md` — written to be read on a phone, at night.

| Section | What's in it |
|---|---|
| **The answer** | Yes, no, or "not this version". Three bullets of why. |
| **Who's already doing this** | Table: company, what they do, price, size, what it tells you |
| **Would people actually pay** | What this market pays for today, in ₹. What it has never paid for. |
| **What has to be true** | One sentence. The belief the whole idea rests on. |
| **How to find out** | A test under ₹20,000 and under two weeks. Numbered, costed. Ends with the number that means yes. |
| **Do this first** | One thing, today, under two hours |
| **What we couldn't find out** | Table: question, why it matters, cheapest way to answer |

If most of the research failed, it says "don't build this" plainly. It doesn't soften it.

---

## Install

### Claude Code (terminal)

```bash
claude plugin marketplace add rishabhrawat35/idea-research
claude plugin install idea-research@idea-research
```

Restart Claude Code. Check with `claude plugin list`.

Already installed? Update instead:

```bash
claude plugin marketplace update idea-research
```

### Claude desktop app

Settings → Capabilities → Skills → add the skill, or paste in the contents of `skills/idea-research/SKILL.md`.

### Anything else that reads Agent Skills

```bash
git clone https://github.com/rishabhrawat35/idea-research
cp -R idea-research/skills/idea-research ~/.claude/skills/
```

Works with Cursor (`~/.cursor/skills/`), Copilot (`~/.copilot/skills/`), Zed (`~/.config/zed/skills/`).

### Needs

- Web search
- Subagents (it runs 6-10 of them)
- Somewhere to write files

---

## Using it

Type any of these:

```
idea-research: an app that helps small Indian gyms manage member payments
```

```
is this worth building — WhatsApp crop advice for cotton farmers in Gujarat
```

```
should I build a compliance tool for Indian diagnostic labs?
```

### What happens

| Step | You see | You do |
|---|---|---|
| 1 | Up to 3 questions, only if needed | Answer briefly |
| 2 | The brief, and which agents will run | Say "go", or fix the brief |
| 3 | Scout result and the mode it picked | Nothing |
| 4 | Researchers running | Nothing, 10 minutes |
| 5 | The answer | Read it. Argue with it. |

### Afterwards

| Say this | It does this |
|---|---|
| "Redo the competitor one, wider" | Reruns one researcher, keeps the rest |
| "The attack was too soft, do it again" | Reruns the sceptic, harder |
| "Try it as B2B instead" | New brief, fresh run, old one kept |
| "Compare this to my last idea" | Reads both answers side by side |

---

## Files it creates

```
runs/<idea>/
├── 00_brief.md      the brief every agent reads first
├── 01_scout.md      does it exist, does anyone pay
├── _findings.md     running list, stops duplicate work
├── _state.md        what has run so far
├── lanes/           one file per researcher
├── 02_attack.md     everything the sceptic found
└── ANSWER.md        what you read
```

Each researcher's file has the same shape: what I found, the numbers, what argues against it, what I couldn't find out, what it means for a founder with no money.

Runs are kept. Comparing an idea against the same idea reshaped a month later is one of the more useful things this does.

---

## When it goes wrong

| What you see | Why | Fix |
|---|---|---|
| Everything says the same thing | Idea too broad | Narrow the brief, rerun |
| It sounds like a consultant wrote it | Writing rules ignored | "Rewrite the answer, follow the banned-words list" |
| Nothing argues against the idea | Sceptic was too polite | "Redo the attack, you're being judged on kills" |
| Took over 30 minutes | Scout was skipped | Scout always runs first |
| The answer is vague | It read raw research instead of the files | It must read the research files and attack file only |
| No Indian sources | No place named in the brief | Put the city or state in the brief |
| Market sizes look invented | They probably are | Check whether the source says "this is a guess" |

---

## Why it's built this way

| Choice | What was rejected | Reason |
|---|---|---|
| Scout runs first, alone | Straight into full research | One agent often ends the run in 5 minutes for the cost of 1/14th of it |
| One sceptic reads everything | One sceptic per researcher | Seven of them previously produced one conclusion |
| Agents write files | Agents report back into the chat | The chat fills up and the run drifts by the fourth agent |
| The writer never sees raw research | It reads everything | Reading everything means being convinced by volume, not by what held up |
| Check back only on lookup-able facts | Check back on everything | Most challenges can only be settled by a live test, and an agent can't run one |
| "What would kill this" written first | Judge at the end | Deciding what failure means after seeing the data is how you get a yes you didn't earn |
| Banned-word list in the skill | Trusting tone instructions | "Write plainly" doesn't work. A list of banned words does. |
| India and ₹0 as defaults | Generic global framing | Generic framing gives generic findings |

---

## Licence

MIT. See [LICENSE](LICENSE).
