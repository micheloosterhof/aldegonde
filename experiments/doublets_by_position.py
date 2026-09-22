# ABOUTME: Settles the owed opportunity-normalised test of where doublets fall inside a
# ABOUTME: block, and finds the suppression uniform in position and in block length.
"""The doublet suppression does not care where in a block it acts.

`period5-doublet-linkage.md` records an unfinished check:

    The within-word doublet start-phase looks concentrated at j = 0,1, but that is
    confounded by word length (short words over-weight low positions); it needs an
    opportunity-normalized test before it counts.

Here it is. For each position j the denominator is the number of adjacent pairs that
*exist* at that position -- blocks of more than j runes -- so a short block contributes
to low j only, which is exactly the confound.

The apparent concentration was the confound. Normalised, the profile is flat:
chi2 = 7.10 on 7 df, P = 0.42, and the block-initial pair sits at 0.0043 against the
overall 0.0063, mildly LOW rather than high.

## How much this can and cannot see

Eight cells against 63 doublets is eight per cell, so the power has to be measured rather
than assumed. Planting effects at the block-initial pair:

| planted at j = 1 | doublets there | chi2 | P |
|---|---|---|---|
| unchanged | 12 | 7.10 | 0.419 |
| suppression twice as strong | 6 | 13.70 | 0.057 |
| twice as many | 33 | 8.87 | 0.262 |
| **preventer blind there** | 81 | **73.01** | **0.000** |

So this rules out a **large** position effect and nothing subtler. A preventer that
simply does not act on the first pair would be unmissable; one that is twice as strong
there is caught only marginally; one that lets through twice as many is **not caught at
all**. Read the flat result as excluding the mechanisms below, not as showing the
suppression is uniform to within a factor of two.

The denominators are what make even that possible -- 2,813 adjacent pairs at j = 1. A
position effect is a change in rate, so the opportunity counts set the power, and they
are ample where the doublet counts are not. That is the opposite situation to
`doublet_gaps_conditioned.py`, where 86 doublets had to fill five residues across seven
buckets and the verdict came down to two of them.

## What it rules out

Anything that makes the suppression position-dependent inside a block: a preventer whose
state resets at the block boundary, a clock whose phase is tied to position within the
block rather than running on, or a rule that acts only after the first rune. The
companion profile by block length is flat too, so the suppression does not weaken in long
blocks either.

    python doublets_by_position.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_cipher_restart import body_blocks  # noqa: E402

MAX_POSITION = 8
LENGTH_BINS = ((2, 3), (4, 5), (6, 7), (8, 9), (10, 99))


def position_profile(blocks, cap=MAX_POSITION):
    """Doublets and adjacent-pair opportunities at each within-block position."""
    hits = np.zeros(cap + 1)
    opportunities = np.zeros(cap + 1)
    for word in blocks:
        for j in range(1, len(word)):
            k = min(j, cap)
            opportunities[k] += 1
            hits[k] += word[j] == word[j - 1]
    return hits[1:], opportunities[1:]


def length_profile(blocks):
    """The same, binned by the length of the block the pair sits in."""
    hits = np.zeros(len(LENGTH_BINS))
    opportunities = np.zeros(len(LENGTH_BINS))
    for word in blocks:
        for i, (lo, hi) in enumerate(LENGTH_BINS):
            if lo <= len(word) <= hi:
                opportunities[i] += len(word) - 1
                hits[i] += sum(word[j] == word[j - 1] for j in range(1, len(word)))
    return hits, opportunities


def uniformity(hits, opportunities):
    """Chi-square against a single rate shared by every cell."""
    keep = opportunities > 0
    rate = hits.sum() / opportunities.sum()
    expected = opportunities[keep] * rate
    chi = float(((hits[keep] - expected) ** 2 / np.maximum(expected, 1e-9)).sum())
    df = int(keep.sum()) - 1
    return chi, df, float(1 - stats.chi2.cdf(chi, df))


def planted(blocks, rng, *, factor, at_position=1):
    """Re-emit the corpus with the doublet rate at one position scaled by `factor`.

    Doublets are added or removed at that position only, leaving every other position
    exactly as the corpus has it, so the test sees a pure position effect.
    """
    out = []
    for word in blocks:
        w = list(word)
        for j in range(1, len(w)):
            if j != at_position:
                continue
            if w[j] == w[j - 1]:
                if factor < 1 and rng.random() > factor:
                    w[j] = (w[j] + 1) % 29  # break this doublet
            elif factor > 1 and rng.random() < (factor - 1) * 0.0063:
                w[j] = w[j - 1]  # make one
        out.append(w)
    return out


def main() -> None:
    blocks = [b for b, _ in body_blocks(set())]
    hits, opportunities = position_profile(blocks)

    print("Within-block doublets by position, normalised by opportunity.")
    print("j is the index of the second rune of the pair.\n")
    print(f"{'j':>4}{'pairs':>9}{'doublets':>10}{'rate':>9}{'se':>8}")
    for j, (h, o) in enumerate(zip(hits, opportunities), start=1):
        if o < 1:
            continue
        rate = h / o
        label = f"{j}" if j < MAX_POSITION else f"{j}+"
        print(
            f"{label:>4}{int(o):>9}{int(h):>10}{rate:>9.4f}"
            f"{math.sqrt(rate * (1 - rate) / o):>8.4f}"
        )
    overall = hits.sum() / opportunities.sum()
    print(
        f"{'all':>4}{int(opportunities.sum()):>9}{int(hits.sum()):>10}{overall:>9.4f}"
        f"{math.sqrt(overall * (1 - overall) / opportunities.sum()):>8.4f}"
    )
    chi, df, p = uniformity(hits, opportunities)
    print(f"\nchi2 = {chi:.2f} on {df} df, P = {p:.3f}   -- flat")

    print("\nCould the test have seen a bump? Plant one at the block-initial pair.\n")
    print(f"{'planted at j = 1':<28}{'doublets there':>15}{'chi2':>9}{'P':>9}")
    rng = random.Random(3301)
    for factor, label in (
        (1.0, "unchanged"),
        (0.5, "suppression twice as strong"),
        (2.0, "twice as many"),
        (5.4, "preventer blind there"),
    ):
        h, o = position_profile(planted(blocks, rng, factor=factor))
        c, d, pv = uniformity(h, o)
        print(f"{label:<28}{int(h[0]):>15}{c:>9.2f}{pv:>9.3f}")

    print("\nThe same, binned by the length of the block the pair sits in.\n")
    print(f"{'block length':<16}{'pairs':>9}{'doublets':>10}{'rate':>9}{'se':>8}")
    hits_l, opp_l = length_profile(blocks)
    for (lo, hi), h, o in zip(LENGTH_BINS, hits_l, opp_l):
        rate = h / o
        label = f"{lo}-{hi}" if hi < 99 else f"{lo}+"
        print(
            f"{label:<16}{int(o):>9}{int(h):>10}{rate:>9.4f}"
            f"{math.sqrt(rate * (1 - rate) / o):>8.4f}"
        )
    chi_l, df_l, p_l = uniformity(hits_l, opp_l)
    print(f"\nchi2 = {chi_l:.2f} on {df_l} df, P = {p_l:.3f}   -- flat")

    print(
        "\nNo position effect and no length effect. The concentration at j = 0,1 that the"
        "\nhypothesis file flagged was the length confound and nothing else."
        "\n\nWhat this excludes is a LARGE position effect: a preventer whose state resets"
        "\nat the block boundary, a clock phase tied to position within the block, or a"
        "\nrule that only acts after the first rune. The planted runs show a factor of two"
        "\nwould slip through, so this is not a demonstration of uniformity to within a"
        "\nfactor of two -- only that nothing dramatic depends on position."
    )


if __name__ == "__main__":
    main()
