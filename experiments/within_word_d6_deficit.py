#!/usr/bin/env python3
"""Robustness of the within-word d=6 match DEFICIT hint.

The distance scan in within-word-d5-coincidence.md showed, alongside the
d=5 excess (p=0.0014), a low-side hint at d=6: 31 matches vs 44.5 ± 6.3
under the word-length permutation null (P(<=) = 0.018, one of 7 scanned
distances). If real, words avoid matching at distance 6 — a second
word-aware signature no proposed mechanism predicts.

Checks here:
1. Reproduce the number with more permutations.
2. Split-half stability (sections 0-4 vs 5-9).
3. Per-section breakdown.
4. Interaction with d=5: is the d=6 deficit carried by words that also
   contain a d=5 match (suggesting one mechanism), or independent?
5. Joint (d5 excess, d6 deficit) Monte Carlo: how often does the null
   produce BOTH |effects| jointly this large (two-cell look-elsewhere)?

Usage: python experiments/within_word_d6_deficit.py [n_perms]
"""

from __future__ import annotations

import random
import sys

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
WORD_BOUNDARIES = set("-.&%")


def parse_clean_sections(path: str = DATA) -> list[list[list[int]]]:
    with open(path) as f:
        text = f.read()
    sec_words: list[list[list[int]]] = [[]]
    cur: list[int] = []
    for ch in text:
        if ch in R2I:
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


def count_d(words: list[list[int]], d: int) -> int:
    return sum(1 for w in words for k in range(len(w) - d)
               if w[k] == w[k + d])


def perm_counts(sections, d: int, n_perms: int, rng) -> np.ndarray:
    streams = [[c for w in s for c in w] for s in sections]
    lens = [[len(w) for w in s] for s in sections]
    out = np.empty(n_perms)
    for it in range(n_perms):
        tot = 0
        for stream, ls in zip(streams, lens):
            ls2 = ls[:]
            rng.shuffle(ls2)
            pos = 0
            for length in ls2:
                w = stream[pos:pos + length]
                pos += length
                tot += sum(1 for k in range(length - d)
                           if w[k] == w[k + d])
        out[it] = tot
    return out


def main() -> None:
    n_perms = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    rng = random.Random(20260707)
    sections = parse_clean_sections()
    words = [w for s in sections for w in s]

    # 1. headline
    obs6 = count_d(words, 6)
    null6 = perm_counts(sections, 6, n_perms, rng)
    p_lo = (np.sum(null6 <= obs6) + 1) / (n_perms + 1)
    print(f"d=6 within-word matches: {obs6} vs null {null6.mean():.1f} "
          f"± {null6.std():.1f}; P(<=) = {p_lo:.4f}")

    # 2. split-half
    for name, half in (("sections 0-4", sections[:5]),
                       ("sections 5-9", sections[5:])):
        hw = [w for s in half for w in s]
        o = count_d(hw, 6)
        nn = perm_counts(half, 6, n_perms // 4, rng)
        print(f"  {name}: {o} vs {nn.mean():.1f} ± {nn.std():.1f} "
              f"(z = {(o-nn.mean())/nn.std():+.2f})")

    # 3. per-section
    print("  per-section (obs, null mean, z):")
    for i, s in enumerate(sections):
        o = count_d(s, 6)
        nn = perm_counts([s], 6, n_perms // 10, rng)
        z = (o - nn.mean()) / nn.std() if nn.std() else 0.0
        print(f"    s{i}: {o:>3} vs {nn.mean():>5.1f} (z={z:+.2f})")

    # 4. interaction with d=5 hits
    hit5 = {id(w) for w in words
            if any(w[k] == w[k + 5] for k in range(len(w) - 5))}
    in_hit = sum(1 for w in words if id(w) in hit5
                 for k in range(len(w) - 6) if w[k] == w[k + 6])
    out_hit = obs6 - in_hit
    opp_in = sum(len(w) - 6 for w in words if id(w) in hit5 and len(w) > 6)
    opp_out = sum(len(w) - 6 for w in words
                  if id(w) not in hit5 and len(w) > 6)
    print(f"\nd=6 matches in d5-hit words: {in_hit}/{opp_in} "
          f"({in_hit/max(opp_in,1):.4f}); in other words: {out_hit}/{opp_out}"
          f" ({out_hit/max(opp_out,1):.4f}); uniform 0.0345")

    # 5. joint two-cell look-elsewhere: P(any of d=2..8 as extreme as the
    # observed d5 excess AND any other as extreme as the d6 deficit)
    dists = range(2, 9)
    obs = {d: count_d(words, d) for d in dists}
    nulls = {d: perm_counts(sections, d, n_perms // 10, rng) for d in dists}
    z_obs = {d: (obs[d] - nulls[d].mean()) / nulls[d].std() for d in dists}
    z5, z6 = z_obs[5], z_obs[6]
    print("\nz by distance: "
          + "  ".join(f"d{d}:{z_obs[d]:+.2f}" for d in dists))
    # Monte Carlo joint: use the null draws as pseudo-experiments
    m = min(len(v) for v in nulls.values())
    hits = 0
    for i in range(m):
        zs = [(nulls[d][i] - nulls[d].mean()) / nulls[d].std()
              for d in dists]
        if max(zs) >= z5 and min(zs) <= z6:
            hits += 1
    print(f"joint look-elsewhere: P(max z >= {z5:.2f} AND min z <= {z6:.2f} "
          f"across d=2..8) = {hits}/{m} = {hits/m:.4f}")


if __name__ == "__main__":
    main()
