# ABOUTME: Tests the full 29x29 table of (c_i, c_(i+k)) for any relation other than equality,
# ABOUTME: within words, across words and on the whole stream, against a pairing-shuffle null.
"""Is there anything at lag k besides "the same rune"?

Every structured alternative to equality -- a shift, an affine map, a subgroup coset -- is
on record as flat at lags 1-5, and under the walk the orbit theorem says nothing but
equality can survive a per-word base. What was never run is the unstructured test: the
full 29x29 contingency table of (c_i, c_(i+k)) restricted to within-word pairs. At lag 5
it was skipped because 2,073 pairs over 784 cells is thin. This file runs it anyway, at
any lag, with a permutation null so the thinness is priced rather than assumed away.

Four readings of each table, in three scopes (within-word, cross-word, whole stream):

1. independence chi-square over all cells;
2. the same over the off-diagonal cells only, which removes the known diagonal;
3. the best off-diagonal relation: the permutation maximising the mass of pairs with
   c_i = pi(c_(i+k)) once the diagonal is zeroed, the concentrated test for "some other
   fixed relation";
4. the top off-diagonal cells individually, Bonferroni over 812.

The null shuffles the second rune across pairs, which keeps both marginals and the pair
count and breaks only the pairing. Within-word pairs use the same parse as
`within_word_d5.py`, so at lag 5 the diagonal reproduces its 102 of 2,073.

`seam_reach_tables.py` and `lag5_match_conditional_table.py` reuse the machinery here.

    python experiments/lag_full_table.py [--lag 5] [--trials 4000]
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import numpy as np
from scipy.stats import poisson

from aldegonde import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from within_word_d5 import M, parse_clean_sections  # noqa: E402

SEED = 20261026

# a pair set is an integer array of shape (n, 2): (c_i, c_(i+k))
Pairs = np.ndarray


def load_sections():
    return parse_clean_sections(str(ROOT / "data/page0-56.txt"))


def pairs_by_scope(sections, lag: int) -> tuple[Pairs, Pairs, Pairs]:
    """(within, cross, whole) pair sets of (c_i, c_(i+lag)) over each section's stream."""
    within, cross, whole = [], [], []
    for words in sections:
        stream = [r for w in words for r in w]
        owner = [k for k, w in enumerate(words) for _ in w]
        for i in range(len(stream) - lag):
            pair = (stream[i], stream[i + lag])
            whole.append(pair)
            (within if owner[i] == owner[i + lag] else cross).append(pair)
    return np.array(within), np.array(cross), np.array(whole)


def table(pairs: Pairs) -> np.ndarray:
    t = np.zeros((M, M))
    np.add.at(t, (pairs[:, 0], pairs[:, 1]), 1)
    return t


def shuffle_pairing(pairs: Pairs, rng: random.Random) -> Pairs:
    out = pairs.copy()
    out[:, 1] = np.random.default_rng(rng.getrandbits(64)).permutation(out[:, 1])
    return out


def chi2_all(pairs: Pairs) -> float:
    return stats.independence(table(pairs)).chi2


def chi2_offdiag(pairs: Pairs) -> float:
    return stats.independence(table(pairs), off_diagonal=True).chi2


def best_offdiag_relation(pairs: Pairs) -> float:
    """Largest number of pairs any one fixed-point-free relation collects."""
    t = table(pairs)
    np.fill_diagonal(t, 0)
    return stats.extremal_relation_rate(t, maximize=True).rate * t.sum()


STATISTICS = (
    ("chi2 all cells", chi2_all),
    ("chi2 off-diagonal", chi2_offdiag),
    ("best off-diag relation", best_offdiag_relation),
)


def compare(
    pairs: Pairs, rng: random.Random, trials: int
) -> dict[str, stats.NullComparison]:
    return {
        label: stats.monte_carlo(
            statistic, shuffle_pairing, pairs, trials=trials, rng=rng
        )
        for label, statistic in STATISTICS
    }


def report(name: str, pairs: Pairs, rng: random.Random, trials: int) -> None:
    t = table(pairs)
    n = len(pairs)
    diag = int(np.trace(t))
    print(
        f"\n== {name}: {n} pairs, diagonal {diag} ({diag / n:.4f}, chance {1 / M:.4f})"
    )
    print(
        f"{'statistic':<24}{'observed':>10}{'null mean':>11}{'sd':>8}{'z':>7}{'P(>=)':>8}"
    )
    for label, r in compare(pairs, rng, trials).items():
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--lag", type=int, default=5)
    ap.add_argument("--trials", type=int, default=4000)
    args = ap.parse_args()
    rng = random.Random(SEED)
    within, cross, whole = pairs_by_scope(load_sections(), args.lag)
    print(f"lag {args.lag}")
    for name, pairs in (
        ("within-word", within),
        ("cross-word", cross),
        ("whole stream", whole),
    ):
        report(name, pairs, rng, args.trials)


if __name__ == "__main__":
    main()
