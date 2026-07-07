#!/usr/bin/env python3
"""Mod-5 (and related) projection battery on the unsolved rune stream.

The constant 5 recurs in the corpus fingerprint (doublet acceptance 1/5,
copy distance 5, dead-time ~5). If the cipher has a 5-state internal
component acting on rune *classes*, projecting the ciphertext through a
class map could expose structure invisible in the 29-symbol domain (a
29-symbol-uniform stream can hide a biased 5-class stream only if the
bias respects the partition — worth closing explicitly).

Projections tested (rune index c = 0..28, gematria value v = nth prime):

    c mod 5, c div 6 (block-of-6 row), c mod 2, c mod 7,
    v mod 5, v mod 3, v last-decimal-digit

For each projected stream: IoC, kappa at lags 1..30, and periodic-IoC at
periods 2..30, each z-scored against doublet-suppressed surrogates pushed
through the SAME projection (the doublet suppression itself induces small
projected effects, so uniform nulls would be wrong).

Usage: python experiments/mod5_projection_battery.py [n_surrogates]
"""

from __future__ import annotations

import sys

import numpy as np

ALPHABET = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
DATA = "data/page0-58.txt"

PRIMES29 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
            59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]

PROJECTIONS = {
    "index mod 5": np.array([c % 5 for c in range(MOD)]),
    "index div 6": np.array([c // 6 for c in range(MOD)]),
    "index mod 2": np.array([c % 2 for c in range(MOD)]),
    "index mod 7": np.array([c % 7 for c in range(MOD)]),
    "value mod 5": np.array([v % 5 for v in PRIMES29]),
    "value mod 3": np.array([v % 3 for v in PRIMES29]),
    "value digit": np.array([v % 10 for v in PRIMES29]),
}

KAPPA_LAGS = range(1, 31)
PERIODS = range(2, 31)


def load_clean() -> np.ndarray:
    r2i = {r: i for i, r in enumerate(ALPHABET)}
    with open(DATA) as f:
        raw = f.read()
    pages = [[r2i[ch] for ch in page if ch in r2i] for page in raw.split("%")]
    pages = [p for p in pages if p][:-2]
    return np.array([x for p in pages for x in p], dtype=np.int64)


def ioc(s: np.ndarray) -> float:
    _, counts = np.unique(s, return_counts=True)
    n = len(s)
    return float((counts * (counts - 1)).sum() / (n * (n - 1)))


def kappa(s: np.ndarray, lag: int) -> float:
    return float((s[:-lag] == s[lag:]).mean())


def periodic_ioc(s: np.ndarray, period: int) -> float:
    return float(np.mean([ioc(s[k::period]) for k in range(period)]))


def stats_vector(s: np.ndarray) -> np.ndarray:
    return np.array([ioc(s)]
                    + [kappa(s, lag) for lag in KAPPA_LAGS]
                    + [periodic_ioc(s, p) for p in PERIODS])


def surrogate(n: int, rate: float, rng: np.random.Generator) -> np.ndarray:
    steps = rng.integers(1, MOD, size=n)
    steps[rng.random(n) < rate] = 0
    steps[0] = rng.integers(0, MOD)
    return np.cumsum(steps) % MOD


def main() -> None:
    n_sur = int(sys.argv[1]) if len(sys.argv) > 1 else 800
    c = load_clean()
    n = len(c)
    rate = float((c[1:] == c[:-1]).mean())
    rng = np.random.default_rng(20260707)

    labels = (["IoC"] + [f"kappa{lag}" for lag in KAPPA_LAGS]
              + [f"period{p}" for p in PERIODS])
    n_stats = len(labels)

    sur_streams = [surrogate(n, rate, rng) for _ in range(n_sur)]

    print(f"corpus {n} runes; {n_sur} doublet-suppressed surrogates; "
          f"{n_stats} statistics per projection\n")
    grand_worst = 0.0
    for name, table in PROJECTIONS.items():
        obs = stats_vector(table[c])
        null = np.array([stats_vector(table[s]) for s in sur_streams])
        z = (obs - null.mean(axis=0)) / null.std(axis=0)
        worst = np.argmax(np.abs(z))
        grand_worst = max(grand_worst, float(np.abs(z).max()))
        # Bonferroni-ish context: expected max |z| over n_stats gaussians
        print(f"{name:>12}: max |z| = {abs(z[worst]):.2f} at {labels[worst]}"
              f"  (IoC z={z[0]:+.2f}, kappa1 z={z[1]:+.2f})")
        big = [f"{labels[i]}:{z[i]:+.2f}" for i in range(n_stats)
               if abs(z[i]) > 3.0]
        if big:
            print(f"{'':>14}|z|>3: {', '.join(big)}")

    n_tests = len(PROJECTIONS) * n_stats
    print(f"\nfamily size {n_tests} tests; expected max |z| under the null "
          f"~{np.sqrt(2*np.log(n_tests)):.1f}; observed grand max "
          f"{grand_worst:.2f}")


if __name__ == "__main__":
    main()
