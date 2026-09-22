# ABOUTME: Fits the merged fraction of long blocks from the d5 rate at each block length,
# ABOUTME: using the measured English within-word curve rather than a single assumed number.
"""The dilution has a predicted shape, not just a size. Use the shape.

`can_d5_see_the_joining.py` compares the body's d5 rate on blocks of eight runes or more
against a single English within-word figure and finds merging detected at two sigma. That
pools two things the model treats differently.

A two-rune merge puts the internal boundary at position 1 or 2, and a d5 pair (i, i+5)
straddles a boundary at `a` only when `i < a <= i+5`. So **exactly two pairs cross,
whatever the block's length** -- and a block of length L has L-5 pairs. The crossing
fraction is therefore `2/(L-5)`, which **falls** as blocks get longer:

| length | d5 pairs | crossing | fraction |
|---|---|---|---|
| 8 | 3 | 2 | 0.67 |
| 10 | 5 | 2 | 0.40 |
| 13 | 8 | 2 | 0.25 |

So the model predicts the largest dilution at length eight and less at every longer length.
That is a shape, and a shape is testable where a single number is not.

## The reference is measured, not assumed

The English within-word d5 rate is needed at each length, and it is not flat: 0.0356 at
six runes, 0.0539 at seven, 0.0687 at eight to nine, 0.0622 beyond. Measured over 203,764
pairs from six Gutenberg registers in runeglish.

An earlier version of this work assumed a flat 0.075 and reached the opposite conclusion,
so the curve is computed here rather than quoted.

## Result: merging detected at 2.8 sigma, with the predicted shape

| length | body d5 | English d5 | crossing fraction | implied merged fraction |
|---|---|---|---|---|
| 6 | 0.0352 +- 0.0115 | 0.0356 | 1.00 | +0.38 +- 10.54 |
| 7 | 0.0440 +- 0.0099 | 0.0539 | 1.00 | +0.51 +- 0.51 |
| **8-9** | **0.0474 +- 0.0076** | **0.0687** | 0.61 | **+1.02 +- 0.36** |
| 10-30 | 0.0612 +- 0.0095 | 0.0622 | 0.35 | +0.10 +- 0.98 |

**Combined: 0.78 +- 0.28, zero excluded at 2.8 sigma.**

**The shape holds.** Each length is an independent estimate of the same quantity, and they
agree at **chi2 = 1.2 on 3 df**. That is the part a single pooled cell could not test: the
model predicts the dilution to fall as `2/(L-5)`, so the 8-9 band should show the effect
most strongly and the 10-30 band least, and it does.

Note the six- and seven-rune bands have a crossing fraction of exactly 1.00 -- a block of
six runes has one d5 pair and a block of seven has two, and a boundary at position 2
crosses all of them. Their dilution should be total if they are merges, and their near-zero
implied fractions say they are not, which is what the model expects of short blocks.

## The one tension

The fitted joining model predicts **0.25** of blocks of 8+ runes are merges. d5 says
**0.78 +- 0.28** -- higher by 1.9 sigma. Three readings, none settled here:

- the true joining rate is higher than the histogram fit gives;
- some merged units are longer than two runes, which would change the crossing fraction
  and hence the inferred rate;
- the English within-word curve is too high for the body's register, inflating the
  apparent dilution.

The third is the one this corpus cannot check. The author's plaintext carries 158 d5 pairs
in total, so the only register-matched reference available is far too small.

    python fit_the_merge_rate_from_d5.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from can_d5_see_the_joining import BODY, d5, words  # noqa: E402
from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402

CHANCE = 1 / 29
BANDS = ((6, 6), (7, 7), (8, 9), (10, 30))
REGISTER_COUNT = 6


def english_words():
    out = []
    for number in REGISTERS[:REGISTER_COUNT]:
        path = fetch(number)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        trim = len(text) // 10
        for token in re.findall(r"[A-Za-z']+", text[trim : len(text) - trim]):
            runes = [c for c in to_runeglish(token.upper()) if c in IDX_ENG]
            if len(runes) >= 6:
                out.append(runes)
    return out


def crossing(lo: int, hi: int, lengths) -> float:
    """Mean fraction of a block's d5 pairs crossing a boundary at position 2."""
    kept = [x for x in lengths if lo <= x <= hi]
    return float(np.mean([min(2, x - 5) / (x - 5) for x in kept])) if kept else 0.0


def main() -> None:
    body = words(BODY)
    english = english_words()
    lengths = [len(w) for w in body]
    print(f"{len(body):,} body blocks; {len(english):,} English words of 6+ runes.\n")
    print(
        f"{'length':>8}{'body d5':>17}{'English d5':>13}{'crossing':>10}"
        f"{'implied merged':>17}"
    )
    rows = []
    for lo, hi in BANDS:
        _, pb, hb = d5(body, lo, hi)
        _, pe, he = d5(english, lo, hi)
        if not pb or not pe:
            continue
        rb, re_ = hb / pb, he / pe
        se = math.sqrt(rb * (1 - rb) / pb)
        frac = crossing(lo, hi, lengths)
        denom = frac * (re_ - CHANCE)
        m = (re_ - rb) / denom if denom > 0 else float("nan")
        sm = se / denom if denom > 0 else float("nan")
        rows.append((m, sm))
        print(
            f"{f'{lo}-{hi}':>8}{f'{rb:.4f} +- {se:.4f}':>17}{re_:>13.4f}"
            f"{frac:>10.2f}{f'{m:+.2f} +- {sm:.2f}':>17}"
        )

    w = np.array([1 / s**2 for _, s in rows])
    m = np.array([v for v, _ in rows])
    combined = float((w * m).sum() / w.sum())
    se = float(1 / math.sqrt(w.sum()))
    chi = float((w * (m - combined) ** 2).sum())
    print(
        f"\ncombined merged fraction {combined:+.2f} +- {se:.2f}"
        f"   (zero excluded at {combined / se:.1f} sigma)"
    )
    print(
        f"consistency across the four lengths: chi2 = {chi:.1f} on {len(rows) - 1} df"
    )
    print(
        "\n  The fitted joining model predicts 0.25 of blocks of 8+ runes are merges."
        "\n  Every cell is an independent estimate of the same quantity, so the chi2"
        "\n  is the check that the model's SHAPE holds, not just its size."
    )


if __name__ == "__main__":
    main()
