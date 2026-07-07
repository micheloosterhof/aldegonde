#!/usr/bin/env python3
"""Verification of the within-word distance-5 coincidence excess.

Reproduces every number in hypotheses/within-word-d5-coincidence.md:

1. Decontaminated counts (clean corpus = sections 0-9 of page0-58.txt)
   with exact binomial p-values.
2. Boundary-permutation null: the rune stream is kept exactly as published
   (preserving ALL stream correlations, including global lag-5 structure and
   the doublet suppression); only each section's word-length sequence is
   shuffled before re-cutting into words. This isolates the claim "word
   boundaries align with distance-5 coincidences".
3. The same permutation test at every distance d=1..8 (multiple-comparison
   context: d=5 must be the only one that fires).
4. Per-section breakdown, distinct-word count, and the bigram-repeat-at-d5
   statistic with its own permutation null.
"""

from __future__ import annotations

import random
import statistics

from scipy.stats import binom

from aldegonde import c3301

M = 29
R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
RUNES = set(R2I)
WORD_BOUNDARIES = set("-.&%")  # '/' and newline are line wraps, not boundaries

N_PERMS = 10000


def parse_clean_sections(path: str = "data/page0-58.txt"):
    """Words per $-section, clean cipher corpus only (sections 0-9).

    Sections 10 (solved AN END page) and 11 (plaintext Parable) are excluded
    — see cryptodiagnostics-page0-58.md.
    """
    with open(path) as f:
        text = f.read()
    sec_words: list[list[list[int]]] = [[]]
    cur: list[int] = []
    for ch in text:
        if ch in RUNES:
            cur.append(R2I[ch])
        elif ch == "$":
            if cur:
                sec_words[-1].append(cur)
                cur = []
            sec_words.append([])
        elif ch in WORD_BOUNDARIES and cur:
            sec_words[-1].append(cur)
            cur = []
    if cur:
        sec_words[-1].append(cur)
    return [s for s in sec_words if s][:10]


def cut_stats(stream: list[int], lens: list[int], d: int):
    """(coincidence hits at distance d, words with >=1 hit, bigram repeats)."""
    hits = wordhits = bigr = 0
    pos = 0
    for length in lens:
        w = stream[pos : pos + length]
        h = 0
        for k in range(length - d):
            if w[k] == w[k + d]:
                h += 1
                if k + d + 1 < length and w[k + 1] == w[k + d + 1]:
                    bigr += 1
        hits += h
        wordhits += 1 if h else 0
        pos += length
    return hits, wordhits, bigr


def main() -> None:
    sec_words = parse_clean_sections()
    streams = [[x for w in s for x in w] for s in sec_words]
    lenseqs = [[len(w) for w in s] for s in sec_words]
    rng = random.Random(1279)

    # 1. exact binomial on the clean corpus
    hits, _, _ = (sum(x) for x in zip(
        *(cut_stats(st, ls, 5) for st, ls in zip(streams, lenseqs)),
    ))
    trials = sum(max(0, length - 5) for ls in lenseqs for length in ls)
    print(f"clean corpus within-word d=5: {hits}/{trials} = {hits/trials:.3%}"
          f"  (1/29 = {1/M:.3%})")
    print(f"  exact binomial P(>= {hits}) = {binom.sf(hits - 1, trials, 1/M):.2e}")

    # 2+3. boundary-permutation null at every distance
    print(f"\nboundary-permutation null ({N_PERMS} perms per distance):")
    for d in range(1, 9):
        obs = sum(cut_stats(st, ls, d)[0]
                  for st, ls in zip(streams, lenseqs))
        null = []
        for _ in range(N_PERMS):
            tot = 0
            for st, ls in zip(streams, lenseqs):
                ls2 = ls[:]
                rng.shuffle(ls2)
                tot += cut_stats(st, ls2, d)[0]
            null.append(tot)
        mu = statistics.mean(null)
        sd = statistics.pstdev(null)
        p_hi = sum(1 for x in null if x >= obs) / N_PERMS
        p_lo = sum(1 for x in null if x <= obs) / N_PERMS
        mark = "  <== " if p_hi < 0.01 or p_lo < 0.01 else ""
        print(f"  d={d}: obs {obs:4d}  null {mu:6.1f}±{sd:4.1f}"
              f"  P(>=obs)={p_hi:.4f}  P(<=obs)={p_lo:.4f}{mark}")

    # 4a. distinct words and bigram repeats at d=5, with permutation null
    obs3 = [sum(x) for x in zip(
        *(cut_stats(st, ls, 5) for st, ls in zip(streams, lenseqs)),
    )]
    nulls: tuple[list[int], ...] = ([], [], [])
    for _ in range(N_PERMS):
        tot = [0, 0, 0]
        for st, ls in zip(streams, lenseqs):
            ls2 = ls[:]
            rng.shuffle(ls2)
            r = cut_stats(st, ls2, 5)
            for i in range(3):
                tot[i] += r[i]
        for i in range(3):
            nulls[i].append(tot[i])
    print("\nd=5 statistics vs permutation null:")
    for i, name in enumerate(
            ("single hits", "distinct words with a hit",
             "bigram repeats at d=5")):
        mu = statistics.mean(nulls[i])
        sd = statistics.pstdev(nulls[i])
        p = sum(1 for x in nulls[i] if x >= obs3[i]) / N_PERMS
        print(f"  {name}: obs {obs3[i]}  null {mu:.1f}±{sd:.1f}"
              f"  P(>=obs)={p:.4f}")
    opp = sum(max(0, length - 6) for ls in lenseqs for length in ls)
    print(f"  (bigram@d5 uniform-random expectation: {opp}/841 = {opp/841:.2f})")

    # 4b. per-section breakdown
    print("\nper-section d=5 (obs vs null, 2000 perms):")
    for si, (st, ls) in enumerate(zip(streams, lenseqs)):
        obs = cut_stats(st, ls, 5)[0]
        null = []
        for _ in range(2000):
            ls2 = ls[:]
            rng.shuffle(ls2)
            null.append(cut_stats(st, ls2, 5)[0])
        mu = statistics.mean(null)
        sd = statistics.pstdev(null) or 1.0
        print(f"  sec {si}: obs {obs:3d}  null {mu:5.1f}±{sd:4.1f}"
              f"  z={(obs - mu) / sd:+.2f}")

    # 4c. the multi-hit words, spelled out
    print("\nwords with >= 2 hits at d=5:")
    for s in sec_words:
        for w in s:
            h = [(k, k + 5) for k in range(len(w) - 5) if w[k] == w[k + 5]]
            if len(h) >= 2:
                runes = "".join(c3301.CICADA_ALPHABET[r] for r in w)
                eng = "·".join(c3301.CICADA_ENGLISH_ALPHABET[r] for r in w)
                print(f"  {runes}  ({eng})  matches {h}")


if __name__ == "__main__":
    main()
