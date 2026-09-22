# ABOUTME: Asks whether the key-free d5 channel can detect the short-unit joining, and
# ABOUTME: shows it cannot, because a merge of a two-rune unit displaces almost no pairs.
"""A merged block spans a word boundary. Can the one key-free channel see it?

`short-units-are-written-joined.md` fits the body's 2-rune deficit with units of two runes
or less merged into a neighbour at q = 0.40, and `merged_or_telegraphic.py` shows the
model earns most of the distance from raw registers (chi2 105 down to 16-67) without
reaching a fit. Something beyond a single short-unit rule is shaping the histogram and
nothing has identified it.

There is one channel that reads the plaintext without a key. Within a block the base
cancels at distance five, so `c_i = c_(i+5)` exactly when `p_i = p_(i+5)`. A **merged**
block is two plaintext words concatenated, so its d5 pairs that straddle the internal
boundary are cross-word pairs -- and the README records cross-word d5 at chance where
within-word d5 runs 4.92%.

That predicts long blocks, which the joining model says are mostly merges, to show a
diluted d5 rate. It is an internal test needing no reference.

## What the measurement shows

| block length | blocks | d5 pairs | rate |
|---|---|---|---|
| 6 | 256 | 256 | 0.0352 |
| 7 | 216 | 432 | 0.0440 |
| 8-9 | 234 | 780 | 0.0474 |
| 10-20 | 109 | 637 | **0.0612** |

The rate **rises** with length. Short blocks (6-7) read 0.0407 and long ones (8+) 0.0536,
a difference of -0.0129 +- 0.0096, z = -1.34.

## Why that is not evidence against joining

It looked like the opposite of the prediction. It is not, and the arithmetic is the point.

**The joining model merges a unit of two runes or less**, so the internal boundary sits at
position 1 or 2, not in the middle. A d5 pair (i, i+5) straddles a boundary at `a` only
when `i < a <= i+5`, so a boundary at position 2 is crossed by exactly **two** pairs
however long the block is:

| L | a | d5 pairs | crossing |
|---|---|---|---|
| 10 | 2 | 5 | 2 |
| 10 | 5 | 5 | 5 |
| 12 | 2 | 7 | 2 |
| 12 | 6 | 7 | 5 |

A merge in the middle would displace every pair. A merge of a two-rune unit displaces two.

Taking the within-word rate at 0.075 and cross-word at chance, the predicted long-block
rate runs from **0.0750** with no merges to **0.0588** with every long block a merge -- a
spread of 0.016 against a measurement error of **+-0.0095**. The channel separates "no
merging at all" from "universal merging" at about **1.7 sigma**, and every intermediate
value less.

## And there is no reference

The author's plaintext pages carry **158 d5 pairs in total**, giving cell rates of 0.0000,
0.1250, 0.0484 and 0.0250 across the four length bands. There is nothing to calibrate
against even if the body's signal were larger.

## Conclusion

**d5 cannot test the joining model.** The route is closed by arithmetic rather than by
sample size: the model's own parameter -- merging units of two runes or less -- is what
makes its effect on the channel too small to see. A model that merged longer units would
be testable this way; this one is not.

    python can_d5_see_the_joining.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
MARKS = set("④⑬③⑩㉓.")
SEPARATORS = set("①-")
BODY = range(15, 71)
PLAIN = (3, 8, 9, 10, 11, 14)
BANDS = ((6, 6), (7, 7), (8, 9), (10, 30))
CHANCE = 1 / 29
WITHIN = 0.075


def words(chunks):
    """Blocks as rune indices, carried across line wraps."""
    text = MASTER.read_text().split("%")
    out, cur = [], []
    for ci in chunks:
        if ci >= len(text):
            continue
        for line in re.split(r"[/\n]", text[ci]):
            if not RUNE.search(line):
                continue
            for ch in line:
                if RUNE.match(ch):
                    cur.append(INDEX[ch])
                elif (ch in MARKS or ch in SEPARATORS) and cur:
                    out.append(cur)
                    cur = []
    if cur:
        out.append(cur)
    return out


def d5(rows, lo, hi):
    pairs = hits = count = 0
    for w in rows:
        if lo <= len(w) <= hi:
            count += 1
            for i in range(len(w) - 5):
                pairs += 1
                hits += w[i] == w[i + 5]
    return count, pairs, hits


def show(label, rows):
    print(f"\n{label}\n")
    print(f"{'length':>10}{'blocks':>9}{'d5 pairs':>10}{'rate':>9}")
    for lo, hi in BANDS:
        count, pairs, hits = d5(rows, lo, hi)
        if pairs:
            print(f"{f'{lo}-{hi}':>10}{count:>9}{pairs:>10}{hits / pairs:>9.4f}")
    _, p1, h1 = d5(rows, 6, 7)
    _, p2, h2 = d5(rows, 8, 30)
    if p1 and p2:
        a, b = h1 / p1, h2 / p2
        se = math.sqrt(a * (1 - a) / p1 + b * (1 - b) / p2)
        print(
            f"{'short 6-7':>10}{'':>9}{p1:>10}{a:>9.4f}\n"
            f"{'long 8+':>10}{'':>9}{p2:>10}{b:>9.4f}\n"
            f"   difference {a - b:+.4f} +- {se:.4f}   z = {(a - b) / se:+.2f}"
        )


def main() -> None:
    show("THE BODY", words(BODY))
    show("THE AUTHOR, plaintext pages (d5 is literal letter equality)", words(PLAIN))

    print("\n\nHow many d5 pairs a merge actually displaces.\n")
    print(f"{'L':>5}{'boundary at':>13}{'d5 pairs':>10}{'crossing':>10}")
    for length in (10, 12):
        for at in (1, 2, length // 2):
            pairs = [(i, i + 5) for i in range(length - 5)]
            crossing = sum(1 for i, j in pairs if i < at <= j)
            print(f"{length:>5}{at:>13}{len(pairs):>10}{crossing:>10}")

    print(
        f"\nWith the within-word rate at {WITHIN} and cross-word at chance"
        f" {CHANCE:.4f},\nand a two-rune merge crossing 2 of a length-10 block's 5 pairs:"
    )
    for m in (0.0, 0.5, 1.0):
        frac = 2 / 5
        print(
            f"   a fraction {m:.1f} of long blocks merged -> predicted"
            f" {(1 - m * frac) * WITHIN + m * frac * CHANCE:.4f}"
        )
    _, pairs, hits = d5(words(BODY), 10, 30)
    print(
        f"   observed                                 "
        f"  {hits / pairs:.4f} +- {math.sqrt((hits / pairs) * (1 - hits / pairs) / pairs):.4f}"
    )
    print(
        "\nThe whole range of the model spans 0.016 against an error of 0.0095, so the"
        "\nchannel separates no merging from universal merging at about 1.7 sigma."
    )


if __name__ == "__main__":
    main()
