#!/usr/bin/env python3
# ABOUTME: Characterizes the spacing of Liber Primus doublets as a point process
# ABOUTME: and tests for any link to mathematical series (primes, totient, lattice).
"""Doublet spacing / point-process analysis for Liber Primus (page0-58).

Tests whether the 89 ciphertext doublets are positioned randomly (Poisson) or by
some deterministic rule. Reports gap distribution, exponential fit, dispersion
(Fano factor), periodicity (DFT), and overlap of positions/gaps with math series.

Result (see hypotheses/doublet-spacing-poisson.md): homogeneous Poisson process,
content-driven, no link to any series.
"""

from __future__ import annotations

from math import gcd

import numpy as np

from aldegonde import c3301

DATA = "data/page0-58.txt"
RUNES = set(c3301.CICADA_ALPHABET)


def sieve(m: int) -> np.ndarray:
    s = np.ones(m + 2, bool)
    s[:2] = False
    for i in range(2, int(m**0.5) + 1):
        if s[i]:
            s[i * i :: i] = False
    return s


def totient(m: int) -> np.ndarray:
    phi = np.arange(m + 1)
    for p in range(2, m + 1):
        if phi[p] == p:  # p is prime
            phi[p::p] -= phi[p::p] // p
    return phi


def main() -> None:
    with open(DATA, encoding="utf-8") as f:
        idx = [c3301.r2i(c) for c in f.read() if c in RUNES]
    n = len(idx)
    pos = np.array([i for i in range(n - 1) if idx[i] == idx[i + 1]])
    D = len(pos)
    lam = D / n
    gaps = np.diff(pos)

    print(f"n={n} runes, D={D} doublets, rate={lam:.5f}, mean spacing 1/rate={1/lam:.1f}")
    print("\n--- GAP DISTRIBUTION ---")
    print(f"min {gaps.min()}  max {gaps.max()}  mean {gaps.mean():.1f}  "
          f"median {int(np.median(gaps))}  std {gaps.std():.1f}")
    print(f"CV std/mean = {gaps.std()/gaps.mean():.3f}  (geometric/exponential -> 1.0)")
    print(f"gaps below 6: {int((gaps < 6).sum())}  "
          f"(exp under exponential ~{len(gaps)*(1-np.exp(-5/(1/lam))):.1f}) "
          f"-- the one micro-anomaly: doublets avoid being within ~5 runes")

    print("\n--- POISSON / DISPERSION (Fano = var/mean of per-bin counts, Poisson=1) ---")
    for b in (50, 100, 200, 400):
        c, _ = np.histogram(pos, bins=range(0, n + b, b))
        print(f"  bin={b:>4}: Fano={c.var()/c.mean():.2f}")
    try:
        from scipy import stats
        ks = stats.kstest(gaps, "expon", args=(0, 1 / lam))
        print(f"  KS gaps vs exponential: D={ks.statistic:.3f} p={ks.pvalue:.3f} "
              f"({'cannot reject' if ks.pvalue > 0.05 else 'rejects'} exponential)")
    except ImportError:
        print("  (scipy unavailable; skipping KS test)")

    print("\n--- PERIODICITY (DFT of indicator) ---")
    ind = np.zeros(n)
    ind[pos] = 1
    ind -= ind.mean()
    power = np.abs(np.fft.rfft(ind)) ** 2
    peak_ratio = power[1:].max() / power[1:].mean()
    print(f"  max-peak / mean-power = {peak_ratio:.2f}  "
          f"(white-noise expectation ~ln(n/2)={np.log(n/2):.1f}; no real period if comparable)")

    print("\n--- MATH-SERIES LINKAGE (positions) ---")
    isprime = sieve(n + 2)
    phi = totient(n)
    fib = set()
    a, b = 1, 2
    while a < n:
        fib.add(a)
        a, b = b, a + b
    series = {
        "primes": isprime[:n],
        "fibonacci": np.array([i in fib for i in range(n)]),
        "squares": np.array([int(i**0.5) ** 2 == i for i in range(n)]),
    }
    for name, mask in series.items():
        obs = int(mask[pos].sum())
        exp = D * mask.mean()
        print(f"  pos in {name:<10}: obs={obs:>3} exp={exp:.2f}")
    for label, m in [("i prime", isprime[pos]),
                     ("i+1 prime", isprime[pos + 1]),
                     ("i-1 prime", isprime[pos - 1])]:
        allm = {"i prime": isprime[:n], "i+1 prime": isprime[1:n + 1],
                "i-1 prime": isprime[np.arange(-1, n - 1).clip(0)]}[label]
        print(f"  {label:<10}: obs={int(m.sum()):>3} exp={D*allm.mean():.2f}")

    print("\n--- MATH-SERIES LINKAGE (gaps & totient) ---")
    gg = gaps[0]
    for x in gaps:
        gg = gcd(int(gg), int(x))
    print(f"  GCD of all gaps: {gg}  (>1 would mean positions on a lattice)")
    chi = ((np.bincount(gaps % 29, minlength=29) - len(gaps) / 29) ** 2
           / (len(gaps) / 29)).sum()
    print(f"  gaps mod 29 chi-sq: {chi:.1f} (uniform if < ~41)")
    print(f"  phi(i) mod 29 mean at doublets: {(phi[pos]%29).mean():.2f}  "
          f"overall: {(phi[1:n]%29).mean():.2f}")


if __name__ == "__main__":
    main()
