#!/usr/bin/env python3
# ABOUTME: Censuses whole-word ciphertext repeats in LP 0-9 against a
# ABOUTME: doublet-preserving null, asking whether any besides DJU-BEI is real.
"""Are there other full-word ciphertext repeats besides DJU-BEI?

DJU-BEI is load-bearing: it is the only claimed state return, so it is the
only cross-word constraint on the (g, sigma) wiring. If other whole-word
repeats are genuine rather than coincidental, each adds an equation.

A repeated ciphertext WORD is weak evidence on its own -- c = base_w(g^j(p))
so the same ciphertext can arise from different plaintext under different
bases. What makes DJU-BEI strong is that it is TWO CONSECUTIVE words
(3+3): the bases stayed synchronised across a word boundary, which chance
alignment does not readily produce. So the census reports repeats by
length, and separately counts runs of consecutive repeated words.

The null must preserve the doublet suppression (`doublet-suppression.md`):
suppressing doublets shrinks the space of realisable words and so RAISES
the collision rate. A uniform-random null would understate chance and
manufacture significance. We use the repo's `doublet_shuffle`, which
resamples the stream at the observed doublet rate, and re-cut it into the
observed word-length sequence.
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde.stats.nulls import doublet_shuffle  # noqa: E402, I001
from lp_corpus import ALPHABET, load_clean  # noqa: E402

M = 29
TRIALS = 400


def cut(stream: list[int], lens: list[int]) -> list[tuple[int, ...]]:
    out, i = [], 0
    for L in lens:
        out.append(tuple(stream[i:i + L]))
        i += L
    return out


def repeat_classes(words: list[tuple[int, ...]], minlen: int) -> dict:
    key: dict[tuple, list[int]] = defaultdict(list)
    for wi, w in enumerate(words):
        if len(w) >= minlen:
            key[w].append(wi)
    return {k: v for k, v in key.items() if len(v) >= 2}


def extra_pairs(words: list[tuple[int, ...]], minlen: int) -> int:
    """Total repeat PAIRS (a class of 3 contributes 3), not classes."""
    return sum(len(v) * (len(v) - 1) // 2
               for v in repeat_classes(words, minlen).values())


def consecutive_runs(words: list[tuple[int, ...]]) -> list[tuple[int, int, int]]:
    """Maximal runs of >=2 consecutive words repeating elsewhere in order.

    Returns (start_a, start_b, run_length) for each pair of positions whose
    words agree over a run of length >= 2. This is the DJU-BEI shape.
    """
    n = len(words)
    pos: dict[tuple, list[int]] = defaultdict(list)
    for wi, w in enumerate(words):
        pos[w].append(wi)
    found = []
    for _w, idxs in pos.items():
        if len(idxs) < 2:
            continue
        for a in idxs:
            for b in idxs:
                if b <= a:
                    continue
                run = 0
                while (a + run < n and b + run < n
                       and words[a + run] == words[b + run]):
                    run += 1
                if run >= 2:
                    found.append((a, b, run))
    # keep maximal: drop (a,b,r) that is the tail of another run
    keep = []
    for a, b, r in found:
        if not any(a2 < a and b2 < b and a - a2 == b - b2 and r2 - (a - a2) >= r
                   for a2, b2, r2 in found):
            keep.append((a, b, r))
    return sorted(set(keep))


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    words = [tuple(d[k]) for k in sorted(d)]
    lens = [len(w) for w in words]
    print(f"clean corpus: {len(stream):,} runes, {len(words):,} words")

    bylen = defaultdict(int)
    for L in lens:
        bylen[L] += 1

    def pairs_by_len(wl: list[tuple[int, ...]]) -> dict[int, int]:
        out: dict[int, int] = defaultdict(int)
        key: dict[tuple, int] = defaultdict(int)
        for w in wl:
            key[w] += 1
        for w, c in key.items():
            if c >= 2:
                out[len(w)] += c * (c - 1) // 2
        return out

    obs_pairs = pairs_by_len(words)
    obs_runs = consecutive_runs(words)

    rate = sum(1 for i in range(len(stream) - 1)
               if stream[i] == stream[i + 1]) / (len(stream) - 1)
    model = doublet_shuffle(rate)
    print(f"null: doublet_shuffle at the observed rate {rate:.5f}, "
          f"re-cut into the real word lengths, {TRIALS} surrogates")

    null_pairs: dict[int, list[int]] = {L: [] for L in bylen}
    null_runlen: list[int] = []
    for _ in range(TRIALS):
        nw = cut(list(model(stream, rng)), lens)
        np_ = pairs_by_len(nw)
        for L in bylen:
            null_pairs[L].append(np_.get(L, 0))
        null_runlen.append(len(consecutive_runs(nw)))

    print("\nrepeated whole ciphertext words, by length:")
    print(f"  {'len':>4}{'words':>8}{'pairs':>7}{'null mean':>11}{'p(hi)':>8}")
    for L in sorted(bylen):
        if bylen[L] < 2:
            continue
        o = obs_pairs.get(L, 0)
        arr = null_pairs[L]
        mu = sum(arr) / len(arr)
        p = (sum(1 for v in arr if v >= o) + 1) / (len(arr) + 1)
        flag = "  <-- excess" if p < 0.05 and o > 0 else ""
        print(f"  {L:>4}{bylen[L]:>8}{o:>7}{mu:>11.2f}{p:>8.3f}{flag}")

    print("\nconsecutive-word repeats (the DJU-BEI shape):")
    def txt(t):
        return "".join(ALPHABET[r] for r in t)
    if not obs_runs:
        print("  none")
    for a, b, r in obs_runs:
        seq = [words[a + i] for i in range(r)]
        runes = sum(len(w) for w in seq)
        print(f"  words {a},{b}: run of {r} ({runes} runes) "
              f"lengths {[len(w) for w in seq]}  {' '.join(txt(w) for w in seq)}")
    mu = sum(null_runlen) / len(null_runlen)
    p = (sum(1 for v in null_runlen if v >= len(obs_runs)) + 1) / (TRIALS + 1)
    print(f"\n  observed: {len(obs_runs)}   null mean {mu:.3f}   p = {p:.4f}")


if __name__ == "__main__":
    main()
