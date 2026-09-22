# ABOUTME: Asks whether the four-dot's minimum spacing is a block count or a rune count,
# ABOUTME: by simulating each floor alone and checking for violations of the other.
"""The floor is real. What does it count?

`the_four_dot_has_a_floor.py` establishes that no two four-dots are one block apart, where
the author's own sentence marks have no such floor -- six of his ninety-four sentences are
a single block. Whatever places the four-dots enforces a minimum unit.

The unit could be counted two ways and they are not the same rule:

    at least two BLOCKS between marks       -- a word count
    at least six RUNES between marks        -- a letter count

Both hold in the body. The smallest gaps are (2 blocks, 6 runes), (2, 7), (2, 7), (4, 7),
(3, 8) -- nothing below two blocks and nothing below six runes.

They are distinguishable in principle because each permits what the other forbids:

- a **block** floor allows a two-block gap made of two very short blocks, four or five
  runes in total;
- a **rune** floor allows a one-block gap when that block is six runes or longer, and
  about a third of the body's blocks are.

## The test

Place 138 marks at uniformly random positions in the body's own block sequence, subject to
one floor, and count violations of the other. The body's real block lengths are used, so
the frequency of short and long blocks is exactly right.

## Result: the corpus cannot say

| rule simulated | one-block gaps produced | sub-6-rune gaps produced |
|---|---|---|
| a block floor alone | 0.00 | **1.06** |
| a rune floor alone | **1.86** | 0.00 |
| both floors | 0.00 | 0.00 |
| **THE BODY** | **0** | **0** |

| rule | violations of the other expected | P(none) |
|---|---|---|
| a block floor alone | 1.06 | **0.35** |
| a rune floor alone | 1.86 | **0.16** |

**Neither single floor is excluded.** Each would break the other about once or twice
across the whole corpus, and the body breaks it never -- a tail of 0.16 to 0.35. That is a
preference for both rules holding, not a demonstration of it.

## What this fixes and what it leaves

The floor itself is NOT established: the 0.00015 it was once priced at came from an
author arm 2.7 times denser than the body, and scale-matched it reads 0.055
(`the_floor_needs_a_scale_matched_reference.py`). This file asks what a floor would
count if there were one
(`the_four_dot_has_a_floor.py`). **What it counts is not**, and the reason is structural
rather than a matter of effort: the whole question turns on one or two expected
violations, so it needs more marks and not a better statistic.

That is worth stating precisely because it is the sharpest open question about the
four-dot. If the unit is a **word count**, the mark divides the text by syntax, however
loosely. If it is a **rune count**, it divides by length, and the text is not involved at
all. Those are different objects and 138 marks cannot separate them.

    python does_the_floor_count_blocks_or_runes.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, blocks  # noqa: E402

MARKS = 138
MIN_BLOCKS = 2
MIN_RUNES = 6
DRAWS = 300


def place(lengths, min_blocks, min_runes, rng, draws=DRAWS):
    """Marks placed under one floor; count how often the other floor is broken."""
    one_block = sub_runes = runs = 0
    n = len(lengths)
    for _ in range(draws):
        chosen: list[int] = []
        tries = 0
        while len(chosen) < MARKS and tries < 20000:
            tries += 1
            p = rng.randrange(1, n)
            ok = True
            for q in chosen:
                if abs(p - q) < min_blocks:
                    ok = False
                    break
                lo, hi = min(p, q), max(p, q)
                if sum(lengths[lo:hi]) < min_runes:
                    ok = False
                    break
            if ok:
                chosen.append(p)
        if len(chosen) < MARKS:
            continue
        runs += 1
        chosen.sort()
        for a, b in zip(chosen, chosen[1:]):
            one_block += (b - a) < MIN_BLOCKS
            sub_runes += sum(lengths[a:b]) < MIN_RUNES
    return one_block / max(runs, 1), sub_runes / max(runs, 1), runs


def main() -> None:
    rng = random.Random(3301)
    lengths = [n for n, _, _ in blocks(BODY)]
    print(f"{len(lengths):,} body blocks, {MARKS} four-dots.\n")
    print(
        f"{'rule simulated':<34}{'one-block gaps':>16}{'sub-6-rune gaps':>18}{'runs':>7}"
    )
    results = {}
    for label, mb, mr in (
        ("a block floor alone", MIN_BLOCKS, 0),
        ("a rune floor alone", 1, MIN_RUNES),
        ("both floors", MIN_BLOCKS, MIN_RUNES),
    ):
        ob, sr, runs = place(lengths, mb, mr, rng)
        results[label] = (ob, sr)
        print(f"{label:<34}{ob:>16.2f}{sr:>18.2f}{runs:>7}")
    print(f"{'THE BODY':<34}{0:>16}{0:>18}")

    print("\nHow surprised each single rule is by what the body shows.\n")
    print(f"{'rule':<34}{'violations expected':>21}{'P(none)':>10}")
    ob, sr = results["a block floor alone"]
    print(f"{'a block floor alone':<34}{sr:>21.2f}{stats.poisson.pmf(0, sr):>10.2f}")
    ob, sr = results["a rune floor alone"]
    print(f"{'a rune floor alone':<34}{ob:>21.2f}{stats.poisson.pmf(0, ob):>10.2f}")

    print(
        "\n  Neither single floor is excluded. Each would break the other about once or"
        "\n  twice across the corpus and the body breaks it never, which is a tail of"
        "\n  0.16 to 0.35 -- a preference for both rules holding, not a demonstration."
        "\n\n  So the floor is established and what it counts is not. Settling it needs"
        "\n  more marks: the whole question turns on one or two expected violations."
    )


if __name__ == "__main__":
    main()
