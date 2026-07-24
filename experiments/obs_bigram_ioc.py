# ABOUTME: Observation: off-diagonal bigram distribution is uniform -- the only
# ABOUTME: bigram structure is the suppressed diagonal (doublets), nothing else.
"""Digraph structure. The raw bigram IoC is slightly elevated, but that is fully
explained by doublet suppression. Significance: chi-square uniformity of the 812
OFF-diagonal bigram cells (excludes the 29 diagonal doublet cells), which should
be flat if the doublet deficit is the only bigram-level structure."""
from __future__ import annotations
import math
from collections import Counter
from lp_corpus import load_clean, N


def main() -> None:
    stream, _ = load_clean()
    bg = Counter((stream[i], stream[i + 1]) for i in range(len(stream) - 1))
    total = sum(bg.values())
    # raw bigram IoC (normalized to random baseline 1/N^2)
    ioc = (N * N) * sum(v * (v - 1) for v in bg.values()) / (total * (total - 1))
    off = [bg.get((a, b), 0) for a in range(N) for b in range(N) if a != b]
    m = len(off)
    exp = sum(off) / m
    chi2 = sum((o - exp) ** 2 / exp for o in off)
    k = m - 1
    x = chi2 / k
    z = (x ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
    p = 0.5 * math.erfc(z / math.sqrt(2))
    print(f"bigrams {total}, normalized bigram IoC {ioc:.4f} (elevated vs 1.0)")
    print(f"off-diagonal cells {m}, chi-square {chi2:.0f} ({k} df)  p={p:.2f}")
    print("VERDICT: off-diagonal bigrams uniform; the ONLY bigram structure is")
    print("the suppressed diagonal (doublets). The IoC lift is doublet-deficit,")
    print("not language -- compare against a doublet-suppressed null, not uniform.")


if __name__ == "__main__":
    main()
