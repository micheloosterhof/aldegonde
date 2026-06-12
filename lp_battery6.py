#!/usr/bin/env python3
"""Battery 6: Monte-Carlo gematria test, transition independence, doublet spacing, repeats."""
import collections
import math
import random
from lp_structure import parse, flat, nioc, N, RUNES

pages = parse("data/page0-58.txt")
pages = pages[:56]
words = [w for p in pages for w in p]
s = flat(pages)
n = len(s)

def sieve(limit):
    pr = []
    is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr

GP = sieve(200)[:29]

def gem_chi2(wordlist, m):
    d = collections.Counter(sum(GP[r] for r in w) % m for w in wordlist)
    mm = len(wordlist)
    return sum((d.get(k, 0) - mm / m) ** 2 / (mm / m) for k in range(m))

print("=== gematria word-sum chi2 vs Monte-Carlo null (shuffled runes, same word lengths) ===")
random.seed(42)
lens = [len(w) for w in words]
for m in (29, 59, 28, 30):
    obs = gem_chi2(words, m)
    null = []
    for _ in range(200):
        sh = s[:]
        random.shuffle(sh)
        ws, pos = [], 0
        for L in lens:
            ws.append(sh[pos:pos + L])
            pos += L
        null.append(gem_chi2(ws, m))
    null.sort()
    pr = sum(1 for x in null if x >= obs) / len(null)
    print(f"mod {m}: obs={obs:.1f} null median={null[100]:.1f} null95={null[190]:.1f} p={pr:.3f}")

print("\n=== transition matrix: is diff distribution independent of current rune? ===")
# contingency 29x28 (current rune x nonzero diff), chi2 test of independence
table = [[0] * N for _ in range(N)]
for i in range(n - 1):
    table[s[i]][(s[i + 1] - s[i]) % N] += 1
chi2 = 0.0
rows = [sum(r) for r in table]
cols = [sum(table[r][c] for r in range(N)) for c in range(N)]
T = sum(rows)
for r in range(N):
    for c in range(N):
        e = rows[r] * cols[c] / T
        chi2 += (table[r][c] - e) ** 2 / e
df = (N - 1) * (N - 1)
print(f"chi2={chi2:.1f} df={df} (mean {df}, sd {math.sqrt(2*df):.0f}, z={(chi2-df)/math.sqrt(2*df):+.2f})")

print("\n=== doublet positions: spacing and parity ===")
dpos = [i for i in range(n - 1) if s[i] == s[i + 1]]
print(f"{len(dpos)} doublets; position mod 2: {collections.Counter(p % 2 for p in dpos)}")
gaps = [b - a for a, b in zip(dpos, dpos[1:])]
print(f"gap stats: min={min(gaps)} max={max(gaps)} mean={sum(gaps)/len(gaps):.0f} (geometric expected mean {n/len(dpos):.0f})")
print("gaps<=10:", sorted(g for g in gaps if g <= 10))

print("\n=== repeated n-grams (isomorph channel) ===")
for L in (4, 5, 6, 7, 8):
    grams = collections.Counter(tuple(s[i:i + L]) for i in range(n - L + 1))
    obs_pairs = sum(v * (v - 1) // 2 for v in grams.values())
    m = n - L + 1
    exp_pairs = m * (m - 1) / 2 / (N ** L)
    print(f"L={L}: repeated-pairs obs={obs_pairs} exp={exp_pairs:.1f}")

print("\n=== pattern-isomorphs within words (e.g. ABAB / ABCA shape counts) ===")
def shape(w):
    m = {}
    out = []
    for r in w:
        if r not in m:
            m[r] = len(m)
        out.append(m[r])
    return tuple(out)
random.seed(7)
obs_shapes = collections.Counter(shape(w) for w in words if len(w) in (4, 5, 6))
# null: shuffled stream
null_tot = collections.Counter()
REP = 50
sh = s[:]
for _ in range(REP):
    random.shuffle(sh)
    ws, pos = [], 0
    for L in lens:
        if L in (4, 5, 6):
            null_tot[shape(sh[pos:pos + L])] += 1
        pos += L
flag = 0
for sp, o in obs_shapes.most_common():
    e = null_tot[sp] / REP
    if e >= 1:
        z = (o - e) / math.sqrt(e)
        if abs(z) > 3:
            print(f"shape {sp}: obs={o} exp={e:.1f} z={z:+.1f}")
            flag += 1
print(f"(shapes with |z|>3: {flag} out of {len(obs_shapes)})")

print("\n=== which page hit nIoC>1.2 with primes c-k? ===")
PR = sieve(200000)
for j, pg in enumerate(pages):
    ps = [r for w in pg for r in w]
    if len(ps) < 50:
        continue
    p = [(ps[i] - PR[i]) % N for i in range(len(ps))]
    v = nioc(p)
    if v > 1.15:
        print(f"page {j}: n={len(ps)} nIoC={v:.3f}")
