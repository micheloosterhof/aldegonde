# ABOUTME: Shows one-block gaps between marks do occur in the body, but never between two
# ABOUTME: four-dots, so the four-dot's floor is a rule rather than a limit of the medium.
"""A floor is only interesting if the alternative was possible.

`the_four_dot_has_a_floor.py` establishes that no two four-dots sit one block apart, where
a memoryless process predicts 6.8 such gaps and the author's own sentence convention
predicts 8.8. `does_the_floor_count_blocks_or_runes.py` leaves open whether the rule counts
words or runes.

Both rest on an assumption nobody checked: that a one-block gap between marks is possible
at all. If the transcription, the scribe's hand or the page never permits two marks that
close together, the four-dot's floor is a property of the medium and not of the mark.

The other marks answer it.

## Result: one-block gaps exist, and never between two four-dots

| pair kind | n | min blocks | min runes |
|---|---|---|---|
| four-dot to four-dot | 123 | **2** | **6** |
| every other pair | 47 | **1** | **3** |

Every pair separated by two blocks or fewer:

    ⑬ -> ⑬   1 block,  3 runes
    ⑬ -> ⑬   1 block,  3 runes
    ⑬ -> ④   2 blocks, 6 runes
    ④ -> ④   2 blocks, 6 runes
    ④ -> ④   2 blocks, 7 runes
    ④ -> ④   2 blocks, 7 runes
    ⑬ -> ⑬   2 blocks, 8 runes
    ④ -> ④   2 blocks, 9 runes
    ⑬ -> ⑬   2 blocks, 9 runes
    ⑬ -> ⑬   2 blocks, 9 runes
    ⑬ -> ⑬   2 blocks, 10 runes

**A one-block gap between marks is possible.** Two thirteen-dots sit one block and three
runes apart, twice. So the four-dot's floor is not a limit of the transcription, the hand
or the page -- the alternative was physically available and the four-dot never takes it.

## The direct comparison is confounded

| | at one block | total |
|---|---|---|
| four-dot to four-dot | 0 | 123 |
| every other pair | 2 | 47 |

Fisher exact **P = 0.075**, and it should not be quoted as the floor's evidence. Both
one-block cases are a **one-word rubricated title** bounded by its own pair of section
marks -- a distinct structure, not a scribe choosing to place two marks close together.

The floor stands on its own comparisons instead: zero against 6.8 expected under a
memoryless process and 8.8 under the author's own sentence convention
(`the_four_dot_has_a_floor.py`). What this file adds is the premise those rest on -- that
the medium permits what the four-dot avoids.

    python the_floor_belongs_to_the_four_dot.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, blocks  # noqa: E402

MARKS = set("④⑬③⑩㉓")
SMALL = 2


def mark_pairs():
    """(previous glyph, glyph, blocks between, runes between) for consecutive marks."""
    seq, nb, nr = [], 0, 0
    for length, glyph, _ in blocks(BODY):
        nb += 1
        nr += length
        if glyph in MARKS:
            seq.append((glyph, nb, nr))
            nb = nr = 0
    return [
        (seq[i - 1][0], seq[i][0], seq[i][1], seq[i][2]) for i in range(1, len(seq))
    ]


def main() -> None:
    pairs = mark_pairs()
    four = [p for p in pairs if p[0] == "④" and p[1] == "④"]
    other = [p for p in pairs if not (p[0] == "④" and p[1] == "④")]
    print(f"{len(pairs)} consecutive mark pairs in the body.\n")
    print(f"{'pair kind':<24}{'n':>6}{'min blocks':>13}{'min runes':>12}")
    print(
        f"{'four-dot to four-dot':<24}{len(four):>6}{min(p[2] for p in four):>13}"
        f"{min(p[3] for p in four):>12}"
    )
    print(
        f"{'every other pair':<24}{len(other):>6}{min(p[2] for p in other):>13}"
        f"{min(p[3] for p in other):>12}"
    )

    print(f"\nEvery pair separated by {SMALL} blocks or fewer:\n")
    for a, b, nb, nr in sorted(
        (p for p in pairs if p[2] <= SMALL), key=lambda p: (p[2], p[3])
    ):
        print(f"   {a} -> {b}   {nb} block{'s' if nb > 1 else ''}, {nr} runes")

    ones = Counter((a, b) for a, b, nb, _ in pairs if nb == 1)
    print(f"\none-block gaps by glyph pair: {dict(ones) or 'none'}")

    a = sum(1 for p in four if p[2] == 1)
    b = len(four) - a
    c = sum(1 for p in other if p[2] == 1)
    d = len(other) - c
    odds, p = stats.fisher_exact([[a, b], [c, d]])
    print(
        f"\n  four-dot pairs at one block: {a} of {len(four)}"
        f"\n  other pairs at one block:    {c} of {len(other)}"
        f"\n  Fisher exact P = {p:.3f}"
    )
    print(
        "\n  A one-block gap between marks IS possible -- two thirteen-dots sit one"
        "\n  block and three runes apart, twice. So the four-dot's floor is not a limit"
        "\n  of the transcription, the hand or the page."
        "\n\n  But the direct glyph comparison is confounded and reaches only P = 0.07:"
        "\n  both one-block cases are a ONE-WORD rubricated title bounded by its pair of"
        "\n  section marks, which is a distinct structure rather than a scribe choosing"
        "\n  to place two marks close together."
        "\n\n  The floor stands on its own comparisons -- 0 against 6.8 expected under a"
        "\n  memoryless process and 8.8 under the author's convention. What this adds is"
        "\n  that the alternative was physically available."
    )


if __name__ == "__main__":
    main()
