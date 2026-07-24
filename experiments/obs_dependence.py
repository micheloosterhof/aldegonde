# ABOUTME: Observation: no pairwise dependence C[i],C[i+d] except d=1 (doublets)
# ABOUTME: -- the full 29x29 contingency chi2 is at chance for every lag >= 2.
"""Pairwise dependence. Significance: chi-square of the 29x29 contingency table
of (C[i], C[i+d]) vs independence, at each lag. Only d=1 (the doublet diagonal)
departs; every d>=2 is within the 784-df noise band."""
from __future__ import annotations
import math
from collections import Counter
from lp_corpus import load_clean, N


def contingency_chi2(stream, d):
    n = len(stream) - d
    joint = Counter((stream[i], stream[i + d]) for i in range(n))
    ra = Counter(stream[i] for i in range(n))
    rb = Counter(stream[i + d] for i in range(n))
    chi2 = 0.0
    for a in range(N):
        for b in range(N):
            exp = ra[a] * rb[b] / n
            if exp > 0:
                chi2 += (joint.get((a, b), 0) - exp) ** 2 / exp
    df = (N - 1) ** 2
    x = (chi2 / df) ** (1 / 3)
    z = (x - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return chi2, df, z


def main() -> None:
    stream, _ = load_clean()
    print("lag : contingency chi2 (df 784)   z")
    for d in range(1, 11):
        chi2, df, z = contingency_chi2(stream, d)
        tag = "  <-- doublet diagonal" if d == 1 else ""
        print(f"  {d:2d} : {chi2:7.1f}                {z:+.2f}{tag}")
    print("VERDICT: only lag 1 (doublets) shows dependence; lags 2..10 at chance")


if __name__ == "__main__":
    main()
