# ABOUTME: Scans the body for a run where the doublet suppression fails, which would be a
# ABOUTME: locally weaker cipher and the only wedge a key search could start from.
"""If the preventer ever lapsed, that stretch is the easiest text in the book.

The doublet suppression is the body's largest signal: 0.0063 against a chance 0.0345 over
10,028 within-word adjacent pairs, and `what_does_the_suppression_cross.py` shows it holds
across separators, line breaks and marks alike. Every test so far has asked whether it
holds **on average**.

A lapse would not show in an average. If one page, or one stretch of a few hundred runes,
were enciphered without the preventer, its doublets would return to chance -- seventeen in
five hundred pairs instead of three -- while the pooled rate moved by less than a tenth of
its own standard error.

That matters beyond tidiness. `why-the-body-resists.md` argues the corpus gives a key
search nothing to climb: 13 bits of local information against 285 of key, and a flat
landscape. **A stretch enciphered with a weaker mechanism is exactly the foothold that
argument says does not exist**, so it is worth looking for directly rather than assuming
uniformity.

## The test

A sliding window over the adjacent-pair stream, counting doublets. The statistic is the
window **maximum**, which is a scan and therefore has to be priced against a surrogate
null rather than a binomial tail -- 12,955 positions give many chances at a high count.
The null shuffles the pair-level doublet flags, which preserves the total exactly and
destroys only their arrangement.

Three window widths, since a lapse could be a page or a section.

## What a positive would mean, and what it would not

A window at chance would say the mechanism was absent there. It would not say the cipher
was different there -- `the-body-is-one-cipher.md` finds no per-page heterogeneity in
doublet rate, d5 or IoC, so any lapse has to be small enough to have passed that test.

## Result: no lapse anywhere, and the scan could see one

12,955 adjacent pairs, 86 doublets, rate 0.0066 -- a 5.2-fold suppression.

| window | expected at the body's rate | expected at chance | observed max | null max | P |
|---|---|---|---|---|---|
| 200 | 1.3 | 6.9 | 5 | 5.5 +- 0.8 | 0.920 |
| 500 | 3.3 | 17.2 | 8 | 8.7 +- 1.2 | 0.863 |
| 1000 | 6.6 | 34.5 | 15 | 13.0 +- 1.5 | 0.150 |

**Nothing.** The densest 500-pair window holds 8 doublets where the shuffle null's maximum
averages 8.7. The 1000-pair cell at P = 0.15 is the only one below a half and is not close.

**The sensitivity is what makes this worth recording.** A 500-pair stretch enciphered
without the preventer would hold 17.2 doublets against a null maximum of 8.7 +- 1.2 --
**seven sigma**, unmissable. The shortest complete lapse the scan resolves is about 200
pairs, roughly one page of runes.

## What it closes

`why-the-body-resists.md` argues a key search has nothing to climb: 13 bits of local
information against 285 of key, and a flat landscape. The obvious hope against that is a
local lapse -- one page where the encipherer forgot the rule, giving a stretch with a
weaker mechanism and a foothold.

**There is no such stretch down to about a page.** The preventer was applied without a gap
across all 12,955 adjacent pairs. That removes a wedge rather than finding one, and it
means a search cannot be seeded from a weak region because none exists.

The complementary limit is worth stating: a lapse shorter than ~200 pairs would pass
unseen, and so would a partial weakening -- the scan tests for absence, not for a lower
phi.

    python is_there_an_unsuppressed_stretch.py
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
CORPUS = ROOT / "data" / "page0-56.txt"
CHANCE = 1.0 / 29
WINDOWS = (200, 500, 1000)
DRAWS = 2000


def flags() -> list[int]:
    """1 where two adjacent runes are equal, over the whole body stream."""
    out, previous = [], None
    for ch in CORPUS.read_text():
        if RUNE.match(ch):
            if previous is not None:
                out.append(int(ch == previous))
            previous = ch
        elif ch in "/\n" or ch in c3301.WORD_BOUNDARY:
            continue
        elif ch in "%$&":
            previous = None
    return out


def window_max(v: np.ndarray, width: int) -> tuple[int, int]:
    run = np.convolve(v, np.ones(width, dtype=int), mode="valid")
    return int(run.max()), int(run.argmax())


def main() -> None:
    v = np.array(flags(), dtype=int)
    total = int(v.sum())
    rate = total / len(v)
    print(f"{len(v):,} adjacent pairs, {total} doublets, rate {rate:.4f}.")
    print(f"Chance is {CHANCE:.4f}, so the suppression is {CHANCE / rate:.1f}-fold.\n")

    rng = random.Random(3301)
    order = list(range(len(v)))
    print(
        f"{'window':>8}{'expected here':>15}{'at chance':>11}"
        f"{'observed max':>14}{'null max':>18}{'P':>8}"
    )
    for width in WINDOWS:
        obs, at = window_max(v, width)
        null = []
        for _ in range(DRAWS):
            rng.shuffle(order)
            null.append(window_max(v[order], width)[0])
        null = np.array(null, float)
        p = float((null >= obs).mean())
        print(
            f"{width:>8}{width * rate:>15.1f}{width * CHANCE:>11.1f}{obs:>14}"
            f"{f'{null.mean():.1f} +- {null.std(ddof=1):.1f}':>18}{p:>8.3f}"
        )

    width = WINDOWS[1]
    obs, at = window_max(v, width)
    null = []
    for _ in range(DRAWS // 4):
        rng.shuffle(order)
        null.append(window_max(v[order], width)[0])
    null_mean, null_sd = float(np.mean(null)), float(np.std(null, ddof=1))
    lapse = width * CHANCE
    print(
        f"\nThe densest {width}-pair window holds {obs} doublets, starting at pair"
        f" {at:,} of {len(v):,}.\n"
    )
    print("Sensitivity, so this is not an empty null:\n")
    print(f"  a {width}-pair stretch with no preventer would hold   {lapse:.1f}")
    print(f"  the scan's null maximum at this width                {null_mean:.1f} +- {null_sd:.1f}")
    print(f"  so a complete lapse would stand out at               {(lapse - null_mean) / null_sd:+.1f} sigma")
    print(
        f"\n  The shortest complete lapse this scan resolves is about"
        f" {math.ceil(3 * math.sqrt(width * rate) / (CHANCE - rate)):d} pairs."
    )


if __name__ == "__main__":
    main()
