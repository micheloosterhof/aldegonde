#!/usr/bin/env python3
"""Pairwise dependence scan for the unsolved LP.

1. Full 29x29 contingency chi-square between C[i] and C[i+d], d=1..100.
   Catches ANY pairwise dependence, not just equality (kappa).
2. Uniformity of linear functionals (C[i+d] + a*C[i]) mod 29 for all a, d.
3. Gematria Primus relations: primality of GP sums of adjacent pairs/words.
"""

import math
from collections import Counter

import numpy as np
from scipy.stats import chi2 as chi2_dist
from sympy import isprime

from anomaly_scan import parse
from aldegonde import c3301

N = 29


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    plain = sections[-1]
    cipher = np.array(stream[: len(stream) - len(plain)], dtype=np.int64)
    n = len(cipher)
    print(f"cipher stream: {n} runes")

    print("\n=== full contingency chi2: C[i] vs C[i+d] ===")
    results = []
    for d in range(1, 101):
        a = cipher[:-d]
        b = cipher[d:]
        m = len(a)
        joint = np.zeros((N, N))
        np.add.at(joint, (a, b), 1)
        ra = joint.sum(axis=1)
        rb = joint.sum(axis=0)
        exp = np.outer(ra, rb) / m
        with np.errstate(divide="ignore", invalid="ignore"):
            stat = np.nansum((joint - exp) ** 2 / exp)
        dof = (N - 1) ** 2
        p = chi2_dist.sf(stat, dof)
        results.append((p, d, stat))
    results.sort()
    print("top 10 most significant distances (784 dof):")
    for p, d, stat in results[:10]:
        print(f"  d={d:3d}: chi2={stat:.1f} p={p:.5f}")
    print(f"(Bonferroni threshold for 100 tests at 0.01: p < 1e-4)")

    print("\n=== linear functionals (C[i+d] + a*C[i] + b*i) mod 29 ===")
    hits = []
    for d in range(1, 21):
        x = cipher[:-d]
        y = cipher[d:]
        for a in range(1, N):
            f = (y + a * x) % N
            counts = np.bincount(f, minlength=N)
            m = len(f)
            stat = ((counts - m / N) ** 2 / (m / N)).sum()
            p = chi2_dist.sf(stat, N - 1)
            if p < 1e-4:
                hits.append((p, d, a, stat))
    # also pure position: C[i] + a*i mod 29
    idx = np.arange(n)
    for a in range(1, N):
        f = (cipher + a * idx) % N
        counts = np.bincount(f, minlength=N)
        stat = ((counts - n / N) ** 2 / (n / N)).sum()
        p = chi2_dist.sf(stat, N - 1)
        if p < 1e-4:
            hits.append((p, 0, a, stat))
    if hits:
        for p, d, a, stat in sorted(hits):
            print(f"  d={d} a={a}: chi2={stat:.1f} p={p:.2e}")
    else:
        print("  none significant at p<1e-4 (560+28 tests)")

    print("\n=== Gematria Primus relations ===")
    gp = np.array([c3301.r2v(c3301.CICADA_ALPHABET[i]) for i in range(N)])
    vals = gp[cipher]
    # adjacent pair sums prime?
    sums = vals[:-1] + vals[1:]
    obs_prime = sum(1 for s in sums if isprime(int(s)))
    # expected under independence: average over all 29x29 pairs
    pp = sum(1 for x in gp for y in gp if isprime(int(x + y))) / (N * N)
    m = len(sums)
    exp = m * pp
    sd = math.sqrt(m * pp * (1 - pp))
    print(f"  adjacent GP sums prime: obs={obs_prime} exp={exp:.1f} "
          f"z={(obs_prime-exp)/sd:+.2f}")
    # word GP sums prime
    wsums = [sum(int(gp[r]) for r in w) for w in words]
    obsw = sum(1 for s in wsums if isprime(s))
    # MC baseline
    rng = np.random.default_rng(1)
    mc = []
    for _ in range(200):
        tot = 0
        for w in words:
            s = int(gp[rng.integers(0, N, len(w))].sum())
            tot += isprime(s)
        mc.append(tot)
    mc = np.array(mc)
    print(f"  word GP sums prime: obs={obsw} mc_exp={mc.mean():.1f} "
          f"mc_sd={mc.std():.1f} z={(obsw-mc.mean())/mc.std():+.2f}")
    # word GP sums mod 29 / mod small primes uniformity
    for mod in (3, 5, 7, 29, 59):
        c = np.bincount(np.array(wsums) % mod, minlength=mod)
        # MC expectation (GP values mod m are not uniform)
        mcc = np.zeros(mod)
        for _ in range(50):
            sims = [int(gp[rng.integers(0, N, len(w))].sum()) % mod for w in words]
            mcc += np.bincount(np.array(sims), minlength=mod)
        mcc /= 50
        stat = ((c - mcc) ** 2 / np.where(mcc > 0, mcc, 1)).sum()
        p = chi2_dist.sf(stat, mod - 1)
        print(f"  word GP sums mod {mod}: chi2={stat:.1f} p={p:.4f}")

    print("\n=== rune vs covariates ===")
    # first rune vs word length
    from scipy.stats import chi2_contingency
    wl = [min(len(w), 8) for w in words]
    fr = [w[0] for w in words]
    tab = np.zeros((8, N))
    for L, r in zip(wl, fr):
        tab[L - 1, r] += 1
    tab = tab[tab.sum(axis=1) > 0]
    stat, p, dof, _ = chi2_contingency(tab)
    print(f"  first-rune vs word-length: chi2={stat:.1f} dof={dof} p={p:.4f}")
    lr = [w[-1] for w in words]
    tab = np.zeros((8, N))
    for L, r in zip(wl, lr):
        tab[L - 1, r] += 1
    tab = tab[tab.sum(axis=1) > 0]
    stat, p, dof, _ = chi2_contingency(tab)
    print(f"  last-rune vs word-length: chi2={stat:.1f} dof={dof} p={p:.4f}")
    # consecutive word lengths
    wlens = [len(w) for w in words]
    a = [min(x, 9) for x in wlens[:-1]]
    b = [min(x, 9) for x in wlens[1:]]
    tab = np.zeros((9, 9))
    for x, y in zip(a, b):
        tab[x - 1, y - 1] += 1
    tab = tab[tab.sum(axis=1) > 0][:, tab.sum(axis=0) > 0]
    stat, p, dof, _ = chi2_contingency(tab)
    print(f"  consecutive word lengths: chi2={stat:.1f} dof={dof} p={p:.4f}")


if __name__ == "__main__":
    main()
