# ABOUTME: Extracts rubricated (red) rune-spans from the page scans -- the same
# ABOUTME: marking that flagged DIVINITY WITHIN, hunted across all 58 pages for cribs.
"""Where else is the text rubricated? Rubricated rune-spans are crib candidates.

The DIVINITY WITHIN crib (`crib_divinity_within.py`) works because page 0 line 0
is rubricated: 13 red runes marking a known-guessable opening. If other pages
carry rubricated rune-SPANS (not just decorative red initials or illustration),
each is a candidate crib of the same kind -- a short, likely-titular phrase whose
plaintext may be guessable and whose runeglish length is fixed by the scan.

This sweeps every page, finds rune-sized connected components that are >50% red
ink inside the text block, groups them into lines by vertical position, and
reports each rubricated line by its red-rune count. A single line of several red
runes is a title-like span (the DIVINITY WITHIN shape); scattered singletons are
red initials or bleed.

NOTE: this is the extraction step only. Mapping each span to its enciphered
section and matching its length to Cicada phrases is the follow-on; a span in the
already-plaintext Parable (section 11) or the solved pages is not a crib.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from locate_marks import IMAGE_DIR  # noqa: E402, I001
from mark_type_split import RUNE_HEIGHT, TEXT_BLOCK  # noqa: E402

LINE_GAP = 90  # red runes within this many rows are one line
RED_MARGIN = 40  # r - (g+b)/2 above this is "red ink"


def red_rune_rows(page: int) -> list[int]:
    """Row (y) of every rune-sized, majority-red glyph inside the text block."""
    im = np.array(Image.open(IMAGE_DIR / f"{page}.jpg").convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    ink = (r + g + b) // 3 < 200
    isred = (r - (g + b) // 2) > RED_MARGIN
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    rows = []
    for sl in ndimage.find_objects(labels):
        y, x = sl[0].start, sl[1].start
        h = sl[0].stop - y
        if not (TEXT_BLOCK[0] <= x <= TEXT_BLOCK[1]):
            continue
        if not (RUNE_HEIGHT[0] <= h <= RUNE_HEIGHT[1]):
            continue
        box_ink = ink[sl]
        if box_ink.sum() and (isred[sl] & box_ink).sum() / box_ink.sum() > 0.5:
            rows.append(y)
    return rows


def lines_from_rows(rows: list[int]) -> list[tuple[int, int]]:
    """Group red-rune rows into lines; return (row, count) per line."""
    out = []
    for y in sorted(rows):
        if out and y - out[-1][0] < LINE_GAP:
            out[-1] = (out[-1][0], out[-1][1] + 1)
        else:
            out.append((y, 1))
    return out


def main() -> None:
    print(
        "rubricated rune-spans (>=3 red runes on a line = title-like crib candidate):\n"
    )
    print(f"{'page':>4}{'line-row':>10}{'red runes':>11}")
    spans = 0
    by_page: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for page in range(58):
        lines = [(y, n) for y, n in lines_from_rows(red_rune_rows(page)) if n >= 3]
        for y, n in lines:
            by_page[page].append((y, n))
            print(f"{page:>4}{y:>10}{n:>11}")
            spans += 1
    print(f"\n{spans} rubricated rune-spans across {len(by_page)} pages.")
    print(
        "page 0's ~13-rune span is DIVINITY WITHIN (the known crib); the rest are new."
    )
    print("Next: map each to its enciphered section and match its length to a phrase.")


if __name__ == "__main__":
    main()
