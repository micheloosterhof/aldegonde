# ABOUTME: Tests whether the hole at length two is positional within the line, and shows
# ABOUTME: the apparent eight-sigma effect is entirely spanning-block length bias.
"""If the scribe merged short words to make lines come out even, it would show by position.

`block-lengths-have-a-hole-at-two.md` leaves the hole unexplained after register,
orthography, section-to-section variation and line-break transcription are all ruled out.
Justification is the remaining scribal story: a scribe fitting text to a 21.8-rune line
might join a short word to its neighbour to make the line come out, and that would leave
a positional signature.

Assigning each block to the line its FIRST rune falls in, and splitting by position, the
signature looks overwhelming -- blocks last to start in a line are a rune and a half
longer than the rest and have half the 2-rune fraction, at eight sigma.

It is an artifact, and the file exists to name it. The block last to START in a line is
the block that SPANS the break, and long blocks span more often. That is the same length
bias `line_layout_and_the_hole.py` already measured: 454 spanning blocks against a
length-bias null of 459.1 +- 9.8.

Conditioning on it removes the effect entirely.

    python line_position_and_length.py
"""

from __future__ import annotations

import collections
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")


def blocks_with_line_position():
    """(length, position in its starting line, whether it spans a line break)."""
    text = (ROOT / "data" / "page0-56.txt").read_text()
    recs, cur, line, start, spans = [], 0, 0, None, False
    for ch in text:
        if RUNE.match(ch):
            if cur == 0:
                start, spans = line, False
            cur += 1
        elif ch in "/\n":
            line += 1
            if cur:
                spans = True
        elif ch in c3301.WORD_BOUNDARY:
            if cur:
                recs.append((cur, start, spans))
            cur = 0
    if cur:
        recs.append((cur, start, spans))
    per_line = collections.Counter(r[1] for r in recs)
    order = collections.Counter()
    out = []
    for length, ln, spans in recs:
        k = order[ln]
        order[ln] += 1
        where = "first" if k == 0 else ("last" if k == per_line[ln] - 1 else "middle")
        out.append((length, where, spans))
    return out


def table(rows, title: str, predicate) -> None:
    print(f"\n{title}\n")
    print(f"{'group':>10}{'blocks':>9}{'mean':>8}{'frac len 2':>12}{'z vs rest':>11}")
    for group in ("first", "middle", "last"):
        a = np.array([L for L, g, s in rows if g == group and predicate(s)], float)
        rest = np.array([L for L, g, s in rows if g != group and predicate(s)], float)
        if len(a) < 20:
            continue
        f1, f2 = (a == 2).mean(), (rest == 2).mean()
        se = math.sqrt(f1 * (1 - f1) / len(a) + f2 * (1 - f2) / len(rest))
        print(
            f"{group:>10}{len(a):>9,}{a.mean():>8.3f}{f1:>12.4f}{(f1 - f2) / se:>11.2f}"
        )


def main() -> None:
    rows = blocks_with_line_position()
    table(rows, "every block, by position in its starting line", lambda s: True)

    print("\nsplit by whether the block spans the line break:\n")
    print(f"{'group':>10}{'spans?':>9}{'blocks':>9}{'mean':>8}{'frac len 2':>12}")
    for group in ("first", "middle", "last"):
        for spans in (False, True):
            a = np.array([L for L, g, s in rows if g == group and s == spans], float)
            if len(a) < 20:
                continue
            print(
                f"{group:>10}{str(spans):>9}{len(a):>9,}{a.mean():>8.3f}"
                f"{(a == 2).mean():>12.4f}"
            )

    table(rows, "non-spanning blocks only", lambda s: not s)
    print(
        "\nThe eight-sigma effect is gone. Blocks last to START in a line are the blocks"
        "\nthat SPAN the break -- 454 of the 590 -- and long blocks span more often,"
        "\nwhich `line_layout_and_the_hole.py` already measured against a length-bias"
        "\nnull. Among blocks no break touches, no position differs from the rest by"
        "\ntwo sigma."
        "\n\nSo justification is not the story. The hole at length 2 is not positional"
        "\nwithin the line, and this is the third length-bias trap in the same statistic:"
        "\nany subset defined by where a block sits relative to a break over-samples long"
        "\nblocks by construction."
    )


if __name__ == "__main__":
    main()
