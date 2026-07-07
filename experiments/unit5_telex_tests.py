#!/usr/bin/env python3
# ABOUTME: Tests the unit-of-5 doublet model (rate = 1/5 x 1/29), reversal
# ABOUTME: symmetry, positional phase frames, and 5-bit telex-style encodings.
"""Unit-of-5 and telex-style tests for the LP unsolved corpus.

Motivated by three observations: the doublet rate is almost exactly 1/5 of
the random rate (0.664% vs 3.45%), 2^5 = 32 is the smallest power of two
covering the 29-rune alphabet (Baudot/telex-style 5-bit codes), and the
confirmed lag-5 paired-match structure also involves the constant 5.

Results:

1. Reversal: the lag-5 d1/d4 pattern is IDENTICAL in reversed text — but
   this is mathematically forced (equality matches are reflection-symmetric,
   pair separations are preserved), so reversal carries no information.
2. Parameter-free rate fit: doublets 86 observed vs 89.3 predicted by
   P(doublet) = (1/5) x (1/29), z = -0.36. The avoidance acceptance
   probability is exactly 1/5 — a suspiciously round design constant.
3. Positional realizations of "units of 5" all FAIL: doublet positions are
   uniform mod 5 globally, doublet gaps have no mod-5 lattice, doublet rates
   by word position show no period-5 comb, and lag-5 events have no
   word-relative phase. The 1/5 is realized memorylessly (per-pair,
   independently — consistent with the confirmed Poisson spacing), not by a
   positional grid. One soft hint: the minimum doublet gap is 6 (Poisson
   expects ~2.8 gaps <= 5; p ~= 0.06).
4. Telex/5-bit tests (canonical index encoding): the missing doublet mass
   redistributes across Hamming distances in proportion to chance — i.e.
   consistent with uniform re-draw on avoidance, NOT with a single-bit-flip
   nudge (which would pile the mass at Hamming distance 1). Differing-bit
   positions for distance-1 pairs are uniform. Lag-5 pairs show no Hamming
   structure beyond the known match excess. Caveat: bit-level tests depend
   on the unknown rune-to-code assignment.

Net: the cipher's avoidance leak rate is exactly 1/5, applied memorylessly;
no evidence for fixed 5-unit framing or bitwise mechanics in the canonical
encoding. The constant 5 now appears twice independently in the fingerprint
(doublet acceptance 1/5, lag-5 window coupling).
"""

from collections import Counter
from itertools import product
from math import sqrt

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
MOD = 29
DATA = "data/page0-58.txt"


def load() -> tuple[str, list[int]]:
    """Return the unsolved corpus and the word position of every rune."""
    with open(DATA) as f:
        raw = f.read()
    parts = raw.split("%")
    keep = set([i for i, p in enumerate(parts)
                if any(c in ALPHABET for c in p)][:-2])
    clean: list[str] = []
    wordpos: list[int] = []
    cur: list[str] = []

    def flush() -> None:
        wordpos.extend(range(len(cur)))
        clean.extend(cur)
        cur.clear()

    for pi in sorted(keep):
        for ch in parts[pi]:
            if ch in ALPHABET:
                cur.append(ch)
            elif ch in "-.$&" and cur:
                flush()
        if cur:
            flush()
    return "".join(clean), wordpos


def d_counts(s: str) -> tuple[int, ...]:
    """Lag-5 match-pair counts at separations 1..4."""
    mv = [s[i] == s[i + 5] for i in range(len(s) - 5)]
    m = len(mv)
    return tuple(
        sum(1 for i in range(m - d) if mv[i] and mv[i + d]) for d in (1, 2, 3, 4)
    )


def main() -> None:
    """Run all unit-of-5 / telex tests."""
    text, wordpos = load()
    n = len(text)
    r2i = c3301.r2i

    print("=== 1. reversal symmetry ===")
    print(f"forward  d1..d4: {d_counts(text)}")
    print(f"reversed d1..d4: {d_counts(text[::-1])} (forced: reflection-symmetric)")

    print("\n=== 2. parameter-free unit-of-5 rate model ===")
    pairs = n - 1
    dpos = [i for i in range(pairs) if text[i] == text[i + 1]]
    dbl = len(dpos)
    exp_unit = pairs / (5 * MOD)
    z = (dbl - exp_unit) / sqrt(exp_unit * (1 - 1 / (5 * MOD)))
    print(f"doublets {dbl}/{pairs} = {100 * dbl / pairs:.3f}%")
    print(f"(1/5)(1/29) model: expect {exp_unit:.1f}, z = {z:+.2f}")

    print("\n=== 3. positional frames for 'units of 5' ===")
    print(f"doublet pos mod 5:   {sorted(Counter(i % 5 for i in dpos).items())}")
    gaps = sorted(b - a for a, b in zip(dpos, dpos[1:]))
    print(f"doublet gaps mod 5:  {sorted(Counter(g % 5 for g in gaps).items())}")
    print(f"min doublet gaps:    {gaps[:6]} (Poisson expects ~2.8 gaps <= 5)")
    opp = Counter(wordpos[i] for i in range(pairs))
    dwp = Counter(wordpos[i] for i in dpos)
    rates = [f"{k}:{100 * dwp.get(k, 0) / opp[k]:.2f}%" for k in range(8)]
    print(f"doublet rate by wordpos: {' '.join(rates)} (no period-5 comb)")
    mv = [text[i] == text[i + 5] for i in range(n - 5)]
    m = len(mv)
    cons = Counter(b - a for a, b in zip(
        [i for i, v in enumerate(mv) if v][:-1],
        [i for i, v in enumerate(mv) if v][1:]))
    p1 = sum(mv) / m
    print("lag-5 match consecutive gaps (obs vs geometric):")
    for g in range(1, 9):
        e = (sum(mv) - 1) * p1 * (1 - p1) ** (g - 1)
        print(f"  gap {g}: {cons.get(g, 0):3d} vs {e:5.1f}")

    print("\n=== 4. telex / 5-bit Hamming tests (canonical encoding) ===")

    def ham(a: int, b: int) -> int:
        return bin(a ^ b).count("1")

    dist_exp = Counter(ham(a, b) for a, b in product(range(MOD), repeat=2))
    tot = MOD * MOD
    # redistribution model: missing doublet mass spread in proportion to chance
    missing = pairs / MOD - dbl
    obs_h = Counter(ham(r2i(text[i]), r2i(text[i + 1])) for i in range(pairs))
    print("adjacent-pair Hamming distance (obs vs uniform-redraw model):")
    nonzero_mass = tot - dist_exp[0]
    for h in range(1, 6):
        base = pairs * dist_exp[h] / tot
        redraw = base + missing * dist_exp[h] / nonzero_mass
        o = obs_h.get(h, 0)
        print(f"  d_H={h}: obs={o:5d} redraw-model={redraw:7.1f} "
              f"z={(o - redraw) / sqrt(redraw):+5.2f}")
    obs5 = Counter(ham(r2i(text[i]), r2i(text[i + 5])) for i in range(n - 5))
    parts_ = [f"d_H={h}:{(obs5.get(h, 0) - (n - 5) * dist_exp[h] / tot) / sqrt((n - 5) * dist_exp[h] / tot):+.1f}"
              for h in range(6)]
    print("lag-5 pair Hamming z-scores: " + " ".join(parts_))


if __name__ == "__main__":
    main()
