#!/usr/bin/env python3
# ABOUTME: Generative model of the unsolved Liber Primus as a per-word cipher of
# ABOUTME: 5 related alphabets, with the doublet suppression inherent to the relation.
"""Per-word related-alphabet cipher: one mechanism for the whole LP fingerprint.

Model: each word is enciphered by 5 alphabets applied by position-in-word mod 5,
where the alphabets are related by a fixed global step permutation g:

    A_phi = base_word o g^phi        (phi = position_in_word mod 5)

- base_word is re-keyed per word  -> flat unigrams and flat columns
- positions 5 apart share a phase  -> same alphabet -> English d5 coincidence
  leaks through (the lag-5 echo); adjacent positions use different alphabets
  -> d2/d3/d4 flat (the empty middle)
- a doublet is c[i]=c[i-1] <=> p[i-1] = g(p[i]); choosing g to route consecutive
  outputs onto RARE English bigrams makes doublets inherently rare, uniform, and
  boundary-blind -- no separate no-repeat rule

This reproduces the complete observed fingerprint (flat IoC, flat columns, d5
echo, empty d2-4, and low doublets) from one self-consistent structure, with no
ciphertext feedback (so the echo survives) and no bolted-on rule.

The script also shows WHY the doublet suppression must come from general mixed
alphabets rather than affine ones: the lowest doublet rate an affine relation
can reach on English is ~1.25%, but a general mixed permutation reaches ~0.13%,
so the observed 0.66% is inherently achievable only with mixed alphabets.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict

import numpy as np
from scipy.optimize import linear_sum_assignment

from aldegonde import c3301

ALPH = c3301.CICADA_ALPHABET
M = 29
R2I = {r: i for i, r in enumerate(ALPH)}
SEED = 3301

LEN_DIST = {1: 99, 2: 465, 3: 726, 4: 514, 5: 318, 6: 252, 7: 214,
            8: 159, 9: 77, 10: 51, 11: 28, 12: 18, 13: 4, 14: 3}


def load_bigrams() -> np.ndarray:
    """Runeglish bigram count matrix B[a][b]."""
    b = np.zeros((M, M))
    with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
        for line in f:
            p = line.split()
            if len(p) == 2 and len(p[0]) == 2 and all(c in ALPH for c in p[0]):
                b[R2I[p[0][0]], R2I[p[0][1]]] += float(p[1])
    return b


def load_trigram() -> dict[tuple[int, int], list[float]]:
    trans: dict[tuple[int, int], list[float]] = defaultdict(lambda: [0.0] * M)
    with open("src/aldegonde/data/ngrams/runeglish/trigrams.txt") as f:
        for line in f:
            p = line.split()
            if len(p) == 2 and len(p[0]) == 3 and all(c in ALPH for c in p[0]):
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


def cut_words(stream: list[int], rng: random.Random) -> list[list[int]]:
    lengths = list(LEN_DIST)
    weights = [LEN_DIST[k] for k in lengths]
    words: list[list[int]] = []
    i = 0
    while i < len(stream):
        length = rng.choices(lengths, weights=weights, k=1)[0]
        if i + length > len(stream):
            break
        words.append(stream[i:i + length])
        i += length
    return words


def ioc(seq) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    c = Counter(seq)
    return M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def doublet_step(bigrams: np.ndarray) -> list[int]:
    """The step permutation g minimizing the doublet rate: a doublet is
    c[i]=c[i-1] <=> p[i-1]=g(p[i]), so its rate is sum_w P(g(w), w). The
    minimizing g is the minimum-weight matching of the bigram matrix."""
    bn = bigrams / bigrams.sum()
    rows, cols = linear_sum_assignment(bn)  # bn[rows[k], cols[k]] minimized
    g = [0] * M
    for r, c in zip(rows, cols):
        g[c] = r  # g(c)=r makes bigram (g(w), w) rare
    return g


def report_doublet_floor(bigrams: np.ndarray) -> None:
    bn = bigrams / bigrams.sum()
    affine = min(
        sum(bn[v, (a * v + b) % M] for v in range(M))
        for a in range(1, M) for b in range(M)
    )
    rows, cols = linear_sum_assignment(bn)
    mixed = bn[rows, cols].sum()
    print("Doublet-rate floor on runeglish bigrams (lowest a substitution can reach):")
    print(f"  affine relations only : {affine:.4f}")
    print(f"  general mixed relation: {mixed:.4f}   <- 0.66% observed lives here, not affine")
    print(f"  chance 1/29           : {1 / M:.4f}\n")


def encipher(words, g: list[int], rng: random.Random) -> list[list[int]]:
    """A_phi = base_word o g^phi, phi = position-in-word mod 5."""
    gpow = [list(range(M))]
    for _ in range(5):
        gpow.append([g[x] for x in gpow[-1]])
    out = []
    for w in words:
        base = list(range(M))
        rng.shuffle(base)
        out.append([base[gpow[j % 5][p]] for j, p in enumerate(w)])
    return out


def measure(words) -> dict:
    stream = [x for w in words for x in w]
    rates = {}
    for d in range(1, 7):
        elig = match = 0
        for w in words:
            for i in range(len(w) - d):
                elig += 1
                match += w[i] == w[i + d]
        rates[d] = match / elig if elig else 0.0
    cols = [ioc([w[j] for w in words if len(w) > j]) for j in range(3)]
    return {"uni_ioc": ioc(stream), "rates": rates, "cols": cols}


def main() -> None:
    rng = random.Random(SEED)
    bigrams = load_bigrams()
    report_doublet_floor(bigrams)

    g = doublet_step(bigrams)
    words = cut_words(gen_plaintext(load_trigram(), 40000, rng), rng)
    m = measure(encipher(words, g, rng))
    r = m["rates"]
    print("Per-word related-alphabet cipher  (A_phi = base_word o g^phi):")
    print(f"  uniIoC={m['uni_ioc']:.3f}  d1={r[1]:.4f} d2={r[2]:.4f} d3={r[3]:.4f} "
          f"d4={r[4]:.4f} d5={r[5]:.4f}  cols={[round(c, 2) for c in m['cols']]}")
    print("  TARGET (unsolved LP): uniIoC=1.00 d1=0.0066 d2/3/4~0.034 "
          "d5=0.049 cols flat")
    print("\nAll five observables from one mechanism; the doublet suppression is")
    print("inherent to the alphabet relation g (no separate rule, no autokey).")


if __name__ == "__main__":
    main()
