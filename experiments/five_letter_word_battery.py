#!/usr/bin/env python3
# ABOUTME: Test battery on the length-5 words of the clean corpus — the exact
# ABOUTME: one-period unit of the letter walk — isolating the g^1..g^4 phase
# ABOUTME: diagonals and the word-bounded (first,last)=g^4 frame pair (d4).
"""Length-5 words: the clean one-period probe of the letter walk.

A 5-letter word spans phases 0,1,2,3,4 exactly once, with no g^5=id
wraparound. Under the length-clocked walk (`length-clocked-walk.md`) the
within-word coincidence rate at distance d = b - a measures g's d-th
diagonal: c_a = c_b iff p_a = g^d(p_b). So the ten within-frame pairs
decompose by distance into direct measurements of g^1..g^4:

  d=1  (0,1)(1,2)(2,3)(3,4)   adjacent — the tuned rare diagonal (doublets)
  d=2  (0,2)(1,3)(2,4)        g^2
  d=3  (0,3)(1,4)             g^3
  d=4  (0,4)                  g^4 = g^-1 — the FIRST/LAST frame pair (d4)

The (0,4) pair is the word-bounded form of the d4 anomaly (the corpus's
one standing +1.85 sigma cell, `mixed-cycle-progression.md`). The d4
anatomy so far used STREAM 5-grams; this uses WORD-aligned 5-frames, a
different plaintext table (word first x last), and tells whether the d4
lean is a word-frame effect or a stream artifact.

Null: shuffle each word's runes internally (preserves per-word rune
multiset, randomizes position) — the honest position-blind baseline,
since a word with a repeated rune coincides at any distance more often
by composition alone.
"""

from __future__ import annotations

import math
import random
from collections import Counter

from d5_partial_leak import to_runeglish
from doublet_position_profile import IDX_ENG
from ea_direction_test import PROSE_CACHE, prose_words
from lp_corpus import load_clean

M = 29
NPERM = 5000
RNG = random.Random(3301)


def words_by_length(L):
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    return [d[k] for k in sorted(d) if len(d[k]) == L]


def register_five_letter_words():
    """Real runeglish 5-rune words from the prose register."""
    out = []
    for w in prose_words(PROSE_CACHE):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if len(r) == 5:
            out.append(r)
    return out


def ioc(seq):
    c = Counter(seq)
    n = len(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1) / M) / M \
        if n > 1 else 0.0


def chi2_uniform(seq):
    c = Counter(seq)
    n = len(seq)
    e = n / M
    return sum((c.get(r, 0) - e) ** 2 / e for r in range(M))


def coincidence_by_distance(words):
    """Observed within-frame coincidence counts/opportunities per distance."""
    hit = {d: 0 for d in range(1, 5)}
    opp = {d: 0 for d in range(1, 5)}
    for w in words:
        for a in range(5):
            for b in range(a + 1, 5):
                d = b - a
                opp[d] += 1
                hit[d] += w[a] == w[b]
    return hit, opp


def perm_null(words):
    """Within-word-shuffle null for the per-distance coincidence counts."""
    dists = range(1, 5)
    samples = {d: [] for d in dists}
    for _ in range(NPERM):
        h = {d: 0 for d in dists}
        for w in words:
            s = w[:]
            RNG.shuffle(s)
            for a in range(5):
                for b in range(a + 1, 5):
                    if s[a] == s[b]:
                        h[b - a] += 1
        for d in dists:
            samples[d].append(h[d])
    return samples


def z_and_p(obs, null):
    mu = sum(null) / len(null)
    sd = (sum((x - mu) ** 2 for x in null) / len(null)) ** 0.5
    ge = sum(1 for x in null if x >= obs)
    p_hi = (ge + 1) / (len(null) + 1)
    z = (obs - mu) / sd if sd else 0.0
    return mu, sd, z, p_hi


