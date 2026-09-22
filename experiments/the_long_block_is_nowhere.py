# ABOUTME: Searches the whole neighbourhood of a mark for English's long sentence-final
# ABOUTME: block, finds it at no offset, and so excludes every displacement variant.
"""The sentence-final long block is not displaced. It is absent from the neighbourhood.

`which_edge_is_anomalous.py` excluded the register escape: the LP author lengthens
sentence-finally at +1.32, on top of a ten-register English mean of +1.17, and the body
reads -0.29. Three readings remain, and one of them -- that the marks sit somewhere other
than the true sentence end -- makes a prediction the others do not. If a mark is merely
**displaced** by a block or two, the long final block should still be there, just at a
different offset.

It is not at any offset. Mean block length at each offset from a mark, against the span
interior, over spans long enough that the offsets stay distinct:

| offset | ten registers | the LP body | z |
|---|---|---|---|
| -4 | +0.01 +- 0.07 | +0.11 +- 0.26 | +0.36 |
| -3 | -0.02 +- 0.11 | -0.20 +- 0.22 | -0.72 |
| -2 | -0.24 +- 0.07 | -0.14 +- 0.22 | +0.45 |
| **-1** | **+1.19 +- 0.23** | **-0.27 +- 0.24** | **-4.42** |
| +1 | -0.71 +- 0.23 | +0.22 +- 0.27 | +2.64 |
| +2 | -0.14 +- 0.18 | +0.30 +- 0.25 | +1.44 |
| +3 | -0.06 +- 0.12 | +0.44 +- 0.26 | +1.78 |
| +4 | -0.01 +- 0.08 | -0.23 +- 0.24 | -0.86 |

The body's **largest** value anywhere in the window is +0.44 at offset +3, against the
+1.19 English puts at -1. Scoring each displacement variant against that +1.19:

    the mark is at the sentence end   offset -1   -0.27 +- 0.24   z = -4.39
    the mark is one block EARLY       offset +1   +0.22 +- 0.27   z = -2.73
    the mark is one block LATE        offset -2   -0.14 +- 0.22   z = -4.18
    the mark is two blocks late       offset -3   -0.20 +- 0.22   z = -4.37
    the mark is two blocks early      offset +2   +0.30 +- 0.25   z = -2.62

All excluded at 2.6 sigma or more.

## What this leaves

The three surviving readings of `sentences-do-not-end-long.md` now say one thing between
them: **whatever the marks are, no sentence ends at or near them.** A displaced sentence
mark is out; what remains is a mark that divides the text somewhere other than at
sentence boundaries -- verse-like units that run on grammatically, a non-linguistic
division, or blocks adjacent to a mark that are not words at all.

That sits oddly beside the spacing, which is ordinary prose-sentence scale: mean 19.6
blocks, CV 0.972, both inside a ten-register range
(`sentence_length_across_registers.py`). Units of sentence size whose edges are not
sentence edges.

## A cell that is not an anomaly

Offset +1 reads z = +2.64, and it is the register property rather than a finding: English
dips to -0.71 there on short opening function words, the LP register does not dip at all,
and the author is flat there too (-0.01 against -0.66). See `which_edge_is_anomalous.py`.

## Scope

The profile needs spans of nine blocks or more so the offsets stay distinct, which leaves
**97 marks** of the body's 148. The -1 cell measured over all spans reads -0.29 +- 0.20
and agrees.

    python the_long_block_is_nowhere.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import body_spans  # noqa: E402

OFFSETS = (-4, -3, -2, -1, 1, 2, 3, 4)
EDGE = 4  # the interior starts this far in, so no offset overlaps it


def profile(spans):
    """Mean block length at each offset from the span end, against the interior."""
    kept = [s for s in spans if len(s) >= 2 * EDGE + 1]
    interior = np.array([x for s in kept for x in s[EDGE : len(s) - EDGE]], float)
    out = {}
    for k in OFFSETS:
        v = np.array([s[k - 1 if k > 0 else len(s) + k] for s in kept], float)
        out[k] = (
            float(v.mean() - interior.mean()),
            math.hypot(
                v.std(ddof=1) / math.sqrt(len(v)),
                interior.std(ddof=1) / math.sqrt(len(interior)),
            ),
            len(v),
        )
    return out


def main() -> None:
    rng = random.Random(3301)
    registers = []
    for number in REGISTERS:
        path = fetch(number)
        if path is not None:
            registers.append(profile(register_spans(path, rng)))
    body = profile(body_spans())

    print("Mean block length at each offset from a mark, against the span interior.")
    print("Offset -1 is the block just before the mark, +1 the block just after.\n")
    print(f"{'offset':>7}{'ten registers':>21}{'the LP body':>21}{'z':>8}{'marks':>7}")
    english = {}
    for k in OFFSETS:
        v = np.array([r[k][0] for r in registers])
        english[k] = (float(v.mean()), float(v.std(ddof=1)))
        b, b_se, n = body[k]
        print(
            f"{k:>+7}{f'{v.mean():+.2f} +- {v.std(ddof=1):.2f}':>21}"
            f"{f'{b:+.2f} +- {b_se:.2f}':>21}"
            f"{(b - v.mean()) / math.hypot(b_se, v.std(ddof=1)):>+8.2f}{n:>7}"
        )

    peak, peak_value = max(((k, body[k][0]) for k in OFFSETS), key=lambda t: t[1])
    final, final_se = english[-1]
    print(
        f"\nThe body's largest value anywhere in the window is {peak_value:+.2f} at "
        f"offset {peak:+d},\nagainst the {final:+.2f} English puts at -1.\n"
    )

    print("Each displacement variant, scored against that lengthening.\n")
    print(f"{'variant':<36}{'offset':>8}{'the body':>18}{'z':>8}")
    for offset, label in (
        (-1, "the mark is at the sentence end"),
        (1, "the mark is one block EARLY"),
        (-2, "the mark is one block LATE"),
        (-3, "the mark is two blocks late"),
        (2, "the mark is two blocks early"),
    ):
        b, b_se, _ = body[offset]
        print(
            f"{label:<36}{offset:>+8}{f'{b:+.2f} +- {b_se:.2f}':>18}"
            f"{(b - final) / math.hypot(b_se, final_se):>+8.2f}"
        )

    print(
        "\nAll excluded. A displaced sentence mark is out, so the three surviving readings"
        "\nnow say one thing between them: no sentence ends at or near a mark. That sits"
        "\noddly beside the spacing, which is ordinary prose-sentence scale -- units of"
        "\nsentence size whose edges are not sentence edges."
        "\n\nOffset +1's z = +2.64 is not an anomaly: English dips there on short opening"
        "\nfunction words, the LP register does not dip at all, and the author is flat"
        "\nthere too."
    )


if __name__ == "__main__":
    main()
