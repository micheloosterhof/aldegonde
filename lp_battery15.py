#!/usr/bin/env python3
"""Battery 15: crib drag + key-fragment structure test.

If the cipher is additive (c = p +/- k) with ANY key, then dragging a known
plaintext crib across the ciphertext yields a candidate key fragment at each
position: k = c -/+ crib. A *correct* placement should produce a key fragment
that is itself meaningful (low entropy / matches a known sequence / repeats).
We don't know the key, but we CAN test whether any crib placement yields a
key fragment with non-random structure (runeglish-like, or constant, or
arithmetic). This is mechanism-agnostic for additive ciphers.

Cribs: common Cicada openers / words, in runeglish.
"""
import math
import collections
import numpy as np
from lp_structure import parse, flat, N, R2I, RUNES

pages = parse("data/page0-58.txt")[:55]
s = np.array(flat(pages))
n = len(s)

# runeglish words -> rune-index sequences. Standard Gematria Primus letter set.
LAT2I = {"F":0,"U":1,"TH":2,"O":3,"R":4,"C":5,"K":5,"G":6,"W":7,"H":8,"N":9,
         "I":10,"J":11,"EO":12,"P":13,"X":14,"S":15,"Z":15,"T":16,"B":17,
         "E":18,"M":19,"L":20,"NG":21,"ING":21,"OE":22,"D":23,"A":24,"AE":25,
         "Y":26,"IA":27,"IO":27,"EA":28}
def to_runes(word):
    word = word.upper()
    out = []
    i = 0
    multi = ["ING","TH","EO","NG","OE","AE","IA","IO","EA"]
    while i < len(word):
        for m in multi:
            if word[i:i+len(m)] == m:
                out.append(LAT2I[m]); i += len(m); break
        else:
            if word[i] in LAT2I:
                out.append(LAT2I[word[i]]); i += 1
            else:
                i += 1
    return out

CRIBS = ["THE","AND","THAT","WITHIN","KNOW","THIS","SACRED","PRIMES","TOTIENT",
         "FUNCTION","ENCRYPTED","SHADOWS","CIRCUMFERENCE","INSTAR","EMERGENCE",
         "WISDOM","TRUTH","DIVINITY","CONSCIOUSNESS","MOBIUS","ANALOG","VOID",
         "CABAL","BUFFERS","CARNAL","ABYSS","FORM","WELCOME","PILGRIM","WARNING",
         "BELIEVE","NOTHING","BOOK","DECEPTION","PRESERVATION","ADHERENCE"]

# runeglish bigram fitness for key fragment
big = collections.Counter(); tot = 0
with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
    for line in f:
        g, c = line.split(); g = g.replace("ᛂ", "ᛄ")
        big[(R2I[g[0]], R2I[g[1]])] = int(c); tot += int(c)
FLOOR = math.log(0.3 / tot)
BLL = np.full((N, N), FLOOR)
for (a, b), v in big.items():
    BLL[a, b] = math.log(v / tot)

def frag_fitness(frag):
    if len(frag) < 2:
        return 0.0
    return sum(BLL[frag[i], frag[i + 1]] for i in range(len(frag) - 1)) / (len(frag) - 1)

# null: fitness of random fragments by length
np.random.seed(0)
null = {}
for L in range(3, 14):
    vals = [frag_fitness(np.random.randint(0, N, L)) for _ in range(3000)]
    null[L] = (float(np.mean(vals)), float(np.std(vals)))

print("=== crib drag: best key-fragment runeglish-fitness z over all placements ===")
print("(additive cipher: if a crib sits correctly, k=c-crib should read runeglish)")
allhits = []
for crib in CRIBS:
    cr = np.array(to_runes(crib))
    L = len(cr)
    if L < 3 or L > 13:
        continue
    mu, sd = null[L]
    best = (-9, -1, "")
    for sign in (-1, 1):
        # k = c - sign*crib  (so c = k + sign*crib)
        for i in range(n - L + 1):
            frag = (s[i:i + L] - sign * cr) % N
            f = frag_fitness(frag)
            z = (f - mu) / sd
            if z > best[0]:
                best = (z, i, "".join(RUNES[x] for x in frag))
    allhits.append((best[0], crib, best[1], best[2]))
allhits.sort(reverse=True)
ntests = sum(2 * (n - len(to_runes(c)) + 1) for c in CRIBS if 3 <= len(to_runes(c)) <= 13)
print(f"total placements tested: {ntests} -> Bonferroni z ~ {(2*math.log(ntests))**0.5:.1f}")
for z, crib, pos, frag in allhits[:12]:
    print(f"  z={z:+5.2f} crib={crib:14s} @pos {pos:5d} keyfrag={frag}")

print("\n=== same, but key fragment must be CONSTANT (monoalpha key) or ARITHMETIC ===")
# correct placement under Vigenere-with-short-key would give a near-constant or
# periodic fragment; measure min within-fragment IoC spike instead.
for crib in ("THE", "WITHIN", "PRIMES", "CIRCUMFERENCE"):
    cr = np.array(to_runes(crib)); L = len(cr)
    arr = []
    for sign in (-1, 1):
        for i in range(n - L + 1):
            frag = (s[i:i + L] - sign * cr) % N
            # arithmetic? constant first difference
            dd = np.diff(frag) % N
            if len(set(dd.tolist())) == 1:
                arr.append((i, sign, "const-diff", frag.tolist()))
    print(f"{crib}: arithmetic-key placements: {len(arr)} (expect ~{2*(n-L+1)/N**(L-2):.2g})")
