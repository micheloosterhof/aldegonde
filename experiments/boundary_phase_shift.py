# ABOUTME: Shifts every block boundary by a fixed number of runes, keeping the length
# ABOUTME: sequence, to test whether the d5 echo is anchored to the visible separators.
"""Are the visible separators the cipher's units, or just where words happen to end?

`separators-are-not-word-boundaries.md` finds the body's block lengths carry no language
order and depend on nothing measurable. That raises an awkward possibility: perhaps the
separators are not cipher structure at all.

They are. The d5 echo -- positions five apart inside a block coinciding above chance,
which is the evidence for a letter step of order 5 -- is anchored to exactly these
positions. Sliding every boundary by a few runes, keeping the same length sequence so the
block structure is identical in shape, destroys it.

One caveat governs how the table is read. Shifting all boundaries by one rune leaves most
PAIRS inside the same block they were in, so small shifts are not independent nulls; the
decay over shifts 1 to 3 is the pair sets decorrelating, not a signal. The comparison
that means something is shift 0 against shifts 4 and beyond.

    python boundary_phase_shift.py [--lag 5] [--shifts 16]
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29


def coincidence(stream: list[int], cuts: list[int], lag: int) -> tuple[int, int]:
    """(hits, pairs) at `lag`, counting only pairs inside one segment."""
    hits = pairs = 0
    for a, b in zip(cuts, cuts[1:]):
        for i in range(a, b - lag):
            pairs += 1
            hits += stream[i] == stream[i + lag]
    return hits, pairs


def main() -> None:
    lag, shifts = 5, 16
    for i, a in enumerate(sys.argv):
        if a == "--lag" and i + 1 < len(sys.argv):
            lag = int(sys.argv[i + 1])
        if a == "--shifts" and i + 1 < len(sys.argv):
            shifts = int(sys.argv[i + 1])

    stream, wid = load_clean()
    n = len(stream)
    bounds = [0] + [i for i in range(1, n) if wid[i] != wid[i - 1]] + [n]
    lengths = [b - a for a, b in zip(bounds, bounds[1:])]

    def shifted(s: int) -> list[int]:
        cuts = [0] + ([s] if s else [])
        pos = s
        for length in lengths:
            pos += length
            if pos >= n:
                break
            cuts.append(pos)
        cuts.append(n)
        return cuts

    print(f"lag {lag}, {len(lengths):,} blocks, mean length {n / len(lengths):.2f}\n")
    print(f"{'shift':>6}{'hits':>7}{'pairs':>8}{'x chance':>11}{'z vs chance':>13}")
    rows = []
    for s in range(shifts):
        h, p = coincidence(stream, shifted(s), lag)
        rate = h / p
        se = math.sqrt((1 / M) * (1 - 1 / M) / p)
        rows.append(rate * M)
        tag = "  <- the real separators" if s == 0 else ""
        print(f"{s:>6}{h:>7}{p:>8}{rate * M:>11.3f}{(rate - 1 / M) / se:>+13.2f}{tag}")

    far = rows[4:]
    mu = sum(far) / len(far)
    sd = (sum((x - mu) ** 2 for x in far) / len(far)) ** 0.5
    print(f"\nshifts 4+ : mean {mu:.3f} sd {sd:.3f} over {len(far)} offsets")
    print(f"shift 0 sits {(rows[0] - mu) / sd:+.2f} sigma above that empirical null.")
    print(
        "\nShifts 1 to 3 decay smoothly because their pair sets still overlap shift 0's;"
        "\nthey are not independent draws. The echo is anchored to the separators the"
        "\nscribe wrote, so those separators are the cipher's units whatever their"
        "\nlengths do or do not encode."
    )


if __name__ == "__main__":
    main()
