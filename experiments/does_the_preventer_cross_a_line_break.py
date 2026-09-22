# ABOUTME: Compares the doublet rate for adjacent rune pairs that straddle a written line
# ABOUTME: break against those that do not, which separates a cipher rule from a scribal one.
"""Is the doublet suppression part of the cipher, or something the scribe did by eye?

The body's adjacent-repeat rate is 0.0063 against a chance 0.0345, a 17-sigma deficit and
the largest single signal in the corpus. `the_transposition_precedes_the_cipher.py` shows
the suppression also acts **across a word boundary** -- the seam rate is 0.0079, four
times below chance -- so whatever does it does not stop at a separator.

A written line break is different in kind. To an algorithm it does not exist: the runes
are a stream and the line is layout. To a person checking his own output for a repeated
rune, a line break is exactly where a repeat stops being visible -- the two runes are at
opposite ends of the page, one at the end of a line and one at the start of the next.

So the two accounts split cleanly:

- **a cipher rule** suppresses straddling pairs at the same rate as any other, 0.0063;
- **a scribal rule applied by eye** lets them through at close to chance, 0.0345.

## Why this has power where other line tests did not

`line_structure.py` asks whether the line is a cipher unit by looking at pairs in the same
line but different blocks, and at position-in-line bucketing. Both spread a small signal
over many cells. This uses the corpus's strongest signal and one cell.

The body has about 600 written lines and 76% of them end mid-word, so roughly 450 adjacent
rune pairs straddle a break. At the suppressed rate that predicts about 3 doublets and at
chance about 16 -- a gap a Poisson count can resolve.

## What it cannot distinguish

A scribe who applied the rule to his exemplar before copying would show suppression
everywhere, including across line breaks of the final copy, because the line breaks were
not yet fixed. So a null here means "not applied at write time", not "not scribal".

## Result: it crosses, and the layout is invisible to it

| cell | pairs | doublets | rate | vs chance |
|---|---|---|---|---|
| inside a word, no line break | 9,640 | 60 | 0.0062 | -15.21 |
| inside a word, across a line break | 388 | 3 | 0.0077 | -2.89 |
| across a separator, no line break | 2,722 | 22 | 0.0081 | -7.55 |
| across a separator and a line break | 205 | 1 | 0.0049 | -2.32 |
| **all straddling a line break** | **593** | **4** | **0.0067** | |
| **all not straddling one** | **12,362** | **82** | **0.0066** | |

**The two rates are the same to the fourth decimal place.** A scribal rule applied by eye
predicts 20.4 doublets in the straddling cell and four were found, P = 9.3e-06. The
likelihood ratio for a stream rule over an eye rule is **25,700 to 1**.

No cell escapes. Suppression holds across a word boundary, across a line break, and across
both at once.

## What this settles

The doublet suppression is a property of the **rune stream**, not of the written page. The
account in which a scribe checked his own output for a repeated rune and adjusted it
cannot be right, because that check is exactly what a line break defeats: the two runes
are at opposite ends of the page.

That supports the preventer as a cipher-level mechanism -- a clock perturbation applied
while enciphering -- rather than a scribal tidy-up, which is what
`doublet-suppression-requires-design.md` assumes and had not tested.

## What it does not settle

A scribe who applied the rule to his **exemplar**, before copying it into the final
layout, would show exactly this pattern, because the line breaks did not exist yet. So the
result is "not applied by eye at write time", not "not scribal at all".

    python does_the_preventer_cross_a_line_break.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
CORPUS = ROOT / "data" / "page0-56.txt"
LINE_BREAKS = "/\n"
CHANCE = 1.0 / 29


def adjacent_pairs():
    """(equal?, straddles a line break?, crosses a separator?) for adjacent rune pairs.

    Adjacency is in the rune stream: two runes with nothing but line breaks and
    separators between them. The flags record what was in between.
    """
    text = CORPUS.read_text()
    out = []
    previous = None
    broke = False
    crossed = False
    for ch in text:
        if RUNE.match(ch):
            if previous is not None:
                out.append((ch == previous, broke, crossed))
            previous, broke, crossed = ch, False, False
        elif ch in LINE_BREAKS:
            broke = True
        elif ch in c3301.WORD_BOUNDARY:
            crossed = True
        elif ch in "%$&":
            previous = None
    return out


def rate(rows):
    hits = sum(1 for eq, _, _ in rows if eq)
    n = len(rows)
    return hits, n, (hits / n if n else float("nan"))


def main() -> None:
    rows = adjacent_pairs()
    print(f"{len(rows):,} adjacent rune pairs in the body.\n")

    cells = (
        ("inside a word, no line break", [r for r in rows if not r[1] and not r[2]]),
        ("inside a word, across a line break", [r for r in rows if r[1] and not r[2]]),
        ("across a separator, no line break", [r for r in rows if not r[1] and r[2]]),
        ("across a separator and a line break", [r for r in rows if r[1] and r[2]]),
    )
    print(f"{'cell':<38}{'pairs':>8}{'doublets':>10}{'rate':>9}{'vs chance':>12}")
    for label, sel in cells:
        hits, n, r = rate(sel)
        if not n:
            continue
        z = (r - CHANCE) / math.sqrt(CHANCE * (1 - CHANCE) / n)
        print(f"{label:<38}{n:>8,}{hits:>10}{r:>9.4f}{z:>+12.2f}")

    straddling = [r for r in rows if r[1]]
    flat = [r for r in rows if not r[1]]
    h1, n1, r1 = rate(straddling)
    h0, n0, r0 = rate(flat)
    print(f"\n{'all pairs straddling a line break':<38}{n1:>8,}{h1:>10}{r1:>9.4f}")
    print(f"{'all pairs not straddling one':<38}{n0:>8,}{h0:>10}{r0:>9.4f}")

    print("\nWhat each account predicts for the straddling cell.\n")
    print(f"{'account':<34}{'predicted doublets':>20}{'P(observed or fewer)':>24}")
    for label, p in (
        ("a cipher rule, rate 0.0063", r0),
        ("a scribal rule by eye, chance", CHANCE),
    ):
        expected = n1 * p
        tail = stats.binom.cdf(h1, n1, p)
        print(
            f"{label:<34}{expected:>20.1f}"
            f"{min(tail, 1 - stats.binom.cdf(h1 - 1, n1, p)):>24.2e}"
        )
    print(
        f"\n  observed {h1} doublets in {n1:,} straddling pairs"
        f"\n  likelihood ratio for the cipher rule: "
        f"{stats.binom.pmf(h1, n1, r0) / stats.binom.pmf(h1, n1, CHANCE):.3g} to 1"
    )


if __name__ == "__main__":
    main()
