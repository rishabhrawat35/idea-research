# Contributing

Thanks for looking. This is one markdown file doing the work, so contributing is easier than most repos.

## The engine is one file

Everything lives in [`skills/idea-research/SKILL.md`](skills/idea-research/SKILL.md). Plain English, no code. If you can read it, you can change it.

## Most useful contributions

### 1. A run that got it wrong

The single most valuable issue you can open. Include:

- The idea you gave it
- The answer it gave you
- What actually happened, or why you think it was wrong

A system like this is only as good as the cases where it failed, and those only show up when people report them.

### 2. A specialist for a new domain

Stage 2 has a table of domain specialists. Legal, logistics, gaming, climate, real estate and hospitality are all missing. A good specialist entry names a real job title and what that person would know that nobody else would.

### 3. A market other than India

The India defaults sit in Stage 0 (the brief) and Stage 2 (the researcher instructions). Adding another market means changing the currency, the regulators, the price anchors and the distribution channels. Keep the structure, swap the specifics.

### 4. Words for the banned list

If an answer sounded like a consultant wrote it, tell us which sentence gave it away. Consultant-speak leaks back in constantly and the banned list is the only thing that holds it out.

## Testing a change

There is no test suite. Run the skill on two or three ideas you already know the answer to, and check three things:

1. Did it finish inside the pipeline's own budget, which SKILL.md puts at thirteen to sixteen agents and twenty at the longest legal path?
2. Does the answer name real companies and real prices?
3. Would you send it to a friend, or does it read like a report?

## Pull requests

- One change per PR
- Say which idea you tested it on
- If you changed the writing rules, paste a before and after

## Code of conduct

Be decent. Disagree with the idea, not the person.
