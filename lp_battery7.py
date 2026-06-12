#!/usr/bin/env python3
"""Battery 7: locate long repeats; confirm page-55 prime shift; clean-corpus recheck."""
import collections
import math
from lp_structure import parse, flat, nioc, N, RUNES

pages = parse("data/page0-58.txt")
allpages = pages
words_per_page = [sum(len(w) for w in p) for p in pages]
print("runes per page:", words_per_page)

def sieve(limit):
    pr = []
    is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr

PR = sieve(10000)

# --- confirm page 55 ---
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IO","EA"]
p55 = [r for w in allpages[55] for r in w]
dec = [(c - PR[i]) % N for i, c in enumerate(p55)]
print("page55 c-primes:", "".join(LAT[x] for x in dec))
dec2 = [(c - (PR[i] - 1)) % N for i, c in enumerate(p55)]
print("page55 c-totient:", "".join(LAT[x] for x in dec2))

# --- clean corpus: drop solved pages 55,56 ---
pages = pages[:55]
s = flat(pages)
n = len(s)
print(f"\nclean corpus: {len(pages)} pages, {n} runes")

# page boundaries in flat index
bounds = []
acc = 0
for p in pages:
    acc += sum(len(w) for w in p)
    bounds.append(acc)
def page_of(i):
    for j, b in enumerate(bounds):
        if i < b:
            return j
    return len(bounds) - 1

print("\n=== long repeats in clean corpus ===")
for L in (5, 6, 7, 8):
    grams = collections.defaultdict(list)
    for i in range(n - L + 1):
        grams[tuple(s[i:i + L])].append(i)
    m = n - L + 1
    exp_pairs = m * (m - 1) / 2 / (N ** L)
    obs = [(g, pos) for g, pos in grams.items() if len(pos) > 1]
    print(f"L={L}: exp pairs {exp_pairs:.2f}, found {sum(len(p)*(len(p)-1)//2 for _,p in obs)}")
    if L >= 6:
        for g, pos in obs:
            txt = "".join(RUNES[x] for x in g)
            dists = [b - a for a, b in zip(pos, pos[1:])]
            print(f"  {txt} at {pos} (pages {[page_of(x) for x in pos]}) dist {dists} factors?")

print("\n=== recheck headline stats on clean corpus ===")
print(f"nIoC: {nioc(s):.4f}")
d0 = sum(1 for i in range(n - 1) if s[i] == s[i + 1])
z = (d0 - (n - 1) / N) / math.sqrt((n - 1) * (1 / N) * (1 - 1 / N))
print(f"doublets: {d0} exp {(n-1)/N:.0f} z={z:+.1f}")
diffs = collections.Counter((s[i + 1] - s[i]) % N for i in range(n - 1))
m = n - 1
chi2_all = sum((diffs[k] - m / N) ** 2 / (m / N) for k in range(N))
chi2_off = sum((diffs[k] - (m - diffs[0]) / 28) ** 2 / ((m - diffs[0]) / 28) for k in range(1, N))
print(f"diff chi2 all={chi2_all:.1f}; off-diagonal vs uniform-28: {chi2_off:.1f} (df=27)")
top = sorted(((diffs[k], k) for k in range(1, N)), reverse=True)
print("top off-diag diffs:", top[:5], "bottom:", top[-3:])
