#!/usr/bin/env python3
"""Battery 10: discriminating evidence between mechanism families.

1. Cicada's own plaintext doubling stats (from plain/mono segments of master LP).
2. Doublet position profile in unsolved corpus: uniform vs plaintext-double profile.
3. Triplets.
4. P(consecutive equal mod 29) of candidate keystreams (S1 residual requirement).
5. Running-key doublet rate.
"""
import collections
import math
from lp_structure import parse, flat, nioc, N, RUNES, R2I

# ---------- 1. plaintext/mono segments of the master transcription ----------
with open("data/liber-primus__transcription--master.txt") as f:
    master = f.read()

print("=== master transcription $-segments: nIoC and doublet stats ===")
plain_words = []
for i, seg in enumerate(master.split("$")):
    runes = [R2I[c] for c in seg if c in R2I]
    if len(runes) < 80:
        continue
    v = nioc(runes)
    tag = ""
    if v > 1.35:  # plaintext or monoalphabetic -> doublet-preserving
        tag = "  <-- plain/mono"
        # collect words for profile
        cur = []
        for ch in seg:
            if ch in R2I:
                cur.append(R2I[ch])
            elif ch in "-./%&\n" or ch.isalnum():
                if cur:
                    plain_words.append(cur)
                    cur = []
        if cur:
            plain_words.append(cur)
    print(f"seg {i:2d}: n={len(runes):5d} nIoC={v:.3f}{tag}")

def pair_profile(words):
    fp = sum(1 for w in words if len(w) >= 2 and w[0] == w[1])
    nfp = sum(1 for w in words if len(w) >= 2)
    it = sum(1 for w in words for i in range(1, len(w) - 1) if w[i] == w[i + 1])
    nit = sum(max(0, len(w) - 2) for w in words)
    cb = sum(1 for a, b in zip(words, words[1:]) if a[-1] == b[0])
    ncb = len(words) - 1
    return (fp, nfp), (it, nit), (cb, ncb)

n_pl = sum(len(w) for w in plain_words)
(fp, nfp), (it, nit), (cb, ncb) = pair_profile(plain_words)
tot_d = fp + it + cb
tot_p = nfp + nit + ncb
print(f"\nCicada plain/mono corpus: {n_pl} runes, {len(plain_words)} words")
print(f"plaintext doublet rate: {tot_d}/{tot_p} = {tot_d/tot_p*100:.2f}%")
print(f"  first-pair: {fp}/{nfp} = {fp/max(nfp,1)*100:.2f}%   interior: {it}/{nit} = {it/nit*100:.2f}%   cross-word: {cb}/{ncb} = {cb/ncb*100:.2f}%")
print(f"  doublet position mix: first {fp/max(tot_d,1)*100:.0f}% interior {it/max(tot_d,1)*100:.0f}% cross {cb/max(tot_d,1)*100:.0f}%")
dbl_runes = collections.Counter()
for w in plain_words:
    for i in range(len(w) - 1):
        if w[i] == w[i + 1]:
            dbl_runes[RUNES[w[i]]] += 1
print("  doubled runes:", dict(dbl_runes.most_common()))

# ---------- 2. unsolved corpus doublet position profile ----------
pages = parse("data/page0-58.txt")[:55]
words = [w for p in pages for w in p]
s = flat(pages)
n = len(s)
(fp, nfp), (it, nit), (cb, ncb) = pair_profile(words)
print(f"\n=== unsolved corpus doublet profile ===")
print(f"first-pair: {fp}/{nfp} ({fp/nfp*100:.2f}%)  interior: {it}/{nit} ({it/nit*100:.2f}%)  cross-word: {cb}/{ncb} ({cb/ncb*100:.2f}%)")
tot_d = fp + it + cb
print(f"position mix: first {fp/tot_d*100:.0f}% interior {it/tot_d*100:.0f}% cross {cb/tot_d*100:.0f}%")
print(f"uniform-null mix would be: first {nfp/(nfp+nit+ncb)*100:.0f}% interior {nit/(nfp+nit+ncb)*100:.0f}% cross {ncb/(nfp+nit+ncb)*100:.0f}%")
# chi2 of observed mix vs uniform-by-opportunity
exp = [tot_d * nfp / (nfp + nit + ncb), tot_d * nit / (nfp + nit + ncb), tot_d * ncb / (nfp + nit + ncb)]
chi2 = sum((o - e) ** 2 / e for o, e in zip((fp, it, cb), exp))
print(f"chi2 vs uniform-opportunity: {chi2:.2f} (df=2)")

# ---------- 3. triplets ----------
trip = sum(1 for i in range(n - 2) if s[i] == s[i + 1] == s[i + 2])
print(f"\ntriplets (ccc): {trip}  (chance given doublets: ~{86*86/n:.2f}; chance uniform: {(n-2)/N/N:.1f})")

# ---------- 4. keystream consecutive-equal rates mod 29 ----------
def sieve(limit):
    pr = []
    is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr
PR = sieve(200000)[:13000]
PI = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
streams = {
    "random": None,
    "primes mod29": [p % N for p in PR],
    "totient(primes) mod29": [(p - 1) % N for p in PR],
    "prime gaps": [(PR[i + 1] - PR[i]) % N for i in range(len(PR) - 1)],
    "pi digits": [int(c) for c in PI * 130],
    "fib mod29": None,
    "index mod29": [i % N for i in range(13000)],
}
fib = [1, 1]
for _ in range(13000):
    fib.append(fib[-1] + fib[-2])
streams["fib mod29"] = [f % N for f in fib[:13000]]
print("\n=== P(k[i+1]==k[i] mod 29) for candidate keystreams (S1 needs ~0.19) ===")
for name, k in streams.items():
    if k is None:
        if name == "random":
            print(f"{name:22s}: {1/N:.3f}")
        continue
    eq = sum(1 for i in range(len(k) - 1) if k[i] == k[i + 1])
    print(f"{name:22s}: {eq/(len(k)-1):.3f}")

# ---------- 5. running-key doublet rate ----------
big = collections.Counter()
tot = 0
with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
    for line in f:
        g, c = line.split()
        g = g.replace("ᛂ", "ᛄ")
        d = (R2I[g[1]] - R2I[g[0]]) % N
        big[d] += int(c)
        tot += int(c)
P = [big[d] / tot for d in range(N)]
rk_vig = sum(P[d] * P[(-d) % N] for d in range(N))   # c=p+k: dbl iff dp=-dk
rk_beau = sum(P[d] * P[d] for d in range(N))          # c=k-p: dbl iff dk=dp
print(f"\nrunning-key (runeglish key) doublet rate: Vigenere {rk_vig*100:.2f}%  Beaufort {rk_beau*100:.2f}%")
print(f"(observed LP: 0.66%; independent-additive floor: min-bin {min(P)*100:.2f}%)")
