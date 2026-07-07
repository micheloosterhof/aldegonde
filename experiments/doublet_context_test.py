#!/usr/bin/env python3
"""Doublet trigger: ciphertext-conditioned variants test.

Generalizing the marker premise: could the doublet trigger involve a
CIPHERTEXT condition — a pair of ciphertext runes, or one ciphertext rune
plus one plaintext rune? Any such trigger with a small ciphertext
condition set must concentrate the runes around doublets on that set:

- trigger involving C at offset d -> identity distribution of C[i+d] at
  doublets concentrates (power: detects sets up to ~15 runes with n=88);
- trigger = small set of ciphertext PAIRS -> pair collisions among the 88
  doublet contexts explode (chance ~4.6; a 6-pair set would give ~600).

Mixed triggers P[i+1] = g(C[i]) with bijective g are excluded by rate
alone (would give 1/29 = 3.45% vs observed 0.675%); with g mapping into
rare letters they are observationally identical to the plain marker class
unless the ciphertext condition set is small — which this test covers.
"""

import numpy as np
from collections import Counter
from scipy.stats import chi2 as chi2_dist, poisson

from anomaly_scan import parse
from aldegonde import c3301

N = 29


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    C = np.array(stream[:-nplain], dtype=np.int64)
    n = len(C)
    dpos = [i for i in range(n - 1) if C[i] == C[i + 1]]
    print(f"{len(dpos)} doublets")

    print("\ncontext IDENTITY distributions (uniform under plaintext-only triggers):")
    for off, name in ((-2, "C[i-2]"), (-1, "C[i-1]"), (2, "C[i+2]"), (3, "C[i+3]")):
        vals = [int(C[i + off]) for i in dpos if 0 <= i + off < n]
        c = np.bincount(vals, minlength=N)
        m = len(vals)
        stat = ((c - m / N) ** 2 / (m / N)).sum()
        print(f"  {name}: chi2={stat:.1f} p={chi2_dist.sf(stat, N - 1):.3f} "
              f"max count {int(c.max())} (exp {m / N:.1f})")

    print("\ncontext PAIR collisions (explode under small pair-trigger sets):")
    for offs, name in (((-2, -1), "(C[i-2],C[i-1])"), ((-1, 0), "(C[i-1],doubled)"),
                       ((2, 3), "(C[i+2],C[i+3])"), ((0, 2), "(doubled,C[i+2])")):
        pairs = [(int(C[i + offs[0]]), int(C[i + offs[1]]))
                 for i in dpos if 0 <= i + offs[0] < n and 0 <= i + offs[1] < n]
        cnt = Counter(pairs)
        coll = sum(v * (v - 1) // 2 for v in cnt.values())
        m = len(pairs)
        exp = m * (m - 1) / 2 / (N * N)
        print(f"  {name}: collisions={coll} exp={exp:.1f} "
              f"P(>=obs)={poisson.sf(coll - 1, exp):.3f}")


if __name__ == "__main__":
    main()
