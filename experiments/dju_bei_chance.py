# ABOUTME: Recomputes the chance probability of the DJU-BEI repeat under three framings,
# ABOUTME: because the figure the project carries matches none of them.
"""The one cell no model reaches rests on a number nobody recomputed.

`returns` is the only battery cell failed by every model in this directory AND by every
deliberately wrong cipher (`models-on-the-informative-cells.md`): the corpus has one exact
state return, the DJU-BEI repeat, and simulations produce none. Its weight depends
entirely on how likely such a repeat is by chance, and the figure carried here --
"~1%", from `rotor-machine-compact-state.md` -- has not been rederived.

Three framings, and they differ by three orders of magnitude:

    all 6-rune windows              any repeated 6-gram anywhere
    block-aligned, whole blocks     what a key-state recurrence would produce
    (3,3) units only                the shape actually observed

The middle one is the principled test. A state return reproduces the same alphabet at the
same phase, so its repeat necessarily starts at a block boundary and spans whole blocks --
that is a prediction of the mechanism, not a filter chosen after the fact. Restricting
further to (3,3) is post-hoc; ignoring alignment altogether tests a different hypothesis.

    python dju_bei_chance.py
"""

from __future__ import annotations

import collections
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29


def blocks_of(stream, wid):
    out, cur = [], []
    for i, v in enumerate(stream):
        if i and wid[i] != wid[i - 1]:
            out.append(tuple(cur))
            cur = []
        cur.append(v)
    out.append(tuple(cur))
    return out


def aligned_windows(blocks, length: int):
    """Windows starting at a block boundary and spanning whole blocks, `length` runes."""
    out = []
    for i in range(len(blocks)):
        total, j = 0, i
        while j < len(blocks) and total < length:
            total += len(blocks[j])
            j += 1
        if total == length:
            out.append(tuple(x for b in blocks[i:j] for x in b))
    return out


def main() -> None:
    stream, wid = load_clean()
    blocks = blocks_of(stream, wid)
    counts = collections.Counter(stream)
    n = len(stream)
    p2 = sum((v / n) ** 2 for v in counts.values())
    print(f"{len(blocks):,} blocks, {n:,} runes")
    print(f"per-rune match probability from the corpus's own unigrams: {p2:.5f}\n")

    windows = [tuple(stream[i : i + 6]) for i in range(n - 5)]
    lam_all = len(windows) * (len(windows) - 1) // 2 * p2**6
    units = [
        (blocks[i], blocks[i + 1])
        for i in range(len(blocks) - 1)
        if len(blocks[i]) == 3 and len(blocks[i + 1]) == 3
    ]
    lam_33 = len(units) * (len(units) - 1) // 2 * p2**6

    lam_aligned = 0.0
    print(f"{'length':>7}{'windows':>9}{'expected repeats':>18}")
    for length in range(6, 15):
        al = aligned_windows(blocks, length)
        e = len(al) * (len(al) - 1) // 2 * p2**length
        lam_aligned += e
        if e > 1e-9:
            print(f"{length:>7}{len(al):>9}{e:>18.6f}")

    print(f"\n{'framing':<40}{'P(at least one)':>18}")
    for label, lam in (
        ("any repeated 6-gram anywhere", lam_all),
        ("block-aligned, whole blocks, 6+ runes", lam_aligned),
        ("(3,3) units only", lam_33),
    ):
        p = 1 - math.exp(-lam)
        print(f"{label:<40}{p:>18.5f}   (1 in {1 / p:,.0f})")
    print(
        "\nThe project records ~1%, which is none of these. The principled figure is the"
        "\nmiddle one: about 1 in 2,700, roughly thirty times more surprising than the"
        "\nnumber in circulation. Longer alignments add nothing -- at length 7 the"
        "\nexpectation is already 1.3e-5 -- so the sum is dominated by length 6."
    )


if __name__ == "__main__":
    main()
