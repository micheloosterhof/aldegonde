#!/usr/bin/env python3
"""Simulation test of the surviving inner-layer class.

Model under test (the survivor of autokey-plus-substitution.md after the
J-stream battery): C[i] = C[i-1] - M[i] mod 29 with inner layer
M[i] = g(P[i], P[i-1]) for a secret mixing table g: 29x29 -> Z29.

If lag-1 inner layers generically leave detectable structure in the
observable J stream (adjacent J symbols share P[t]), then the observed
flatness of J excludes the whole class and pushes the required context to
>= 2 extra runes. Method: generate runeglish-like plaintext from the
repo's trigram table (order-2 Markov), encrypt with random tables g,
measure the same statistics we measured on the real cipher:

  - J marginal chi2 (observed: 41.7, p=0.035)
  - J d=1 contingency chi2 (observed: ~dof, p>0.03)
  - doublet rate (observed: 0.675%)

Also simulates the memoryless variant M[i] = g(P[i]) as a sanity check
(should fail wildly) and the lag-2 variant M[i] = g3(P[i], P[i-1], P[i-2])
(should pass, showing the test discriminates).
"""

from collections import defaultdict

import numpy as np
from scipy.stats import chi2 as chi2_dist
from scipy.stats import chi2_contingency

from aldegonde import c3301

N = 29
M = 28


def load_trigram_model():
    """Order-2 Markov transition table from the runeglish trigram counts."""
    counts = np.zeros((N, N, N))
    with open("src/aldegonde/data/ngrams/runeglish/trigrams.txt") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 2:
                continue
            tri, cnt = parts
            if len(tri) == 3 and all(ch in c3301.CICADA_ALPHABET for ch in tri):
                a, b, c = (c3301.r2i(ch) for ch in tri)
                counts[a, b, c] += float(cnt)
    counts += 1.0  # smoothing
    trans = counts / counts.sum(axis=2, keepdims=True)
    # stationary digraph distribution for seeding
    dig = counts.sum(axis=2)
    dig = dig / dig.sum()
    return trans, dig


def load_quadgram_model():
    """Order-3 Markov transition table from the runeglish quadgram counts."""
    counts = np.zeros((N, N, N, N))
    with open("src/aldegonde/data/ngrams/runeglish/quadgrams.txt") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 2:
                continue
            q, cnt = parts
            if len(q) == 4 and all(ch in c3301.CICADA_ALPHABET for ch in q):
                a, b, c, d = (c3301.r2i(ch) for ch in q)
                counts[a, b, c, d] += float(cnt)
    counts += 0.5
    trans = counts / counts.sum(axis=3, keepdims=True)
    tri = counts.sum(axis=3)
    tri = tri / tri.sum()
    return trans, tri


def gen_plaintext3(trans, tri, n, rng):
    flat = tri.ravel()
    seed = rng.choice(len(flat), p=flat)
    a, r = divmod(seed, N * N)
    b, c = divmod(r, N)
    out = [a, b, c]
    for _ in range(n - 3):
        p = trans[out[-3], out[-2], out[-1]]
        out.append(rng.choice(N, p=p))
    return np.array(out)


def gen_plaintext(trans, dig, n, rng):
    flat = dig.ravel()
    seed = rng.choice(len(flat), p=flat)
    a, b = divmod(seed, N)
    out = [a, b]
    for _ in range(n - 2):
        p = trans[out[-2], out[-1]]
        out.append(rng.choice(N, p=p))
    return np.array(out)


def encrypt(P, g, context):
    """Outer ciphertext autokey C[i] = C[i-1] - M[i], inner M = g(context)."""
    n = len(P)
    C = np.zeros(n, dtype=np.int64)
    C[0] = P[0]  # first symbol arbitrary
    for i in range(1, n):
        if context == 0:
            m = g[P[i]]
        elif context == 1:
            m = g[P[i], P[i - 1]]
        elif context == 2:
            m = g[P[i], P[i - 1], P[i - 2]] if i >= 2 else g[P[i], P[i - 1], 0]
        else:
            m = (g[P[i], P[i - 1], P[i - 2], P[i - 3]]
                 if i >= 3 else g[P[i], P[i - 1], 0, 0])
        C[i] = (C[i - 1] - m) % N
    return C


def encrypt_flat(P, g, k):
    """Outer autokey with inner table over (P[i], ..., P[i-k]), table given
    as a flat int8 array of size 29^(k+1), mixed-radix indexed."""
    n = len(P)
    C = np.zeros(n, dtype=np.int64)
    C[0] = P[0]
    for i in range(1, n):
        idx = 0
        for j in range(k + 1):
            src = P[i - j] if i - j >= 0 else 0
            idx = idx * N + int(src)
        C[i] = (C[i - 1] - int(g[idx])) % N
    return C


