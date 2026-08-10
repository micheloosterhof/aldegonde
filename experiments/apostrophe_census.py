# ABOUTME: Sweeps all 58 Liber Primus page images for the raised tick glyph,
# ABOUTME: separating apostrophes from double quotes, dot marks and artwork.
"""Locate every apostrophe and quotation mark in the LP page scans.

The working transcriptions record runes, the word separator and the sentence
mark, but drop a whole punctuation class: a raised tick that appears alone
(apostrophe) and in adjacent pairs (double quote).

The glyph classes are cleanly separable by connected-component geometry at the
native 2400x3600 resolution:

    runes        h ~ 114
    tick         h = 40,  w = 12
    dot marks    h = 9-10, w = 9-10
    artwork      varies; lies outside the text block

Two ticks on the same baseline about 20 px apart are one double-quote glyph; a
tick with no neighbour is an apostrophe.

Usage:  python3 experiments/apostrophe_census.py [image_dir]
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

IMAGE_DIR = Path("/Users/mich/src/cicada-2014/stage11/ky2khlqdf7qdznac.onion")

# The pages are digital renderings at a fixed glyph size, so the tick has an
# exact footprint. Loosening these past 42 x 13 starts admitting artwork
# strokes from the marginal illustrations.
TICK_HEIGHT = (38, 42)
TICK_WIDTH = (10, 13)
PAIR_SPACING = 40  # px between the two ticks of a double quote
TEXT_BLOCK_X = (500, 2000)  # margins hold artwork, not text
INK = 128


def components(path: Path) -> list[tuple[int, int, int, int]]:
    """Bounding boxes (y, x, h, w) of every ink blob on the page."""
    ink = np.array(Image.open(path).convert("L")) < INK
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    boxes = []
    for ys, xs in ndimage.find_objects(labels):
        boxes.append((ys.start, xs.start, ys.stop - ys.start, xs.stop - xs.start))
    return boxes


def ticks(path: Path) -> list[tuple[int, int]]:
    """Tick glyphs (y, x) inside the text block, in reading order."""
    found = [
        (y, x)
        for y, x, h, w in components(path)
        if TICK_HEIGHT[0] <= h <= TICK_HEIGHT[1]
        and TICK_WIDTH[0] <= w <= TICK_WIDTH[1]
        and TEXT_BLOCK_X[0] <= x <= TEXT_BLOCK_X[1]
    ]
    return sorted(found)


def classify(marks: list[tuple[int, int]]) -> tuple[list, list]:
    """Split ticks into apostrophes and double quotes by adjacency."""
    quotes, apostrophes = [], []
    used = set()
    for i, (y, x) in enumerate(marks):
        if i in used:
            continue
        partner = next(
            (
                j
                for j in range(i + 1, len(marks))
                if j not in used
                and abs(marks[j][0] - y) < 10
                and 0 < marks[j][1] - x <= PAIR_SPACING
            ),
            None,
        )
        if partner is None:
            apostrophes.append((y, x))
        else:
            used.add(partner)
            quotes.append((y, x))
    return apostrophes, quotes


def main() -> None:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else IMAGE_DIR
    pages = sorted(
        directory.glob("*.jpg"),
        key=lambda p: int(p.stem),
    )
    if not pages:
        sys.exit(f"no page images under {directory}")

    totals: defaultdict[str, int] = defaultdict(int)
    for path in pages:
        page = int(path.stem)
        apostrophes, quotes = classify(ticks(path))
        if not (apostrophes or quotes):
            continue
        totals["apostrophe"] += len(apostrophes)
        totals["quote"] += len(quotes)
        parts = []
        if apostrophes:
            parts.append(f"{len(apostrophes)} apostrophe at {apostrophes}")
        if quotes:
            parts.append(f"{len(quotes)} quote at {quotes}")
        print(f"{page:3}.jpg  " + "; ".join(parts))

    print(
        f"\ntotal: {totals['apostrophe']} apostrophes, "
        f"{totals['quote']} quotation marks"
    )


if __name__ == "__main__":
    main()
