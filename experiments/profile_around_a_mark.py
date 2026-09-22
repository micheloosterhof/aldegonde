# ABOUTME: Measures unit length at each offset from a sentence mark, and finds the body
# ABOUTME: carries none of the three-point profile both English references share.
"""English marks a sentence end with three units, not one. The body marks it with none.

`sentences_do_not_end_long.py` measured one cell -- the unit just before a mark -- and
found no lengthening. Widening that to a profile over offsets shows the cell sits inside
a shape, and that both reference texts agree on the whole shape:

| offset | what it is | Austen | the LP author |
|---|---|---|---|
| -2 | penultimate: usually a function word before the final noun | -0.41 | -0.57 |
| **-1** | **final: a content word** | **+0.97** | **+1.26** |
| +1 | initial: usually a function word | -0.40 | -0.31 |

Three points, same sign, in a 5,361-sentence corpus and in the book's own author. The
body reads -0.01, **-0.21**, +0.07. Flat.

Only the -1 cell is individually decisive (z = -5.03 against joined Austen). The other
two lean the same way at 1.3 and 1.7 sigma, which is not evidence on its own -- 156
spans will not resolve a 0.3-rune contrast. The joint test over the three
pre-specified cells gives chi2 = 29.7 on 3 df, and it is dominated by -1.

**The +2 cell is not pre-specified.** It came out at +0.37 +- 0.21 against a predicted
-0.14, z = +2.45, and it was noticed in the data rather than predicted from English. It
is printed below and excluded from the joint test.

## What this corrects

`sentences_do_not_end_long.py` called the sentence-initial cell a control and said it
passes. That rested on comparing the body against the **author's 73 sentences**, where
the error bar is +-0.29 and nothing is resolvable. Against Austen the body's +1 contrast
is +0.07 +- 0.21 where -0.30 +- 0.03 is predicted: the wrong sign, at 1.67 sigma. The
control does not fail, but it does not pass either -- it is equivocal, and the earlier
file overstated it.

## What this adds

The marks partition the body at ordinary prose sentence density, which nothing so far
had checked. Units between consecutive marks: **17.2** in the body against **17.5** for
Austen once the body's own joining model is applied, and 19.2 before it. That is the
second check the joining model passes without having been fitted to it, the first being
the interior mean. It also does not match the author's own solved pages, which run 7.9
units per sentence -- those pages are aphoristic, the body's marks are prose-spaced.

    python profile_around_a_mark.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402
from sentences_do_not_end_long import (  # noqa: E402
    BODY,
    SENTENCE_MARKS,
    blocks,
    join,
    prose_sentences,
    walk,
)

# offsets English predicts a contrast at; +2 is printed but was not predicted
PREDICTED = (-2, -1, 1)
REPORTED = (-2, -1, 1, 2)
EDGE = 4  # a unit this far from either end counts as span interior


def spans_of(lengths_and_marks) -> list[list[int]]:
    """Unit lengths grouped into the runs between consecutive marks."""
    out: list[list[int]] = []
    current: list[int] = []
    for row in lengths_and_marks:
        current.append(row[0])
        if row[2]:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def body_spans() -> list[list[int]]:
    return spans_of(walk(BODY.read_text(), SENTENCE_MARKS))


def author_spans() -> list[list[int]]:
    """The sixteen solved pages, where the sentence mark is a period."""
    pages = MASTER.read_text().split("%")
    rows: list[tuple[int, bool, bool]] = []
    for n in PLAIN_PAGES:
        rows += blocks(pages[n], {"."})
    for t in json.loads(TRIPLES.read_text()):
        rows += blocks(pages[t["page"]], {"."})
    return spans_of(rows)


def contrasts(spans):
    """Each offset against the span interior, which is kept disjoint from every offset.

    The interior must start EDGE units in. Taking it from offsets +-3 and +-4 instead
    makes it overlap the signature cells in short spans -- in a five-unit span, offset
    +4 and offset -2 are the same unit.
    """
    cells: dict[int, list[int]] = {k: [] for k in REPORTED}
    interior: list[int] = []
    for s in spans:
        n = len(s)
        for k in REPORTED:
            j = k - 1 if k > 0 else n + k
            if 0 <= j < n:
                cells[k].append(s[j])
        interior += s[EDGE : n - EDGE]
    base = np.array(interior, float)
    out = {}
    for k in REPORTED:
        v = np.array(cells[k], float)
        out[k] = (
            float(v.mean() - base.mean()),
            math.hypot(
                v.std(ddof=1) / math.sqrt(len(v)),
                base.std(ddof=1) / math.sqrt(len(base)),
            ),
            len(v),
        )
    return out, float(base.mean()), len(base)


def main() -> None:
    rng = random.Random(3301)
    austen = prose_sentences()
    joined = [
        j for j in (join(s, 0.40, rng, forward=True) for s in austen) if len(j) >= 3
    ]
    texts = {
        "Pride and Prejudice": austen,
        "  same, joined q=0.40": joined,
        "the LP author": [s for s in author_spans() if len(s) >= 3],
        "the LP body": [s for s in body_spans() if len(s) >= 3],
    }

    print("Mean unit length at each offset from a mark, against the span interior.")
    print("Offset -1 is the unit just before a mark, +1 the unit just after.\n")
    header = f"{'text':<26}{'interior':>17}"
    for k in REPORTED:
        header += f"{k:>+15}"
    print(header)
    stats = {}
    for name, spans in texts.items():
        c, base, n_base = contrasts(spans)
        stats[name.strip()] = c
        row = f"{name:<26}{f'{base:.2f} ({n_base:,})':>17}"
        for k in REPORTED:
            row += f"{f'{c[k][0]:+.2f}+-{c[k][1]:.2f}':>15}"
        print(row)

    print("\nThe body against Austen carrying the body's own joining model.\n")
    print(f"{'offset':>7}{'body':>18}{'predicted':>18}{'z':>8}   note")
    chi = 0.0
    for k in REPORTED:
        lb, sb, _ = stats["the LP body"][k]
        la, sa, _ = stats["same, joined q=0.40"][k]
        z = (lb - la) / math.hypot(sa, sb)
        note = "predicted by English" if k in PREDICTED else "NOT pre-specified"
        if k in PREDICTED:
            chi += z * z
        print(
            f"{k:>+7}{f'{lb:+.2f} +- {sb:.2f}':>18}"
            f"{f'{la:+.2f} +- {sa:.2f}':>18}{z:>+8.2f}   {note}"
        )
    print(
        f"\njoint chi2 over the {len(PREDICTED)} pre-specified offsets = {chi:.1f} on"
        f" {len(PREDICTED)} df, dominated by offset -1"
    )

    print("\nDo the marks sit at sentence density? Units between consecutive marks.\n")
    for name, spans in (
        ("the LP body", body_spans()),
        ("Austen, joined q=0.40", joined),
        ("Austen, raw", austen),
        ("the LP author", author_spans()),
    ):
        v = np.array([len(s) for s in spans], float)
        print(
            f"  {name:<24}{v.mean():>6.1f}   (median {np.median(v):.0f},"
            f" {len(v):,} spans)"
        )
    print(
        "\nThe body matches prose spacing once its own joining is applied, and does not"
        "\nmatch the author's own pages, which are aphoristic at 7.9 units a sentence."
    )


if __name__ == "__main__":
    main()
