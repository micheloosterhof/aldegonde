# ABOUTME: Tests whether the letter step changes at any point in the body, not only at the
# ABOUTME: midpoint, by scoring d-profile heterogeneity across several segments.
"""A midpoint test is blind to a change at a quarter point.

`does_g_change_mid_book.py` splits the body in half and compares the two d-profiles,
getting chi2 6.9 on 5 df and a likelihood ratio of about 5 to 1 for one letter step. That
is the right statistic for the question it asks, and the question is narrow: **a change at
any other point is diluted.** If g changed a quarter of the way in, three quarters of the
corpus shares one step and the halves differ by only a fraction of the true gap.

Every pooled result in this directory spans the whole body, so "one g throughout" needs
testing throughout.

## The statistic

Split the body into k segments of equal block count. For each of the five usable lags,
the segments give a k x 2 table of coincidences against trials, and a heterogeneity chi2
on k-1 degrees of freedom. Summing over the lags gives 5(k-1) df and uses every pair
rather than the difference between two aggregates.

Both arms are planted: one g throughout, and g changing once at a point drawn uniformly
inside the corpus rather than at the midpoint, which is the case the existing test cannot
see.

## Result: nothing at any split

| segments | df | the body | planted one g | planted a change | LR for one g |
|---|---|---|---|---|---|
| 2 | 5 | 6.9 | 7.7 | 14.0 | 2.5 |
| 3 | 10 | 9.7 | 10.6 | 24.8 | 2.2 |
| 4 | 15 | 19.6 | 18.9 | 30.2 | 4.3 |
| 6 | 25 | 36.6 | 31.7 | 45.6 | 4.0 |

**The body sits on the one-g arm at every split** and below the changed arm at every
split. The k = 2 cell reproduces `does_g_change_mid_book.py` exactly at 6.9, which is the
consistency check that matters since the two files share no code beyond the lag list.

The likelihood ratios are 2.2 to 4.3 and should not be multiplied together: the four
splits use the same 2,928 blocks and are heavily correlated. Taken singly the strongest is
4.3 to 1 at four segments.

## Why the ratios stay modest

The planted-change arm is skewed, as the midpoint file already records: two random order-5
permutations sometimes give similar d-profiles by chance, so a fraction of changed-key
trials land as low as the body does however clean the data is. That caps the achievable
ratio regardless of corpus size, which is a property of the statistic and not of this
corpus.

## What it adds

`does_g_change_mid_book.py` tests the midpoint only, and a change at a quarter point
leaves three quarters of the corpus sharing one step, so the halves differ by a fraction
of the true gap. Splitting into three, four and six segments covers changes anywhere and
finds none. Every pooled result in this directory spans the whole body, so this is the
assumption they all rest on, tested where it is actually used.

    python does_g_change_anywhere.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_constrains_g import LAGS, make_pool, walk  # noqa: E402
from fingerprint_battery import M, lp_words, prose_corpora  # noqa: E402

SEGMENTS = (2, 3, 4, 6)
TRIALS = 24


def counts(blocks):
    """{lag: (hits, trials)} over within-block pairs."""
    out = {}
    for k in LAGS:
        hits = pairs = 0
        for w in blocks:
            for i in range(len(w) - k):
                pairs += 1
                hits += w[i] == w[i + k]
        out[k] = (hits, pairs)
    return out


def heterogeneity(blocks, k: int) -> tuple[float, int]:
    """Summed chi2 for equal coincidence rates across k equal segments."""
    step = len(blocks) // k
    parts = [blocks[i * step : (i + 1) * step] for i in range(k)]
    total_chi, df = 0.0, 0
    for lag in LAGS:
        table = []
        for part in parts:
            hits, pairs = counts(part)[lag]
            if pairs < 40:
                continue
            table.append([hits, pairs - hits])
        if len(table) < 2:
            continue
        arr = np.array(table, float)
        if arr[:, 0].sum() < 5:
            continue
        chi, _, dof, _ = stats.chi2_contingency(arr, correction=False)
        total_chi += float(chi)
        df += dof
    return total_chi, df


def planted(n_blocks, rng, *, change_at=None):
    plain = prose_corpora(n_blocks, 1)[0]
    sigma = rng.sample(range(M), M)
    g1 = make_pool(1, rng.randrange(10**6))[0]
    if change_at is None:
        return walk(g1, sigma, plain, rng)
    cut = int(n_blocks * change_at)
    g2 = make_pool(1, rng.randrange(10**6))[0]
    return walk(g1, sigma, plain[:cut], rng) + walk(g2, sigma, plain[cut:], rng)


def main() -> None:
    body = lp_words()
    print(f"{len(body):,} body blocks. Heterogeneity chi2 across equal segments.\n")
    print(f"{'segments':>9}{'df':>5}{'the body':>11}{'one g':>18}{'g changes once':>20}{'LR':>8}")
    for k in SEGMENTS:
        obs, df = heterogeneity(body, k)
        arms = {}
        for label in ("one", "change"):
            vals = []
            for t in range(TRIALS):
                r = random.Random(500 + t)
                where = None if label == "one" else r.uniform(0.2, 0.8)
                blocks = planted(len(body), r, change_at=where)
                vals.append(heterogeneity(blocks, k)[0])
            arms[label] = np.array(vals)
        a = max(float((arms["one"] <= obs).mean()), 1 / TRIALS)
        b = max(float((arms["change"] <= obs).mean()), 1 / TRIALS)
        print(
            f"{k:>9}{df:>5}{obs:>11.1f}"
            f"{np.median(arms['one']):>18.1f}{np.median(arms['change']):>20.1f}"
            f"{a / b:>8.1f}"
        )

    print(
        "\n  LR is for one letter step over a single change at a uniformly drawn point."
        "\n  The planted-change arm is skewed: two random order-5 permutations sometimes"
        "\n  give similar d-profiles, which caps the ratio however clean the data is."
    )


if __name__ == "__main__":
    main()
