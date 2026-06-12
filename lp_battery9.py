#!/usr/bin/env python3
"""Battery 9: prefix attack + drift-tolerant (Viterbi) keystream attack."""
import collections
import math
import random
from lp_structure import parse, flat, nioc, N, RUNES, R2I

pages = parse("data/page0-58.txt")[:55]

def sieve(limit):
    pr = []
    is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr
PR = sieve(50000)

# runeglish unigram log-probs
uni = collections.Counter()
with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
    for line in f:
        g, c = line.split()
        g = g.replace("ᛂ", "ᛄ")
        uni[R2I[g]] += int(c)
tot = sum(uni.values())
LP_ = [math.log((uni[i] + 1) / tot) for i in range(N)]
LL_UNIF = math.log(1 / N)

def ll_gain(seq):
    return sum(LP_[x] - LL_UNIF for x in seq)

maxlen = max(sum(len(w) for w in p) for p in pages) + 30
fib = [1, 1]
while len(fib) < maxlen + 5:
    fib.append(fib[-1] + fib[-2])
PI = "14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
streams = {
    "primes": PR[:maxlen],
    "totient": [p - 1 for p in PR[:maxlen]],
    "primes+1": [p + 1 for p in PR[:maxlen]],
    "fib": fib[:maxlen],
    "index": list(range(maxlen)),
    "pi": [int(c) for c in (PI * 3)[:maxlen]],
}

print("=== prefix attack: decrypt first K runes of each page, sum LL gain over pages ===")
random.seed(5)
for K in (15, 25):
    # Monte-Carlo null: LL gain of K uniform-random runes
    null = []
    for _ in range(2000):
        null.append(sum(ll_gain([random.randrange(N)]) for _ in range(K)))
    mu = sum(null) / len(null)
    sd = math.sqrt(sum((x - mu) ** 2 for x in null) / len(null))
    print(f"\nK={K}: null per-page LL mu={mu:.2f} sd={sd:.2f}; corpus z uses sqrt(55)*sd")
    for name, k in streams.items():
        for sign in (-1, 1):
            tot_ll = 0.0
            best = []
            for j, pg in enumerate(pages):
                ps = [r for w in pg for r in w][:K]
                dec = [(c + sign * k[i]) % N for i, c in enumerate(ps)]
                g = ll_gain(dec)
                tot_ll += g
                best.append((g, j))
            z = (tot_ll - 55 * mu) / (math.sqrt(55) * sd)
            best.sort(reverse=True)
            note = f" top pages {[(round(g,1),j) for g,j in best[:3]]}" if z > 3 else ""
            print(f"  {name:9s} {'-' if sign<0 else '+'}: total LL={tot_ll:8.1f} z={z:+5.2f}{note}")

print("\n=== Viterbi drift attack: c[i] decrypted with k[i+drift], drift non-decreasing ===")
# state: drift d in 0..DMAX; at each position may stay or +1 (penalty); emission = unigram LL
DMAX = 25
SKIP_LOGP = math.log(0.05)   # prior prob of a skip at any position
STAY_LOGP = math.log(0.95)

def viterbi_page(cs, key, sign):
    m = len(cs)
    NEG = -1e18
    cur = [NEG] * (DMAX + 1)
    cur[0] = 0.0
    for i in range(m):
        nxt = [NEG] * (DMAX + 1)
        for d in range(DMAX + 1):
            if cur[d] == NEG:
                continue
            # emit with drift d
            e = LP_[(cs[i] + sign * key[i + d]) % N] - LL_UNIF
            # stay
            v = cur[d] + e + STAY_LOGP
            if v > nxt[d]:
                nxt[d] = v
            # skip (advance drift) before emitting
            if d + 1 <= DMAX:
                e2 = LP_[(cs[i] + sign * key[i + d + 1]) % N] - LL_UNIF
                v2 = cur[d] + e2 + SKIP_LOGP
                if v2 > nxt[d + 1]:
                    nxt[d + 1] = v2
        cur = nxt
    return max(cur)

random.seed(9)
# null distribution: random pages
nulls = []
for _ in range(60):
    cs = [random.randrange(N) for _ in range(236)]
    nulls.append(viterbi_page(cs, PR, -1))
mu = sum(nulls) / len(nulls)
sd = math.sqrt(sum((x - mu) ** 2 for x in nulls) / len(nulls))
print(f"null (random 236-rune page, primes-): mu={mu:.1f} sd={sd:.1f}")

for name in ("primes", "totient", "fib", "index"):
    k = streams[name]
    for sign in (-1, 1):
        scores = []
        for j, pg in enumerate(pages):
            cs = [r for w in pg for r in w]
            sc = viterbi_page(cs, k, sign)
            # normalize roughly by length
            scores.append((sc - mu * len(cs) / 236, j, len(cs)))
        scores.sort(reverse=True)
        top = [(round(sc, 1), j) for sc, j, L in scores[:3]]
        print(f"{name:8s} {'-' if sign<0 else '+'}: top pages {top}")

# sanity: does viterbi light up on the SOLVED page 55 (re-parse with it included)?
all_pages = parse("data/page0-58.txt")
p55 = [r for w in all_pages[55] for r in w]
print(f"\nsanity solved page55, totient-: viterbi={viterbi_page(p55, streams['totient'], -1):.1f} (null mu~{mu*len(p55)/236:.0f} sd~{sd:.0f})")
