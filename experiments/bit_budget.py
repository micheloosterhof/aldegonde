# ABOUTME: Totals what every measured channel supplies against what the key costs, and
# ABOUTME: corrects the cycle-structure result, which is 99.8% of the space and so vacuous.
"""The entropy check applied to the whole project rather than to one detector.

`d5-pattern-carries-no-identity.md` records the rule: before building a detector, compare
the entropy it supplies with the entropy needed. Run over every channel this directory
has measured, that check does two things. It totals the position, and it corrects one
result whose information content was computed against the wrong prior.

`d-profile-pins-g-to-five-cycles.md` filters a pool that is uniform over cycle counts
1 to 5. The real space is not: a permutation of 29 points with order 5 has five
five-cycles 99.8% of the time. So "g has five five-cycles" is almost the generic case,
and the filter's hundredfold reduction is partly the rejection of low-cycle g that the
real space barely contains.

Both are measured here rather than argued: the class sizes exactly, and the filter's
worth by ranking a planted g inside a pool drawn only from the realistic class.

    python bit_budget.py [--trials 6]
"""

from __future__ import annotations

import random
import sys
from math import comb, factorial, log2
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_constrains_g import chi2, lag_tables, measure, walk  # noqa: E402
from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, prose_corpora  # noqa: E402


def order5_count(k: int) -> int:
    """Permutations of 29 points with exactly k five-cycles."""
    return comb(M, 5 * k) * factorial(5 * k) // (5**k * factorial(k))


def pool_k5(n: int, seed: int):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        points = rng.sample(range(M), 25)
        g = list(range(M))
        for c in range(5):
            cycle = points[5 * c : 5 * c + 5]
            for i in range(5):
                g[cycle[i]] = cycle[(i + 1) % 5]
        out.append(g)
    return out


def main() -> None:
    trials = 6
    for i, a in enumerate(sys.argv):
        if a == "--trials" and i + 1 < len(sys.argv):
            trials = int(sys.argv[i + 1])

    total = sum(order5_count(k) for k in range(1, 6))
    print("the real prior over g's cycle structure\n")
    print(f"{'five-cycles':>12}{'permutations':>30}{'share':>10}")
    for k in range(1, 6):
        print(f"{k:>12}{order5_count(k):>30,}{order5_count(k) / total:>10.5f}")
    print(f"\nSo C-0 -- 'g has five five-cycles' -- is 99.8% of the space and worth "
          f"{log2(total / order5_count(5)):.4f} bits.")
    print("The result is real; its value as a search constraint is not. The filter's"
          "\nhundredfold reduction was measured on a pool uniform over cycle counts,"
          "\nwhich over-represents the 0.2% the real space barely contains.")

    prose = list(prose_corpora(2928, 60))
    mats, tot = lag_tables(prose)
    rk = random.Random(77)
    ranks = []
    print("\n\nthe filter's worth INSIDE the realistic class\n")
    print(f"{'trial':>6}{'rank of the planted g in 6,000 five-cycle permutations':>58}")
    for t in range(trials):
        g = order5_fixing(rk.sample(range(M), 4), rk)
        sigma = rk.sample(range(M), M)
        m = measure(walk(g, sigma, prose[t], random.Random(1)))
        pool = pool_k5(6000, 100 + t)
        scores = np.array([chi2(h, m, mats, tot) for h in pool])
        rank = int((scores < chi2(g, m, mats, tot)).sum())
        ranks.append(rank + 1)
        print(f"{t:>6}{f'{rank} / 6,000   (top {100 * rank / 6000:.2f}%)':>58}")
    median = float(np.median(ranks))
    worth = log2(6000 / median)
    print(f"\nmedian rank {median:.0f} of 6,000 -> about {worth:.1f} bits, and unreliable:"
          f"\n{sum(1 for r in ranks if r > 120)} of {trials} trials put the true g "
          f"outside the top 2%.")

    key = log2(order5_count(5)) + 2 * log2(factorial(M) // 2)
    print(f"\n\nthe budget\n")
    print(f"{'part of the key':<34}{'bits':>8}{'channel':>26}{'supplied':>10}")
    print(f"{'g (five-cycle class)':<34}{log2(order5_count(5)):>8.1f}"
          f"{'d-profile filter':>26}{worth:>10.1f}")
    print(f"{'sigma (A29)':<34}{log2(factorial(M) // 2):>8.1f}"
          f"{'cross-seam cells':>26}{'< 10':>10}")
    print(f"{'base_0 (A29)':<34}{log2(factorial(M) // 2):>8.1f}{'none':>26}{'0':>10}")
    print(f"{'total':<34}{key:>8.0f}{'':>26}{f'{worth + 10:.0f} at best':>10}")
    print(
        f"\nSo the statistical channels reach {(worth + 10) / key:.1%} of the key, and the"
        "\nlargest part of it -- the starting base, 102 bits -- has no channel at all,"
        "\nsince every block draws its own alphabet and nothing accumulates across them."
        "\n\nThe cross-seam figure is the optimistic one: it exists only under a"
        "\nright-acting base step, which `the-base-step-may-act-on-the-left.md` leans"
        "\nagainst at about two sigma. Under a left action that column is zero too."
        "\n\nThat is the case for a search that DECRYPTS rather than one that measures."
    )


if __name__ == "__main__":
    main()
