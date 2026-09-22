# ABOUTME: Decomposes the missing final-block lengthening by length class, to find whether
# ABOUTME: the body's span-final blocks fail at the short end, the long end, or both.
"""The final-block gap is a mean. Means hide which part of the distribution moved.

`which_edge_is_anomalous.py` reads both span edges as mean lengths and concludes the
initial edge cannot discriminate, because the LP author is as flat there as the body
(-0.01 against a ten-register mean of -0.66). That is true of the mean and not of the
distribution: `titles_are_just_sentence_initial.py` reports the body's share of two-rune
blocks rising from 0.154 to 0.224 after a mark, and the author's from 0.232 to 0.417.
**Both carry a span-initial signature that the mean cancels**, because the LP opens
sentences on long content verbs at the same time as on short function words.

So the mean is the wrong instrument and the whole length distribution should be read at
each edge. This asks where the missing lengthening actually is:

- if the body's span-final blocks are depleted of short words like English but never
  reach English's long tail, the anomaly is in the upper tail;
- if they look like ordinary interior blocks at every length, the final position carries
  no information at all;
- if they are *enriched* in short words, something is putting short blocks there.

Those are three different problems and the mean gives the same number for all of them.

## Why the edges must be read together

Three readings are on the table (`sentences-do-not-end-long.md`). Each predicts a pattern
across the two edges, not a single number:

| | span-initial signature | span-final signature |
|---|---|---|
| ④ closes a sentence, words in order | present | present |
| the words are transposed within the span | absent | absent |
| ④ is unrelated to the syntax | absent | absent |

A corpus showing one and not the other fits none of them, so the pair is worth more than
either cell.

    python where_in_the_distribution_is_the_anomaly.py
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

CLASSES = ((1, 2, "1-2"), (3, 4, "3-4"), (5, 6, "5-6"), (7, 99, "7+"))
MIN_SPAN = 3


def cells(spans):
    """(first blocks, last blocks, interior blocks) over spans of three or more."""
    kept = [s for s in spans if len(s) >= MIN_SPAN]
    return (
        [s[0] for s in kept],
        [s[-1] for s in kept],
        [x for s in kept for x in s[1:-1]],
    )


def profile(values) -> np.ndarray:
    a = np.array(values, float)
    return np.array([((a >= lo) & (a <= hi)).mean() for lo, hi, _ in CLASSES])


def lift(edge, interior) -> np.ndarray:
    """Share in each length class at the edge, minus the same at the interior."""
    return profile(edge) - profile(interior)


def se_of_lift(edge, interior) -> np.ndarray:
    pe, pi = profile(edge), profile(interior)
    return np.sqrt(pe * (1 - pe) / len(edge) + pi * (1 - pi) / len(interior))


def show(label, edge, interior, reference=None):
    d = lift(edge, interior)
    se = se_of_lift(edge, interior)
    row = f"{label:<26}{len(edge):>7}"
    for k in range(len(CLASSES)):
        cell = f"{d[k]:+.3f}"
        if reference is not None:
            cell += f" ({(d[k] - reference[k][0]) / math.hypot(se[k], reference[k][1]):+.1f})"
        row += f"{cell:>17}"
    print(row)
    return d, se


def main() -> None:
    rng = random.Random(3301)
    registers = [
        register_spans(p, rng) for p in (fetch(n) for n in REGISTERS) if p is not None
    ]
    body, author = body_spans(), author_spans()

    header = f"{'text':<26}{'blocks':>7}" + "".join(
        f"{label:>17}" for _, _, label in CLASSES
    )
    for edge_index, edge_name in ((0, "FIRST"), (1, "LAST")):
        print(f"\n{edge_name} block of a span, share in each length class minus the")
        print("same share in that span's interior.\n")
        print(header)
        ref = []
        per_register = []
        for spans in registers:
            c = cells(spans)
            per_register.append(lift(c[edge_index], c[2]))
        per_register = np.array(per_register)
        for k in range(len(CLASSES)):
            ref.append((per_register[:, k].mean(), per_register[:, k].std(ddof=1)))
        row = f"{'ten registers':<26}{'':>7}"
        for m, s in ref:
            row += f"{f'{m:+.3f} +- {s:.3f}':>17}"
        print(row)
        for label, spans in (("the LP author", author), ("the LP body", body)):
            c = cells(spans)
            show(label, c[edge_index], c[2], ref)
        print("  (bracketed: sigma from the ten-register mean, carrying its spread)")

    print("\nThe same two edges as plain means, for continuity with earlier work.\n")
    print(f"{'text':<26}{'first':>20}{'last':>20}")
    for label, spans in (("the LP author", author), ("the LP body", body)):
        first, last, interior = cells(spans)
        mid = np.mean(interior)
        for name, v in (("", first), ("", last)):
            pass
        row = f"{label:<26}"
        for v in (first, last):
            a = np.array(v, float)
            se = math.hypot(
                a.std(ddof=1) / math.sqrt(len(a)),
                np.std(interior, ddof=1) / math.sqrt(len(interior)),
            )
            row += f"{f'{a.mean() - mid:+.2f} +- {se:.2f}':>20}"
        print(row)


if __name__ == "__main__":
    main()
