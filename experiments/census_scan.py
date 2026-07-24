#!/usr/bin/env python3
# ABOUTME: Exhaustive scan of all cycle censuses (partitions of 29) for the
# ABOUTME: letter step g, scored with the refined inheritance model against the
# ABOUTME: within-word distance profile (mixed-cycle-progression.md).
"""Which loop censuses can fit the within-word profile?

Refined model: for a class of letters on an L-loop, the relation at
distance d is g^(d mod L):
    d mod L == 0        -> return: leak K_d (plaintext coincidence)
    d mod L in {1, L-1} -> the tuned diagonal (g or its inverse): shared
                           suppressed rate s (one free parameter, fitted
                           per census by weighted least squares over
                           d = 2..8, clamped to [0, background])
    otherwise           -> background b_d = (1 - K_d)/28
Fixed points (L = 1) always return. Feasibility filter on d1: fixed
points leak plaintext doublets, n_fix * K1 / 29 must not exceed the
observed doublet rate (n_fix <= 5).

Scores every partition of 29, prints the leaders with per-cell pulls,
the permutation order (lcm), and where the hand-proposed censuses rank.
"""

from __future__ import annotations

import math
import random
import sys
import urllib.request
from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish
from doublet_position_profile import IDX_ENG
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words
from lp_corpus import load_clean

M = 29
DS = tuple(range(2, 9))


def partitions(n: int, maxpart: int):
    if n == 0:
        yield ()
        return
    for p in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - p, p):
            yield (p,) + rest


def lp_rates():
    stream, wid = load_clean()
    words: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        words.setdefault(w, []).append(stream[i])
    m: Counter = Counter()
    s: Counter = Counter()
    for w in words.values():
        L = len(w)
        for j in range(L):
            for d in DS:
                if j + d < L:
                    s[d] += 1
                    m[d] += w[j] == w[j + d]
    obs = {d: m[d] / s[d] for d in DS}
    se = {d: math.sqrt(obs[d] * (1 - obs[d]) / s[d]) for d in DS}
    lens = [len(w) for w in words.values()]
    return obs, se, lens


def prose_K(lens, rng, samples=40):
    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    if not prose_path.exists():
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    prose = [IDX_ENG[t] for w in prose_words(prose_path)
             for t in to_runeglish(w)]
    m: Counter = Counter()
    s: Counter = Counter()
    for _ in range(samples):
        off = rng.randrange(len(prose) - sum(lens))
        pos = off
        for L in lens:
            w = prose[pos:pos + L]
            pos += L
            for j in range(L):
                for d in DS:
                    if j + d < L:
                        s[d] += 1
                        m[d] += w[j] == w[j + d]
    return {d: m[d] / s[d] for d in DS}


def score(census, obs, se, K, B):
    """Weighted LS over DS with s free in [0, mean background]."""
    A = {}
    Bs = {}
    for d in DS:
        a = 0.0
        bsum = 0.0
        for L in census:
            phi = L / M
            mres = d % L
            if mres == 0:
                a += phi * K[d]
            elif mres in (1, L - 1) and L >= 2:
                bsum += phi
            else:
                a += phi * B[d]
        A[d] = a
        Bs[d] = bsum
    w = {d: 1 / se[d] ** 2 for d in DS}
    num = sum(w[d] * Bs[d] * (obs[d] - A[d]) for d in DS)
    den = sum(w[d] * Bs[d] ** 2 for d in DS)
    s_hat = num / den if den > 0 else 0.0
    s_hat = min(max(s_hat, 0.0), 0.0345)
    chi = sum(w[d] * (A[d] + Bs[d] * s_hat - obs[d]) ** 2 for d in DS)
    return chi, s_hat, A, Bs


def main() -> None:
    rng = random.Random(3301)
    obs, se, lens = lp_rates()
    K = prose_K(lens, rng)
    B = {d: (1 - K[d]) / 28 for d in DS}
    print("LP within-word rates: "
          + "  ".join(f"d{d} {obs[d]:.4f}" for d in DS))

    results = []
    n_scanned = 0
    for census in partitions(M, M):
        n_fix = sum(1 for L in census if L == 1)
        if n_fix > 5:
            continue  # fixed-point doublet leak exceeds observed rate
        n_scanned += 1
        chi, s_hat, A, Bs = score(census, obs, se, K, B)
        results.append((chi, census, s_hat))
    results.sort()
    print(f"\nscanned {n_scanned} feasible censuses (of 4565 partitions); "
          f"top 15:")
    print(f"{'census':>34} {'chi2':>7} {'s':>7} {'order':>6}  worst cells")
    for chi, census, s_hat in results[:15]:
        order = 1
        for L in set(census):
            order = order * L // math.gcd(order, L)
        _, _, A, Bs = score(census, obs, se, K, B)
        pulls = sorted(
            ((abs((A[d] + Bs[d] * s_hat - obs[d]) / se[d]), d,
              (A[d] + Bs[d] * s_hat - obs[d]) / se[d]) for d in DS),
            reverse=True)[:2]
        wc = ", ".join(f"d{d}:{z:+.1f}" for _, d, z in pulls)
        cs = "+".join(str(L) for L in sorted(census, reverse=True) if L > 1)
        nf = sum(1 for L in census if L == 1)
        label = cs + (f"+{nf}f" if nf else "")
        print(f"{label:>34} {chi:>7.2f} {s_hat:>7.4f} {order:>6}  {wc}")

    # reference censuses
    print("\nreference censuses:")
    for name, census in (
            ("Michel 4x5+2x4+1f", (5, 5, 5, 5, 4, 4, 1)),
            ("standard 5x5+4f", (5, 5, 5, 5, 5, 1, 1, 1, 1)),
            ("prime 5+5+5+7+7", (5, 5, 5, 7, 7)),
            ("primes 11+7+5+3+2+1f", (11, 7, 5, 3, 2, 1))):
        chi, s_hat, A, Bs = score(census, obs, se, K, B)
        rank = 1 + sum(1 for c, _, _ in results if c < chi - 1e-12)
        cells = "  ".join(
            f"d{d}:{(A[d] + Bs[d] * s_hat - obs[d]) / se[d]:+.1f}" for d in DS)
        print(f"  {name:<22} chi2 {chi:6.2f}  s {s_hat:.4f}  "
              f"rank {rank:>4}/{n_scanned}  {cells}")


if __name__ == "__main__":
    main()
