# Idea Research

**An adversarial multi-agent research system for pressure-testing startup ideas in the Indian market.**

Most idea research tells you why an idea is good. This system is built to tell you why it is not — and then reports what survived.

- Runs inside Claude (Cowork desktop app or Claude Code terminal)
- No infrastructure, no API keys, no database
- Every agent writes to a file, so long runs do not drift or hallucinate
- Ends with a decision, not a report

---

## Table of contents

- [What problem this solves](#what-problem-this-solves)
- [How it works](#how-it-works)
- [The agent roster](#the-agent-roster)
- [The adaptive layer](#the-adaptive-layer)
- [How drift and hallucination are prevented](#how-drift-and-hallucination-are-prevented)
- [What you get out](#what-you-get-out)
- [Install](#install)
- [How to run it](#how-to-run-it)
- [File layout of a run](#file-layout-of-a-run)
- [Cost and time](#cost-and-time)
- [Troubleshooting](#troubleshooting)
- [Design decisions and why](#design-decisions-and-why)

---

## What problem this solves

Asking any AI "is this a good startup idea?" produces a confident yes. Three failures cause it:

| Failure | What it looks like | What this system does |
|---|---|---|
| **Agreeableness** | Every idea comes back promising | Half the agents are paid to kill the idea |
| **Context rot** | Long research runs forget the original question and drift | Findings live in files; the orchestrator holds only a status table |
| **Invented specifics** | Market sizes and prices with no source | Every claim carries a confidence tag and a URL, or is marked as an assumption and attacked |

It is written for a founder with no capital, no team and no network. Every finding must end in a consequence for that person, or it gets cut.

---

## How it works

Four phases. Each one closes before the next opens.

```
                        ┌──────────────────────────┐
   your raw idea  ───▶  │  PHASE 0 — SCOPE         │
                        │  orchestrator, no agents │
                        │  • writes the contract   │
                        │  • picks the roster      │
                        │  • you approve           │
                        └───────────┬──────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
      ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
      │ PHASE 1       │     │ PHASE 1       │     │ PHASE 1       │
      │ Researcher L1 │ ... │ Researcher L4 │ ... │ Researcher A1 │
      │ writes L1.md  │     │ writes L4.md  │     │ writes A1.md  │
      └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
              ▼                     ▼                     ▼
      ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
      │ PHASE 2       │     │ PHASE 2       │     │ PHASE 2       │
      │ Challenger L1 │     │ Challenger L4 │     │ Challenger A1 │
      │ appends to    │     │ appends to    │     │ appends to    │
      │ the same file │     │ the same file │     │ the same file │
      │ verdict ▸     │     │ verdict ▸     │     │ verdict ▸     │
      └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
              │  one rebuttal round if WOUNDED or DEAD    │
              └─────────────────────┬─────────────────────┘
                                    ▼
                        ┌──────────────────────────┐
                        │  PHASE 3 — ASSESS        │
                        │  reads lane files only   │
                        │  never the raw research  │
                        └───────────┬──────────────┘
                                    ▼
                          BUILD / RESHAPE / KILL
```

### Phase 0 — Scope

The orchestrator alone. No agents spawn yet, so this phase is nearly free.

1. Asks at most 3 clarifying questions, and only if the idea cannot be scoped without them
2. Writes a **scope contract**: who hurts, what they do today, what they pay today, geography, category, and the founder's existing position
3. Writes **kill criteria** — the findings that would end the idea — *before* any research runs
4. Selects the agent roster for this specific domain
5. Shows you the roster and waits for a one-line go-ahead

Writing kill criteria first is the single most important step. It is what stops the system from talking itself into a yes later.

### Phase 1 — Ground

All researchers spawn in parallel. Each one:

- Reads the scope contract verbatim as its first action
- Works one lane only
- Tags every claim with a confidence level and source
- Is required to report disconfirming evidence
- Writes to its own file and returns **five lines** to the orchestrator

Researchers are forbidden from recommending anything. They gather; someone else decides.

### Phase 2 — Challenge

One challenger per lane, spawned in parallel. Each reads only its own lane file and attacks in a fixed order:

1. Every low-confidence or assumed claim the conclusion depends on
2. The Indian-market reality the lane ignored — price sensitivity, cash flow, tier-2/3 behaviour, regulation, language, trust, cost to serve
3. The strongest version of the counter-case
4. What a well-resourced incumbent does the day this starts working

It appends its attack to the same file and returns a verdict: **SURVIVES**, **WOUNDED**, or **DEAD**.

A wounded or dead lane gets **one** rebuttal round — the researcher answers the challenger's single sharpest question — and then the lane closes permanently. This hard cap is what prevents the infinite agent-versus-agent loop that kills most adversarial systems.

### Phase 3 — Assess

One agent that did none of the research. It reads the lane files and the scope contract, nothing else, and produces the decision memo.

Keeping the assessor away from raw research is deliberate. It cannot be persuaded by volume — only by what survived challenge.

---

## The agent roster

Five core lanes run on every idea. Three of them (marked ★) also run in lite mode.

| Lane | Researcher persona | What it must answer | Challenger persona |
|---|---|---|---|
| **L1 · Market & Money** | Bootstrapped India operator | Who writes the cheque. What they pay today in ₹. The realistically reachable buyer set in year one. What breaks the unit economics. | **The CFO** — has read 100 decks, kills fantasy arithmetic |
| **L2 · Competitors & Incumbents** ★ | Category historian | Who is doing this now. Who tried and died, and what killed them. Why the obvious incumbent has not shipped it. Which adjacent industry could enter and win on distribution alone. | **Incumbent's Head of Product** — "we ship this in a quarter and crush you" |
| **L3 · Demand Signal** ★ | Community lurker | Where these people complain in public, in their own words. Whether anyone is hacking a workaround today. Directional movement in news over 18 months. Where the silence is. | **The Churned User** — tried something like this, stopped paying, says why |
| **L4 · Wedge & Distribution** ★ | Zero-budget growth operator | The first 100 users, named specifically. How to reach them with ₹0. The narrowest use case that gets a yes fastest. Device, language and payment reality. | **Growth Lead with no budget** — "your CAC is unpayable" |
| **L5 · Capital & Survival** | India seed scout | Which Indian funds wrote cheques here in the last 8 quarters. What a fundable version looks like. What causes a 30-second pass. Whether a bootstrapped version reaches ₹1 lakh a month. | **Seed Partner who passes on 99%** — writes you the actual pass email |

Each researcher-challenger pair shares one file. The claim, the attack on it, the rebuttal and the resolution sit together, so nothing has to be reassembled later.

---

## The adaptive layer

The system reads the domain first and **builds its own roster** before it executes. A pharma idea and a manufacturing idea do not get the same agents.

| Domain archetype | Adaptive researcher added | Its challenger |
|---|---|---|
| Pharma, health, medtech | Regulatory analyst — CDSCO, NMC, ABDM, clinical claims | Hospital compliance head |
| Fintech, lending, insurance | Regulatory analyst — RBI, IRDAI, SEBI, DPDP | Risk and compliance officer |
| Manufacturing, hardware, D2C physical | Supply chain and import-export analyst — BIS, customs, landed cost | Freight and customs veteran |
| Sports, fitness | The practitioner — athlete or coach | Practitioner who has watched 10 apps come and go |
| Education | The practitioner — teacher, or the parent paying fees | School procurement decision maker |
| Agri, rural | The practitioner — farmer or FPO operator | Rural distribution veteran |
| B2B, enterprise SaaS | Channel partner and systems integrator | Enterprise procurement head |
| Consumer social, creator | Community moderator or creator | Platform policy and dependency risk analyst |
| Logistics, mobility | Fleet and last-mile operator | Unit-economics operator from a delivery company |
| **Nothing fits** | **The system invents one.** It names the role a real insider would hold, writes a one-line brief, and pairs it with the skeptic who would most want that insider to be wrong. | |

Rules on the adaptive layer:

- Maximum **3** adaptive lanes per run
- Needing more than 3 is a signal the scope is too wide — narrow the scope instead of adding agents
- Every adaptive lane gets a challenger. There are no unopposed agents in the system

---

## How drift and hallucination are prevented

Seven mechanisms. Each one closes a specific failure mode observed in long multi-agent runs.

| # | Mechanism | Failure it closes |
|---|---|---|
| 1 | **Agents write files; the orchestrator reads five-line summaries** | Context window fills with raw research, and the run forgets its own question |
| 2 | **Confidence tags on every claim** — `[HIGH\|2+ sources]`, `[MED\|1 source]`, `[LOW]` inference, `[ASSUMPTION]` invented | Invented figures pass as facts because nothing distinguishes them |
| 3 | **Scope contract pasted verbatim into every agent prompt** | Agents wander into adjacent topics that feel relevant |
| 4 | **Off-scope findings go in a `DRIFT_REQUEST` line, never in findings** | Interesting tangents quietly become the research |
| 5 | **Hard search and word budgets per agent** | Agents pad to fill space instead of ranking what matters |
| 6 | **One rebuttal round per lane, then the lane closes** | Challenger and researcher argue forever, burning the run |
| 7 | **Kill criteria written before research begins** | The system rationalises a yes after the fact |

Two more constraints shape output quality:

- **Disconfirming evidence is mandatory.** A lane that reports no counter-evidence is treated as a lane that did not look properly.
- **Every lane ends in a founder consequence.** A finding with no consequence for someone with ₹0 gets cut, no matter how interesting.

---

## What you get out

A decision memo — `99_verdict.md` — not a research report.

| Section | Contents |
|---|---|
| **Verdict** | BUILD, RESHAPE or KILL, with two lines of reasoning. Unhedged. |
| **The three real gaps** | Each with *why the gap is still open* and *why that reason is beatable now*. A gap with no explanation of why nobody filled it is flagged as a hole in the research, not sold as an opportunity. |
| **Three threats as leverage** | Each threat, how it converts into an advantage, and what flipping it costs |
| **The killer assumption** | The single belief that ends the idea if wrong. One line. |
| **The ₹20k test** | A two-week experiment that falsifies the killer assumption. Numbered steps, each with cost and time. Total under ₹20,000. |
| **Monday morning** | One action, under 2 hours, doable today |
| **What we still do not know** | Ranked, each with the cheapest way to find out |

Hard rules the assessor follows:

- Conclusions resting on low-confidence or assumed claims are down-weighted and named
- If three or more lanes resolved DEAD, the verdict is KILL, unsoftened
- No recommendation may require money, headcount or a network the founder does not have

---

## Install

### Claude Code (terminal)

```bash
claude plugin marketplace add rishabhrawat35/idea-research
claude plugin install idea-research@idea-research
```

Restart Claude Code. Verify:

```bash
claude plugin list
```

### Claude desktop app (Cowork)

Settings → Capabilities → Skills → add the skill, or paste the contents of `skills/idea-research/SKILL.md` when creating a new skill.

### Any other agent-skills harness

Copy the skill folder into whatever path your agent scans:

```bash
git clone https://github.com/rishabhrawat35/idea-research
cp -R idea-research/skills/idea-research ~/.claude/skills/
```

Works with Cursor (`~/.cursor/skills/`), Copilot (`~/.copilot/skills/`), Zed (`~/.config/zed/skills/`) and anything else that reads Agent Skills.

### Requirements

| Requirement | Why |
|---|---|
| Web search enabled | Every researcher needs it |
| Subagent or Task tool | The system spawns 7-18 agents per run |
| Write access to a folder | Lane files and verdict are written to disk |

---

## How to run it

### Start a run

Type any of these:

```
idea-research: an app that helps small Indian gyms manage member payments
```

```
validate this idea — WhatsApp-based crop advisory for cotton farmers in Gujarat
```

```
should I build a compliance tool for Indian diagnostic labs?
```

### Triage several ideas cheaply

```
idea-research lite: <idea>
```

Runs 3 lanes, about 7 agents, 8-12 minutes. Use it to kill weak ideas before spending a full run on one.

### What happens next

| Step | What you see | What you do |
|---|---|---|
| 1 | Up to 3 clarifying questions, only if the idea is unscopeable | Answer briefly |
| 2 | The scope contract and the agent roster, as a table | Reply "go" — or correct the scope first |
| 3 | Researchers running in parallel | Nothing. 10-15 minutes. |
| 4 | Challengers running, verdicts per lane | Nothing |
| 5 | The decision memo | Read it. Argue with it. |

### Useful follow-ups after a run

| Ask | Effect |
|---|---|
| "Rerun L2 with a wider competitor net" | Re-runs one lane only, keeps the rest |
| "The challengers were too soft, rerun phase 2" | Re-challenges every lane harder |
| "Reshape it as B2B and rerun" | New scope contract, fresh run, old run preserved |
| "Compare this run against my earlier idea" | Reads both verdict files side by side |

### Reading the verdicts

| Verdict | Meaning | What to do |
|---|---|---|
| **SURVIVES** | The lane held under attack | Trust it, within its confidence tags |
| **WOUNDED** | A real hole, not necessarily fatal | Read the challenger's question — it is usually the thing to test first |
| **DEAD** | The lane's core claim did not hold | Treat as a finding. Three DEAD lanes means KILL. |

---

## File layout of a run

```
runs/<idea-slug>/
├── 00_scope.md              the contract every agent reads first
├── 01_roster.md             which lanes ran, and why each was chosen
├── _state.md                phase and per-lane status table
├── lanes/
│   ├── L1_market.md         findings → challenge → rebuttal → verdict
│   ├── L2_competitors.md
│   ├── L3_demand.md
│   ├── L4_wedge.md
│   ├── L5_capital.md
│   └── A1_<adaptive>.md
└── 99_verdict.md            the decision memo
```

Every lane file has the same shape:

| Section | Written by |
|---|---|
| `FINDINGS` | Researcher |
| `EVIDENCE TABLE` — claim, tag, source, why it matters | Researcher |
| `DISCONFIRMING EVIDENCE` | Researcher |
| `OPEN QUESTIONS` | Researcher |
| `SO WHAT FOR A ₹0 FOUNDER` | Researcher |
| `DRIFT_REQUEST` | Researcher |
| `CHALLENGE` — fatal, serious, noted | Challenger |
| `VERDICT` | Challenger |
| `REBUTTAL` and `RESOLVED VERDICT` | Researcher, once, only if wounded or dead |

Runs are kept. Comparing an idea against the same idea reshaped three weeks later is one of the more useful things the system does.

---

## Cost and time

| Mode | Lanes | Agents | Wall time | Roughly |
|---|---|---|---|---|
| `lite` | 3 | ~7 | 8-12 min | Triage pass |
| `full` | 5-8 | 12-18 | 25-40 min | Serious evaluation |

Ways to spend less:

1. Run `lite` first. Most ideas die there, and that is the point.
2. Narrow the scope. A tighter scope contract means fewer searches per lane.
3. Cut adaptive lanes to 1 if the domain is not heavily regulated.
4. Rerun single lanes instead of whole runs when following up.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Every lane says roughly the same thing | Scope is too broad | Rewrite `00_scope.md` narrower and rerun |
| Every lane came back SURVIVES | Challengers were too polite | "Rerun phase 2 — you are being graded on kills" |
| The verdict reads generic | Assessor saw raw research instead of lane files | It must read `lanes/` only |
| An agent went off-topic | Scope contract was not pasted into its prompt | Paste it verbatim into every agent prompt |
| The run stalls midway | Too many agents spawned at once | Cap parallel spawns at 6 and run in two waves |
| No Indian sources came back | Searches were not localised | Add "India" and the state or city to the scope contract's geography line |
| Market sizes look invented | They probably are | Check the tag. `[ASSUMPTION]` means invented, and the CFO challenger should have flagged it |

---

## Design decisions and why

| Decision | Alternative rejected | Reason |
|---|---|---|
| Agents write to files | Agents return findings to the orchestrator | The orchestrator's context fills and the run drifts by lane 4 |
| One file per lane, shared by researcher and challenger | Separate research and critique files | The argument and its resolution belong together, and nothing needs reassembling |
| One rebuttal round, hard cap | Iterate until convergence | Adversarial pairs do not converge; they burn the run |
| Assessor never sees raw research | Assessor reads everything | An assessor that reads everything is persuaded by volume rather than by what survived |
| Kill criteria written before research | Judge at the end | Deciding what counts as failure after seeing the data is how a system talks itself into a yes |
| 5 consolidated lanes, not 9 granular ones | One lane per research question | News, Reddit and Quora answer the same question. Splitting them produces four files restating one finding |
| Roster built per domain at runtime | Fixed agent set | A pharma idea needs a regulator; a manufacturing idea needs customs. A fixed roster serves neither |
| India and ₹0 as defaults | Generic global framing | Generic framing produces generic findings. Constraints are what make the output usable |

---

## Licence

MIT. See [LICENSE](LICENSE).
