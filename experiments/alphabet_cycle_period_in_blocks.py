# ABOUTME: Scans block distances 1..600 for a period in blocks at which alphabets repeat, by
# ABOUTME: matched-position coincidence over all positions and over phase-0 runes alone.
"""Does the alphabet set cycle with some period in blocks?

If the phase-0 alphabet (or the whole set) ran through a fixed cycle of P alphabets, one
per block, then blocks w and w+P would be enciphered with the same alphabets and would
coincide at matched positions at the plaintext word-aligned rate (about 0.079, chance
0.0345), at distance P and its multiples. `alphabet_sharing_by_word_distance.py` read
distances to 50 and skipped 29; this reads every distance to 600, over all matched
positions and over the phase-0 positions (0, 5, 10) alone, so a cycle confined to one
phase is caught too. A full-sharing period gives +20 sigma at any distance; the scan is
over-powered, and the Bonferroni bar for 600 distances is z = 3.9.

    python experiments/alphabet_cycle_period_in_blocks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from within_word_d5 import M, parse_clean_sections  # noqa: E402

MAX_D = 600
NAMED = (5, 10, 25, 29, 30, 58, 87, 116, 145, 290)
CHANCE = 1 / M


def coincidences(sections, distance: int, *, phase_only: bool) -> tuple[int, int]:
    hits = pairs = 0
    for words in sections:
        for a, b in zip(words, words[distance:]):
            n = min(len(a), len(b))
            positions = range(0, n, 5) if phase_only else range(n)
            for j in positions:
                pairs += 1
                hits += a[j] == b[j]
    return hits, pairs


def main() -> None:
    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    for label, phase_only in (
        ("all matched positions", False),
        ("phase-0 positions only", True),
    ):
        z = np.zeros(MAX_D + 1)
        rate = np.zeros(MAX_D + 1)
        for d in range(1, MAX_D + 1):
            h, p = coincidences(sections, d, phase_only=phase_only)
            rate[d] = h / p
            z[d] = (h - p * CHANCE) / np.sqrt(p * CHANCE * (1 - CHANCE))
        top = np.argsort(z[1:])[::-1][:5] + 1
        print(f"\n{label}: distances 1..{MAX_D}")
        print(
            f"  max z {z[1:].max():+.2f} at D = {z[1:].argmax() + 1}; Bonferroni bar for {MAX_D} distances 3.9"
        )
        print(
            "  top five: "
            + ", ".join(f"D={d} z={z[d]:+.2f} rate={rate[d]:.4f}" for d in top)
        )
        print("  named periods: " + ", ".join(f"D={d} z={z[d]:+.2f}" for d in NAMED))
        print(
            f"  share of distances with |z| > 2: {np.mean(np.abs(z[1:]) > 2):.3f} (chance 0.046)"
        )


if __name__ == "__main__":
    main()
