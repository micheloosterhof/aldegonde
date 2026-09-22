# ABOUTME: Rescales the floor test's references to the body's own mark rate, because the
# ABOUTME: headline P = 0.00015 came from an author arm 2.7 times denser than the body.
"""The four-dot's floor was priced against a reference at the wrong scale.

`the_four_dot_has_a_floor.py` reports zero one-block gaps in 138 where three arms predict
6.8, 8.8 and 4.6. The strongest of those, **P = 0.00015 under "the author's own
convention"**, applies the author's raw fraction of one-block sentences -- 6 of 94, rate
0.0638 -- to the body's 138 gaps. But the author's sentences average **7.65 blocks** and
the body's four-dot gaps **20.4**. The arm is 2.7 times denser than the thing it prices.

That is the error this directory keeps making: comparing against a reference that differs
from the corpus in a variable the prediction depends on. A denser marking process produces
more short gaps for reasons that have nothing to do with a floor.

## The scale-matched version

`are_the_four_dot_gaps_memoryless.py` already established the right relationship: the
body's gap law fits **the author's own spans thinned to p = 0.357**. Thinning is the
correct way to match the scales, because it is a model of the body marking a subset of the
same kind of boundary -- and it makes the prediction sharply weaker, since a surviving
one-block gap now needs a one-block sentence *and* both of its bounding marks retained.

Each reference is thinned to the body's observed mean gap, then 138 gaps are drawn and the
count at exactly one block recorded. The author's arm is bootstrapped over his 94
sentences so the reference's own sampling error is carried.

## Result: the floor drops from P = 0.00015 to P = 0.055

    arm                                 p     E[1-block]   P(zero)   P(min >= 2)
    memoryless, matched to the body    --         6.77      0.0011      0.0010
    the author's sentences, thinned   0.375       3.32       0.0332      0.0332
    English sentences, thinned        0.901       4.11       0.0150      0.0150

Carrying the author's own sampling error over his 94 sentences, his arm expects
**3.45 +- 2.31** one-block gaps and gives **P(zero) = 0.055**.

**The headline number was inflated by more than two orders of magnitude.** Against the
reference the gap law itself prefers, zero one-block gaps is a 1.6-sigma event, not a
3.8-sigma one.

## What survives

The floor is no longer established. What remains is a short-gap deficit of the ordinary
kind: fewer small gaps than a memoryless process gives, which is exactly what fitting a
non-memoryless gap law already said. The memoryless arm is the only one that still rejects
at 0.001, and `are_the_four_dot_gaps_memoryless.py` rejects that arm on shape grounds
independently (likelihood ratio 0.134 against the thinned-author arm), so it cannot carry
the conclusion either.

`the_floor_belongs_to_the_four_dot.py` compared the four-dot against other glyph pairs and
reached only P = 0.075 on its own. Both routes now land in the same place: **the four-dot's
minimum unit is suggestive at around 2 sigma and is not a rule.**

    python the_floor_needs_a_scale_matched_reference.py
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from the_four_dot_has_a_floor import body_gaps, english_sentences  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

DRAWS = 20_000


def thin(units, p, count, rng):
    """`count` gaps from a stream of units where each boundary survives with prob p."""
    out, run = [], 0
    while len(out) < count:
        run += units[rng.randrange(len(units))]
        if rng.random() < p:
            out.append(run)
            run = 0
    return out


def retention(units, target):
    """Survival probability that puts the thinned mean gap at `target`."""
    return float(np.mean(units)) / target


def main() -> None:
    rng = random.Random(3301)
    gaps = body_gaps()
    n, mean = len(gaps), float(np.mean(gaps))
    observed = Counter(gaps).get(1, 0)

    author = [len(s) for s in author_spans()]
    english = english_sentences(rng)

    print(f"the body: {n} four-dot gaps, mean {mean:.1f} blocks, min {min(gaps)}")
    print(f"the author: {len(author)} sentences, mean {np.mean(author):.2f} blocks")
    print(f"English: {len(english):,} sentences, mean {np.mean(english):.1f} blocks")
    print(
        f"\nThe author's arm is {mean / np.mean(author):.1f}x sparser in the body than in"
        "\nhis own pages, so his raw one-block rate cannot be applied to it directly.\n"
    )

    print(f"{'arm':<36}{'p':>7}{'E[1-block]':>13}{'P(zero)':>10}{'P(min>=2)':>12}")

    rate = 1 / mean
    print(
        f"{'memoryless, matched to the body':<36}{'--':>7}{rate * n:>13.2f}"
        f"{stats.poisson.cdf(observed, rate * n):>10.4f}"
        f"{(1 - rate) ** n:>12.4f}"
    )

    for label, units in (
        ("the author's sentences, thinned", author),
        ("English sentences, thinned", english),
    ):
        p = retention(units, mean)
        ones, floors = [], 0
        for _ in range(DRAWS // (20 if units is english else 1)):
            draw = thin(units, p, n, rng)
            counts = Counter(draw)
            ones.append(counts.get(1, 0))
            floors += min(draw) >= 2
        ones = np.array(ones, float)
        print(
            f"{label:<36}{p:>7.3f}{ones.mean():>13.2f}"
            f"{np.mean(ones <= observed):>10.4f}{floors / len(ones):>12.4f}"
        )

    # The author's own 94 sentences are a small reference; carry their sampling error.
    boot = []
    for _ in range(400):
        resample = [author[rng.randrange(len(author))] for _ in author]
        p = retention(resample, mean)
        draw = thin(resample, p, n, rng)
        boot.append(Counter(draw).get(1, 0))
    boot = np.array(boot, float)
    print(
        f"\nCarrying the author's own sampling error over his 94 sentences:"
        f"\n  E[1-block] = {boot.mean():.2f} +- {boot.std(ddof=1):.2f}"
        f"   P(zero) = {np.mean(boot <= observed):.3f}"
    )

    print(
        "\nThe headline P = 0.00015 came from an unmatched arm. Scale-matched, zero"
        "\none-block gaps is an ordinary short-gap deficit -- the same thing the fitted"
        "\nnon-memoryless gap law already reported. The floor is not established."
    )


if __name__ == "__main__":
    main()
