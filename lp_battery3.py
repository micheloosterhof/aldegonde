#!/usr/bin/env python3
"""Battery 3: word/sentence/line/page anchored statistics."""
import collections
import math
from lp_structure import parse, flat, ioc, nioc, N, R2I

pages = parse("data/page0-58.txt")
words = [w for p in pages for w in p]
s = flat(pages)
n = len(s)

def z_ioc(seq):
    # z-score of nIoC vs uniform-random null: var of IoC approx
    m = len(seq)
    pairs = m * (m - 1) / 2
    p = 1 / N
    mu = p
    sd = math.sqrt(p * (1 - p) / pairs)  # approx, ignoring pair dependence
    return (ioc(seq) - mu) / sd

print("=== IoC of runes at fixed position within words ===")
for pos in range(8):
    seq = [w[pos] for w in words if len(w) > pos]
    print(f"pos {pos}: n={len(seq):5d} nIoC={nioc(seq):.4f} z={z_ioc(seq):+.2f}")
seq = [w[-1] for w in words]
print(f"last : n={len(seq):5d} nIoC={nioc(seq):.4f} z={z_ioc(seq):+.2f}")

print("\n=== IoC of position-in-word columns, by word length ===")
for L in range(1, 9):
    ws = [w for w in words if len(w) == L]
    if len(ws) < 30:
        continue
    iocs = [f"{nioc([w[i] for w in ws]):.3f}" for i in range(L)]
    print(f"len {L} (n={len(ws)}): {' '.join(iocs)}")

print("\n=== repeated whole ciphertext words ===")
wt = collections.Counter(tuple(w) for w in words)
rep = {k: v for k, v in wt.items() if v > 1 and len(k) >= 2}
# expected number of repeated words under uniform random by length
bylen = collections.Counter(len(w) for w in words)
print("len | #words | #distinct-repeated | E[#pairs] uniform | obs pairs")
for L in range(1, 13):
    ws = [tuple(w) for w in words if len(w) == L]
    m = len(ws)
    if m < 2:
        continue
    c = collections.Counter(ws)
    obs_pairs = sum(v * (v - 1) // 2 for v in c.values())
    exp_pairs = m * (m - 1) / 2 / (N ** L)
    nrep = sum(1 for v in c.values() if v > 1)
    print(f"{L:3d} | {m:5d} | {nrep:3d} | {exp_pairs:9.2f} | {obs_pairs}")
top = sorted(rep.items(), key=lambda kv: (-kv[1], -len(kv[0])))[:10]
for k, v in top:
    print("  repeated:", "".join("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"[i] for i in k), f"x{v} len={len(k)}")

print("\n=== aligned-position kappa between consecutive pages (key restart per page?) ===")
tot = eq = 0
for a, b in zip(pages, pages[1:]):
    fa, fb = [r for w in a for r in w], [r for w in b for r in w]
    L = min(len(fa), len(fb))
    eq += sum(1 for i in range(L) if fa[i] == fb[i])
    tot += L
print(f"consecutive pages aligned: {eq}/{tot} exp {tot/N:.1f} z={(eq-tot/N)/math.sqrt(tot*(1/N)*(1-1/N)):+.2f}")

tot = eq = 0
for i in range(len(pages)):
    for j in range(i + 1, len(pages)):
        fa = [r for w in pages[i] for r in w]
        fb = [r for w in pages[j] for r in w]
        L = min(len(fa), len(fb))
        eq += sum(1 for k in range(L) if fa[k] == fb[k])
        tot += L
print(f"all page pairs aligned:    {eq}/{tot} exp {tot/N:.1f} z={(eq-tot/N)/math.sqrt(tot*(1/N)*(1-1/N)):+.2f}")

print("\n=== aligned kappa between consecutive words (key restart per word?) ===")
tot = eq = 0
for a, b in zip(words, words[1:]):
    L = min(len(a), len(b))
    eq += sum(1 for i in range(L) if a[i] == b[i])
    tot += L
print(f"consecutive words: {eq}/{tot} exp {tot/N:.1f} z={(eq-tot/N)/math.sqrt(tot*(1/N)*(1-1/N)):+.2f}")

# all word pairs of same length (sampled)
import itertools, random
random.seed(1)
tot = eq = 0
for L in range(2, 10):
    ws = [w for w in words if len(w) == L]
    for a, b in itertools.combinations(ws, 2):
        eq += sum(1 for i in range(L) if a[i] == b[i])
        tot += L
print(f"all same-length word pairs: {eq}/{tot} exp {tot/N:.1f} z={(eq-tot/N)/math.sqrt(tot*(1/N)*(1-1/N)):+.2f}")

print("\n=== sentence-initial / word stats ===")
# sentences: split on '.' in raw text
with open("data/page0-58.txt") as f:
    raw = f.read()
sent = []
cur = []
for ch in raw:
    if ch in R2I:
        cur.append(R2I[ch])
    elif ch == ".":
        if cur:
            sent.append(cur)
            cur = []
if cur:
    sent.append(cur)
print(f"{len(sent)} sentences, first-rune nIoC: {nioc([x[0] for x in sent]):.3f} z={z_ioc([x[0] for x in sent]):+.2f}")

print("\n=== per-page IoC and per-section ($) IoC ===")
vals = [nioc([r for w in p for r in w]) for p in pages]
print("page nIoC: min %.3f max %.3f mean %.3f" % (min(vals), max(vals), sum(vals) / len(vals)))
hi = [(i, round(v, 3)) for i, v in enumerate(vals) if v > 1.15]
print("pages with nIoC>1.15:", hi)

segs = raw.split("$")
print(f"{len(segs)} $-segments:")
for i, sg in enumerate(segs):
    rr = [R2I[c] for c in sg if c in R2I]
    if len(rr) > 60:
        print(f"  seg {i}: n={len(rr)} nIoC={nioc(rr):.4f} z={z_ioc(rr):+.2f}")

print("\n=== word-length sequence structure ===")
wl = [len(w) for w in words]
# autocorrelation of word lengths
mu = sum(wl) / len(wl)
var = sum((x - mu) ** 2 for x in wl) / len(wl)
for d in range(1, 6):
    cov = sum((wl[i] - mu) * (wl[i + d] - mu) for i in range(len(wl) - d)) / (len(wl) - d)
    print(f"wordlen autocorr lag {d}: {cov/var:+.3f}", end="  ")
print()
