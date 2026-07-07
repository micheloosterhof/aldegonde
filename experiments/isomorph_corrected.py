#!/usr/bin/env python3
"""Isomorph statistics with a doublet-corrected null model.

The library's random_isomorph_statistics uses uniform random text. The LP's
doublet suppression alone reduces pattern diversity, which inflates
duplicate-isomorph counts. Here the null is a Markov chain with
P(next == cur) = observed doublet rate (0.00675), all other symbols equal.
Any remaining excess is structure beyond doublet suppression.

Pattern encoding: for each position, distance to the previous occurrence of
the same symbol if it falls inside the window, else 0. This is a bijection
with the isomorph class.
"""

import math
from collections import Counter

import numpy as np

from anomaly_scan import parse

N = 29
LENGTHS = (6, 8, 10, 12, 14, 16, 18, 20)


def prev_distance(a: np.ndarray) -> np.ndarray:
    last = {}
    out = np.zeros(len(a), dtype=np.int32)
    for i, x in enumerate(a):
        if x in last:
            out[i] = i - last[x]
        last[x] = i
    return out


def stats_for(a: np.ndarray, lengths=LENGTHS) -> dict[int, tuple[int, int]]:
    n = len(a)
    pd = prev_distance(a)
    res = {}
    for L in lengths:
        cnt = Counter()
        for s in range(n - L + 1):
            w = pd[s : s + L]
            offs = np.arange(L)
            code = np.where(w <= offs, w, 0)
            cnt[code.tobytes()] += 1
        distinct = len(cnt)
        duplicate = sum(v for v in cnt.values() if v > 1)
        res[L] = (distinct, duplicate)
    return res


def markov_sample(n: int, p_dd: float, rng) -> np.ndarray:
    out = np.empty(n, dtype=np.int64)
    out[0] = rng.integers(0, N)
    same = rng.random(n) < p_dd
    jump = rng.integers(0, N - 1, n)
    for i in range(1, n):
        if same[i]:
            out[i] = out[i - 1]
        else:
            j = jump[i]
            out[i] = j if j < out[i - 1] else j + 1
    return out


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain])
    n = len(cipher)
    dbl = int(np.count_nonzero(cipher[:-1] == cipher[1:]))
    p_dd = dbl / (n - 1)
    print(f"cipher: {n} runes, doublet rate {p_dd:.5f}")

    obs = stats_for(cipher)

    SAMPLES = 60
    rng = np.random.default_rng(42)
    acc = {L: ([], []) for L in LENGTHS}
    for s in range(SAMPLES):
        sim = markov_sample(n, p_dd, rng)
        r = stats_for(sim)
        for L in LENGTHS:
            acc[L][0].append(r[L][0])
            acc[L][1].append(r[L][1])

    print(f"\nnull = Markov chain with suppressed diagonal, {SAMPLES} samples")
    print(f"{'L':>3} {'obs_dist':>9} {'null_dist':>16} {'z':>7}   "
          f"{'obs_dup':>8} {'null_dup':>16} {'z':>7}")
    for L in LENGTHS:
        d0, u0 = obs[L]
        dm, ds = np.mean(acc[L][0]), np.std(acc[L][0])
        um, us = np.mean(acc[L][1]), np.std(acc[L][1])
        zd = (d0 - dm) / ds if ds > 0 else float("nan")
        zu = (u0 - um) / us if us > 0 else float("nan")
        print(f"{L:>3} {d0:>9} {dm:>10.1f}±{ds:<5.1f} {zd:>+7.2f}   "
              f"{u0:>8} {um:>10.1f}±{us:<5.1f} {zu:>+7.2f}")


if __name__ == "__main__":
    main()