def main():
    W = words_by_length(5)
    runes = [r for w in W for r in w]
    print(f"length-5 words: {len(W)}  ({len(runes)} runes)\n")

    print("== concatenated-stream fingerprint ==")
    print(f"  IoC (normalized): {ioc(runes):.4f}  (flat = 1.00)")
    chi = chi2_uniform(runes)
    print(f"  unigram chi2 vs uniform: {chi:.1f}  (df 28, "
          f"mean 28, ~1.6 sd = {28 + 1.65 * (2*28)**0.5:.0f})")

    print("\n== per-position (phase) unigram uniformity ==")
    for k in range(5):
        col = [w[k] for w in W]
        print(f"  position {k} (phase {k}): chi2 {chi2_uniform(col):.1f} "
              f"(n={len(col)})")

    print("\n== within-frame coincidence by distance (= g^d diagonal) ==")
    hit, opp = coincidence_by_distance(W)
    null = perm_null(W)
    print(f"  {'d':>2} {'phase rel':>10} {'obs':>5} {'opp':>4} "
          f"{'rate':>7} {'null rate':>10} {'z':>6} {'p(>=)':>7}")
    rel = {1: 'g^1', 2: 'g^2', 3: 'g^3', 4: 'g^4=g^-1'}
    for d in range(1, 5):
        mu, sd, z, p = z_and_p(hit[d], null[d])
        print(f"  {d:>2} {rel[d]:>10} {hit[d]:>5} {opp[d]:>4} "
              f"{hit[d]/opp[d]:>7.4f} {mu/opp[d]:>10.4f} {z:>6.2f} {p:>7.4f}")

    print("\n== the (0,4) frame pair — word-bounded d4, in detail ==")
    obs04 = sum(1 for w in W if w[0] == w[4])
    null04 = []
    for _ in range(NPERM):
        c = 0
        for w in W:
            s = w[:]
            RNG.shuffle(s)
            c += s[0] == s[4]
        null04.append(c)
    mu, sd, z, p = z_and_p(obs04, null04)
    print(f"  first == last rune: {obs04}/{len(W)} = {obs04/len(W):.4f}")
    print(f"  within-word-shuffle null: {mu:.1f} +- {sd:.1f}  "
          f"(z = {z:+.2f}, p(>=) = {p:.4f})")
    print(f"  corpus-wide d4 leans +1.85 sigma; here z = {z:+.2f} "
          f"on {len(W)} word frames")

    print("\n== plaintext control: register 5-letter words ==")
    print("  (ciphertext coincidence at distance d leaks plaintext p_a=p_b")
    print("  through g^d's fixed points; if plaintext already coincides more")
    print("  at d=3,4, the cipher elevation is fixed-point leak, not anomaly)")
    pt5 = register_five_letter_words()
    RNG.shuffle(pt5)
    pt5 = pt5[:2000]          # cap for the permutation null's cost
    print(f"  register length-5 words (sampled): {len(pt5)}")
    phit, popp = coincidence_by_distance(pt5)
    pnull = perm_null(pt5)
    print(f"  {'d':>2} {'obs':>5} {'opp':>5} {'rate':>7} {'null':>7} {'z':>6}")
    for d in range(1, 5):
        mu, sd, z, p = z_and_p(phit[d], pnull[d])
        print(f"  {d:>2} {phit[d]:>5} {popp[d]:>5} {phit[d]/popp[d]:>7.4f} "
              f"{mu/popp[d]:>7.4f} {z:>6.2f}")

    print("\n== interpretation ==")
    print("  d=1 rare -> adjacent doublet suppression present in 5-frames;")
    print("  compare the cipher d=3,4 z-scores against the plaintext control:")
    print("  if plaintext shows the same d=3,4 lean, the cipher elevation is")
    print("  fixed-point leak of a plaintext positional effect (expected");
    print("  under the walk); if plaintext is flat there, it is anomalous.")


if __name__ == "__main__":
    main()
