#!/usr/bin/env python3
# ABOUTME: Closes the per-word VARYING Hill matrix remainder left open by
# ABOUTME: hill-cipher-per-word.md: simulated doublet rate under random
# ABOUTME: per-word invertible matrices vs the observed suppression.
"""Per-word varying Hill matrices cannot suppress doublets.

A within-word ciphertext doublet under C_w = M_w * P_w is the hyperplane
condition (row_i - row_{i+1}) . P_w = 0. For an invertible matrix chosen
independently of the plaintext, that hyperplane is hit at ~1/29 per
adjacency regardless of how M_w varies per word — the same generic-rate
argument as README structural constraint 1, at the word-block level. Only
matrices TUNED to the plaintext bigram distribution escape, which
collapses the family into the constraint's known escape (bigram-tuned
alphabet relations). Verified by simulation: random invertible matrices
per word over GF(29) on runeglish plaintext give ~3.4% within-word
doublets vs the observed 0.63%.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from solved_plaintext_running_key import recover_plaintext, solved_segments

M = 29
REPS = 40  # plaintext passes, fresh matrices each


def random_invertible(rng: random.Random, n: int) -> np.ndarray:
    while True:
        m = np.array([[rng.randrange(M) for _ in range(n)] for _ in range(n)])
        if round(np.linalg.det(m)) % M != 0:
            return m


def main() -> None:
    rng = random.Random(3301)
    plaintext = recover_plaintext(solved_segments())
    # re-segment the register plaintext into LP-like word lengths
    lens = []
    i = 0
    while i < len(plaintext):
        L = rng.choice((2, 3, 3, 4, 4, 4, 5, 5, 6, 7, 8))
        lens.append(min(L, len(plaintext) - i))
        i += L
    doublets = pairs = 0
    for _ in range(REPS):
        pos = 0
        for L in lens:
            w = np.array(plaintext[pos : pos + L])
            pos += L
            if L < 2:
                continue
            c = (random_invertible(rng, L) @ w) % M
            pairs += L - 1
            doublets += int((c[:-1] == c[1:]).sum())
    print(
        f"random per-word invertible matrices: within-word doublet rate "
        f"{doublets / pairs:.4f} over {pairs} adjacencies "
        f"(observed 0.0063; generic expectation 1/29 = 0.0345)"
    )


if __name__ == "__main__":
    main()
