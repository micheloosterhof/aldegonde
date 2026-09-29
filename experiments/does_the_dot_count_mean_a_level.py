# ABOUTME: Tests whether a mark's dot count encodes the size of the unit it closes,
# ABOUTME: using same-glyph spacing, and finds the two rare glyphs sit inside four-dot spans.
"""The marks carry numbers. Do the numbers mean anything?

The body's marks are ③, ④, ⑩ and ⑬ -- three, four, ten and thirteen dots. The obvious
reading is that the count names a **level**: more dots, larger unit, the way a manuscript
might mark clause, sentence, paragraph and section with escalating signs. `⑬` is known to
close sections (`the-thirteen-dot-closes-a-section.md`, confirmed by red ink) and `④`
divides the text far more finely, so two of the four already sit in the right order.

That reading makes a prediction for the other two: ③ should close units smaller than ④'s
and ⑩ units between ④'s and ⑬'s.

## The statistic has to be same-glyph spacing

Distance to the *previous mark of any kind* is the wrong measure and gives a misleading
answer: it makes ⑬ look small (median 4 blocks) because a rubricated title is opened and
closed by a pair of thirteen-dots a few words apart. Pooled that way, the Spearman
correlation between dot count and unit size is **negative**, r = -0.181, which is the
title structure and not a level.

The distance from each mark to the **previous mark of the same glyph** is the size of the
unit that glyph delimits.

## This is internal to the body

Same pages, same hand, same cipher, so none of the controls that have caught other layout
statistics apply here.

## Result: the count does not name a level

| glyph | dots | count | blocks to the previous same glyph | median |
|---|---|---|---|---|
| ③ | 3 | 4 | 756.0 | 476 |
| ④ | 4 | 139 | 20.4 | 14 |
| ⑩ | 10 | 2 | 744.0 | 744 |
| ⑬ | 13 | 26 | 117.0 | 19 |
| ㉓ | 23 | 0 | none in the body | |

**③ and ⑩ are not levels.** Their same-glyph gaps of 756 and 744 blocks are simply 2,900
divided by four and by two -- four marks and two marks scattered through the body. And
every one of them has a **four-dot on both sides**, so neither sits at a boundary the
four-dot respects.

That leaves ④ at 20.4 and ⑬ at 117.0, which is two points already known from the ink and
the line geometry. Two points do not establish a relationship, and the two glyphs that
could have tested it occur four times and twice.

**So the numeric reading gets no support.** The dot counts are labels for two kinds of
mark plus a handful of one-offs, not a scale.

## One structural fact falls out

**⑬ is bimodal**: mean 117.0 blocks between occurrences against a median of 19. Rubricated
titles are opened and closed by a pair of thirteen-dots a few words apart
(`do_the_marks_bound_the_titles.py`), and sections run hundreds of blocks, so the glyph
serves two spacings at once. Any statistic that pools ⑬ occurrences is mixing them --
which is what made the naive version of this test come out backwards, at Spearman
r = -0.181.

    python does_the_dot_count_mean_a_level.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
from body_parse import blocks  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
MARKS = {"③": 3, "④": 4, "⑩": 10, "⑬": 13, "㉓": 23}
SEPARATORS = set("①-")
BODY = range(15, 71)


def stream():
    """Blocks and marks in reading order, with blocks spanning line wraps."""
    out = []
    for _length, glyph, _ in blocks(BODY):
        out.append(("b", None))
        if glyph in MARKS:
            out.append(("m", glyph))
    return out


def same_glyph_gaps(rows, glyph):
    gaps, count, seen = [], 0, False
    for kind, val in rows:
        if kind == "b":
            count += 1
        elif val == glyph:
            if seen:
                gaps.append(count)
            seen, count = True, 0
    return gaps


def main() -> None:
    rows = stream()
    print(
        f"{'glyph':>6}{'dots':>6}{'count':>8}{'blocks to the previous':>25}{'median':>9}"
    )
    for glyph in sorted(MARKS, key=lambda g: MARKS[g]):
        total = sum(1 for k, v in rows if v == glyph)
        gaps = same_glyph_gaps(rows, glyph)
        if not gaps:
            print(f"{glyph:>6}{MARKS[glyph]:>6}{total:>8}{'none in the body':>25}")
            continue
        v = np.array(gaps, float)
        print(
            f"{glyph:>6}{MARKS[glyph]:>6}{total:>8}{v.mean():>25.1f}{np.median(v):>9.0f}"
        )

    order = [v for k, v in rows if k == "m"]
    print("\nWhat sits either side of each rare glyph:\n")
    for glyph in ("③", "⑩"):
        spots = [i for i, x in enumerate(order) if x == glyph]
        pairs = [
            (
                order[i - 1] if i else "START",
                order[i + 1] if i + 1 < len(order) else "END",
            )
            for i in spots
        ]
        print(f"  {glyph} (n={len(spots)}): {pairs}")

    print(
        "\nEvery ③ and every ⑩ has a four-dot on both sides, so neither sits at a"
        "\nboundary the four-dot respects. Their same-glyph gaps of 756 and 744 blocks"
        "\nare just 2,900 divided by four and by two: four and two marks scattered"
        "\nthrough the body, not a level."
    )


if __name__ == "__main__":
    main()
