# ABOUTME: Tests the full 29x29 table of (c_i, c_(i+5)) for any relation other than equality,
# ABOUTME: within words, across words and on the whole stream, against a pairing-shuffle null.
"""Is there anything at lag 5 besides "the same rune"?

Every structured alternative to equality at lag 5 -- a shift, an affine map, a subgroup
coset -- is on record as flat, and under the walk the orbit theorem says nothing but
equality can survive a per-word base. What was never run is the unstructured test: the
full 29x29 contingency table of (c_i, c_(i+5)) restricted to within-word pairs. It was
skipped because 2,073 pairs over 784 cells is thin. This file runs it anyway, with a
permutation null so the thinness is priced rather than assumed away.

Four readings of each table, in three scopes (within-word, cross-word, whole stream):

1. independence chi-square over all cells;
2. the same over the off-diagonal cells only, which removes the known echo;
3. the best off-diagonal relation: the permutation maximising the mass of pairs with
   c_i = pi(c_(i+5)) once the diagonal is zeroed, the concentrated test for "some other
   fixed relation";
4. the top off-diagonal cells individually, Bonferroni over 812.

The null shuffles the second rune across pairs, which keeps both marginals and the pair
count and breaks only the pairing. Within-word pairs use the same parse as
`within_word_d5.py`, so the diagonal reproduces its 102 of 2,073.

    python experiments/lag5_full_table.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
from scipy.stats import poisson

from aldegonde import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from within_word_d5 import M, parse_clean_sections  # noqa: E402

LAG = 5
TRIALS = 4000
SEED = 20261026

Pair = tuple[int, int]


def pairs_by_scope(sections) -> tuple[list[Pair], list[Pair], list[Pair]]:
    """(within, cross, whole) lists of (c_i, c_(i+5)) over each section's rune stream."""
    within: list[Pair] = []
    cross: list[Pair] = []
    whole: list[Pair] = []
    for words in sections:
        stream = [r for w in words for r in w]
        owner = [k for k, w in enumerate(words) for _ in w]
        for i in range(len(stream) - LAG):
            pair = (stream[i], stream[i + LAG])
            whole.append(pair)
            (within if owner[i] == owner[i + LAG] else cross).append(pair)
    return within, cross, whole


def table(pairs: list[Pair]) -> np.ndarray:
    return stats.pair_counts([[u, v] for u, v in pairs], M, lag=1)


def shuffle_pairing(pairs: list[Pair], rng: random.Random) -> list[Pair]:
    second = [v for _, v in pairs]
    rng.shuffle(second)
    return [(u, v) for (u, _), v in zip(pairs, second)]


def chi2_all(pairs: list[Pair]) -> float:
    return stats.independence(table(pairs)).chi2


def chi2_offdiag(pairs: list[Pair]) -> float:
    return stats.independence(table(pairs), off_diagonal=True).chi2


def best_offdiag_relation(pairs: list[Pair]) -> float:
    """Largest number of pairs any one fixed-point-free relation collects."""
    t = table(pairs).astype(float)
    np.fill_diagonal(t, 0)
    return stats.extremal_relation_rate(t, maximize=True).rate * t.sum()


def report(name: str, pairs: list[Pair], rng: random.Random) -> None:
    t = table(pairs)
    n = len(pairs)
    diag = int(np.trace(t))
    print(
        f"\n== {name}: {n} pairs, diagonal {diag} ({diag / n:.4f}, chance {1 / M:.4f})"
    )
    print(
        f"{'statistic':<24}{'observed':>10}{'null mean':>11}{'sd':>8}{'z':>7}{'P(>=)':>8}"
    )
    for label, statistic in (
        ("chi2 all cells", chi2_all),
        ("chi2 off-diagonal", chi2_offdiag),
        ("best off-diag relation", best_offdiag_relation),
    ):
        r = stats.monte_carlo(statistic, shuffle_pairing, pairs, trials=TRIALS, rng=rng)
        print(
            f"{label:<24}{r.observed:>10.1f}{r.null_mean:>11.1f}{r.null_sd:>8.1f}"
            f"{r.z:>7.2f}{r.p_upper:>8.4f}"
        )

    e = np.outer(t.sum(1), t.sum(0)) / t.sum()
    cells = [
        (int(t[i, j]), e[i, j], i, j) for i in range(M) for j in range(M) if i != j
    ]
    cells.sort(key=lambda c: poisson.sf(c[0] - 1, c[1]))
    print("top off-diagonal cells (Poisson tail, Bonferroni over 812):")
    for count, exp, i, j in cells[:5]:
        p = poisson.sf(count - 1, exp)
        print(
            f"  ({i:>2},{j:>2}) {count:>3} vs {exp:5.1f}  p={p:.2e}  x812={min(1, p * 812):.3f}"
        )


def main() -> None:
    rng = random.Random(SEED)
    within, cross, whole = pairs_by_scope(
        parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    )
    for name, pairs in (
        ("within-word", within),
        ("cross-word", cross),
        ("whole stream", whole),
    ):
        report(name, pairs, rng)


if __name__ == "__main__":
    main()
