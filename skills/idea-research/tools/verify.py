#!/usr/bin/env python3
"""Build a worklist for spot-checking that cited sources say what is claimed.

Usage:  python3 tools/verify.py runs/<slug>/ [--sample 8] [--seed 1]

Reads claims.jsonl, samples claims that carry a URL, and writes:
  verify_queue.md  a numbered worklist with three boxes to tick per claim
  verify.json      the same sample as data, so a later run can compare

This script cannot fetch anything. An agent or a person opens each URL and
fills the boxes in. Pass --seed to get the same sample twice.

Exit 0 on success, 1 on a real failure, 2 on bad usage. Standard library only.
"""
import json
import random
import sys
from pathlib import Path

USAGE = "usage: python3 verify.py runs/<slug>/ [--sample 8] [--seed 1]"

DEFAULT_SAMPLE = 8
MAX_CLAIM_CHARS = 400


def parse_args(argv):
    """Returns (run_dir, sample, seed) or None on bad usage."""
    positional, sample, seed, i = [], DEFAULT_SAMPLE, None, 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--sample", "--seed"):
            if i + 1 >= len(argv):
                return None
            try:
                value = int(argv[i + 1])
            except ValueError:
                return None
            if arg == "--sample":
                if value < 1:
                    return None
                sample = value
            else:
                seed = value
            i += 2
            continue
        if arg.startswith("-"):
            return None
        positional.append(arg)
        i += 1
    if len(positional) != 1:
        return None
    return positional[0], sample, seed


def load_claims(path):
    claims = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
        if not line.strip():
            continue
        try:
            claim = json.loads(line)
        except ValueError:
            print("skipped malformed claims.jsonl line %d" % (i + 1))
            continue
        if isinstance(claim, dict) and claim.get("text"):
            claims.append(claim)
    return claims


def pick(sourced, size, rng):
    """Sample without replacement, one URL each before repeating any URL.

    Eight entries pointing at the same page would check one page, not eight.
    """
    pool = list(sourced)
    rng.shuffle(pool)
    chosen, seen, spare = [], set(), []
    for claim in pool:
        if claim["url"] in seen:
            spare.append(claim)
            continue
        seen.add(claim["url"])
        chosen.append(claim)
        if len(chosen) == size:
            return chosen
    return chosen + spare[:size - len(chosen)]


def shorten(text):
    text = " ".join(text.replace("|", " / ").split())
    return text if len(text) <= MAX_CLAIM_CHARS else text[:MAX_CLAIM_CHARS - 3] + "..."


def write_queue(run_dir, sample, sourced_total):
    out = ["# Source spot-check queue", "",
           "%d of %d sourced claims, sampled at random by tools/verify.py."
           % (len(sample), sourced_total),
           "Open each URL, decide whether the page states the claim, and mark one",
           "box. Read the figure, not the gist: a page that says something near",
           "the claim but not the claim is NOT SUPPORTED.", ""]
    for i, claim in enumerate(sample, 1):
        out += ["## %d. %s:%d" % (i, claim["file"], claim["line"]),
                "",
                "Claim: %s" % shorten(claim["text"]),
                "",
                "Figure: %s" % (claim.get("figure") or "(none)"),
                "URL: %s" % claim["url"],
                "",
                "- [ ] SUPPORTED",
                "- [ ] NOT SUPPORTED",
                "- [ ] COULD NOT FETCH",
                "",
                "Note:",
                ""]
    if not sample:
        out += ["Nothing to check: no claim in claims.jsonl carries a URL.", ""]
    (run_dir / "verify_queue.md").write_text("\n".join(out), encoding="utf-8")


def main(argv):
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__.strip())
        return 0
    parsed = parse_args(argv)
    if not parsed:
        print(USAGE)
        return 2
    run_dir, size, seed = parsed

    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        print("no such run directory: %s" % run_dir)
        return 1
    claims_path = run_dir / "claims.jsonl"
    if not claims_path.is_file():
        print("no claims.jsonl in %s -- run claims.py first" % run_dir)
        return 1

    claims = load_claims(claims_path)
    sourced = [c for c in claims
               if c.get("status") == "sourced" and c.get("url")]
    rng = random.Random(seed)
    sample = pick(sourced, size, rng)

    write_queue(run_dir, sample, len(sourced))
    (run_dir / "verify.json").write_text(json.dumps(
        {"sourced_claims": len(sourced), "requested": size, "seed": seed,
         "sample": sample}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("sampled %d of %d sourced claims (%d claims in all) -> %s"
          % (len(sample), len(sourced), len(claims), run_dir / "verify_queue.md"))
    if len(sample) < size:
        print("only %d sourced claims available, asked for %d" % (len(sample), size))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
