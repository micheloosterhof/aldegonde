#!/usr/bin/env python3
# ABOUTME: Corrected cycle-census analysis: real-word K_d baselines (not
# ABOUTME: random stream segments) and diagonal tuning at the LP-implied level
# ABOUTME: (not the annealing floor). Supersedes the numbers in census_scan /
# ABOUTME: census_walk_sim where they differ.
"""Cycle census analysis, corrected.

Two flaws in the first pass (census_scan.py, census_walk_sim.py):
  1. K_d was measured on prose cut into LP word lengths at RANDOM
     offsets — arbitrary segments whose statistics approach the
     unconditional stream coincidence, not real within-word rates.
     Here the reference corpus is REAL prose word tokens sampled by
     length to match the LP word-length sequence, so morphology aligns
     with boundaries. The same corpus is the simulation plaintext.
  2. Diagonals were annealed to their floors (~0.0023) where the LP
     implies ~0.006; the d6 dip depth scales with tuning depth, so
     floor-tuning overstated the dip. Here the anneal targets the
     LP-implied level.

Outputs: corrected K_d and phi ladder, corrected census scan leaders,
and corrected full-battery walk simulations for the candidate censuses.
"""

from __future__ import annotations

import math
import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from census_scan import partitions  # noqa: E402
from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from sigma_power_kill import compose  # noqa: E402

M = 29
MAXD = 10
DS = tuple(range(2, 9))
RUNS = 12
DIAG_TARGET = 0.0058  # LP within-word doublet rate net of fixed-point leak


def real_word_pools(prose_path: Path):
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        runes = [IDX_ENG[t] for t in to_runeglish(w)]
        if runes:
            pools.setdefault(len(runes), []).append(runes)
    return pools


def sample_corpus(lp_lens, pools, rng):
    """Real prose words matched to the LP length sequence."""
    out = []
    maxlen = max(pools)
    for L in lp_lens:
        LL = L
        while LL not in pools and maxlen > LL:
            LL += 1
        w = rng.choice(pools[LL])[:L]
        out.append(w)
    return out


def profile(words, maxd=MAXD):
    m: Counter = Counter()
    s: Counter = Counter()
    for w in words:
        L = len(w)
        for j in range(L):
            for d in range(1, min(maxd + 1, L - j)):
                s[d] += 1
                m[d] += w[j] == w[j + d]
    return {d: m[d] / s[d] for d in s if s[d]}


def make_g(census, rng):
    pts = list(range(M))
    rng.shuffle(pts)
    g = list(range(M))
    i = 0
    for L in census:
        cyc = pts[i : i + L]
        i += L
        for k in range(L):
            g[cyc[k]] = cyc[(k + 1) % L]
    return g


def conjugate(g, a, b):
    t = list(range(M))
    t[a], t[b] = b, a
    return [t[g[t[x]]] for x in range(M)]


