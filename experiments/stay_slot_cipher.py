#!/usr/bin/env python3
# ABOUTME: Head-to-head test of the two lead cipher designs for the unsolved LP:
# ABOUTME: V1 order-5 orbit + group walk, V2 stay-slot orbit (order-4 g, 1-in-5 hold).
"""Two candidate mechanisms, one complete battery.

V1  ORBIT+WALK   c[i] = base_w( g5^(j mod 5)( p[i] ) ),  g5 of order 5,
                 base_{w+1} = base_w o s_k (safe steps s1/s2, a group walk)

V2  STAY-SLOT    within a word the alphabet ADVANCES by g4 (order 4) on four of
                 every five steps and HOLDS once (at per-word keyed slot r_w);
                 any 5 consecutive positions contain exactly one hold, so the
                 net advance over 5 is g4^4 = id -> sharp d5 echo. Doublets:
                 impossible-ish on advance steps (tuned rare diagonal), and on
                 the hold step they are exactly PLAINTEXT doublets -> rate
                 ~ (1/5) x plaintext-doublet-rate, parameter-free. The hold
                 slots within a word are 5 apart -> doublet dead-time inherent.

Both use a per-word base walk (two tuned safe generators) so seams are
suppressed (boundary-blind) and the state count grows without bound (flat
unigrams, flat columns, Kasiski-silent).

Battery targets (clean LP corpus):
  uniIoC 1.000 | d1 within 0.0063 | d1 seam 0.0079 | d2/3/4 ~0.0345
  d5 within 0.049 | d5 cross ~0.030 | columns ~1.00 | periodic IoC ~1.00
  doublets flat by pos mod 5 | doublet min gap 6, no gaps <= 5
  d1 delta chi2 excluding delta0 ~ 41 (df 27, mildly elevated)
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict

from aldegonde import c3301

ALPH = c3301.CICADA_ALPHABET
M = 29
R2I = {r: i for i, r in enumerate(ALPH)}
SEED = 3301

LEN_DIST = {1: 99, 2: 465, 3: 726, 4: 514, 5: 318, 6: 252, 7: 214,
            8: 159, 9: 77, 10: 51, 11: 28, 12: 18, 13: 4, 14: 3}


def load_trigram():
    trans = defaultdict(lambda: [0.0] * M)
    with open("src/aldegonde/data/ngrams/runeglish/trigrams.txt") as f:
        for line in f:
            p = line.split()
            if len(p) == 2 and len(p[0]) == 3 and all(ch in ALPH for ch in p[0]):
                a, b, c = (R2I[ch] for ch in p[0])
                trans[(a, b)][c] += float(p[1])
    return trans


def gen_plaintext(trans, n: int, rng: random.Random) -> list[int]:
    keys = list(trans)
    a, b = rng.choice(keys)
    out = [a, b]
    for _ in range(n - 2):
        w = trans.get((a, b))
        if not w or sum(w) == 0:
            a, b = rng.choice(keys)
            w = trans[(a, b)]
        c = rng.choices(range(M), weights=w, k=1)[0]
        out.append(c)
        a, b = b, c
    return out


def cut_words(stream, rng):
    lengths = list(LEN_DIST)
    weights = [LEN_DIST[k] for k in lengths]
    words = []
    i = 0
    while i < len(stream):
        length = rng.choices(lengths, weights=weights, k=1)[0]
        if i + length > len(stream):
            break
        words.append(stream[i:i + length])
        i += length
    return words


# ---------- permutation tooling ----------

def perm_from_cycles(cycle_lengths, rng):
    elems = list(range(M))
    rng.shuffle(elems)
    p = [0] * M
    pos = 0
    for length in cycle_lengths:
        cyc = elems[pos:pos + length]
        for k in range(length):
            p[cyc[k]] = cyc[(k + 1) % length]
        pos += length
    return p


def conj_swap(p, x, y):
    t = list(range(M))
    t[x], t[y] = y, x
    return [t[p[t[i]]] for i in range(M)]


def tune(p, objective, rng, iters=20000):
    best, bval = p, objective(p)
    for _ in range(iters):
        x, y = rng.randrange(M), rng.randrange(M)
        if x == y:
            continue
        cand = conj_swap(best, x, y)
        v = objective(cand)
        if v < bval:
            best, bval = cand, v
    return best


def ppow(p, k):
    out = list(range(M))
    for _ in range(k):
        out = [p[x] for x in out]
    return out


def pair_matrices(words, dmax=5):
    """Within-word plaintext pair distributions P_d[a][b], d = 1..dmax."""
    mats = {}
    for d in range(1, dmax + 1):
        mat = [[0.0] * M for _ in range(M)]
        tot = 0
        for w in words:
            for i in range(len(w) - d):
                mat[w[i]][w[i + d]] += 1
                tot += 1
        mats[d] = ([[c / tot for c in row] for row in mat], tot)
    return mats


def diag_rate(mat, rel):
    """Rate of pairs (u, v) with u = rel(v)."""
    return sum(mat[rel[v]][v] for v in range(M))


# ---------- ciphers ----------

def encipher_v1(words, g5, base0, steps, stepkey, rng):
    gp = [ppow(g5, k) for k in range(5)]
    base = base0[:]
    out = []
    for wi, w in enumerate(words):
        out.append([base[gp[j % 5][p]] for j, p in enumerate(w)])
        s = steps[stepkey[wi % len(stepkey)]]
        base = [base[s[x]] for x in range(M)]
    return out


def encipher_v2(words, g4, base0, steps, stepkey, rng):
    base = base0[:]
    out = []
    for wi, w in enumerate(words):
        r = rng.randrange(5)  # per-word hold slot
        cw = []
        e = 0
        for j, p in enumerate(w):
            if j > 0 and j % 5 != r:
                e = (e + 1) % 4
            cw.append(base[ppow(g4, e)[p]] if False else base[_G4P[e][p]])
        out.append(cw)
        s = steps[stepkey[wi % len(stepkey)]]
        base = [base[s[x]] for x in range(M)]
    return out


_G4P = None  # set in main: powers of g4


# ---------- battery ----------

def ioc(seq):
    n = len(seq)
    if n < 2:
        return 0.0
    c = Counter(seq)
    return M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def battery(label, ct_words):
    stream = [x for w in ct_words for x in w]
    wid = []
    for wi, w in enumerate(ct_words):
        wid += [wi] * len(w)
    n = len(stream)

    def rate(d, *, same):
        m = e = 0
        for i in range(n - d):
            if (wid[i] == wid[i + d]) == same:
                e += 1
                m += stream[i] == stream[i + d]
        return (m / e if e else 0.0), m, e

    print(f"--- {label} ---")
    print(f"  uniIoC {ioc(stream):.3f} (1.000)", end="  ")
    r1w = rate(1, same=True)[0]
    r1x = rate(1, same=False)[0]
    print(f"d1w {r1w:.4f} (0.0063)  d1seam {r1x:.4f} (0.0079)")
    print(f"  d2w {rate(2, same=True)[0]:.4f}  d3w {rate(3, same=True)[0]:.4f}  "
          f"d4w {rate(4, same=True)[0]:.4f}  (all 0.0345)")
    print(f"  d5w {rate(5, same=True)[0]:.4f} (0.049)   d5x {rate(5, same=False)[0]:.4f} (0.030)")
    cols = [round(ioc([w[j] for w in ct_words if len(w) > j]), 2) for j in range(3)]
    pioc = [round(sum(ioc(stream[k::p]) for k in range(p)) / p, 2) for p in (2, 5)]
    print(f"  cols {cols} (1.0)   periodicIoC p2,p5 {pioc} (1.0)")
    # doublet flatness by pos mod 5, min gap, dead time
    dbl_phase = Counter()
    elig = Counter()
    for w in ct_words:
        for j in range(1, len(w)):
            elig[j % 5] += 1
            dbl_phase[j % 5] += w[j] == w[j - 1]
    phases = [f"{dbl_phase[m] / elig[m]:.4f}" if elig[m] else "-" for m in range(5)]
    dpos = [i for i in range(1, n) if stream[i] == stream[i - 1]]
    gaps = [dpos[k + 1] - dpos[k] for k in range(len(dpos) - 1)]
    small = sum(1 for gp in gaps if gp <= 5)
    print(f"  doublets {len(dpos)}; by pos%5 {phases} (flat)")
    print(f"  doublet gaps<=5: {small}/{len(gaps)}  min gap {min(gaps) if gaps else '-'}"
          f"  (LP: 0 gaps<=5, min 6)")
    # d1 delta chi2 excluding delta0
    dc = Counter((stream[i] - stream[i - 1]) % M for i in range(1, n))
    nz = sum(dc.values()) - dc[0]
    e = nz / (M - 1)
    chi = sum((dc[k] - e) ** 2 / e for k in range(1, M))
    print(f"  d1 delta chi2 excl0: {chi:.1f} df27 (LP 41.4)")
    print()


def main() -> None:
    global _G4P
    rng = random.Random(SEED)
    words = cut_words(gen_plaintext(load_trigram(), 40000, rng), rng)
    mats = pair_matrices(words)
    P1 = mats[1][0]
    pt_dbl = diag_rate(P1, list(range(M)))
    print(f"plaintext: {len(words)} words; plaintext doublet rate {pt_dbl:.4f}")
    print(f"predicted V2 doublet rate (1/5 x that + advance leak): "
          f"~{pt_dbl / 5:.4f}+eps   (LP 0.0066)\n")

    chance = 1 / M

    # V1 tuning: g5 order 5; diag on P1 rare, g^d diag on P_d ~ chance (C5)
    def g5_obj(g):
        v = diag_rate(P1, g) * 3.0
        acc = g
        for d in (2, 3, 4):
            acc = [g[x] for x in acc]
            v += 40.0 * (diag_rate(mats[d][0], acc) - chance) ** 2
        return v

    g5 = min((tune(perm_from_cycles([5] * 5 + [1] * 4, rng), g5_obj, rng)
              for _ in range(4)), key=g5_obj)

    # V2 tuning: g4 order 4 (7 four-cycles + 1 fixed); same objective shape
    def g4_obj(g):
        v = diag_rate(P1, g) * 3.0
        acc = g
        for d in (2, 3):
            acc = [g[x] for x in acc]
            v += 40.0 * (diag_rate(mats[d][0], acc) - chance) ** 2
        return v

    g4 = min((tune(perm_from_cycles([4] * 7 + [1], rng), g4_obj, rng)
              for _ in range(4)), key=g4_obj)
    _G4P = [ppow(g4, k) for k in range(4)]

    print(f"g5 diagonal on P1: {diag_rate(P1, g5):.4f}   "
          f"g4 diagonal on P1: {diag_rate(P1, g4):.4f}")

    # walk generators: tuned so seam diagonals are rare for both schedules
    def seam_obj_for(gpows):
        def obj(s):
            v = 0.0
            for a in range(len(gpows)):
                rel = [gpows[a][s[x]] for x in range(M)]
                v += diag_rate(P1, rel)
            return v / len(gpows)
        return obj

    g5p = [ppow(g5, k) for k in range(5)]
    steps1 = [tune(perm_from_cycles([9, 7, 7, 3, 3], rng),
                   seam_obj_for(g5p), rng, iters=12000) for _ in range(2)]
    steps2 = [tune(perm_from_cycles([9, 7, 7, 3, 3], rng),
                   seam_obj_for(_G4P), rng, iters=12000) for _ in range(2)]
    stepkey = [rng.randrange(2) for _ in range(4096)]

    base0 = list(range(M))
    rng.shuffle(base0)

    battery("V1 ORBIT+WALK (g order 5)",
            encipher_v1(words, g5, base0, steps1, stepkey, rng))
    battery("V2 STAY-SLOT (g order 4, 1-in-5 hold)",
            encipher_v2(words, g4, base0, steps2, stepkey, rng))


if __name__ == "__main__":
    main()
