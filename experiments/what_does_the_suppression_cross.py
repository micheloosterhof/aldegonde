# ABOUTME: A complete census of what the doublet suppression crosses -- separators, line
# ABOUTME: breaks, marks, page and section breaks -- which bounds the cipher stream's extent.
"""What has to sit between two runes before the suppression stops seeing them as adjacent?

The body's adjacent-repeat rate is 0.0063 against a chance 0.0345, the largest single
signal in the corpus. Two of its boundaries are known:

- it crosses a **word separator** -- seam rate 0.0079
  (`the_transposition_precedes_the_cipher.py`);
- it crosses a **written line break** -- 0.0067 against 0.0066, at 25,700 to 1 over an
  eye rule (`the-preventer-is-in-the-stream.md`).

The remaining boundaries have never been tested, and one of them is a live question. If
the suppression does **not** cross a four-dot, then the four-dot interrupts the cipher
stream and is a cipher-level object rather than a scribal one. `does_the_cipher_restart.py`
excludes a base *reset* at a mark and a cycling key is excluded too
(`a_shifted_stop_or_a_switched_key.py`), but neither tests whether the stream itself
continues through the mark.

This is a different question from those. A base reset changes the alphabet; a break in the
stream changes what counts as adjacent. The preventer is the only instrument that can see
the second.

## The cells and what they can resolve

Every adjacent pair of runes is classified by what lies between them. The count sets the
resolution, so each cell is reported with the doublets each account predicts:

- a **stream** account predicts the within-word rate, about 0.0063;
- a **break** account predicts chance, 0.0345.

At 182 pairs across a mark those are 1.2 and 6.3, which a Poisson count separates. Below
about 60 pairs -- page breaks, section breaks -- nothing can be resolved and the cells are
printed for completeness only.

## Result: it crosses everything that can be tested

Within-word rate 0.0062; chance 0.0345.

| what lies between the two runes | pairs | doublets | rate | vs chance | stream predicts | break predicts | LR for stream |
|---|---|---|---|---|---|---|---|
| nothing (inside a word) | 9,640 | 60 | 0.0062 | -15.21 | 60.0 | 332.4 | (the baseline) |
| a separator only | 2,587 | 21 | 0.0081 | -7.35 | 16.1 | 89.2 | **3e+16 to 1** |
| a line break only | 389 | 3 | 0.0077 | -2.89 | 2.4 | 13.4 | **403 to 1** |
| **a MARK (any dot cluster)** | **156** | **1** | **0.0064** | -1.92 | 1.0 | 5.4 | **16 to 1** |
| a separator and a line break | 124 | 1 | 0.0081 | -1.61 | 0.8 | 4.3 | 6 to 1 |
| a page break | 45 | 0 | 0.0000 | -1.27 | 0.3 | 1.6 | - |
| a section break | 14 | 0 | 0.0000 | -0.71 | 0.1 | 0.5 | - |

**The mark cell reads 0.0064 -- the within-word rate.** One doublet where a break at the
mark predicts 5.4: P = 0.028 against a break, and 0.62 against a continuing stream. At 16
to 1 that is support, not proof, and the cell is small.

Page and section breaks give 45 and 14 pairs. Neither can resolve the question and both
are printed for completeness only.

## What this adds

**The cipher stream runs through the four-dot.** Three separate things are now excluded at
the mark: the base does not reset (`does_the_cipher_restart.py`, z = -0.96 against +53 for
a planted reset), the key does not cycle through any period to eight
(`a_shifted_stop_or_a_switched_key.py`), and the stream does not break.

Those are different claims. A base reset changes the alphabet; a cycling key changes which
alphabet; a stream break changes what counts as adjacent. The preventer is the only
instrument that can see the third, because it is the only mechanism in the model that
depends on adjacency.

So the four-dot is invisible to the cipher in every way the corpus can test. Taken with
`the-four-dot-is-not-layout-coupled.md` -- it gets no line break and no extra space -- and
with the absent sentence-final lengthening, the mark is now something the cipher ignores,
the scribe's layout ignores, and the syntax does not obviously drive.

    python what_does_the_suppression_cross.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))


RUNE = re.compile(r"[ᚠ-᛿]")
CORPUS = ROOT / "data" / "page0-56.txt"
LINE_BREAKS = "/\n"
MARKS = set("④⑬③⑩㉓.")
SEPARATORS = set("①-")
PAGE = "%"
SECTION = set("$&")
CHANCE = 1.0 / 29
RESOLVABLE = 60


def pairs():
    """(equal?, frozenset of what lay between) for every adjacent rune pair."""
    out = []
    previous = None
    between: set[str] = set()
    for ch in CORPUS.read_text():
        if RUNE.match(ch):
            if previous is not None:
                out.append((ch == previous, frozenset(between)))
            previous, between = ch, set()
        elif ch in LINE_BREAKS:
            between.add("line")
        elif ch in MARKS:
            between.add("mark")
        elif ch in SEPARATORS:
            between.add("separator")
        elif ch == PAGE:
            between.add("page")
        elif ch in SECTION:
            between.add("section")
    return out


def cell(rows, keep, drop=()):
    return [
        r
        for r in rows
        if all(k in r[1] for k in keep) and not any(d in r[1] for d in drop)
    ]


def report(label, rows, baseline, *, is_baseline=False):
    hits, n = sum(1 for eq, _ in rows if eq), len(rows)
    if not n:
        return
    r = hits / n
    z = (r - CHANCE) / math.sqrt(CHANCE * (1 - CHANCE) / n)
    stream, brk = n * baseline, n * CHANCE
    lr = (
        stats.binom.pmf(hits, n, baseline) / stats.binom.pmf(hits, n, CHANCE)
        if n
        else float("nan")
    )
    if is_baseline:
        verdict = "(the baseline)"
    elif n < RESOLVABLE:
        verdict = "-"
    elif lr > 1e4:
        verdict = f"{lr:.0e} to 1"
    else:
        verdict = f"{lr:,.0f} to 1"
    print(
        f"{label:<34}{n:>7,}{hits:>6}{r:>9.4f}{z:>10.2f}"
        f"{stream:>8.1f}{brk:>8.1f}{verdict:>16}"
    )


def main() -> None:
    rows = pairs()
    inside = cell(rows, [], ["line", "mark", "separator", "page", "section"])
    baseline = sum(1 for eq, _ in inside if eq) / len(inside)
    print(f"{len(rows):,} adjacent rune pairs in the body.")
    print(f"Within-word rate {baseline:.4f}; chance {CHANCE:.4f}.\n")
    print(
        f"{'what lies between the two runes':<34}{'pairs':>7}{'dbl':>6}{'rate':>9}"
        f"{'vs chance':>10}{'stream':>8}{'break':>8}{'LR for stream':>16}"
    )
    report("nothing (inside a word)", inside, baseline, is_baseline=True)
    report("a line break only", cell(rows, ["line"], ["mark", "separator", "page", "section"]), baseline)
    report("a separator only", cell(rows, ["separator"], ["mark", "line", "page", "section"]), baseline)
    report("a separator and a line break", cell(rows, ["separator", "line"], ["mark", "page", "section"]), baseline)
    report("a MARK (any dot cluster)", cell(rows, ["mark"], ["page", "section"]), baseline)
    report("a page break", cell(rows, ["page"], ["section"]), baseline)
    report("a section break", cell(rows, ["section"]), baseline)

    print(
        "\n  'stream' and 'break' are the doublets each account predicts."
        f"\n  Cells under {RESOLVABLE} pairs cannot separate them and print no verdict."
    )

    marked = cell(rows, ["mark"], ["page", "section"])
    hits, n = sum(1 for eq, _ in marked if eq), len(marked)
    print(
        f"\nThe mark cell: {hits} doublets in {n} pairs."
        f"\n  P(this few or fewer under a break at the mark) = "
        f"{stats.binom.cdf(hits, n, CHANCE):.2e}"
        f"\n  P(this many or more under a continuing stream)  = "
        f"{stats.binom.sf(hits - 1, n, baseline):.2f}"
    )


if __name__ == "__main__":
    main()
