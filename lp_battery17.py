#!/usr/bin/env python3
"""Battery 17: remove the doublets, analyse what remains.

Two derived streams from the clean corpus (pages 0-54):
  A: deduped value stream -- drop the second glyph of every doublet pair
     (0 triplets exist, so result has exactly zero doublets).
  D: the nonzero first-difference stream d = c[i+1]-c[i] mod 29, d != 0,
     remapped to base-28 symbols 0..27. Under the no-repeat model this IS
     the message channel; if the doublets were masking structure, it must
     show here.
"""
import collections
import math
import numpy as np
from lp_structure import parse, flat, nioc, N, RUNES, R2I

pages = parse("data/page0-58.txt")[:55]
s = flat(pages)
n = len(s)

# --- stream A: dedup ---
A = [s[0]]
removed_pos = []
for i in range(1, n):
    if s[i] == s[i - 1]:
        removed_pos.append(i)
        continue
    A.append(s[i])
print(f"stream A (deduped): {len(A)} runes ({len(removed_pos)} removed)")

# --- stream D: nonzero differences, base 28 ---
D = [((s[i + 1] - s[i]) % N) - 1 for i in range(n - 1) if s[i + 1] != s[i]]
M = 28
print(f"stream D (nonzero diffs, base 28): {len(D)} symbols\n")

def ioc_base(seq, base):
    c = collections.Counter(seq)
    m = len(seq)
    return sum(v * (v - 1) for v in c.values()) / (m * (m - 1)) * base

def chi2_uni(seq, base):
    c = collections.Counter(seq)
    m = len(seq)
    return sum((c[k] - m / base) ** 2 / (m / base) for k in range(base))

def digram_ioc(seq, base, d=1):
    prs = list(zip(seq, seq[d:]))
    c = collections.Counter(prs)
    m = len(prs)
    return sum(v * (v - 1) for v in c.values()) / (m * (m - 1)) * base * base

def kappa_scan(seq, base, maxlag):
    a = np.array(seq)
    out = []
    for d in range(1, maxlag + 1):
        m = len(a) - d
        eq = int((a[:-d] == a[d:]).sum())
        z = (eq - m / base) / math.sqrt(m * (1 / base) * (1 - 1 / base))
        out.append((z, d))
    return out

def periodic_max(seq, base, maxp):
    best = (0, 0)
    for p in range(2, maxp + 1):
        avg = sum(ioc_base(seq[i::p], base) for i in range(p)) / p
        if avg > best[0]:
            best = (avg, p)
    return best

for name, seq, base in (("A dedup", A, N), ("D diffs", D, M)):
    print(f"=== stream {name} (base {base}) ===")
    print(f"unigram chi2: {chi2_uni(seq, base):.1f} (df={base-1})")
    print(f"nIoC: {ioc_base(seq, base):.4f}")
    print(f"digram IoC d=1..6: " + " ".join(f"{digram_ioc(seq, base, d):.4f}" for d in range(1, 7)))
    ks = kappa_scan(seq, base, 3000)
    ks_sorted = sorted(ks, reverse=True)
    big = [(d, round(z, 2)) for z, d in ks if abs(z) > 3.5]
    print(f"kappa lags 1..3000: |z|>3.5 at {big if big else 'none'} "
          f"(expect ~{3000*2*(1-0.999767):.1f} by chance); top: {[(d, round(z,2)) for z,d in ks_sorted[:3]]}")
    mx, mp = periodic_max(seq, base, 80)
    print(f"max periodic avg-column IoC p=2..80: {mx:.4f} at p={mp}")
    # doublet rate of the stream itself
    d0 = sum(1 for i in range(len(seq) - 1) if seq[i] == seq[i + 1])
    e = (len(seq) - 1) / base
    zz = (d0 - e) / math.sqrt((len(seq) - 1) * (1 / base) * (1 - 1 / base))
    print(f"own doublets: {d0} exp {e:.0f} z={zz:+.2f}")
    print()

print("=== subgroup structure of D (28 = 4 x 7) ===")
for m in (2, 4, 7, 14):
    proj = [x % m for x in D]
    print(f"D mod {m}: chi2={chi2_uni(proj, m):.2f} (df={m-1})", end="   ")
print()
for m in (2, 4, 7):
    proj = [x // (28 // m) for x in D]
    print(f"D div-bucket {m}: chi2={chi2_uni(proj, m):.2f}", end="   ")
print("\n")

print("=== keystream sweep on D (mod 28), both signs ===")
def sieve(limit):
    pr = []; isc = bytearray(limit)
    for i in range(2, limit):
        if not isc[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                isc[j] = 1
    return pr
PR = sieve(200000)
PI = "14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
fib = [1, 1]
while len(fib) < len(D) + 5:
    fib.append((fib[-1] + fib[-2]) % M)
streams = {
    "primes": [p % M for p in PR[:len(D)]],
    "totient": [(p - 1) % M for p in PR[:len(D)]],
    "index": [i % M for i in range(len(D))],
    "fib": fib[:len(D)],
    "pi": [int(c) % M for c in PI * (len(D) // len(PI) + 1)][:len(D)],
}
for nm, k in streams.items():
    b = 0
    for sign in (-1, 1):
        t = [(D[i] + sign * k[i]) % M for i in range(len(D))]
        b = max(b, ioc_base(t, M))
    print(f"{nm:8s}: best nIoC {b:.4f}")

print("\n=== splice points of A: do the 86 new adjacencies carry structure? ===")
# After dedup, position of each splice in A; check the diff at splices
Apos = []
ai = 0
rp = set(removed_pos)
for i in range(n):
    if i in rp:
        continue
    Apos.append(i)
splice_diffs = []
for j in range(1, len(A)):
    if Apos[j] - Apos[j - 1] == 2:  # a removal happened between
        splice_diffs.append((A[j] - A[j - 1]) % N)
c = collections.Counter(splice_diffs)
m = len(splice_diffs)
chi = sum((c[k] - m / 28) ** 2 / (m / 28) for k in range(1, N))
print(f"{m} splice diffs, chi2 vs uniform-28: {chi:.1f} (df=27)")
print("splice diff counts:", dict(sorted(c.items())))

print("\n=== was something hiding at lag 2 of A (old lag-2 became adjacent)? ===")
# compare digram IoC of A vs original s at small distances
for d in range(1, 5):
    print(f"d={d}: A {digram_ioc(A, N, d):.4f}  vs original {digram_ioc(s, N, d):.4f}")
