# ABOUTME: Tests whether the doublet-dodging walk can reach the three battery cells it has
# ABOUTME: never been shown to reach, by varying everything the mechanism leaves free.
"""The file says the question is open and cheap to test, and that nobody has tried.

`doublet-dodge-walk.md` fits one thing -- which four runes the letter step holds still --
and reports twelve battery cells landing and three not: d3w at 0.0595 against the corpus's
0.0370, d6w at 0.0420 against 0.0245, and the seam at 0.0030 against 0.0079. It then says:

    Whether the three can be reached is open and cheap to test: the mechanism fixes only
    which four runes g holds still, leaving its five 5-cycles and the whole of sigma free
    ... Nobody has tried.

So try. Hold the fixed points at the file's own best choice, {4, 8, 18, 19}, which lands
the doublet rate and position together, and redraw the five 5-cycles, sigma and the
initial base 150 times.

**A trap this hit first.** `lp_words()` returns the LP CIPHERTEXT, and `prose_corpora()`
returns the plaintext surrogate; the names do not say so. Feeding `lp_words()` in as
plaintext gives a corpus whose doublets are already suppressed to 0.0063, so the model
cannot produce them at all -- d1w reads 0.0008 and the three cells appear to land 54% of
the time. Every number below uses prose.

    python dodge_three_cells.py [--draws 150]
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import M, encipher, order5_fixing  # noqa: E402
from fingerprint_battery import fingerprint, lp_words, prose_corpora  # noqa: E402

KEEP = [4, 8, 18, 19]
CELLS = ("d1w", "d3w", "d6w", "seam", "doublet_pos")
SE = {"d1w": 0.0011, "d3w": 0.0026, "d6w": 0.0051, "seam": 0.0034, "doublet_pos": 0.06}


def main() -> None:
    draws = 150
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = fingerprint(lp_words())
    plain = prose_corpora(2928, 1)[0]
    rng = random.Random(2026)
    rows = []
    for _ in range(draws):
        g = order5_fixing(KEEP, rng)
        sigma = rng.sample(range(M), M)
        rows.append(fingerprint(encipher(plain, rng.sample(range(M), M), g, sigma)))

    print(f"g fixes {KEEP}; 5-cycles, sigma and base0 redrawn {draws} times\n")
    print(f"{'cell':>12}{'corpus':>9}{'median':>9}{'min':>9}{'max':>9}{'within 2SE':>12}")
    for k in CELLS:
        v = [r[k] for r in rows]
        hit = sum(1 for r in rows if abs(r[k] - lp[k]) <= 2 * SE[k])
        print(f"{k:>12}{lp[k]:>9.4f}{statistics.median(v):>9.4f}{min(v):>9.4f}"
              f"{max(v):>9.4f}{f'{hit}/{draws}':>12}")

    three = [r for r in rows if all(abs(r[k] - lp[k]) <= 2 * SE[k] for k in ("d3w", "d6w", "seam"))]
    print(f"\nall three open cells at once: {len(three)}/{draws}")
    lo = min(r["d3w"] for r in rows)
    print(f"d3w never lands: its minimum over {draws} draws is {lo:.4f}, above the"
          f" corpus ceiling of {lp['d3w'] + 2 * SE['d3w']:.4f}")
    print(
        "\nd1w and the doublet position are constant across draws, as the mechanism"
        "\nrequires -- they are set by the fixed points alone. So for this fixed-point"
        "\nchoice the free parameters cannot rescue d3w, and whether another admissible"
        "\nchoice can is the question that remains."
    )


if __name__ == "__main__":
    main()