def encrypt_hash(P, seed, k):
    """Generic table g(context) realized as a strong integer hash -> Z29.
    Memory-free equivalent of a random 29^(k+1) table (verified: reproduces
    the explicit-array lag-4 statistics exactly)."""
    n = len(P)
    C = np.zeros(n, dtype=np.int64)
    C[0] = P[0]
    mask = (1 << 64) - 1
    for i in range(1, n):
        idx = 0
        for j in range(k + 1):
            idx = idx * N + int(P[i - j]) if i - j >= 0 else idx * N
        h = (idx + seed) * 0x9E3779B97F4A7C15 & mask
        h ^= h >> 29
        h = h * 0xBF58476D1CE4E5B9 & mask
        h ^= h >> 32
        C[i] = (C[i - 1] - (h % N)) % N
    return C


def j_stats(C):
    delta = (C[1:] - C[:-1]) % N
    nz = delta != 0
    J = ((delta[nz] - 1) % M).astype(np.int64)
    nj = len(J)
    c = np.bincount(J, minlength=M)
    marg = float(((c - nj / M) ** 2 / (nj / M)).sum())
    a, b = J[:-1], J[1:]
    joint = np.zeros((M, M))
    np.add.at(joint, (a, b), 1)
    stat, p, dof, _ = chi2_contingency(joint + 1e-9)
    dbl = float((~nz).mean())
    return marg, float(stat), dbl


def main() -> None:
    rng = np.random.default_rng(101)
    trans, dig = load_trigram_model()
    n = 13041
    SAMPLES = 12

    print(f"{'model':<22} {'J marginal chi2':>16} {'J d=1 chi2':>12} {'dbl rate':>9}")
    print(f"{'observed cipher':<22} {41.7:>16.1f} {729.0:>12.0f} {'0.675%':>9}")
    for context, label in ((0, "memoryless g(P)"), (1, "lag-1 g(P,P')"),
                           (2, "lag-2 g(P,P',P'')")):
        margs, d1s, dbls = [], [], []
        for _ in range(SAMPLES):
            P = gen_plaintext(trans, dig, n, rng)
            shape = (N,) * (context + 1)
            g = rng.integers(0, N, size=shape)
            C = encrypt(P, g, context)
            marg, d1, dbl = j_stats(C)
            margs.append(marg)
            d1s.append(d1)
            dbls.append(dbl)
        print(f"{label:<22} {np.mean(margs):>10.0f}±{np.std(margs):<5.0f} "
              f"{np.mean(d1s):>7.0f}±{np.std(d1s):<4.0f} "
              f"{100 * np.mean(dbls):>8.2f}%")

    # lag-3 with order-3 plaintext (fair: richest available plaintext model)
    trans3, tri3 = load_quadgram_model()
    margs, d1s, dbls = [], [], []
    for _ in range(8):
        P = gen_plaintext3(trans3, tri3, n, rng)
        g = rng.integers(0, N, size=(N, N, N, N))
        C = encrypt(P, g, 3)
        marg, d1, dbl = j_stats(C)
        margs.append(marg)
        d1s.append(d1)
        dbls.append(dbl)
    print(f"{'lag-3 g(4 runes)':<22} {np.mean(margs):>10.0f}±{np.std(margs):<5.0f} "
          f"{np.mean(d1s):>7.0f}±{np.std(d1s):<4.0f} "
          f"{100 * np.mean(dbls):>8.2f}%")

    # lag-4 (5 runes of context), flat int8 table of 29^5 cells.
    # NOTE: the order-3 plaintext model only carries genuine structure up to
    # 4-grams, so this UNDERSTATES the detectability of a real lag-4 cipher
    # on real text — the simulated values are a lower bound.
    margs, d1s, dbls = [], [], []
    for _ in range(10):
        P = gen_plaintext3(trans3, tri3, n, rng)
        g = rng.integers(0, N, size=N**5, dtype=np.int8)
        C = encrypt_flat(P, g, 4)
        marg, d1, dbl = j_stats(C)
        margs.append(marg)
        d1s.append(d1)
        dbls.append(dbl)
    print(f"{'lag-4 g(5 runes)':<22} {np.mean(margs):>10.0f}±{np.std(margs):<5.0f} "
          f"{np.mean(d1s):>7.0f}±{np.std(d1s):<4.0f} "
          f"{100 * np.mean(dbls):>8.2f}%")

    # lag-5 (6 runes of context) via hash-realized table (29^6 cells would
    # not fit in memory as an array)
    margs, d1s, dbls = [], [], []
    for _ in range(30):
        P = gen_plaintext3(trans3, tri3, n, rng)
        C = encrypt_hash(P, int(rng.integers(1, 2**62)), 5)
        marg, d1, dbl = j_stats(C)
        margs.append(marg)
        d1s.append(d1)
        dbls.append(dbl)
    print(f"{'lag-5 g(6 runes)':<22} {np.mean(margs):>10.0f}±{np.std(margs):<5.0f} "
          f"{np.mean(d1s):>7.0f}±{np.std(d1s):<4.0f} "
          f"{100 * np.mean(dbls):>8.2f}%")
    print(f"\nnull references: J marginal dof={M - 1} (mean 27), "
          f"d=1 contingency dof={(M - 1) ** 2} (mean 729); "
          f"observed exact: marginal 41.7, d=1 contingency 684.2")


if __name__ == "__main__":
    main()
