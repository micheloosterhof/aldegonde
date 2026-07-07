#!/usr/bin/env python3
"""Battery 13: deterministic collision-restep decryption.

Model: c[i] = p[i] +/- k[j], j advances 1 per rune, PLUS an extra advance
around each OBSERVED doublet (the rule fired and still collided / lapsed).
Variants: extra +1 after doublet, +1 before, +2, +29. Score with runeglish
unigram LL per page (key restarts per page) and over the whole corpus.
"""
import math
import collections
import numpy as np
from lp_structure import parse, flat, N, R2I

pages = parse("data/page0-58.txt")[:55]
s = flat(pages)

def sieve(limit):
    pr = []; is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr
PR = sieve(300000)

uni = collections.Counter()
with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
    for line in f:
        g, c = line.split(); g = g.replace("ᛂ", "ᛄ")
        uni[R2I[g]] += int(c)
tot = sum(uni.values())
LL = np.array([math.log((uni[i] + 1) / tot) - math.log(1 / N) for i in range(N)])

PI = "14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
E = "27182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320030599218174135966290435729003342952605956307381323286279434907632338298807531952510190"
mx = 30000
fib = [1, 1]
while len(fib) < mx:
    fib.append((fib[-1] + fib[-2]) % N)
lucas = [2, 1]
while len(lucas) < mx:
    lucas.append((lucas[-1] + lucas[-2]) % N)
STREAMS = {
    "primes": np.array(PR[:mx]) % N,
    "totient": (np.array(PR[:mx]) - 1) % N,
    "index": np.arange(mx) % N,
    "tri": np.array([i * (i + 1) // 2 for i in range(mx)]) % N,
    "fib": np.array(fib[:mx]) % N,
    "lucas": np.array(lucas[:mx]) % N,
    "pi": np.array([int(c) for c in PI * (mx // len(PI) + 1)][:mx]),
    "e": np.array([int(c) for c in E * (mx // len(E) + 1)][:mx]),
    "2^i": np.array([pow(2, i, N) for i in range(mx)]),
}

def key_indices(cs, mode):
    """key index j(i) for each rune position, with extra advances at doublets."""
    j = 0
    out = []
    for i, c in enumerate(cs):
        if i > 0 and cs[i] == cs[i - 1]:
            if mode == "after":
                pass  # extra advance applied after emitting (below)
            elif mode == "before+1":
                j += 1
            elif mode == "before+2":
                j += 2
            elif mode == "before+29":
                j += 29
        out.append(j)
        j += 1
        if mode == "after" and i > 0 and cs[i] == cs[i - 1]:
            j += 1
    return np.array(out)

null_mu, null_sd = 0.0, math.sqrt(float(np.mean(LL ** 2)) - float(np.mean(LL)) ** 2)
print("per-rune null LL gain: mu=%.4f sd=%.4f" % (float(np.mean(LL)), null_sd))

print("\n=== corpus-wide (key continuous over all 55 pages) ===")
best = []
cs = s
for mode in ("none", "before+1", "before+2", "before+29", "after"):
    ji = key_indices(cs, mode)
    for name, K in STREAMS.items():
        for sign in (-1, 1):
            dec = (np.array(cs) + sign * K[ji]) % N
            g = float(LL[dec].sum())
            zz = (g - len(cs) * float(np.mean(LL))) / (null_sd * math.sqrt(len(cs)))
            best.append((zz, mode, name, sign))
best.sort(reverse=True)
for zz, mode, name, sign in best[:8]:
    print(f"z={zz:+5.2f} mode={mode:10s} {name} {'-' if sign<0 else '+'}")

print("\n=== per-page (key restarts each page), top combos by max page z ===")
results = []
for mode in ("none", "before+1", "before+2", "before+29", "after"):
    for name, K in STREAMS.items():
        for sign in (-1, 1):
            zs = []
            for pj, pg in enumerate(pages):
                cs = [r for w in pg for r in w]
                ji = key_indices(cs, mode)
                dec = (np.array(cs) + sign * K[ji]) % N
                g = float(LL[dec].sum())
                zz = (g - len(cs) * float(np.mean(LL))) / (null_sd * math.sqrt(len(cs)))
                zs.append((zz, pj))
            zs.sort(reverse=True)
            results.append((zs[0][0], mode, name, sign, zs[:3]))
results.sort(reverse=True)
ntests = 5 * len(STREAMS) * 2 * 55
print(f"({ntests} page-tests; need max z ~> 4.4 after correction)")
for zz, mode, name, sign, top in results[:8]:
    print(f"max page z={zz:+5.2f} mode={mode:10s} {name} {'-' if sign<0 else '+'} top {[(round(a,2),b) for a,b in top]}")
