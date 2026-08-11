# ABOUTME: Anatomy of the within-word d5 matches: word-edge alignment and spatial
# ABOUTME: clustering of the 91 hit words (both null).
"""Anatomy of the within-word distance-5 matches: where do they sit?

Given that the within-word d=5 excess behaves like literal copies
(within_word_delta_mixture.py), map their geometry:

1. Position-in-word distribution of matched pairs (start k) against the
   opportunity null (matched pairs should be multinomial over all pairs
   if position-blind).
2. Alignment tests: start-aligned (k = 0) and end-aligned (k+5 = L-1)
   enrichment; both-aligned (words of length exactly 6..?).
3. Length-resolved match rates with exact binomial intervals, against
   uniform (3.45%) and full plaintext leak (6.1%).
4. The XY..XY words: lengths, positions, whether the repeat opens and/or
   closes the word.
5. Spatial clustering of hit words along the corpus: window-count
   variance and nearest-neighbour distances under a permutation null
   that reassigns hits to words with probability proportional to their
   pair count (so word-length structure is controlled).

Usage: python experiments/within_word_match_anatomy.py [n_perms]
"""

from __future__ import annotations

import sys
from collections import Counter

import numpy as np
from scipy.stats import binomtest

from aldegonde import c3301

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
WORD_BOUNDARIES = set(c3301.MARK_CHARS + "&%" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS)
D = 5


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


def main() -> None:
    n_perms = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    sections = parse_clean_sections()
    words = [w for s in sections for w in s]

    pairs = []  # (word_index, k, L, matched)
    for wi, w in enumerate(words):
        L = len(w)
        for k in range(L - D):
            pairs.append((wi, k, L, w[k] == w[k + D]))
    matched = [p for p in pairs if p[3]]
    n_pairs, n_match = len(pairs), len(matched)
    print(f"{n_pairs} pairs, {n_match} matches")

    # 1. position-in-word distribution --------------------------------
    pos_all = Counter(p[1] for p in pairs)
    pos_hit = Counter(p[1] for p in matched)
    print("\nstart position k: matches / pairs (rate)")
    for k in sorted(pos_all):
        n, m = pos_all[k], pos_hit.get(k, 0)
        print(f"  k={k}: {m:>3} / {n:>4}  ({m / n:.4f})")

    # 2. alignment tests ----------------------------------------------
    def enrich(name, sel):
        tot = sum(1 for p in pairs if sel(p))
        hit = sum(1 for p in matched if sel(p))
        exp = n_match * tot / n_pairs
        # permutation: choose n_match of n_pairs without replacement
        var = (
            n_match
            * (tot / n_pairs)
            * (1 - tot / n_pairs)
            * (n_pairs - n_match)
            / (n_pairs - 1)
        )
        z = (hit - exp) / var**0.5 if var else 0.0
        print(f"  {name}: {hit} vs {exp:.1f} expected (z={z:+.2f})")

    print("\nalignment of matched pairs:")
    enrich("start-aligned (k=0)", lambda p: p[1] == 0)
    enrich("end-aligned (k+5=L-1)", lambda p: p[1] + D == p[2] - 1)
    enrich("both (L=6, k=0)", lambda p: p[1] == 0 and p[2] == 6)

    # 3. length-resolved rates ----------------------------------------
    print("\nby word length L: matches/pairs rate [95% CI]")
    by_len: dict[int, list[int]] = {}
    for _, _k, L, m in pairs:
        d = by_len.setdefault(min(L, 13), [0, 0])
        d[0] += 1
        d[1] += int(m)
    for L in sorted(by_len):
        n, m = by_len[L]
        bt = binomtest(m, n, 1 / MOD)
        lo, hi = bt.proportion_ci(0.95)
        lab = f"{L}" if L < 13 else "13+"
        print(f"  L={lab:>3}: {m:>3}/{n:>4} = {m / n:.4f} [{lo:.4f},{hi:.4f}]")

    # 4. XY..XY words --------------------------------------------------
    print("\nXY..XY words (digraph repeat at distance 5):")
    for wi, w in enumerate(words):
        L = len(w)
        for k in range(L - D - 1):
            if w[k] == w[k + D] and w[k + 1] == w[k + D + 1]:
                opens = k == 0
                closes = k + D + 1 == L - 1
                print(
                    f"  word {wi} L={L} k={k} "
                    f"opens={opens} closes={closes} "
                    f"runes={''.join(RUNES[c] for c in w)}"
                )

    # 5. spatial clustering of hit words -------------------------------
    hit_words = sorted({p[0] for p in matched})
    weights = np.array([max(0, len(w) - D) for w in words], dtype=float)
    k_hits = len(hit_words)
    print(
        f"\n{k_hits} distinct hit words; clustering tests "
        f"(null: hits reassigned ∝ word pair count):"
    )

    def nn_stat(hw: list[int]) -> float:
        arr = np.array(sorted(hw))
        return float(np.diff(arr).mean())

    def window_var(hw: list[int], win: int = 100) -> float:
        counts = np.zeros(len(words) // win + 1)
        for i in hw:
            counts[i // win] += 1
        return float(counts.var())

    obs_nn, obs_wv = nn_stat(hit_words), window_var(hit_words)
    p_idx = weights / weights.sum()
    nn_null = np.empty(n_perms)
    wv_null = np.empty(n_perms)
    rng_np = np.random.default_rng(3)
    for i in range(n_perms):
        # sample words without replacement, prob ∝ pair count
        hw = rng_np.choice(len(words), size=k_hits, replace=False, p=p_idx)
        nn_null[i] = nn_stat(hw.tolist())
        wv_null[i] = window_var(hw.tolist())
    for name, obs, null in (
        ("mean gap between hit words", obs_nn, nn_null),
        ("100-word window count variance", obs_wv, wv_null),
    ):
        z = (obs - null.mean()) / null.std()
        p_two = (
            min(
                (np.sum(null >= obs) + 1) / (n_perms + 1),
                (np.sum(null <= obs) + 1) / (n_perms + 1),
            )
            * 2
        )
        print(
            f"  {name}: {obs:.2f} vs {null.mean():.2f} ± {null.std():.2f} "
            f"(z={z:+.2f}, two-sided p={p_two:.3f})"
        )


if __name__ == "__main__":
    main()
