# Block tags for ANSWER.md

Write tags as HTML comments. The markdown stays valid anywhere else, and the tag
applies to **the block that follows it** (a block = consecutive lines, no blank line
inside). Optional text after a pipe becomes the label, title, attribution or summary:
`<!--::warn|Do not do this-->`. Untagged content renders as plain prose, so tag only
what earns a component.

| Tag | Content type it holds |
|---|---|
| `::meta` | Date, status, owner. One block, `Key: value` per line. Put it above the H1's answer, first in the file. |
| `::verdict` | The single recommendation. One block, largest thing on the page. Use once. |
| `::stat` | Numbers that each carry an argument. Three or four per block, `value :: label`. |
| `::finding` | One claim plus its evidence, cost strip and next step. Repeat for a numbered run. |
| `::note` | Neutral context the reader needs but would not act on. |
| `::tip` | A practical shortcut. |
| `::important` | The one belief everything rests on. |
| `::warn` | A cost, a limit, a thing that will bite. |
| `::caution` | A legal, ethical or safety line you must not cross. |
| `::compare` | Options scored on shared axes. A markdown table; bold the first cell of the winning row. |
| `::quote` | A cited voice. Attribution after the pipe, or on its own line starting with an em dash. |
| `::steps` | A sequential instruction list. Numbered markdown list. |
| `::cards` | What to read or run next. `name :: one line of description`. |
| `::ranked` | An ordered list where the order is the argument. `claim :: why it ranks there`. Numbers run on across the whole PART. |
| `::timeline` | A phased plan. `phase :: the item :: the number that means it worked`. |
| `::asks` | People to approach. `name :: why them :: question \| question`. |
| `::figure` | A figure with furniture. Title after the pipe, a `Source:` line last. |
| `::appendix` | Sources, methodology, raw rows. Placed before an `##` heading it collapses that whole section. |

## Examples

```markdown
<!--::meta-->
Status: Draft | Owner: founder | Checked: 2026-09-10

<!--::verdict|The call-->
Do not build the subscription app. Sell a one-off audit at Rs 499, because five
better-funded companies already declined the recurring-payment channel.

<!--::stat-->
- Rs 18,000-39,000 :: what one urban couple spends in the year
- 0 :: companies publishing partner activation

<!--::finding-->
**Arva already owns the content and the counsellors.**
It began in 2022 as fertility education and today sells single sessions at Rs 500.
COST: Rs 0 | EFFORT: 1 day | OWNER: founder
Next: email Arva and ask for one partner arrangement.

<!--::note-->
Telemedicine Practice Guidelines 2020, section 5.4, allow general health information.
They do not allow counselling or prescribing.

<!--::tip-->
Charge before you deliver.
Twenty free sign-ups teach you nothing about whether this is a business.

<!--::important-->
One belief carries the whole plan.
A couple must pay to be told what not to buy, with the husband listening.

<!--::warn|Do not do this-->
Never take a referral cut from a doctor or an IVF clinic.
Fee-splitting with practitioners is prohibited under Indian medical ethics rules.

<!--::caution-->
The saving figure is a guess.
No research file contains a benchmark for it.

<!--::compare-->
| Option | Price | Humans needed | Verdict |
|---|---|---|---|
| **One-off audit** | Rs 499 | none | Test this |
| Subscription app | Rs 208/mo | none | Closed |

<!--::quote|Bezos, 2017 shareholder letter-->
We don't do PowerPoint presentations at Amazon.
Instead, we write narratively structured six-page memos.

<!--::steps-->
1. Build the fourteen-question form and a payment page at Rs 499.
2. Write the "do not buy this" list once, as a template.

<!--::cards-->
- Claim ledger :: every figure, and whether it was sourced or guessed
- Contradiction check :: rows where two sources disagree

<!--::ranked-->
- **No lab has quoted a per-booking rate in writing.** :: The revenue model rests
  on a commission nobody agreed. Three partner desks were emailed, none replied.
- **The couple may never pay directly.** :: The stated ceiling is Rs 199 to Rs 499
  a month, and one competitor is priced at zero.

<!--::timeline-->
- Days 1 to 14 :: Get a written per-booking rate from one named lab. :: Rs 300 or more per couple
- Days 1 to 14 :: Run the form ad to a single two-name form. :: 10 or more forms carry two names
- Days 15 to 45 :: Book ten couples into two panels each. :: 7 or more men complete a collection

<!--::asks-->
- Redcliffe Labs partner desk :: Runs the home collection network the route needs. :: What do you pay per completed booking? | Which partner categories are paused?
- Fertilia, via its Rs 399 consult :: Already sells a 90-day plan to the same buyer. :: What do you spend per client on coaching hours? | What did you last stop paying for?

<!--::figure|Spend concentrates in the first three months-->
Labs 42 percent, pharmacy 31 percent, clinics 27 percent.
Source: R1_money.md, the researcher's own arithmetic

<!--::appendix|101 rows-->
## Appendix A. Sources and calculations
```

