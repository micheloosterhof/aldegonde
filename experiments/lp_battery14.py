#!/usr/bin/env python3
"""Battery 14: per-page keystream OFFSET brute force.

For each page and stream family, try all starting offsets 0..NOFF and score
the decryption with runeglish unigram LL (vectorized). The distribution of
scores over wrong offsets self-calibrates the null; a true (stream, offset)
should stand out at z >> 5 (Bonferroni over ~27.5M trials needs ~5.9).
Also tests stride-2 prime streams and reversed streams.
"""
import math
import collections
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from lp_structure import parse, N, R2I

pages = parse("data/page0-58.txt")[:55]

def sieve(limit):
    pr = []; is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr
PR = sieve(400000)

uni = collections.Counter()
with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
    for line in f:
        g, c = line.split(); g = g.replace("ᛂ", "ᛄ")
        uni[R2I[g]] += int(c)
tot = sum(uni.values())
LL = np.array([math.log((uni[i] + 1) / tot) - math.log(1 / N) for i in range(N)])

NOFF = 25000
PI = "14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
E = "27182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320030599218174135966290435729003342952605956307381323286279434907632338298807531952510190"
mxlen = 280
need = NOFF + mxlen + 1
pr = np.array(PR[:need + 10])
STREAMS = {
    "totient": (pr - 1) % N,
    "primes": pr % N,
    "primes-str2": pr[::2][:need] % N,
    "pi": np.array([int(c) for c in PI * (need // len(PI) + 2)][:need]),
    "e": np.array([int(c) for c in E * (need // len(E) + 2)][:need]),
}
STREAMS["totient-rev"] = STREAMS["totient"][::-1].copy()

hits = []
print(f"pages: {len(pages)}, offsets per test: {NOFF}, streams: {list(STREAMS)}")
for name, K in STREAMS.items():
    W = sliding_window_view(K, mxlen)[:NOFF]  # (NOFF, mxlen)
    for sign in (-1, 1):
        allbest = []
        for pj, pg in enumerate(pages):
            cs = np.array([r for w in pg for r in w])
            L = len(cs)
            dec = (cs[None, :] + sign * W[:, :L]) % N
            sc = LL[dec].sum(axis=1)
            mu, sd = float(sc.mean()), float(sc.std())
            z = (sc - mu) / sd
            b = int(z.argmax())
            allbest.append((float(z[b]), pj, b))
            if z[b] > 5.5:
                hits.append((float(z[b]), name, sign, pj, b))
        allbest.sort(reverse=True)
        top = [(round(a, 2), p, o) for a, p, o in allbest[:3]]
        print(f"{name:12s} {'-' if sign<0 else '+'}: top (z,page,offset) {top}")

print(f"\nBonferroni threshold for {len(STREAMS)*2*55*NOFF/1e6:.1f}M trials: z ~ 5.9")
print("HITS above 5.5:", hits if hits else "NONE")

# sanity: the solved page 55 must light up with totient at offset 0
all_pages = parse("data/page0-58.txt")
cs = np.array([r for w in all_pages[55] for r in w])
K = STREAMS["totient"]
W = sliding_window_view(K, len(cs))[:NOFF]
sc = LL[(cs[None, :] - W) % N].sum(axis=1)
z = (sc - sc.mean()) / sc.std()
print(f"\nsanity solved page55 totient-: best offset {int(z.argmax())} z={float(z.max()):.1f}")
