#!/usr/bin/env python3
"""Battery 8: boundary homogeneity + simulation of candidate mechanisms."""
import collections
import math
import random
from lp_structure import parse, flat, nioc, N, RUNES, R2I

pages = parse("data/page0-58.txt")[:55]
words = [w for p in pages for w in p]
s = flat(pages)
n = len(s)

print("=== homogeneity of off-diagonal diff distribution: within-word vs cross-word ===")
wd = collections.Counter()
bd = collections.Counter()
for w in words:
    for i in range(len(w) - 1):
        d = (w[i + 1] - w[i]) % N
        if d:
            wd[d] += 1
for a, b in zip(words, words[1:]):
    d = (b[0] - a[-1]) % N
    if d:
        bd[d] += 1
nw, nb = sum(wd.values()), sum(bd.values())
chi2 = 0.0
for k in range(1, N):
    tot = wd[k] + bd[k]
    ew, eb = tot * nw / (nw + nb), tot * nb / (nw + nb)
    chi2 += (wd[k] - ew) ** 2 / ew + (bd[k] - eb) ** 2 / eb
print(f"2x28 homogeneity chi2={chi2:.1f} df=27 (within n={nw}, cross n={nb})")

print("\n=== doublet rate by position of pair within word ===")
first = sum(1 for w in words if len(w) >= 2 and w[0] == w[1])
nfirst = sum(1 for w in words if len(w) >= 2)
inter = sum(1 for w in words for i in range(1, len(w) - 1) if w[i] == w[i + 1])
ninter = sum(max(0, len(w) - 2) for w in words)
for name, o, m in [("first-pair", first, nfirst), ("interior", inter, ninter)]:
    e = m / N
    print(f"{name}: {o}/{m} exp {e:.1f} z={(o-e)/math.sqrt(m*(1/N)*(1-1/N)):+.2f}")

# ---------- simulations ----------
# build Markov-1 runeglish generator from bigram table
big = collections.defaultdict(collections.Counter)
uni = collections.Counter()
with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
    for line in f:
        g, c = line.split()
        g = g.replace("ᛂ", "ᛄ")
        big[R2I[g[0]]][R2I[g[1]]] += int(c)
        uni[R2I[g[0]]] += int(c)

random.seed(123)
def gen_plain(total):
    out = [random.choices(range(N), weights=[uni[i] for i in range(N)])[0]]
    while len(out) < total:
        prev = out[-1]
        ws = [big[prev][j] for j in range(N)]
        out.append(random.choices(range(N), weights=ws)[0])
    return out

lens = [len(w) for w in words]
plain = gen_plain(n)

def stats(c, label):
    m = len(c)
    d0 = sum(1 for i in range(m - 1) if c[i] == c[i + 1])
    diffs = collections.Counter((c[i + 1] - c[i]) % N for i in range(m - 1))
    chi2_all = sum((diffs[k] - (m - 1) / N) ** 2 / ((m - 1) / N) for k in range(N))
    off = m - 1 - diffs[0]
    chi2_off = sum((diffs[k] - off / 28) ** 2 / (off / 28) for k in range(1, N))
    cnt = collections.Counter(c)
    chi2_uni = sum((cnt[i] - m / N) ** 2 / (m / N) for i in range(N))
    # lag-2 coincidence
    d2 = sum(1 for i in range(m - 2) if c[i] == c[i + 2])
    z2 = (d2 - (m - 2) / N) / math.sqrt((m - 2) * (1 / N) * (1 - 1 / N))
    print(f"{label:28s} nIoC={nioc(c):.4f} unigram-chi2={chi2_uni:6.1f} doublets={d0:3d}({d0/(m-1)*100:.2f}%) "
          f"diff-chi2-off={chi2_off:6.1f} lag2-z={z2:+.1f}")

print("\n=== simulations (n=%d, same length), target = LP clean corpus ===" % n)
stats(s, "LP clean corpus")
stats(plain, "plaintext (Markov runeglish)")

# Model A: Wheatstone-style two mixed disks, outer 29 runes (no space), always advance >=1
def wheatstone(plain, outer_perm, inner_perm, ratio_outer=N, ratio_inner=N):
    pos_out = 0
    pos_in = 0
    out = []
    opos = {r: i for i, r in enumerate(outer_perm)}
    for p in plain:
        target = opos[p]
        adv = (target - pos_out) % ratio_outer
        if adv == 0:
            adv = ratio_outer  # full revolution for repeated letter
        pos_out = target
        pos_in = (pos_in + adv) % ratio_inner
        out.append(inner_perm[pos_in])
    return out

op = list(range(N)); random.shuffle(op)
ip = list(range(N)); random.shuffle(ip)
cw = wheatstone(plain, op, ip)
stats(cw, "Wheatstone 29/29 mixed")

# Model A2: inner ring of 28? not possible with 29 symbols; instead inner advances adv+1
def wheatstone2(plain, outer_perm, inner_perm):
    pos_out = 0; pos_in = 0; out = []
    opos = {r: i for i, r in enumerate(outer_perm)}
    for p in plain:
        target = opos[p]
        adv = (target - pos_out) % N
        if adv == 0:
            adv = N
        pos_out = target
        pos_in = (pos_in + adv + 1) % N  # gear offset
        out.append(inner_perm[pos_in])
    return out
cw2 = wheatstone2(plain, op, ip)
stats(cw2, "Wheatstone 29/29 gear+1")

# Model B: OTP + rejection (re-key if output equals previous output)
def otp_reject(plain):
    out = []
    prev = None
    for p in plain:
        c = (p + random.randrange(N)) % N
        while c == prev:
            c = (p + random.randrange(N)) % N
        # allow tiny failure rate? strict here
        out.append(c)
        prev = c
    return out
stats(otp_reject(plain), "OTP + strict no-doublet")

# Model C: autokey ciphertext, mixed TR: c[i] = perm[(p[i] + c[i-1]) % N]
def ct_autokey(plain, perm):
    out = []
    prev = 0
    for p in plain:
        c = perm[(p + prev) % N]
        out.append(c)
        prev = c
    return out
pp = list(range(N)); random.shuffle(pp)
stats(ct_autokey(plain, pp), "ciphertext-autokey mixedTR")

# Model D: plain Vigenere with random (OTP) key, no rejection - control
stats([(p + random.randrange(N)) % N for p in plain], "pure OTP control")
