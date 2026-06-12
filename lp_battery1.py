#!/usr/bin/env python3
"""Battery 1: lag statistics, periodic IoC, difference-stream structure."""
import collections
import math
from lp_structure import parse, flat, ioc, nioc, N

pages = parse("data/page0-58.txt")
s = flat(pages)
n = len(s)

def zscore(count, trials, p):
    mu = trials * p
    sd = math.sqrt(trials * p * (1 - p))
    return (count - mu) / sd

print("=== KAPPA: P(c[i]==c[i+d]) z-scores, d=1..60 ===")
sig = []
for d in range(1, 101):
    cnt = sum(1 for i in range(n - d) if s[i] == s[i + d])
    z = zscore(cnt, n - d, 1 / N)
    if abs(z) > 2.5:
        sig.append((d, z))
    if d <= 60:
        print(f"{d:3d}:{z:+5.1f}", end="  " if d % 6 else "\n")
print()
print("significant |z|>2.5:", [(d, round(z, 2)) for d, z in sig])

print("\n=== chi2 of (c[i+d]-c[i]) mod 29 distribution vs uniform, d=1..40 ===")
# df=28; mean 28, sd ~7.5; flag chi2 > 56 (~p<0.001)
for d in range(1, 41):
    diffs = collections.Counter((s[i + d] - s[i]) % N for i in range(n - d))
    m = n - d
    chi2 = sum((diffs[k] - m / N) ** 2 / (m / N) for k in range(N))
    flag = " ***" if chi2 > 56.9 else (" *" if chi2 > 48.3 else "")
    print(f"d={d:3d} chi2={chi2:6.1f}{flag}", end="   " if d % 4 else "\n")

print("\n=== chi2 of (c[i+d]+c[i]) mod 29 distribution, d=1..10 ===")
for d in range(1, 11):
    sums = collections.Counter((s[i + d] + s[i]) % N for i in range(n - d))
    m = n - d
    chi2 = sum((sums[k] - m / N) ** 2 / (m / N) for k in range(N))
    print(f"d={d:2d} chi2={chi2:6.1f}", end="   " if d % 5 else "\n")

print("\n=== periodic IoC (avg column nIoC) periods 2..80 ===")
for p in range(2, 81):
    cols = [s[i::p] for i in range(p)]
    avg = sum(nioc(c) for c in cols) / p
    flag = " ***" if avg > 1.10 else ""
    print(f"p={p:2d}:{avg:.3f}{flag}", end="  " if p % 6 else "\n")
print()

print("\n=== delta stream IoC (c[i+k]-c[i] as new stream), k=1..5 ===")
for k in range(1, 6):
    d1 = [(s[i + k] - s[i]) % N for i in range(n - k)]
    print(f"k={k}: nIoC={nioc(d1):.4f}", end="  ")
    # and periodic IoC of delta stream for small periods
print()
d1 = [(s[i + 1] - s[i]) % N for i in range(n - 1)]
print("delta1 periodic IoC p=2..20:", " ".join(f"{p}:{sum(nioc(d1[i::p]) for i in range(p))/p:.3f}" for p in range(2, 21)))
d2 = [(d1[i + 1] - d1[i]) % N for i in range(len(d1) - 1)]
print(f"second difference nIoC: {nioc(d2):.4f}")

print("\n=== bigram diversity at distance d (digraphic IoC), d=1..20 ===")
# IoC over pairs (s[i], s[i+d]); expected 1/841 for uniform
for d in range(1, 21):
    prs = [(s[i], s[i + d]) for i in range(n - d)]
    c = collections.Counter(prs)
    m = len(prs)
    io = sum(v * (v - 1) for v in c.values()) / (m * (m - 1)) * (N * N)
    print(f"d={d:2d}: {io:.4f}", end="  " if d % 5 else "\n")
