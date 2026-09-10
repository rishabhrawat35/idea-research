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

<!--::figure|Spend concentrates in the first three months-->
Labs 42 percent, pharmacy 31 percent, clinics 27 percent.
Source: R1_money.md, the researcher's own arithmetic

<!--::appendix|101 rows-->
## Appendix A. Sources and calculations
```

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
