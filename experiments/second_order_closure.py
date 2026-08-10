#!/usr/bin/env python3
# ABOUTME: Direct test of second-order-difference.md: recover P from C = delta^2(P)
# ABOUTME: by double cumulative sum over all 29 ramp slopes; IoC of each candidate.
"""Second-order difference cipher, tested directly.

If C[i] = P[i] - 2P[i-1] + P[i-2] (mod 29), then P is recovered from C by a
double cumulative sum up to two integration constants: the first shifts P
by a constant (IoC-invariant), the second adds a linear ramp c1*i. So the
candidate plaintexts are S[i] + a*i (mod 29) for the 29 slopes a, where S
is the double cumsum of C. If the hypothesis were true, one slope would
show plaintext IoC (~1.7 normalized); measured on the clean corpus all 29
are flat. (The earlier kill in second-order-difference.md tested doublets
of delta^2(C) = delta^4(P), about which the hypothesis predicts nothing —
this is the direct analogue of the first-difference cumsum test.)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lp_corpus import load_clean

M = 29


def nioc(v: np.ndarray) -> float:
    c = np.bincount(v, minlength=M)
    n = len(v)
    return float((c * (c - 1)).sum()) / (n * (n - 1)) * M


def main() -> None:
    clean = np.array(load_clean()[0])
    s1 = np.cumsum(clean) % M
    s2 = np.cumsum(s1) % M
    i = np.arange(len(clean))
    vals = sorted(nioc((s2 + a * i) % M) for a in range(M))
    print(f"double-cumsum candidates, nIoC over 29 slopes: "
          f"min {vals[0]:.4f}  max {vals[-1]:.4f}  (plaintext ~1.7)")
    # first-order for reference
    v1 = sorted(nioc((s1 + a) % M) for a in range(M))
    print(f"single-cumsum reference (first-difference):    "
          f"min {v1[0]:.4f}  max {v1[-1]:.4f}")


if __name__ == "__main__":
    main()
