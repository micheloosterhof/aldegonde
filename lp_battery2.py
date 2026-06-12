#!/usr/bin/env python3
"""Battery 2: dissect the lag-1 difference structure."""
import collections
import math
from lp_structure import parse, flat, nioc, N

pages = parse("data/page0-58.txt")
words = [w for p in pages for w in p]
s = flat(pages)
n = len(s)

def hist_z(pairs):
    m = len(pairs)
    c = collections.Counter(pairs)
    out = []
    for k in range(N):
        mu = m / N
        sd = math.sqrt(m * (1 / N) * (1 - 1 / N))
        out.append((k, c[k], (c[k] - mu) / sd))
    chi2 = sum((c[k] - m / N) ** 2 / (m / N) for k in range(N))
    return out, chi2, m

print("=== (c[i+1]-c[i]) mod 29: full stream ===")
diffs = [(s[i + 1] - s[i]) % N for i in range(n - 1)]
out, chi2, m = hist_z(diffs)
for k, cnt, z in out:
    bar = "#" * int(abs(z))
    print(f"diff {k:2d}: {cnt:4d}  z={z:+6.2f} {'-' if z<0 else '+'}{bar}")
print(f"chi2={chi2:.1f} n={m}")

print("\n=== within-word vs cross-boundary lag-1 pairs ===")
wpairs = []
for w in words:
    for i in range(len(w) - 1):
        wpairs.append((w[i + 1] - w[i]) % N)
bpairs = []
for a, b in zip(words, words[1:]):
    bpairs.append((b[0] - a[-1]) % N)
for name, prs in [("within-word", wpairs), ("cross-boundary", bpairs)]:
    out, chi2, m = hist_z(prs)
    z0 = out[0][2]
    big = [(k, round(z, 1)) for k, _, z in out if abs(z) > 3]
    print(f"{name}: n={m} chi2={chi2:.1f}  z(diff=0)={z0:+.2f}  |z|>3: {big}")

print("\n=== doublet (equal neighbor) rate detail ===")
eq_w = sum(1 for w in words for i in range(len(w) - 1) if w[i] == w[i + 1])
eq_b = sum(1 for a, b in zip(words, words[1:]) if a[-1] == b[0])
print(f"within-word equal pairs: {eq_w} / {len(wpairs)} (exp {len(wpairs)/29:.1f})")
print(f"cross-boundary equal:    {eq_b} / {len(bpairs)} (exp {len(bpairs)/29:.1f})")

print("\n=== is the lag-1 structure stationary across the corpus? ===")
# split stream into 8 chunks, chi2 each
k8 = n // 8
for j in range(8):
    chunk = s[j * k8:(j + 1) * k8]
    d = [(chunk[i + 1] - chunk[i]) % N for i in range(len(chunk) - 1)]
    _, chi2, m = hist_z(d)
    d0 = sum(1 for x in d if x == 0)
    print(f"chunk {j}: chi2={chi2:6.1f}  doublets={d0:3d} (exp {m/29:.0f})")

print("\n=== lag-1 difference structure per PAGE (first 20 pages) ===")
for j, p in enumerate(pages[:57]):
    ps = [r for w in p for r in w]
    d = [(ps[i + 1] - ps[i]) % N for i in range(len(ps) - 1)]
    if len(d) < 50:
        continue
    _, chi2, m = hist_z(d)
    d0 = sum(1 for x in d if x == 0)
    if j < 20 or chi2 > 60:
        print(f"page {j:2d}: n={m:4d} chi2={chi2:6.1f} doublets={d0} (exp {m/29:.1f})")
