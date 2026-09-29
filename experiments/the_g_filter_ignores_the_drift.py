# ABOUTME: Shows the d-profile filter on g compares observed rates against undrifted
# ABOUTME: predictions, measures the bias that introduces, and supplies the correction.
"""The filter that supplies g's 16 bits does not model the preventer's clock drift.

`d_profile_constrains_g.py` scores a candidate `g` by

    chi2 = sum over k of ((observed d_k - m_k(g)) / se)^2,  m_k(g) = P(p_i = g^(k mod 5)(p_(i+k)))

and `key-local-channel-is-empty.md` reports that 46 of 3,000,000 random order-5
permutations pass all seven lags at 2 sigma, a 65,000-fold cut worth **16.0 bits** against
g's 79.7. Every sweep costed against that number inherits it.

The predictor is wrong in a way that grows with k. The doublet preventer advances the
clock by one extra step whenever it fires. A distance-k pair keeps its phase relation only
if no firing falls between the two runes, so with a firing rate q per position

    E[d_k]  =  (1-q)^k * m_k(g)  +  (1 - (1-q)^k) * (1/29)

The observed rate is pulled towards chance, by 6% at k = 2 and **22% at k = 7** for
q = 0.034. Comparing it with the undrifted m_k(g) therefore prefers candidates whose true
masses are closer to 1/29 than the real key's, and rejects the real key when its masses
are extreme -- which is exactly the case the filter exists to find.

This measures the size of that error rather than assuming it matters.

## Method

Plant a known `g`, encipher prose with the walk and a preventer at rate q, and read the
profile back. Score the planted `g` against a pool of random ones under both predictors
and record where the true key ranks. A correct filter puts it near the top.

## Result: the omission is real and the bias is small

**How far the drift moves a prediction, at q = 0.034:**

| distance | fraction of pairs keeping their phase | a mass of 0.050 reads as |
|---|---|---|
| 2 | 0.933 | 0.0490 |
| 3 | 0.901 | 0.0485 |
| 4 | 0.871 | 0.0480 |
| 6 | 0.813 | 0.0471 |
| 7 | 0.785 | 0.0467 |

The largest shift is 0.0033 at distance 7, against an observed standard error of 0.0075
there. **The bias is under half a standard error at every distance**, which is why it does
not matter despite being a genuine model error.

**Planting a known g and asking where it ranks in a pool of 4,000:**

| preventer phi | measured firing rate | uncorrected | corrected |
|---|---|---|---|
| 0.0 | 0.0000 | 0.061 | 0.061 |
| 0.5 | 0.0164 | 0.072 | 0.066 |
| 0.9 | 0.0295 | 0.077 | 0.070 |
| 1.0 | 0.0328 | 0.079 | 0.072 |

The preventer costs the filter a little power -- the true key slips from the top 6.1% to
the top 7.7% -- and the correction recovers about half of that. Neither number changes
what the filter can do.

**On the body:** survivors of 4,000 at 2 sigma on all five lags are 29, 29, 30 and 35 for
q = 0, 0.020, 0.034 and 0.050, that is 7.11, 7.11, 7.06 and 6.84 bits. The admitted set
barely moves.

(These 7.1 bits are not the 16.0 of `key-local-channel-is-empty.md`. That figure uses
seven lags and a pool of 3,000,000; a pool of 4,000 cannot resolve a 16-bit cut, so 7.1 is
a floor set by the pool size and the two are consistent.)

## Conclusion

The correction is supplied here and should be used, since it costs nothing. **It does not
change any published number and no result needs revising.** The worth of this file is that
the doubt is now measured rather than outstanding: a sweep costed against the d-profile
filter is not searching a biased region.

## What would make it matter

A larger firing rate, a longer usable distance, or a smaller standard error. The bias
scales as `1 - (1-q)^k`, so a corpus with blocks long enough to use distances 10 and
beyond would need it -- but the body has only 88 pairs at distance 10 and 10 at distance
12, so that case does not arise here.

    python the_g_filter_ignores_the_drift.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_constrains_g import (  # noqa: E402
    LAGS,
    lag_tables,
    make_pool,
    measure,
    predict,
)
from fingerprint_battery import M, compose, lp_words, ppow, prose_corpora  # noqa: E402

PHI = 0.90
CHANCE = 1.0 / M
POOL = 4000
PLANTS = 8
DRIFTS = (0.0, 0.02, 0.034, 0.05)
PHIS = (0.0, 0.5, 0.9, 1.0)


def drifted(mass: float, k: int, q: float) -> float:
    """What a distance-k rate becomes when a firing rate q perturbs the clock."""
    keep = (1.0 - q) ** k
    return keep * mass + (1.0 - keep) * CHANCE


def encipher_with_preventer(plain, g, rng, phi=PHI):
    """The length-clocked walk; on an adjacent repeat the clock takes an extra step."""
    powers = [ppow(g, k) for k in range(5)]
    sigma = rng.sample(range(M), M)
    base = rng.sample(range(M), M)
    clock, previous, fired, positions = 0, None, 0, 0
    out = []
    for word in plain:
        block = []
        for p in word:
            c = base[powers[clock % 5][p]]
            if c == previous and rng.random() < phi:
                clock += 1
                c = base[powers[clock % 5][p]]
                fired += 1
            block.append(c)
            previous = c
            clock += 1
            positions += 1
        out.append(block)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
    return out, fired / positions


def chi2(g, meas, mats, tot, q) -> float:
    return sum(
        ((meas[k][0] - drifted(predict(g, k, mats, tot), k, q)) / meas[k][1]) ** 2
        for k in LAGS
    )


def rank_of(truth, pool, meas, mats, tot, q) -> float:
    """Where the true g sits among the pool, as a percentile; 0 is best."""
    mine = chi2(truth, meas, mats, tot, q)
    better = sum(1 for g in pool if chi2(g, meas, mats, tot, q) < mine)
    return better / len(pool)


def main() -> None:
    corpora = prose_corpora(4000, 6)
    mats, tot = lag_tables(corpora)
    pool = make_pool(POOL, 11)

    print("How much the drift pulls each distance towards chance, at q = 0.034.\n")
    print(f"{'distance':>10}{'kept':>9}{'a mass of 0.050 reads as':>28}")
    for k in LAGS:
        print(f"{k:>10}{(1 - 0.034) ** k:>9.3f}{drifted(0.050, k, 0.034):>28.4f}")

    print("\nPlanting a known g, enciphering with a preventer, and asking where the")
    print("true key ranks in a pool of 4,000. Lower is better; 0.5 is useless.\n")
    print(
        f"{'preventer phi':<16}{'firing rate':>13}{'uncorrected':>14}{'corrected':>12}"
    )
    for phi in PHIS:
        raw, fixed, seen = [], [], []
        for t in range(PLANTS):
            rng = random.Random(500 + t)
            truth = make_pool(1, 900 + t)[0]
            plain = prose_corpora(2900, 1)[0]
            cipher, rate = encipher_with_preventer(plain, truth, rng, phi)
            meas = measure(cipher)
            seen.append(rate)
            raw.append(rank_of(truth, pool, meas, mats, tot, 0.0))
            fixed.append(rank_of(truth, pool, meas, mats, tot, rate))
        print(
            f"{phi:<16.1f}{np.mean(seen):>13.4f}"
            f"{np.mean(raw):>14.3f}{np.mean(fixed):>12.3f}"
        )

    print("\nThe body, scored both ways. Survivors at 2 sigma on all five lags.\n")
    body = lp_words()
    meas = measure(body)
    print(f"{'assumed firing rate':<24}{'survivors of 4,000':>20}{'bits':>8}")
    for q in DRIFTS:
        keep = [
            g
            for g in pool
            if all(
                abs(meas[k][0] - drifted(predict(g, k, mats, tot), k, q))
                <= 2 * meas[k][1]
                for k in LAGS
            )
        ]
        bits = math.log2(len(pool) / len(keep)) if keep else float("inf")
        print(f"{f'q = {q:.3f}':<24}{len(keep):>20}{bits:>8.2f}")


if __name__ == "__main__":
    main()