## The three ordered components in detail

All three split their fields on `::` and nothing else, so a claim may contain a
hyphen without being cut in half. A line that does not start with a list marker
belongs to the item above it, which is how a long evidence line gets its own
line. All three go to a single column under 620px.

**`::ranked`** is for a list where the position is part of the argument, such as
the problems worst first. Each item renders as a hanging number in the accent
colour, one bold claim line, and one indented evidence line under it with a rule
down its left edge. **The number is a CSS counter reset at the PART heading**, so
two `::ranked` blocks in one part continue the same run rather than both starting
at 1. On a phone the number moves onto its own line above the claim.

**`::timeline`** is for a phased plan. Rows that repeat a phase label collapse
into one node, so a horizon with two items reads as one horizon. Wide screens get
a rule down the left with a ring node per phase, the label in the second column
and the items in the third. The third field is the number that means it worked
and renders as a pill reading "Target: ...". Under 620px the rule and the nodes
are dropped and each phase becomes a stacked row under a top border.

**`::asks`** is for the people to approach. Each becomes a card with the name, one
muted line on why them, and the questions as separate ruled rows, each marked
with a question mark in the accent colour. That is what stops three questions
from reading as a paragraph. Wide screens fit a compact grid of cards at 255px
minimum, so three sit across a normal report column; a phone gets one card each.

## Themes

`render/themes.py` holds four complete token sets and nothing generates a fifth.
`report.css` carries the `clinical` set inline as its default, and
`render.py --theme <theme.json>` substitutes another set into that one `:root`
block at build time. There is one stylesheet, never four.

| Theme | Ground | For |
|---|---|---|
| `clinical` | cool light paper, teal accent | Health, medtech, diagnostics, pharma |
| `warm` | warm stone paper, rose-plum accent | Consumer, family, wellness, education, food |
| `industrial` | warm graphite, safety-orange accent | Hardware, manufacturing, logistics, B2B |
| `financial` | cool ink, terminal-teal accent | Fintech, lending, insurance, markets |

`theme.json` may override the accent, name a Google font family for display and
body text, and ask for `"density": "compact"`. With no `--theme` flag at all the
render runs on `clinical`, but a `--theme` path that was passed and cannot be read
exits 1 and writes nothing, so a mistyped path never ships an unmeasured palette. Run
`python3 render/themes.py` to print every contrast ratio in all four.

## The clean markdown

Every render also writes `ANSWER_clean.md` next to `report.html`, and that is the
file a person is handed. It contains no engine syntax at all: no `<!--` comment,
no `[[badge]]`, no `::` separator. A badge keeps its own word inside brackets, so
`[[warn:Thin]]` reads `(status: Thin)`. A tag's label after the pipe is promoted
to a bold lead-in line, so `<!--::warn|This is the cost that will bite-->`
becomes `**This is the cost that will bite**` above the paragraph.

## Inline badge

`[[Sourced]]` renders a pill. Tones: `[[ok:Sourced]]`, `[[warn:Thin]]`, `[[bad:Not
found]]`, `[[flat:Carried]]`. Use it on a claim or a table cell, not in a heading.

## What happens without a tag

- **Section numbers** come from CSS counters, so do not type them. A number you do
  type at the front of an `##` heading is stripped and replaced with the counter.
- **The italic one-liner** directly under a heading becomes the section subtitle.
- **Any `## Appendix ...` heading** collapses into a closed `<details>` on its own,
  with or without the `::appendix` tag.
- **Every table** gets a phone card collapse and per-cell labels automatically.
  Write a plain markdown table; add `::compare` only when options are being scored.
- Everything else is paragraphs, lists, links and code, styled as prose.

## Rules the renderer will not fix for you

Headings state the finding, not the topic, and read correctly with the section
covered. Three or more related data points become a table row. Nothing over 25
words. Three sentences per paragraph. One fact has one owning section; later
mentions cross-reference it. Appendices open closed, so nothing a reader needs in
order to act may sit inside one.
