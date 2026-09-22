# ABOUTME: Separates the two span edges against ten registers, showing the initial flatness
# ABOUTME: is an LP-register property and only the final edge is the body's own anomaly.
"""Only one of the two edges is anomalous, and the author shows which.

`sentences-do-not-end-long.md` measures the block before a mark and finds no lengthening.
It also records the block *after* a mark as "equivocal, not passing", against Austen alone.
With ten registers both edges can be read properly, and they separate.

## The two edges

First and last block of a span, each against that span's own interior:

| register | FIRST | LAST |
|---|---|---|
| pg1342 | -0.26 | +0.79 |
| pg205 | -0.68 | +1.12 |
| pg16643 | -0.22 | +1.37 |
| pg2945 | -0.62 | +1.43 |
| pg4363 | -0.96 | +1.40 |
| pg3296 | -0.81 | +0.90 |
| pg1497 | -0.79 | +1.50 |
| pg14209 | -1.00 | +1.26 |
| pg2680 | -0.62 | +1.15 |
| pg131 | -0.58 | +0.75 |
| **across ten** | **-0.66 +- 0.26** | **+1.17 +- 0.27** |
| **the LP body** | **+0.07 +- 0.23  (z = +2.08)** | **-0.29 +- 0.20  (z = -4.31)** |
| **the LP author** | **-0.01 +- 0.27** | **+1.32 +- 0.26** |

## What the author's row settles

**The first edge is not a body anomaly.** The author is flat there too (-0.01 against a
register mean of -0.66), so the LP's register simply lacks English's sentence-initial dip.
That dip comes from sentences opening on short function words; the LP opens on
imperatives -- `BELIEUE NOTHNG`, `TEST THE CNOWLEDGE`, `FIND YOUR TRUTH`,
`EXPERIENCE YOUR DEATH` -- which start on content verbs. Nothing to detect.

**The last edge is the body's alone.** The author lengthens at +1.32 +- 0.26, sitting on
top of the ten-register mean of +1.17 +- 0.27 (z = +0.42). The body reads -0.29 +- 0.20.

## The reading this excludes

`sentences-do-not-end-long.md` lists as its first reading that "the body's plaintext does
not lengthen its sentence-final words" -- a register property rather than a cipher or
scribal one. **That is now excluded by the book itself.** The LP author's own register
lengthens sentence-finally exactly as English does, so a register explanation requires the
body to be a different register from the front matter, which the block-length evidence
denies (`blocks-are-still-words.md`, `short-units-are-written-joined.md`).

It does not settle the remaining three. The initial edge cannot discriminate whether the
marks open or close, because the LP register has no dip there for either arrangement to
disturb.

    python which_edge_is_anomalous.py
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
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402


def edges(spans):
    """(first-block gap, last-block gap) against the span interior, with errors."""
    kept = [s for s in spans if len(s) >= 3]
    interior = np.array([x for s in kept for x in s[1:-1]], float)

    def gap(values):
        v = np.array(values, float)
        return (
            float(v.mean() - interior.mean()),
            math.hypot(
                v.std(ddof=1) / math.sqrt(len(v)),
                interior.std(ddof=1) / math.sqrt(len(interior)),
            ),
        )

    return gap([s[0] for s in kept]), gap([s[-1] for s in kept]), len(kept)


def main() -> None:
    rng = random.Random(3301)
    print("First and last block of a span, against that span's own interior.\n")
    print(f"{'register':<12}{'spans':>8}{'FIRST':>19}{'LAST':>19}")
    first, last = [], []
    for number in REGISTERS:
        path = fetch(number)
        if path is None:
            continue
        (f, f_se), (l, l_se), n = edges(register_spans(path, rng))
        first.append(f)
        last.append(l)
        print(
            f"pg{number:<10}{n:>8,}{f'{f:+.2f} +- {f_se:.2f}':>19}"
            f"{f'{l:+.2f} +- {l_se:.2f}':>19}"
        )

    first, last = np.array(first), np.array(last)
    spread = (first.std(ddof=1), last.std(ddof=1))
    print(
        f"{'across ten':<12}{'':>8}"
        f"{f'{first.mean():+.2f} +- {spread[0]:.2f}':>19}"
        f"{f'{last.mean():+.2f} +- {spread[1]:.2f}':>19}"
    )

    for label, source in (("the LP body", body_spans), ("the LP author", author_spans)):
        (f, f_se), (l, l_se), n = edges(source())
        zf = (f - first.mean()) / math.hypot(f_se, spread[0])
        zl = (l - last.mean()) / math.hypot(l_se, spread[1])
        print(
            f"{label:<12}{n:>8}{f'{f:+.2f} +- {f_se:.2f}':>19}"
            f"{f'{l:+.2f} +- {l_se:.2f}':>19}"
        )
        print(f"{'':<12}{'':>8}{f'z = {zf:+.2f}':>19}{f'z = {zl:+.2f}':>19}")

    print(
        "\nThe first edge is not a body anomaly: the author is flat there too, so the LP's"
        "\nregister lacks English's sentence-initial dip. That dip comes from sentences"
        "\nopening on short function words; the LP opens on imperatives -- BELIEUE NOTHNG,"
        "\nTEST THE CNOWLEDGE, FIND YOUR TRUTH -- which start on content verbs."
        "\n\nThe last edge is the body's alone. The author lengthens at +1.32, on top of the"
        "\nten-register mean of +1.17. So 'the body's plaintext simply does not lengthen'"
        "\nis excluded by the book itself: the same author's register does lengthen, and"
        "\nthe block-length evidence says the two halves share a register."
    )


if __name__ == "__main__":
    main()
