# ABOUTME: Tests every mark the body records for the sentence-final lengthening, and
# ABOUTME: finds none of them behaves like a full stop.
"""If the four-dot is not the full stop, nothing recorded in the body is.

Michel's reading of the result -- the words look English, the sentence structure does not,
and the four-dot may not be a full stop -- raises the obvious next question. The body
records several marks besides the four-dot. Does any of them carry the lengthening a full
stop carries?

Ten English registers put **+1.19 +- 0.28** runes on the block before a full stop, and the
LP author +1.32 +- 0.26. Every mark in the body, against blocks closed by the ordinary
separator:

| mark closing the block | n | gap vs interior | z vs +1.19 |
|---|---|---|---|
| four-dot | 136 | -0.32 +- 0.20 | **-4.41** |
| thirteen-dot | 25 | +0.03 +- 0.39 | -2.41 |
| three-dot | 4 | +0.51 +- 1.96 | -0.34 |
| quote | 7 | +0.51 +- 0.76 | -0.84 |
| ten-dot | 2 | too few | |
| all non-separator, non-four-dot | 39 | +0.21 +- 0.35 | -2.20 |
| **every mark together** | **175** | **-0.20 +- 0.17** | **-4.22** |

The ampersand and the section break close no block at all: they sit on their own lines,
which is why `does_the_cipher_restart.py` treats them as standalone markers.

The pooled non-four-dot row rests on 39 marks and reads -2.20 on its own -- suggestive,
not decisive. The row that carries the conclusion is **every mark together**: 175 marks,
-0.20 +- 0.17, four sigma below English.

## What this means

One hundred and seventy-five marks, and not one class of them precedes a long block. Combined with
`scans_verify_the_marks.py` -- the transcription's mark record is about 96% complete and
misplaces none -- the full stop is not a recorded mark being misread. It is either absent
from the record entirely, or absent from the text.

That is as far as the length channel reaches. It cannot say which, because a mark that
was never written leaves nothing to measure.

## What it does not show

The small cells are not evidence of anything on their own: three-dot has four marks and
quote seven, and both sit closer to +1.19 than to zero. Only the four-dot (136) and the
all-marks row (175) carry enough to exclude the lengthening; the thirteen-dot's 25 leave
it at -2.41 and the pooled remainder's 39 at -2.20, both suggestive rather than decisive.

    python no_mark_is_a_full_stop.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_cipher_restart import ANNOTATION, RUNE, STANDALONE  # noqa: E402
from sentences_do_not_end_long import BODY  # noqa: E402

from aldegonde import c3301  # noqa: E402

SEPARATOR = "①"
ENGLISH = (1.19, 0.28)  # final_lengthening_across_registers.py
MIN_CELL = 3


def closed_blocks():
    """(block length, the separator that closes it), on the corrected parse."""
    text = "\n".join(
        line
        for line in BODY.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    out, length = [], 0
    for ch in text:
        if RUNE.match(ch):
            length += 1
        elif ch == "\n" or ch in STANDALONE:
            continue
        elif ch in c3301.WORD_BOUNDARY and length:
            out.append((length, ch))
            length = 0
    if length:
        out.append((length, None))
    return out


def main() -> None:
    blocks = closed_blocks()
    interior = np.array([n for n, c in blocks if c == SEPARATOR], float)
    print(f"{len(blocks)} blocks, {len(interior)} closed by the ordinary separator.\n")
    print(
        f"{'mark closing the block':<28}{'n':>5}{'mean':>8}"
        f"{'gap vs interior':>19}{'z vs +1.19':>12}"
    )

    def cell(values):
        gap = float(values.mean() - interior.mean())
        se = math.hypot(
            values.std(ddof=1) / math.sqrt(len(values)),
            interior.std(ddof=1) / math.sqrt(len(interior)),
        )
        return gap, se

    for glyph, label in (
        ("④", "four-dot"),
        ("⑬", "thirteen-dot"),
        ("③", "three-dot"),
        ("⑩", "ten-dot"),
        ('"', "quote"),
    ):
        v = np.array([n for n, c in blocks if c == glyph], float)
        if len(v) < MIN_CELL:
            print(f"{label:<28}{len(v):>5}{'':>8}{'too few':>19}")
            continue
        gap, se = cell(v)
        print(
            f"{label:<28}{len(v):>5}{v.mean():>8.2f}{f'{gap:+.2f} +- {se:.2f}':>19}"
            f"{(gap - ENGLISH[0]) / math.hypot(se, ENGLISH[1]):>+12.2f}"
        )

    pooled = np.array([n for n, c in blocks if c not in (SEPARATOR, "④", None)], float)
    gap, se = cell(pooled)
    print(
        f"\n{'all non-separator, non-4-dot':<28}{len(pooled):>5}{pooled.mean():>8.2f}"
        f"{f'{gap:+.2f} +- {se:.2f}':>19}"
        f"{(gap - ENGLISH[0]) / math.hypot(se, ENGLISH[1]):>+12.2f}"
    )
    everything = np.array([n for n, c in blocks if c not in (SEPARATOR, None)], float)
    gap, se = cell(everything)
    print(
        f"{'every mark together':<28}{len(everything):>5}{everything.mean():>8.2f}"
        f"{f'{gap:+.2f} +- {se:.2f}':>19}"
        f"{(gap - ENGLISH[0]) / math.hypot(se, ENGLISH[1]):>+12.2f}"
    )

    print(
        f"\nTen English registers put {ENGLISH[0]:+.2f} +- {ENGLISH[1]:.2f} before a full"
        "\nstop, and the LP author +1.32 +- 0.26. Not one mark in the body does."
        "\n\nWith the transcription's mark record about 96% complete and misplacing none"
        "\n(scans_verify_the_marks.py), the full stop is not a recorded mark being"
        "\nmisread. It is either absent from the record or absent from the text, and the"
        "\nlength channel cannot say which: a mark never written leaves nothing to measure."
    )


if __name__ == "__main__":
    main()
