#!/usr/bin/env python3
# ABOUTME: Quantitative closure of plaintext-autokey.md: predicted repeated
# ABOUTME: ciphertext n-grams from real LP-register plaintext vs the observed
# ABOUTME: at-chance repeat census. TR-independent.
"""Plaintext autokey: the repeat-rate kill, quantified.

Under ANY plaintext autokey C[i] = TR[P[i-1]][P[i]] (any tabula recta,
Vigenere/Beaufort/custom), a repeated plaintext (n+1)-gram forces a
repeated ciphertext n-gram — the cipher n-gram is a function of the
plaintext (n+1)-gram alone, position-free. So the ciphertext's repeated
n-gram count is bounded below by the plaintext's repeated (n+1)-gram count.

The plaintext register is measured on the recovered solved-section
plaintext (2,797 runes, experiments/solved_plaintext_running_key.py) and
scaled quadratically to clean-corpus size (pair counts scale as length^2
for fixed register). Observed ciphertext repeats are counted directly and
compared against the doublet-corrected null from covert_channels.py.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from solved_plaintext_running_key import (  # noqa: E402
    recover_plaintext,
    solved_segments,
)


def repeated_pairs(stream: list[int], n: int) -> int:
    c = Counter(tuple(stream[i:i + n]) for i in range(len(stream) - n + 1))
    return sum(v * (v - 1) // 2 for v in c.values())


def main() -> None:
    plaintext = recover_plaintext(solved_segments())
    clean, _ = load_clean()
    scale = (len(clean) / len(plaintext)) ** 2
    print(f"\nplaintext register: {len(plaintext)} runes; clean corpus "
          f"{len(clean)} runes; pair-count scale x{scale:.1f}")
    print(f"\n{'n':>2} {'pt (n+1)-gram pairs':>20} {'-> predicted ct pairs':>21} "
          f"{'observed ct pairs':>18}")
    for n in (4, 5, 6):
        pt_pairs = repeated_pairs(plaintext, n + 1)
        pred = pt_pairs * scale
        obs = repeated_pairs(clean, n)
        print(f"{n:>2} {pt_pairs:>20} {pred:>21.0f} {obs:>18}")
    print("\n(doublet-corrected chance for the observed column: 4-grams "
          "124 ± 10, 5-grams 4 ± 2 — covert_channels.py section N. The "
          "prediction is a LOWER bound: chance repeats add on top.)")


if __name__ == "__main__":
    main()
