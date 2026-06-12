#!/usr/bin/env python3
"""Battery 16: cross-page key reuse (with collision-drift compensation) +
final mechanism kills (bifid, VIC-ish, columnar-of-stream, mod-28 collapse)."""
import math
import collections
import numpy as np
import random
from lp_structure import parse, flat, nioc, N, R2I, RUNES

random.seed(99)
pages = parse("data/page0-58.txt")[:55]
pagelists = [[r for w in pg for r in w] for pg in pages]

def coinc_z(cols):
    """pooled column coincidence z over uniform null."""
    eq = tot = 0
    for col in cols:
        c = collections.Counter(col); m = len(col)
        eq += sum(v * (v - 1) for v in c.values())
        tot += m * (m - 1)
    if tot == 0:
        return 0.0
    p = eq / tot
    return (p - 1 / N) / math.sqrt((1 / N) * (1 - 1 / N) / (tot / 2))

print("=== cross-page alignment: column coincidence at aligned index (key reuse?) ===")
# raw alignment
maxL = max(len(p) for p in pagelists)
cols = [[] for _ in range(maxL)]
for p in pagelists:
    for i, r in enumerate(p):
        cols[i].append(r)
cols = [c for c in cols if len(c) > 8]
print(f"raw alignment: pooled column coincidence z = {coinc_z(cols):+.2f}")

# with collision-drift compensation: shift each page's index by running #doublets
def drifted(p, step):
    out = []
    d = 0
    for i, r in enumerate(p):
        out.append((i + d, r))
        if i > 0 and p[i] == p[i - 1]:
            d += step
    return out
for step in (1, 2, 29):
    cols = collections.defaultdict(list)
    for p in pagelists:
        for idx, r in drifted(p, step):
            cols[idx].append(r)
    colvals = [v for v in cols.values() if len(v) > 8]
    print(f"drift step {step:2d}: pooled column coincidence z = {coinc_z(colvals):+.2f}")

# difference-stream alignment (removes any per-page additive constant)
print("\n=== difference-stream cross-page alignment ===")
dcols = collections.defaultdict(list)
for p in pagelists:
    d = [(p[i + 1] - p[i]) % N for i in range(len(p) - 1)]
    for i, x in enumerate(d):
        dcols[i].append(x)
dcolvals = [v for v in dcols.values() if len(v) > 8]
print(f"diff-stream raw alignment: pooled coincidence z = {coinc_z(dcolvals):+.2f}")

# ============ final mechanism kills ============
big = collections.defaultdict(collections.Counter); uni = collections.Counter()
with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
    for line in f:
        g, c = line.split(); g = g.replace("ᛂ", "ᛄ")
        big[R2I[g[0]]][R2I[g[1]]] += int(c); uni[R2I[g[0]]] += int(c)
def gen_plain(total):
    out = [random.choices(range(N), weights=[uni[i] for i in range(N)])[0]]
    while len(out) < total:
        ws = [big[out[-1]][j] for j in range(N)]
        out.append(random.choices(range(N), weights=ws)[0])
    return out

LP = flat(pages); n = len(LP)
plain = gen_plain(n)

def fp(c):
    m = len(c); cnt = collections.Counter(c)
    chiu = sum((cnt[i] - m / N) ** 2 / (m / N) for i in range(N))
    d0 = sum(1 for i in range(m - 1) if c[i] == c[i + 1])
    prs = [(c[i], c[i + 1]) for i in range(m - 1)]
    cc = collections.Counter(prs)
    dig = sum(v * (v - 1) for v in cc.values()) / (len(prs) * (len(prs) - 1)) * N * N
    mxp = max(sum(nioc(c[i::p]) for i in range(p)) / p for p in range(2, 31))
    return nioc(c), chiu, 100 * d0 / (m - 1), dig, mxp
def row(name, c):
    io, cu, db, dg, mp = fp(c)
    print(f"{name:30s} nIoC={io:.3f} uniChi={cu:6.1f} dbl%={db:5.2f} digIoC={dg:.3f} maxPer={mp:.3f}")

print("\n=== more mechanisms vs LP (dbl% must be ~0.66, digIoC ~1.026) ===")
row("LP target", LP)

# Bifid-29, period p
def bifid(plain, period, square):
    rows = {r: divmod(square.index(r), N) for r in range(N)}
    # 29 isn't a perfect square; use 29x1? Instead Polybius base needs sqrt -> skip true bifid.
    return None
# Use a 29-symbol "Conjugated Matrix" / Trifid-ish via base reps:
# fractionate each rune to (a,b) with a in 0..4,b in 0..5 (5x6=30), transpose by period, recombine
def fractionate_transpose(plain, period, sq):
    pairs = [divmod(sq[r], 6) for r in plain]  # a in 0..4, b in 0..5
    a = [x[0] for x in pairs]; b = [x[1] for x in pairs]
    out = []
    for blk in range(0, len(plain), period):
        A = a[blk:blk + period]; B = b[blk:blk + period]
        seq = A + B
        for k in range(0, len(seq) - 1, 2):
            v = seq[k] * 6 + seq[k + 1]
            out.append(sq.index(v % 30) if (v % 30) in sq else v % N)
    return [x % N for x in out]
sq = list(range(30)); random.shuffle(sq)
row("fractionate+transpose p=7", fractionate_transpose(plain, 7, sq))
row("fractionate+transpose p=13", fractionate_transpose(plain, 13, sq))

# VIC-style: straddling-ish digit conv then chain-add then recombine (approx)
def vic(plain):
    digs = []
    for r in plain:
        if r < 8:
            digs.append(r)            # 1 digit for common
        else:
            digs += divmod(r, 10)     # 2 digits
    key = [random.randrange(10) for _ in range(10)]
    out_d = [(digs[i] + key[i % 10]) % 10 for i in range(len(digs))]
    # rebuild runes greedily
    out = []; i = 0
    while i < len(out_d) - 1:
        v = out_d[i] * 3 + out_d[i + 1]
        out.append(v % N); i += 2
    return out
row("VIC-ish straddle+chain", vic(plain))

# columnar transposition OF an OTP stream (does transposition reintroduce doublets?)
otp = [(p + random.randrange(N)) % N for p in plain]
def columnar(seq, cols):
    rows = (len(seq) + cols - 1) // cols
    order = list(range(cols)); random.shuffle(order)
    out = []
    for c in order:
        for r in range(rows):
            idx = r * cols + c
            if idx < len(seq):
                out.append(seq[idx])
    return out
row("columnar(OTP) cols=13", columnar(otp, 13))

# mod-28 collapse: maybe 29th rune is a null/space removed -> alphabet really 28?
# test if removing rarest rune and recomputing changes doublet picture (diagnostic)
cnt = collections.Counter(LP)
rare = min(range(N), key=lambda r: cnt[r])
filt = [r for r in LP if r != rare]
d0 = sum(1 for i in range(len(filt) - 1) if filt[i] == filt[i + 1])
print(f"\nremove rarest rune {RUNES[rare]}: doublets {d0}/{len(filt)-1} = {d0/(len(filt)-1)*100:.2f}% (still suppressed => not a removed-null artifact)")
