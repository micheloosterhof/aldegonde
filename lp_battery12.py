#!/usr/bin/env python3
"""Battery 12: difference-domain reframing + fractionation/bigram kills.

The cipher behaves as: c[i] = c[i-1] + d[i] (mod 29), where d[i] is uniform
over {1..28} with 0 suppressed (the 86 doublets). So the REAL message channel
is the difference stream d. Attack d directly.
"""
import collections
import math
import random
from lp_structure import parse, flat, nioc, N, RUNES, R2I

random.seed(11)
pages = parse("data/page0-58.txt")[:55]
words = [w for p in pages for w in p]
s = flat(pages)
n = len(s)

# difference stream (whole corpus, continuous)
d = [(s[i + 1] - s[i]) % N for i in range(n - 1)]

print("=== difference stream d = c[i+1]-c[i] (mod 29) as the message channel ===")
print(f"len {len(d)}, nIoC {nioc(d):.4f} (inflated only by the 0-suppression)")

# remove zeros entirely and renormalise: is the NONZERO d-stream uniform over 1..28?
dnz = [x for x in d if x != 0]
cnt = collections.Counter(dnz)
m = len(dnz)
chi = sum((cnt[k] - m / 28) ** 2 / (m / 28) for k in range(1, N))
print(f"nonzero-d: n={m} chi2 vs uniform-28 = {chi:.1f} (df=27, p05~40.1)")
io28 = sum(v * (v - 1) for v in cnt.values()) / (m * (m - 1)) * 28
print(f"nonzero-d nIoC (base 28) = {io28:.4f}")

print("\n=== periodicity of d-stream (avg column nIoC), p=2..60 ===")
hi = []
for p in range(2, 61):
    avg = sum(nioc(d[i::p]) for i in range(p)) / p
    if avg > 1.05:
        hi.append((p, round(avg, 3)))
print("periods with avg-col nIoC>1.05:", hi if hi else "NONE (all ~1.02, doublet artifact)")

print("\n=== keystream sweep on the d-stream (c[i+1]-c[i]-key), nIoC>1.05 flagged ===")
def sieve(limit):
    pr = []; is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr
PR = sieve(200000)
PI = "141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982"
fib = [1, 1]
while len(fib) < n + 5:
    fib.append(fib[-1] + fib[-2])
streams = {
    "primes": PR[:n], "totient": [p - 1 for p in PR[:n]],
    "index": list(range(n)), "fib": fib[:n],
    "pi": [int(c) for c in PI * (n // len(PI) + 1)][:n],
    "primes mod29": [p % N for p in PR[:n]],
}
for name, k in streams.items():
    best = 0
    for sign in (-1, 1):
        p = [(d[i] + sign * k[i]) % N for i in range(len(d))]
        best = max(best, nioc(p))
    print(f"{name:14s}: best nIoC {best:.4f}{'  <<<' if best>1.05 else ''}")

# d-stream as VIGENERE: try all periods, Friedman-style — already flat above.

print("\n=== second-order: is d periodic under a SHORT key (brute small periods, chi2 on each col)? ===")
for p in range(2, 30):
    cols_chi = []
    for off in range(p):
        col = [x for x in d[off::p] if x != 0]
        if len(col) < 50:
            continue
        cc = collections.Counter(col)
        mm = len(col)
        cols_chi.append(sum((cc[k] - mm / 28) ** 2 / (mm / 28) for k in range(1, N)))
    mx = max(cols_chi) if cols_chi else 0
    if mx > 60:
        print(f"period {p}: max column chi2 = {mx:.1f}  <<<")
print("(no period flagged above => d has no short-key periodicity)")

# ============ fractionation / bigram kills ============
print("\n=== fractionation signature test ===")
# If each rune -> two base-b symbols then transposed/recombined, the unigram
# of recombined runes is uniform BUT the conditional entropy structure differs.
# Test: does LP look like a base-29 = 2x(base sqrt) tomographic cipher?
# Signature: bigram (c[2i],c[2i+1]) distribution vs (c[2i+1],c[2i+2]).
even = [(s[2 * i], s[2 * i + 1]) for i in range(n // 2)]
odd = [(s[2 * i + 1], s[2 * i + 2]) for i in range((n - 1) // 2)]
def big_io(prs):
    c = collections.Counter(prs); mm = len(prs)
    return sum(v * (v - 1) for v in c.values()) / (mm * (mm - 1)) * N * N
print(f"even-aligned bigram IoC {big_io(even):.4f}, odd-aligned {big_io(odd):.4f} (both ~1 => no 2-periodic fractionation)")

print("\n=== Playfair/bigram-substitution kill ===")
# In a digraphic substitution over pairs, repeated plaintext bigrams -> repeated
# cipher bigrams at EVEN offset. Count repeated even-aligned bigrams vs odd.
ce = collections.Counter(even); co = collections.Counter(odd)
re = sum(v * (v - 1) // 2 for v in ce.values())
ro = sum(v * (v - 1) // 2 for v in co.values())
exp = (n // 2) * (n // 2 - 1) / 2 / (N * N)
print(f"repeated even-bigram pairs {re}, odd {ro}, expected {exp:.1f} (no excess => not digraphic)")
# also Playfair forbids doubled letters within a digraph (even-aligned doublets=0)
ed = sum(1 for a, b in even if a == b)
print(f"even-aligned doublets: {ed} (Playfair would force 0; expected {n//2/N:.0f})")

print("\n=== interrupted/autoclave keyed by a rune value: c[i]=p[i]+k[i], key advances")
print("    only when previous cipher rune != a trigger; test fit is in battery11. ===")

# ============ NEW: is the 0-suppression a KEY property or PLAINTEXT property? ============
print("\n=== does suppression sit in fixed positions across pages? (key-driven) ===")
# For an additive cipher c=p+k, a doublet needs dp[i] = -dk[i]. If k is fixed
# per-page-position, doublet POSITIONS would cluster at positions where dk is rare.
bounds = []; acc = 0
for pg in pages:
    L = sum(len(w) for w in pg);
    bounds.append((acc, acc + L)); acc += L
# position-within-page histogram of doublets
posbins = collections.Counter()
for a, b in bounds:
    for i in range(a, b - 1):
        if s[i] == s[i + 1]:
            posbins[(i - a) // 20] += 1
print("doublets by position-in-page (bins of 20):", dict(sorted(posbins.items())))
print("(flat => suppression is not tied to absolute page position => not a fixed periodic key)")