def anneal_to_target(g, T1, rng, target, iters=6000):
    """Anneal |diag - target| so the tuning depth matches the LP, not the
    floor."""

    def obj(gg):
        return abs(sum(T1[gg[y]][y] for y in range(M)) - target)

    cur = obj(g)
    best_g, best = g[:], cur
    temp = 0.003
    for _ in range(iters):
        a, b = rng.sample(range(M), 2)
        g2 = conjugate(g, a, b)
        v = obj(g2)
        if v < cur or rng.random() < math.exp(-(v - cur) / temp):
            g, cur = g2, v
            if v < best:
                best_g, best = g2[:], v
        temp *= 0.9995
    return best_g


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    words_d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        words_d.setdefault(w, []).append(stream[i])
    lp_words = [words_d[k] for k in sorted(words_d)]
    lp_lens = [len(w) for w in lp_words]
    lp_prof = profile(lp_words)
    counts: Counter = Counter()
    for w in lp_words:
        L = len(w)
        for j in range(L):
            for d in range(1, min(MAXD + 1, L - j)):
                counts[d] += 1
    se = {d: math.sqrt(lp_prof[d] * (1 - lp_prof[d]) / counts[d]) for d in lp_prof}

    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    if not prose_path.exists():
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    pools = real_word_pools(prose_path)

    # corrected K_d: mean over real-word corpora matched to LP lengths
    acc: Counter = Counter()
    nacc: Counter = Counter()
    for _ in range(30):
        c = sample_corpus(lp_lens, pools, rng)
        p = profile(c)
        for d, v in p.items():
            acc[d] += v
            nacc[d] += 1
    K = {d: acc[d] / nacc[d] for d in acc}
    B = {d: (1 - K[d]) / 28 for d in K}
    print(
        "corrected real-word K_d: "
        + "  ".join(f"d{d} {K[d]:.4f}" for d in sorted(K) if d <= 8)
    )
    print("(first-pass segment K_d was d2 .0430 d3 .0576 d4 .0581 d5 .0602)")

    print("\ncorrected phi ladder:")
    for d in DS:
        b = B[d]
        phi = (lp_prof[d] - b) / (K[d] - b)
        sd = se[d] / (K[d] - b)
        print(
            f"  d={d}: phi {phi:+.2f} ± {sd:.2f}"
            + ("  (order-5 predicts 1.0)" if d == 5 else "")
        )

    # corrected census scan
    def score(census):
        A, Bs = {}, {}
        for d in DS:
            a = bsum = 0.0
            for L in census:
                p = L / M
                r = d % L
                if r == 0:
                    a += p * K[d]
                elif r in (1, L - 1) and L >= 2:
                    bsum += p
                else:
                    a += p * B[d]
            A[d], Bs[d] = a, bsum
        w = {d: 1 / se[d] ** 2 for d in DS}
        den = sum(w[d] * Bs[d] ** 2 for d in DS)
        s_hat = (
            sum(w[d] * Bs[d] * (lp_prof[d] - A[d]) for d in DS) / den if den else 0.0
        )
        s_hat = min(max(s_hat, 0.0), 0.0345)
        chi = sum(w[d] * (A[d] + Bs[d] * s_hat - lp_prof[d]) ** 2 for d in DS)
        return chi, s_hat

    results = []
    for census in partitions(M, M):
        if sum(1 for L in census if L == 1) > 5:
            continue
        chi, s_hat = score(census)
        results.append((chi, census))
    results.sort()
    print("\ncorrected scan top 8:")
    for chi, census in results[:8]:
        cs = "+".join(str(L) for L in sorted(census, reverse=True) if L > 1)
        nf = sum(1 for L in census if L == 1)
        print(f"  {cs + (f'+{nf}f' if nf else ''):>30}  chi2 {chi:6.2f}")
    for name, census in (
        ("5+5+5+7+7", (7, 7, 5, 5, 5)),
        ("4x5+2x4+1f", (5, 5, 5, 5, 4, 4, 1)),
        ("5x5+4f", (5, 5, 5, 5, 5, 1, 1, 1, 1)),
    ):
        chi, _ = score(census)
        rank = 1 + sum(1 for c, _ in results if c < chi - 1e-12)
        print(f"  {name:>30}  chi2 {chi:6.2f}  rank {rank}/{len(results)}")

    # corrected simulations: real-word plaintext, target-level tuning
    T1 = np.zeros((M, M))
    for _ in range(10):
        for w in sample_corpus(lp_lens, pools, rng):
            for j in range(len(w) - 1):
                T1[w[j]][w[j + 1]] += 1
    T1 /= T1.sum()

    print(f"\ncorrected simulations (real words, diagonal tuned to {DIAG_TARGET}):")
    print(f"{'model':<18}" + "".join(f"{f'd{d}':>7}" for d in range(1, MAXD + 1)))
    print(
        f"{'LP observed':<18}"
        + "".join(f"{lp_prof.get(d, 0):>7.4f}" for d in range(1, MAXD + 1))
    )
    for name, census in (
        ("5+5+5+7+7", (7, 7, 5, 5, 5)),
        ("4x5+2x4+1f", (5, 5, 5, 5, 4, 4, 1)),
        ("5x5+4f", (5, 5, 5, 5, 5, 1, 1, 1, 1)),
    ):
        order = 1
        for L in set(census):
            order = order * L // math.gcd(order, L)
        pacc: Counter = Counter()
        pn: Counter = Counter()
        for _ in range(RUNS):
            g = anneal_to_target(make_g(census, rng), T1, rng, DIAG_TARGET)
            gp = [list(range(M))]
            for _ in range(order - 1):
                gp.append(compose(g, gp[-1]))
            sigma = list(range(M))
            rng.shuffle(sigma)
            base = list(range(M))
            rng.shuffle(base)
            ct = []
            for w in sample_corpus(lp_lens, pools, rng):
                ct.append([base[gp[j % order][p]] for j, p in enumerate(w)])
                base = compose(base, compose(gp[(len(w) - 1) % order], sigma))
            p = profile(ct)
            for d, v in p.items():
                pacc[d] += v
                pn[d] += 1
        print(
            f"{name:<18}"
            + "".join(
                f"{pacc[d] / pn[d]:>7.4f}" if pn[d] else f"{'·':>7}"
                for d in range(1, MAXD + 1)
            )
        )


if __name__ == "__main__":
    main()
