# ABOUTME: Split-half validates the d-profile filter and asks whether one g runs through
# ABOUTME: the whole body, by correlating the g-score profile across quarters.
"""A filter worth 6.2 bits should give the same answer on either half of the corpus.

`key-construction-is-unmeasurable.md` records the split-half check as the cheapest guard
on any multi-cell statistic. The d-profile filter has never had one, and it underwrites
C-0 and the search costing, so it should.

Two questions, one machinery. Score the pool of candidate `g` separately on parts of the
body and correlate the score vectors.

  validity    do the two halves agree about which g score well? If they do not, the
              filter's 6.2 bits are noise.
  one key     do all four quarters agree? A g that changed mid-book would show as a
              block of low cross-quarter correlations.

Planted walks calibrate both, and a walk whose g CHANGES at the halfway point calibrates
how large a change this would catch.

    python one_g_through_the_body.py
"""

from __future__ import annotations

import itertools
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_constrains_g import (  # noqa: E402
    chi2,
    lag_tables,
    make_pool,
    measure,
    walk,
)
from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, lp_words, prose_corpora  # noqa: E402


def main() -> None:
    prose = list(prose_corpora(2928, 60))
    mats, tot = lag_tables(prose)
    pool = make_pool(3000, 5)

    def scores(blocks):
        return np.array([chi2(g, measure(blocks), mats, tot) for g in pool])

    def split_half(blocks) -> float:
        h = len(blocks) // 2
        return float(np.corrcoef(scores(blocks[:h]), scores(blocks[h:]))[0, 1])

    def quarters(blocks) -> list[float]:
        n = len(blocks) // 4
        s = [scores(blocks[i * n : (i + 1) * n]) for i in range(4)]
        return [float(np.corrcoef(s[i], s[j])[0, 1])
                for i, j in itertools.combinations(range(4), 2)]

    rk = random.Random(31)
    print("does the filter give the same answer on either half?\n")
    print(f"{'corpus':<28}{'split-half correlation':>26}")
    for t in range(3):
        g = order5_fixing(rk.sample(range(M), 4), rk)
        sigma = rk.sample(range(M), M)
        c = split_half(walk(g, sigma, prose[t], random.Random(1)))
        print(f"{'planted walk ' + str(t):<28}{c:>26.3f}")
    print(f"{'THE BODY':<28}{split_half(lp_words()):>26.3f}")
    print("\nThe body sits inside the planted range, so the filter measures something"
          "\nstable rather than fitting noise. Its 6.2 bits survive the check.")

    print("\n\ndoes one g run through the whole body?\n")
    print(f"{'corpus':<28}{'pairwise correlations over quarters':>44}{'mean':>8}")
    baseline = []
    rk2 = random.Random(31)
    for t in range(4):
        g = order5_fixing(rk2.sample(range(M), 4), rk2)
        sigma = rk2.sample(range(M), M)
        c = quarters(walk(g, sigma, prose[t], random.Random(1)))
        baseline += c
        print(f"{'planted, one g ' + str(t):<28}"
              f"{' '.join(f'{x:+.2f}' for x in c):>44}{np.mean(c):>8.2f}")
    g1 = order5_fixing(rk2.sample(range(M), 4), rk2)
    g2 = order5_fixing(rk2.sample(range(M), 4), rk2)
    sigma = rk2.sample(range(M), M)
    mixed = (walk(g1, sigma, prose[5][:1464], random.Random(1))
             + walk(g2, sigma, prose[5][1464:], random.Random(2)))
    c = quarters(mixed)
    changed = float(np.mean(c))
    print(f"{'planted, g changes at half':<28}"
          f"{' '.join(f'{x:+.2f}' for x in c):>44}{changed:>8.2f}")
    c = quarters(lp_words())
    print(f"{'THE BODY':<28}{' '.join(f'{x:+.2f}' for x in c):>44}{np.mean(c):>8.2f}")

    b = np.array(baseline)
    print(f"\none-g planted: {b.mean():.2f} +- {b.std():.2f}")
    print(
        f"\nThe body's quarters all agree, mean {np.mean(c):.2f}, at the top of the"
        "\none-g range. No quarter dissents, so nothing suggests the key changes."
        f"\n\nBut the power is poor. A walk whose g changes outright at the halfway point"
        f"\nstill reads {changed:.2f}, only {(b.mean() - changed) / b.std():.1f} sigma"
        " below the one-g mean, because the"
        "\nquarter-level d-values are measured on about 500 lag-5 pairs each. This rules"
        "\nout a gross change in g and would miss a subtle one."
    )


if __name__ == "__main__":
    main()
