# ABOUTME: Measures the final-block gap at the section boundaries the red ink confirms,
# ABOUTME: which is the anomaly's strongest form: a boundary known real from outside the text.
"""A boundary the ink confirms, and the block before it still does not lengthen.

`sentences-do-not-end-long.md` rests on a comparison the corpus cannot fully underwrite:
the body's blocks before a mark do not lengthen, where ten English registers and the LP
author's own prose give +1.2 to +1.3. The standing objection has always been that the
marks might not be boundaries at all, in which case there is nothing to explain.

`do_the_marks_bound_the_titles.py` removed that objection for one glyph. The rubricated
titles are located from red ink and word lengths, with no mark used to find them, and the
thirteen-dot sits on their edges 6 times out of 6 mid-page (P = 9e-13) with 11 of 11
page-opening titles preceded by a page-final mark. **⑬ is a section boundary, confirmed
from outside the text.**

So the question can be asked in its strongest form. Take the boundaries the ink
corroborates and measure the block that ends them.

## Result: the ink anchor does not add power, and the anomaly stays where it was

| cell | blocks | gap vs interior | z vs +1.19 |
|---|---|---|---|
| before a ⑬ | 29 | +0.05 ± 0.36 | −2.51 |
| ...closing a red title | 14 | −0.29 ± 0.48 | −2.65 |
| ...closing ordinary prose | 15 | **+0.37 ± 0.52** | **−1.39** |
| before an ink-confirmed title | 16 | −0.24 ± 0.48 | −2.58 |
| before a ④ | 138 | −0.17 ± 0.21 | **−3.90** |

The pooled ⑬ cell looks like a 2.5-sigma confirmation, and the split shows it is not one.
Half of it is blocks that close a *red title*, where +1.19 is the wrong reference — that
figure is measured on sentence-final words in running prose, and a title is a noun phrase.
The other half, the fifteen ⑬ that close ordinary prose, is the cell with a matched
reference, and it reads **+0.37 ± 0.52: 0.7 sigma above zero and 1.4 below English.** It
discriminates nothing.

**So the ink confirms ⑬ is a boundary and cannot say whether the block before it
lengthens.** Thirty-one thirteen-dots is simply too few. The anomaly continues to rest
where it did, on the 138 blocks before a four-dot, which no ink anchors.

## One thing the titles do say

Inside a title, the first block runs short and the last does not:

| | blocks | mean length | share at 2 runes |
|---|---|---|---|
| first block of a title | 13 | 3.38 ± 0.47 | **0.385** |
| last block of a title | 13 | 4.46 ± 0.54 | 0.154 |
| every mark-free body block | 2,755 | 4.43 ± 0.04 | 0.161 |

**Last minus first, inside a title: +1.08 ± 0.72.** This is a paired contrast within the
same thirteen titles, so it needs no external reference. English titles run light to
heavy — THE, AN, OF are two runes in runeglish — so it is positive under word order in
place and zero under transposition. At 1.5 sigma from zero it leans against transposing
the titles and settles nothing.

    python the_ink_confirmed_boundary_does_not_lengthen.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from do_the_marks_bound_the_titles import (  # noqa: E402
    BODY,
    MASTER,
    TITLES,
    chunk_words,
)

SEPARATOR = "①"
MARKS = set("④⑬③⑩㉓")
ENGLISH_GAP = 1.19  # ten registers, final_lengthening_across_registers.py
ENGLISH_SE = 0.28
AUTHOR_GAP = 1.32  # the LP author's own prose, same file
MIN_TITLE_WORDS = 2


def body_stream():
    """(length, closing separator, chunk, index within the chunk) across the body."""
    chunks = {i: chunk_words(c) for i, c in enumerate(MASTER.read_text().split("%"))}
    out = []
    for i in BODY:
        for j, (n, sep) in enumerate(chunks.get(i, [])):
            out.append((n, sep, i, j))
    return out, chunks


def gap(chosen, interior) -> tuple[float, float, int]:
    a, b = np.array(chosen, float), np.array(interior, float)
    if len(a) < 3:
        return float("nan"), float("nan"), len(a)
    se = math.hypot(
        a.std(ddof=1) / math.sqrt(len(a)), b.std(ddof=1) / math.sqrt(len(b))
    )
    return float(a.mean() - b.mean()), se, len(a)


def report(label, chosen, interior, predicted=ENGLISH_GAP, pred_se=ENGLISH_SE):
    g, se, n = gap(chosen, interior)
    if math.isnan(g):
        print(f"{label:<38}{n:>8}{'too few':>20}")
        return
    z = (g - predicted) / math.hypot(se, pred_se)
    print(f"{label:<38}{n:>8}{f'{g:+.2f} +- {se:.2f}':>20}{z:>+14.2f}")


def main() -> None:
    stream, chunks = body_stream()
    titles = json.loads(TITLES.read_text())
    index = {}
    at = 0
    for i in BODY:
        for j in range(len(chunks.get(i, []))):
            index[(i, j)] = at
            at += 1

    interior = [n for n, sep, _, _ in stream if sep == SEPARATOR]
    print(f"{len(stream):,} body blocks, {len(interior):,} of them mark-free.\n")

    title_first, title_last, before_title = [], [], []
    for t in titles:
        a, b = t["word_range"]
        if (t["chunk"], b) not in index or (t["chunk"], a) not in index:
            continue
        first, last = index[(t["chunk"], a)], index[(t["chunk"], b)]
        if b - a + 1 >= MIN_TITLE_WORDS:
            title_first.append(stream[first][0])
            title_last.append(stream[last][0])
        if first > 0:
            before_title.append(stream[first - 1][0])

    print(
        "English predicts every one of these lifts. The author's own prose gives "
        f"{AUTHOR_GAP:+.2f}.\n"
    )
    print(f"{'cell':<38}{'blocks':>8}{'gap vs interior':>20}{'z vs +1.19':>14}")
    closes_title = {
        index[(t["chunk"], t["word_range"][1])]
        for t in titles
        if (t["chunk"], t["word_range"][1]) in index
    }
    thirteen = [i for i, (_, s, _, _) in enumerate(stream) if s == "⑬"]
    report("before a thirteen-dot", [stream[i][0] for i in thirteen], interior)
    report(
        "   of those, closing a red title",
        [stream[i][0] for i in thirteen if i in closes_title],
        interior,
    )
    report(
        "   of those, closing ordinary prose",
        [stream[i][0] for i in thirteen if i not in closes_title],
        interior,
    )
    report("before an ink-confirmed title", before_title, interior)
    report("before a four-dot", [n for n, s, _, _ in stream if s == "④"], interior)
    report("before any mark", [n for n, s, _, _ in stream if s in MARKS], interior)

    print("\nThe mirror signature: units that START run short.\n")
    print(f"{'cell':<38}{'blocks':>8}{'mean length':>20}{'share at 2 runes':>18}")
    for label, cell in (
        ("the first block of a title", title_first),
        ("the last block of a title", title_last),
        ("every mark-free body block", interior),
    ):
        a = np.array(cell, float)
        print(
            f"{label:<38}{len(a):>8}"
            f"{f'{a.mean():.2f} +- {a.std(ddof=1) / math.sqrt(len(a)):.2f}':>20}"
            f"{(a == 2).mean():>18.3f}"
        )

    a, b = np.array(title_first, float), np.array(title_last, float)
    d = b.mean() - a.mean()
    se = math.hypot(
        a.std(ddof=1) / math.sqrt(len(a)), b.std(ddof=1) / math.sqrt(len(b))
    )
    print(
        f"\nlast minus first, inside a title: {d:+.2f} +- {se:.2f} on {len(a)} titles."
        "\nEnglish noun phrases run light to heavy, so this is positive under word order"
        "\nin place and zero under transposition. With this sample the two differ by"
        f" {1.19 / se:.1f}"
        "\nsigma at best, so read it as a direction, not a verdict."
    )


if __name__ == "__main__":
    main()
