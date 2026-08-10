#!/usr/bin/env python3
# ABOUTME: Two-gear cipher model for the unsolved Liber Primus: one order-5 rune
# ABOUTME: gear g (doublets + lag-5 echo) and one per-word gear h (word-locality).
"""Two-gear cipher: doublets and the lag-5 echo from one permutation.

    c[i] = base( h^w( g^(i mod 5)( p[i] ) ) )

    g : mixed permutation of ORDER 5 (five 5-cycles + 4 fixed points),
        advanced by a GLOBAL rune counter that never resets
    h : mixed permutation advanced one step per WORD (order chosen from the
        divisors of 1449, the DJU-BEI word distance)
    base : fixed mixed permutation

Both anomalies come from g itself:
  - its DIAGONAL: adjacent runes differ by one g-step, so a doublet is
    p[i-1] = g(p[i]); the 5-cycles are chosen to route that onto rare English
    bigrams. The counter never resets, so the seam between words carries the
    same relation (composed with one h-step) -> boundary-blind suppression.
  - its ORDER: g^5 = id, so positions 5 apart share the g-power; same word
    -> same h-power -> identical alphabet -> the English within-word d5
    coincidence leaks through. Different word -> the h-step breaks it ->
    cross-word d5 at chance.

This script (1) computes the doublet floor CONSTRAINED to order-5 g (vs the
unconstrained 0.13% and the observed 0.66%), (2) tunes h so the five seam
diagonals are also rare, and (3) runs the COMPLETE battery, including the
cross-word checks that falsified the per-word related-alphabet model:
within/seam d1, within/cross d5, d2-4, unigram IoC, columns, periodic IoC,
and doublet flatness by position-in-word mod 5.
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

LEN_DIST = {
    1: 99,
    2: 465,
    3: 726,
    4: 514,
    5: 318,
    6: 252,
    7: 214,
    8: 159,
    9: 77,
    10: 51,
    11: 28,
    12: 18,
    13: 4,
    14: 3,
}


# ---------- data ----------


def load_bigrams() -> np.ndarray:
    b = np.zeros((M, M))
    with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
        for line in f:
            p = line.split()
            if len(p) == 2 and len(p[0]) == 2 and all(c in ALPH for c in p[0]):
                b[R2I[p[0][0]], R2I[p[0][1]]] += float(p[1])
    return b / b.sum()


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
        words.append(stream[i : i + length])
        i += length
    return words


# ---------- permutation tooling ----------


def perm_from_cycles(cycle_lengths: list[int], rng: random.Random) -> list[int]:
    """Random permutation with the given cycle type (lengths must sum to 29)."""
    elems = list(range(M))
    rng.shuffle(elems)
    p = [0] * M
    pos = 0
    for length in cycle_lengths:
        cyc = elems[pos : pos + length]
        for k in range(length):
            p[cyc[k]] = cyc[(k + 1) % length]
        pos += length
    return p


def conj_swap(p: list[int], x: int, y: int) -> list[int]:
    """Conjugate p by the transposition (x y) -- preserves the cycle type."""
    t = list(range(M))
    t[x], t[y] = y, x
    return [t[p[t[i]]] for i in range(M)]


def tune(p: list[int], objective, rng: random.Random, iters: int = 30000) -> list[int]:
    """Hill-climb over conjugates (cycle type preserved)."""
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


def ppow(p: list[int], k: int) -> list[int]:
    out = list(range(M))
    for _ in range(k):
        out = [p[x] for x in out]
    return out


# ---------- the cipher ----------


def encipher(words, g, h, base) -> list[list[int]]:
    gp = [ppow(g, k) for k in range(5)]
    hw = list(range(M))  # h^0
    out = []
    i = 0
    for w in words:
        cw = []
        for p in w:
            cw.append(base[hw[gp[i % 5][p]]])
            i += 1
        out.append(cw)
        hw = [hw[h[x]] for x in range(M)]  # h^(w+1)
    return out


# ---------- the complete battery ----------


def ioc(seq) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    c = Counter(seq)
    return M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def battery(ct_words) -> None:
    stream = [x for w in ct_words for x in w]
    wid = []
    for wi, w in enumerate(ct_words):
        wid += [wi] * len(w)
    n = len(stream)

    def rate(d: int, *, same_word: bool) -> tuple[int, int]:
        m = e = 0
        for i in range(n - d):
            if (wid[i] == wid[i + d]) == same_word:
                e += 1
                m += stream[i] == stream[i + d]
        return m, e

    print(f"  unigram IoC: {ioc(stream):.3f}   (target 1.00)")
    for d, sw, target in (
        (1, True, 0.0063),
        (1, False, 0.0079),
        (2, True, 0.034),
        (3, True, 0.034),
        (4, True, 0.034),
        (5, True, 0.049),
        (5, False, 0.030),
    ):
        m, e = rate(d, same_word=sw)
        where = "within" if sw else "cross "
        print(f"  d{d} {where}: {m:4d}/{e:<6d} = {m / e:.4f}   (LP {target})")
    cols = [round(ioc([w[j] for w in ct_words if len(w) > j]), 2) for j in range(3)]
    print(f"  columns 0-2 IoC: {cols}   (target ~1.0)")
    pioc = [round(sum(ioc(stream[k::p]) for k in range(p)) / p, 2) for p in (2, 5, 7)]
    print(f"  periodic IoC p=2,5,7: {pioc}   (target ~1.0, no period)")
    # doublet flatness by position-in-word mod 5
    dbl = Counter()
    elig = Counter()
    for w in ct_words:
        for j in range(1, len(w)):
            elig[j % 5] += 1
            dbl[j % 5] += w[j] == w[j - 1]
    rates = [f"{dbl[m] / elig[m]:.4f}" if elig[m] else "-" for m in range(5)]
    print(f"  within-word doublet rate by pos mod 5: {rates}   (target flat)")


def main() -> None:
    rng = random.Random(SEED)
    B = load_bigrams()

    # --- g: order-5 (five 5-cycles + 4 fixed points), diagonal tuned rare ---
    rows, cols = linear_sum_assignment(B)
    print(f"doublet floor, unconstrained permutation: {B[rows, cols].sum():.4f}")

    def g_obj(g):
        return sum(B[g[x], x] for x in range(M))

    g = min(
        (tune(perm_from_cycles([5] * 5 + [1] * 4, rng), g_obj, rng) for _ in range(6)),
        key=g_obj,
    )
    fixed = [x for x in range(M) if g[x] == x]
    print(
        f"doublet floor, ORDER-5 constrained:       {g_obj(g):.4f}   "
        f"(observed LP 0.0066)"
    )
    print(f"  g fixed points: {[c3301.CICADA_ENGLISH_ALPHABET[x] for x in fixed]}")

    # --- h: order 63 (cycles 9,7,7,3,3; 63 | 1449), seam diagonals tuned ---
    gp = [ppow(g, k) for k in range(5)]
    gi = [ppow(g, (5 - k) % 5) for k in range(5)]  # g^-k = g^(5-k)

    def h_obj(h):
        # seam doublet: g^a(u) = h(g^(a+1)(v))  ->  u = g^-a(h(g^(a+1)(v)))
        total = 0.0
        for a in range(5):
            total += sum(B[gi[a][h[gp[(a + 1) % 5][v]]], v] for v in range(M))
        return total / 5

    h = min(
        (tune(perm_from_cycles([9, 7, 7, 3, 3], rng), h_obj, rng) for _ in range(4)),
        key=h_obj,
    )
    print(
        f"seam-diagonal mean (h tuned, order 63):   {h_obj(h):.4f}   "
        f"(observed seam rate 0.0079)\n"
    )

    # --- generate and measure ---
    base = list(range(M))
    rng.shuffle(base)
    words = cut_words(gen_plaintext(load_trigram(), 40000, rng), rng)
    pt_stream = [x for w in words for x in w]
    print(
        f"plaintext: {len(words)} words, {len(pt_stream)} runes, "
        f"IoC {ioc(pt_stream):.2f}"
    )
    print("\nTWO-GEAR CIPHER  c[i] = base(h^w(g^(i mod 5)(p[i]))):")
    battery(encipher(words, g, h, base))


if __name__ == "__main__":
    main()
