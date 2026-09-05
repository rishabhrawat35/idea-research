<div align="center">

# Idea Research

**Tells you whether a startup idea is worth building — by trying to kill it, then trying to save it.**

Ask any AI "is this a good idea?" and you get a confident yes. This runs research agents that argue with each other and hands you a verdict in plain English.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-8A63D2)](https://code.claude.com/docs/en/skills)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-compatible-2ea44f)](https://agentskills.io)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

<br>

<div align="center">
  <img src="docs/images/example-answer.png" alt="A real answer from Idea Research: an AI pregnancy app idea, checked against Mylo, Healofy, BabyChakra and Flo" width="820">
  <br>
  <em>A real run. The idea, the companies that already failed at it, and what people actually pay for.</em>
</div>

<br>

## Try it in 30 seconds

```bash
claude plugin marketplace add rishabhrawat35/idea-research
claude plugin install idea-research@idea-research
```

Restart Claude Code, then type:

```
idea-research: an app that helps small Indian gyms manage member payments
```

That's it. No servers, no API keys, no database.

<br>

## The problem it solves

An AI asked to judge an idea has two ways to be wrong, and most tools only avoid one of them.

| Mistake | What it looks like | How this avoids it |
|---|---|---|
| **Saying yes to a corpse** | The idea has been tried and refused. Nobody mentions the bodies. | An agent is paid to kill it and name who died |
| **Saying no to something new** | Nobody paid to summon a car by phone before GPS phones existed | Scout asks what changed in the last 24-36 months |

Those two look identical if you only count today's revenue. Telling them apart is the whole job.

<br>

## What changed in the output

Same research engine. The difference is a banned-word list and a builder agent.

<table>
<tr>
<td width="50%" valign="top">

### Before

> **VERDICT: KILL**
>
> Five of seven lanes could not clear their own kill criteria, and three resolved DEAD.
>
> **THE THREE REAL GAPS**
>
> A priced, zero-human, keepable gynae artefact — the research does not explain this, and that is a hole, not a finding.
>
> **THE ₹20K TEST**
>
> Buy the traffic, because there is no network to borrow.

</td>
<td width="50%" valign="top">

### After

> **No. Not the three-phase plan.**
>
> Mylo raised $24.25M and ran your exact plan for eight years. FY25 revenue ₹63.4 Cr, loss ₹19 Cr.
>
> **What has to be true**
>
> Indian couples will pay for guidance before a positive test, with no doctor and no product attached.
>
> **How to find out**
>
> Run Meta ads, ₹12,000 over 7 days, women 26-34, Mumbai and Pune.

</td>
</tr>
</table>

<br>

## How it runs

Five stages, 7-11 agents, about 20 minutes. Stage 1 often ends it in five.

| Stage | Agents | What happens |
|---|---|---|
| **0 · Brief** | 0 | Writes down what would kill this idea, *before* researching |
| **1 · Scout** | 1 | Does it exist, does anyone pay, and what changed recently |
| **2 · Research** | 3-6 | Parallel diggers, one file each, sources on everything |
| **3 · Attack + Build** | 2 | One tries to kill it. One tries to find the way in. |
| **4 · Answer** | 1 | Reads both sides, writes what you read |

Scout decides how expensive the rest gets:

| Scout finds | Run becomes |
|---|---|
| Funded competitor, nothing has changed | Teardown — 3 researchers |
| Nobody pays, people already refused | Money-first — 3 researchers |
| Nobody pays, but the ground moved | **New-thing mode** — 4 researchers |
| Actually open | Full — 5-6 researchers |

<details>
<summary><strong>See the full pipeline diagram</strong></summary>

<br>

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
 │             │  exists? anyone paying? and WHAT CHANGED?
 └──────┬──────┘
        │
        ├── competitor found ────▶ teardown mode  (3 researchers)
        ├── nobody pays, refused ▶ money-first mode (3)
        ├── the ground moved ────▶ new-thing mode (4)
        └── open field ──────────▶ full mode (5-6)
        │
        ▼
 ┌─────────────┐
 │ 2  RESEARCH │  3-6 agents in parallel · 10 min
 │             │  one file each, sources on everything
 └──────┬──────┘
        ▼
 ┌──────────────────────────────┐
 │ 3  ATTACK  ⚔  BUILD          │  2 agents · 5 min
 │  sceptic tries to kill it    │
 │  builder tries to find a way │
 └──────────────┬───────────────┘
                ▼
 ┌─────────────┐
 │ 4  ANSWER   │  1 agent · 4 min
 │             │  reads the files, not the raw research
 └──────┬──────┘
        ▼
   yes / no / not this version
```

</details>

<br>

## The two agents that matter

**The sceptic** hunts for claims with nothing behind them, Indian realities the research skipped, and the strongest argument that this fails. It must say plainly whether nobody pays because people *refused* this, or because it *wasn't possible yet*.

**The builder** exists because a system with only critics rejects everything with no track record. Uber had no evidence anyone would summon a car by phone. Airbnb had no evidence anyone would sleep in a stranger's spare room. Neither was found by research.

It has to find six things, or say plainly that it can't:

| | What it looks for |
|---|---|
| The manual version | Done by hand, badly, for 20 people, this week |
| The borrowed version | Whose audience, licence, stock or shelf you rent instead of build |
| The narrower version | The one customer who'd pay today, even at 2% of the vision |
| The different money | Same insight, someone else pays |
| The unscalable thing | What you'd do for the first 50 that a funded company never would |
| The incumbent's constraint | What they can't do without breaking a payroll or a promise |

Guardrails so it doesn't become a cheerleader: every idea under ₹20,000 and two weeks, real named tactics only, **no vote on whether the idea is good**, and it must say "there's no way in" when that's the truth.

<br>

## What you get

`ANSWER.md`, written to be read on a phone at night.

| Section | What's in it |
|---|---|
| The answer | Yes, no, or "not this version". Three bullets. |
| Why nobody is doing this | Refused, not yet possible, or untried. This decides everything else. |
| Who's already tried | Company, what they did, money raised, revenue, where they are now |
| Would people actually pay | Real ₹ prices. What nobody has ever paid for. |
| The way in | The cheapest manual version that could exist by Friday |
| What has to be true | One sentence |
| How to find out | A test under ₹20,000, under two weeks, with a yes/no number |
| Do this first | One thing, today, under two hours |
| What we couldn't find out | Including which sources were blocked and what was tried instead |

<br>

<details>
<summary><strong>How it stays honest</strong></summary>

<br>

| Mechanism | What it stops |
|---|---|
| Agents write files, orchestrator reads 5-line summaries | The chat filling up and the run forgetting the question |
| Every fact needs a URL, or is marked "this is a guess" | Invented numbers passing as facts |
| The brief goes into every agent's instructions | Agents wandering into next-door topics |
| Hard search and word limits | Padding instead of prioritising |
| One attack round, then it's settled | Agents arguing forever |
| "What would kill this" written before research | The system rationalising a yes afterwards |

Two more rules: finding nothing against the idea is treated as not having looked, and every finding must matter to someone with no money.

### Blocked sources are not an excuse

An early run hit a blocked Reddit and reported it as a limitation. That's a researcher giving up. There's now a ladder, and the file has to say which rungs it tried:

1. Search for the content instead of the page — threads get quoted in search results
2. A different community: forums, app store reviews, YouTube comments, Trustpilot
3. **The same question about another country** — often better evidence, and it feeds the "what changed" test
4. Someone who already did the reading: market reports, journalism, dissertations
5. The browser tools, if the session has them, and actually go look
6. Only then "could not find out", listing the five things tried

"It was blocked" on its own gets sent back once.

</details>

<details>
<summary><strong>How it stays fast</strong></summary>

<br>

An early version took 35 minutes and 14 agents to produce five findings, two of which arrived in the first five minutes.

| Rule | Why |
|---|---|
| Scout runs alone, first | One agent often ends the run before the expensive part |
| Mode chosen after Scout | No point running six researchers on a settled question |
| One attacker, not one per researcher | Seven attackers once reached one conclusion |
| Sceptic and builder run together | Same wall-clock as running one |
| Check back only on facts you can look up | "Needs a live test" doesn't need an agent to say it |
| Shared findings list, read before writing | Stops researchers re-deriving each other |
| 12 agents, hard ceiling | More means the idea is scoped too wide |

</details>

<details>
<summary><strong>How it writes (the banned-word list)</strong></summary>

<br>

The research was never the weak part. The writing was.

| Never | Instead |
|---|---|
| artefact, offering, solution, proposition | the PDF, the app, the thing |
| keepable, actionable, learnings, surface | say what it actually is |
| leverage, unlock, enable | use, let, allow |
| ecosystem, landscape, moat, thesis | name the actual thing |
| "Buy the traffic" | "Run Meta ads, ₹12,000" |
| "VERDICT: KILL" | "Should you build this? No." |
| "Three lanes resolved DEAD" | "Three of the seven checks failed" |

The system's own vocabulary is banned too. You never see the words lane, verdict, kill criteria, or confidence tag.

Required: three sentences per paragraph, nothing over 25 words, table cells under 15 words, real names and real prices, and the words "we're guessing" when it's a guess.

</details>

<details>
<summary><strong>Files a run creates</strong></summary>

<br>

```
runs/<idea>/
├── 00_brief.md      the brief every agent reads first
├── 01_scout.md      does it exist, does anyone pay, what changed
├── _findings.md     running list, stops duplicate work
├── _state.md        what has run so far
├── lanes/           one file per researcher
├── 02_attack.md     the sceptic
├── 03_build.md      the builder
└── ANSWER.md        what you read
```

Runs are kept. Comparing an idea against the same idea reshaped a month later is one of the more useful things this does.

</details>

<details>
<summary><strong>When it goes wrong</strong></summary>

<br>

| What you see | Why | Fix |
|---|---|---|
| Every idea comes back as no | Builder skipped, or Scout never asked what changed | "Rerun the builder" |
| A file says a source was blocked and stops | The ladder was ignored | "Send it back, use the ladder" |
| Everything says the same thing | Idea too broad | Narrow the brief, rerun |
| Sounds like a consultant wrote it | Writing rules ignored | "Rewrite the answer, follow the banned list" |
| Nothing argues against the idea | Sceptic too polite | "Redo the attack, you're judged on kills" |
| The builder wrote a pep talk | It thinks it's a coach | "Rerun it: real tactics, ₹ and days, no encouragement" |
| Took over 30 minutes | Scout was skipped | Scout always runs first |
| No Indian sources | No place in the brief | Put the city or state in the brief |

</details>

<details>
<summary><strong>Why it's built this way</strong></summary>

<br>

| Choice | Rejected | Reason |
|---|---|---|
| Scout runs first, alone | Straight into full research | One agent often ends the run for 1/14th of the cost |
| Scout asks what changed | Only asking who pays today | "Nobody pays" is true of every new category before it exists |
| A builder runs against the sceptic | Sceptic alone | A system with only critics says no to everything untried |
| The builder gets no vote | Builder scores the idea | Two agents arguing to a score is theatre |
| One sceptic reads everything | One per researcher | Seven of them previously produced one conclusion |
| Agents write files | Agents report into the chat | The chat fills up and the run drifts by the fourth agent |
| The writer never sees raw research | It reads everything | Reading everything means being convinced by volume |
| Ladder for blocked sources | Reporting the block | An agent that stops at a 403 has done a quarter of the job |
| Banned-word list in the skill | Trusting tone instructions | "Write plainly" doesn't work. A list does. |
| India and ₹0 as defaults | Generic global framing | Generic framing gives generic findings |

</details>

<br>

## Install anywhere else

<details>
<summary><strong>Claude desktop app, Cursor, Copilot, Zed</strong></summary>

<br>

**Claude desktop app** — Settings → Capabilities → Skills → add the skill, or paste in the contents of `skills/idea-research/SKILL.md`.

**Anything that reads Agent Skills:**

```bash
git clone https://github.com/rishabhrawat35/idea-research
cp -R idea-research/skills/idea-research ~/.claude/skills/
```

Swap the path for `~/.cursor/skills/`, `~/.copilot/skills/` or `~/.config/zed/skills/`.

**Already installed and want the latest?**

```bash
claude plugin marketplace update idea-research
```

**Needs:** web search, subagents, and somewhere to write files.

</details>

<br>

## Make it yours

The whole engine is one file: [`skills/idea-research/SKILL.md`](skills/idea-research/SKILL.md). It's plain English, not code.

Change the default market from India, add a specialist for your domain, adjust the banned-word list, or move the ₹20,000 test budget. Fork it, edit that file, then:

```bash
claude plugin uninstall idea-research
claude plugin marketplace remove idea-research
claude plugin marketplace add <your-username>/idea-research
claude plugin install idea-research@idea-research
```

<br>

## Contributing

Pull requests welcome, especially:

- **Specialists for new domains** — legal, logistics, gaming, climate
- **Markets other than India** — the defaults are in Stage 0 and Stage 2
- **Words for the banned list** — if the output sounded like a consultant, say which sentence gave it away
- **A run that got it wrong** — the most useful thing you can file is an idea it judged badly, with what actually happened

Open an issue with the idea you ran and the answer you got.

<br>

## Licence

MIT. See [LICENSE](LICENSE).
