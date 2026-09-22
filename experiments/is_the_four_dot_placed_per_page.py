# ABOUTME: Tests whether the four-dot's spacing is set by the page rather than the text,
# ABOUTME: using per-page dispersion with the other two glyphs as internal controls.
"""If the four-dot is not tied to sentence ends, what sets its spacing?

`the_thinning_model_is_dead.py` excludes the reading that every four-dot sits at a real
sentence end, at seven sigma. What survives is a small mixture at the layout rate or none
at all -- in either case, most four-dots are not sentence ends, and something else decides
where they go.

The gap law says the placement is not memoryless: nine gaps of three blocks or less where
a constant-rate process predicts 18.4 (`are_the_four_dot_gaps_memoryless.py`). Something
keeps them apart.

A production explanation would do that. If the scribe put two or three marks on each page
by habit -- filling a page and marking it off -- the count per page would be **under-
dispersed**, tighter than a constant per-rune rate allows, and short gaps would be rare
because a mark near the end of a page is followed by a fresh page.

## The test and its controls

Count each glyph per body page and compare against a constant per-rune rate, which handles
pages differing in length. The other two glyphs say what the test can see:

- **⑬** is a section mark confirmed by red ink, and sections cluster -- a title is opened
  and closed by a pair a few words apart. It should read **over**-dispersed.
- **①** is the word separator, and the number of words on a page is nearly fixed by its
  rune count. It should read heavily **under**-dispersed.

If those two come out as expected, the four-dot's cell means something.

This is internal to the body: same pages, same hand, same cipher.

## Result: no page structure at all

| glyph | total | per page | chi2 | df | P | reading |
|---|---|---|---|---|---|---|
| **④** | 139 | 2.53 | 55.8 | 54 | **0.406** | Poisson at a constant rate |
| ⑬ | 26 | 0.47 | 82.8 | 54 | **0.007** | over-dispersed, clustered |
| ① | 2,722 | 49.49 | 13.9 | 54 | **1.000** | under-dispersed, near-determined |

**Three glyphs, three regimes, and the two controls land where they must.** The section
mark clusters because a rubricated title is opened and closed by a pair a few words apart
and sections fall on particular pages. The word separator is nearly fixed by a page's rune
count, since words have almost constant mean length. So the test discriminates, and the
four-dot's cell is readable.

**It sits exactly on a constant per-rune rate.** The page is invisible to it.

## What that closes

A production explanation for the four-dot's spacing. Its gaps are not memoryless -- nine
of three blocks or less where a constant-rate process predicts 18.4 -- and the natural way
to get that without any reference to the text is a scribe marking off each page by habit.
That would show as under-dispersion, and there is none: P = 0.406 against a hypothesis
that ignores the page entirely.

So whatever keeps four-dots apart acts on the **rune stream**, not on the page. That is the
same conclusion the doublet preventer reached from a different direction
(`the-preventer-is-in-the-stream.md`): the mechanisms in this book do not see the layout.

## What it does not explain

The short-gap deficit itself. Something spaces the four-dots more evenly than chance and
it is not the page; this file says only where not to look.

    python is_the_four_dot_placed_per_page.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, MASTER, chunk_blocks  # noqa: E402

GLYPHS = ("④", "⑬", "①")


def per_page():
    """{glyph: counts per page} plus each page's rune total."""
    text = MASTER.read_text().split("%")
    counts = {g: [] for g in GLYPHS}
    runes = []
    for ci in BODY:
        if ci >= len(text):
            continue
        blocks = chunk_blocks(text[ci])
        if not blocks:
            continue
        runes.append(sum(n for n, _, _ in blocks))
        for g in GLYPHS:
            counts[g].append(sum(1 for _, glyph, _ in blocks if glyph == g))
    return counts, np.array(runes, float)


def main() -> None:
    counts, runes = per_page()
    print(f"{len(runes)} body pages, {runes.sum():,.0f} runes.\n")
    print(
        f"{'glyph':>6}{'total':>8}{'per page':>10}{'Fano':>8}"
        f"{'chi2':>9}{'df':>5}{'P':>9}  reading"
    )
    for g in GLYPHS:
        c = np.array(counts[g], float)
        expected = c.sum() / runes.sum() * runes
        chi = float(((c - expected) ** 2 / np.maximum(expected, 0.5)).sum())
        df = len(c) - 1
        p = float(stats.chi2.sf(chi, df))
        reading = (
            "over-dispersed, clustered"
            if p < 0.05
            else "under-dispersed, near-determined"
            if p > 0.95
            else "Poisson at a constant rate"
        )
        print(
            f"{g:>6}{int(c.sum()):>8}{c.mean():>10.2f}{c.var(ddof=1) / c.mean():>8.2f}"
            f"{chi:>9.1f}{df:>5}{p:>9.3f}  {reading}"
        )

    four = Counter(counts["④"])
    print(f"\nfour-dots per page: {dict(sorted(four.items()))}")
    print(
        "\n  The two controls behave as they must -- the section mark clusters, the word"
        "\n  separator is fixed by the page's rune count -- so the four-dot's cell is"
        "\n  readable. It sits exactly on a constant per-rune rate."
    )


if __name__ == "__main__":
    main()
