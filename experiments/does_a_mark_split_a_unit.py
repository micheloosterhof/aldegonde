# ABOUTME: Tests whether a mark cuts a word or unit in two, and excludes it on the sum,
# ABOUTME: the variance and the correlation of the blocks either side.
"""Nothing is cut at a mark. The blocks either side are two ordinary independent blocks.

`sentences-do-not-end-long.md` keeps as one of three surviving readings that "a block
adjacent to a mark is not a word but a cipher-cut remainder". The **local** form of that
-- the mark falls inside a unit and splits it -- makes three predictions the other
readings do not, and block lengths are otherwise i.i.d.
(`block-lengths-are-detached`), so the control is clean.

| | splitting predicts | independence predicts | observed |
|---|---|---|---|
| mean of (before + after) | one unit, about 4.5 | two blocks, about 8.9 | **8.71 +- 0.25** |
| var(sum) / 2 var(block) | about 0.5 | 1.0 | **0.904 +- 0.099** |
| correlation across the mark | strongly negative | 0 | **-0.097, P = 0.21** |

The sum is **17 sigma** above one block. The variance ratio is **+4.07** from the 0.5 a
split would give and **-0.97** from the 1.0 independence gives. The correlation is 1.25
sigma from zero and would have to be far more negative for two halves of a fixed total.

Against the same statistics at every other adjacent pair -- mean 8.96, ratio 0.99,
r = -0.010 -- the mark-straddling pair is ordinary on all three.

Blocks two apart across a mark give r = -0.048, P = 0.54, so nothing is cut across a
wider span either.

## What it narrows

Reading 3's **local** form is excluded: no word and no unit of any size is divided at a
mark. What survives of it is the **global** form -- that no block anywhere is a word, the
mark-adjacent ones included -- which is not a claim about marks at all and belongs to
`blocks-are-still-words.md`, where the length distribution disfavours it: smooth cutting
laws are rejected with two free parameters where joined words fit with one.

Two readings are left standing as claims about the marks:

1. the marks are not sentence marks;
2. the marks open verse-like units that run on grammatically.

    python does_a_mark_split_a_unit.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from what_the_marks_are import blocks_with  # noqa: E402

MARKS = set("④⑬③⑩")


def pairs():
    """(before, after) block lengths across a mark, and at every other boundary."""
    rows = blocks_with(MARKS)
    lengths = np.array([r[0] for r in rows], float)
    precedes = [r[2] for r in rows]
    across = np.array(
        [[lengths[i], lengths[i + 1]] for i in range(len(lengths) - 1) if precedes[i]]
    )
    other = np.array(
        [
            [lengths[i], lengths[i + 1]]
            for i in range(len(lengths) - 1)
            if not precedes[i]
        ]
    )
    return across, other, lengths


def main() -> None:
    across, other, lengths = pairs()

    print("If a mark split a unit, the two halves would sum to that unit: a smaller")
    print("mean, a smaller variance, and a negative correlation between them.\n")
    print(
        f"{'pair':<30}{'n':>7}{'mean sum':>11}{'var(sum)':>11}"
        f"{'2 x var(block)':>16}{'r':>9}"
    )
    for label, v in (
        ("straddling a mark", across),
        ("every other adjacent pair", other),
    ):
        total = v[:, 0] + v[:, 1]
        independent = v[:, 0].var(ddof=1) + v[:, 1].var(ddof=1)
        r, _ = stats.pearsonr(v[:, 0], v[:, 1])
        print(
            f"{label:<30}{len(v):>7}{total.mean():>11.2f}{total.var(ddof=1):>11.2f}"
            f"{independent:>16.2f}{r:>9.3f}"
        )

    total = across[:, 0] + across[:, 1]
    independent = across[:, 0].var(ddof=1) + across[:, 1].var(ddof=1)
    n = len(across)
    ratio = total.var(ddof=1) / independent
    ratio_se = ratio * math.sqrt(2 / (n - 1))
    mean_se = total.std(ddof=1) / math.sqrt(n)
    r, p = stats.pearsonr(across[:, 0], across[:, 1])

    print("\nScoring the split against each statistic.\n")
    print(f"{'statistic':<34}{'observed':>18}{'vs split':>11}{'vs independent':>16}")
    print(
        f"{'mean of (before + after)':<34}{f'{total.mean():.2f} +- {mean_se:.2f}':>18}"
        f"{(total.mean() - lengths.mean()) / mean_se:>+11.1f}"
        f"{(total.mean() - 2 * lengths.mean()) / mean_se:>+16.2f}"
    )
    print(
        f"{'var(sum) / 2 var(block)':<34}{f'{ratio:.3f} +- {ratio_se:.3f}':>18}"
        f"{(ratio - 0.5) / ratio_se:>+11.2f}{(ratio - 1.0) / ratio_se:>+16.2f}"
    )
    print(
        f"{'correlation across the mark':<34}{f'{r:+.3f}':>18}"
        f"{'strongly -':>11}{r / (1 / math.sqrt(n)):>+16.2f}"
    )

    rows = blocks_with(MARKS)
    L = [x[0] for x in rows]
    pre = [x[2] for x in rows]
    far = np.array(
        [[L[i - 1], L[i + 1]] for i in range(1, len(L) - 1) if pre[i]], float
    )
    r2, p2 = stats.pearsonr(far[:, 0], far[:, 1])
    print(
        f"\nBlocks two apart across a mark: r = {r2:+.3f}, P = {p2:.3f} (n = {len(far)})"
    )

    print(
        "\nNo word and no unit of any size is divided at a mark. That excludes the LOCAL"
        "\nform of the cut-remainder reading. Its global form -- that no block anywhere is"
        "\na word -- is not a claim about marks and belongs to blocks-are-still-words.md,"
        "\nwhere smooth cutting laws are rejected with two free parameters and joined"
        "\nwords fit with one."
    )


if __name__ == "__main__":
    main()
