# ABOUTME: Uses the body's within-block coincidence profile as a key-free filter on g,
# ABOUTME: validated by planted controls, and reads off g's cycle structure.
"""Every lag except 5 measures the plaintext through a power of g.

Inside a block the alphabet at position j is `base o g^(c+j)`, so for a lag-k pair

    c_i = c_(i+k)   <=>   g^(c+i)(p_i) = g^(c+i+k)(p_(i+k))   <=>   p_i = g^k(p_(i+k))

and since `g` has order 5 only `k mod 5` matters. The base drops out entirely. So

    d_k  =  P(p_i = g^(k mod 5)(p_(i+k)))

is a function of the PLAINTEXT and of `g` alone -- no base, no sigma, no key. At k = 5
the power is the identity and d5 is the plaintext's own coincidence, which is what makes
it the leak. At every other k it is a measurement of g.

Five lags are usable: 2, 3, 4, 6 and 7. Lag 1 is spoiled because the preventer suppresses
adjacent repeats, and lag 5 carries no g.

The filter scores a pool of random order-5 permutations by how well their predicted
profile matches the body's. Absolute chi2 is contaminated by model error -- the plaintext
lag-k tables come from prose, not from the body's own plaintext -- so the valid output is
a RANK, and planted controls calibrate it.

    python d_profile_constrains_g.py [--pool 6000]
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import M, compose, lp_words, ppow, prose_corpora  # noqa: E402

LAGS = (2, 3, 4, 6, 7)


def lag_tables(corpora) -> tuple[dict[int, np.ndarray], dict[int, float]]:
    mats = {k: np.zeros((M, M)) for k in LAGS}
    for c in corpora:
        for w in c:
            for k in LAGS:
                for i in range(len(w) - k):
                    mats[k][w[i], w[i + k]] += 1
    return mats, {k: float(mats[k].sum()) for k in LAGS}


def inverse(p):
    q = [0] * M
    for i, x in enumerate(p):
        q[x] = i
    return q


def predict(g, k: int, mats, tot) -> float:
    """P(p_i = g^(k mod 5)(p_(i+k))) under the plaintext tables."""
    back = inverse(ppow(g, k % 5))
    return sum(mats[k][x, back[x]] for x in range(M)) / tot[k]


def measure(words) -> dict[int, tuple[float, float]]:
    out = {}
    for k in LAGS:
        hits = pairs = 0
        for w in words:
            for i in range(len(w) - k):
                pairs += 1
                hits += w[i] == w[i + k]
        r = hits / pairs
        out[k] = (r, math.sqrt(r * (1 - r) / pairs))
    return out


def chi2(g, meas, mats, tot) -> float:
    return sum(
        ((meas[k][0] - predict(g, k, mats, tot)) / meas[k][1]) ** 2 for k in LAGS
    )


def make_pool(n: int, seed: int) -> list[list[int]]:
    """Order-5 permutations with 1 to 5 five-cycles, uniformly over the count."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        k = rng.randint(1, 5)
        points = rng.sample(range(M), 5 * k)
        g = list(range(M))
        for c in range(k):
            cycle = points[5 * c : 5 * c + 5]
            for i in range(5):
                g[cycle[i]] = cycle[(i + 1) % 5]
        out.append(g)
    return out


def walk(g, sigma, plain, rng):
    gp = [ppow(g, i) for i in range(5)]
    base = rng.sample(range(M), M)
    out, clock = [], 0
    for word in plain:
        cw = []
        for p in word:
            cw.append(base[gp[clock % 5][p]])
            clock += 1
        out.append(cw)
        base = compose(base, compose(gp[(clock - 1) % 5], sigma))
    return out


def cycles(g) -> int:
    return sum(1 for x in range(M) if g[x] != x) // 5


def main() -> None:
    size = 6000
    for i, a in enumerate(sys.argv):
        if a == "--pool" and i + 1 < len(sys.argv):
            size = int(sys.argv[i + 1])

    prose = list(prose_corpora(2928, 60))
    mats, tot = lag_tables(prose)
    pool = make_pool(size, 5)
    counts = np.array([cycles(g) for g in pool])

    print(
        f"pool of {size:,} order-5 permutations, five-cycle counts "
        f"{np.bincount(counts, minlength=6)[1:]}\n"
    )

    print("planted controls: encipher prose with a known g and see whether the top 1%")
    print("by chi2 recovers its cycle structure.\n")
    print(
        f"{'true k':>7}{'rank of the true g':>21}"
        f"{'five-cycle counts in the top 1%':>36}"
    )
    rng = random.Random(51)
    for true_k in (1, 3, 5):
        points = rng.sample(range(M), 5 * true_k)
        g = list(range(M))
        for c in range(true_k):
            cycle = points[5 * c : 5 * c + 5]
            for i in range(5):
                g[cycle[i]] = cycle[(i + 1) % 5]
        sigma = rng.sample(range(M), M)
        cipher = []
        for c in prose[:2]:
            cipher += walk(g, sigma, c, random.Random(1))
        meas = measure(cipher)
        scores = np.array([chi2(h, meas, mats, tot) for h in pool])
        top = scores <= np.percentile(scores, 1)
        rank = int((scores < chi2(g, meas, mats, tot)).sum())
        print(
            f"{true_k:>7}{f'{rank}/{size}':>21}"
            f"{str(np.bincount(counts[top], minlength=6)[1:]):>36}"
        )
    print("\nThe top-1% profile tracks the truth, and the filter sharpens as g moves")
    print("more points: a g with one five-cycle is nearly the identity and many others")
    print("mimic it.")

    meas = measure(lp_words())
    print(f"\n\nthe body's profile (chance {1 / M:.4f}):\n")
    print(f"{'lag':>4}{'g power':>9}{'measured':>20}{'pool prediction':>26}")
    for k in LAGS:
        v = np.array([predict(g, k, mats, tot) for g in pool])
        print(
            f"{k:>4}{k % 5:>9}{f'{meas[k][0]:.4f} +- {meas[k][1]:.4f}':>20}"
            f"{f'{v.mean():.4f} +- {v.std():.4f}':>26}"
        )

    scores = np.array([chi2(g, meas, mats, tot) for g in pool])
    print(
        f"\nchi2 over the pool: min {scores.min():.1f}, median {np.median(scores):.1f}"
    )
    for pct in (1, 5):
        keep = scores <= np.percentile(scores, pct)
        print(
            f"  top {pct}% ({int(keep.sum())} permutations, "
            f"{100 // pct}x reduction): five-cycle counts "
            f"{np.bincount(counts[keep], minlength=6)[1:]}"
        )
    print(
        "\nThe body's top 1% is concentrated on five five-cycles, matching the k=5"
        "\ncontrol almost exactly. So g fixes 4 of the 29 runes and moves the other 25."
        "\n\nThe reason is plain in the table: the body's d-values at lags 2, 3, 4, 6 and 7"
        "\nsit much closer to chance than the plaintext's do, so g has to move enough"
        "\npoints to destroy the plaintext's lag-k structure. A g with one five-cycle"
        "\nleaves most of it intact and predicts values far too high."
    )


if __name__ == "__main__":
    main()
