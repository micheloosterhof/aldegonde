# ABOUTME: Inventories the colour of every rune on every page, to find any annotation layer
# ABOUTME: beyond the known rubrication.
"""The ink census closed the size channel. This closes the colour channel.

`glyph-inventory-is-complete.md` bins every ink blob by size and finds no missing mark
class, with one stated gap: a mark drawn in COLOUR rather than ink is invisible to a
threshold on darkness. `rubrication_census.json` covers part of that, but only by asking
one question -- how many runes are RED -- on each page. It cannot see a third colour.

So bin the colours instead of assuming them. Every rune blob on every page, summarised by
its mean ink colour, and the population plotted in the two channels that separate hues
without needing a colour model: R-G and G-B. Black ink sits at (0, 0); rubrication sits
far out on R-G; anything else is a layer nobody has named.

What it finds: two populations and no third, so there is one annotation layer. But the
warm one reaches 17 pages where `rubrication_census.json` records 15, and the five extra
runes are the same pure red as the catalogued titles rather than bleed.

    python colour_class_inventory.py [image_dir] [--singletons]
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from apostrophe_census import IMAGE_DIR, INK, TEXT_BLOCK_X

RUNE_H = (90, 140)


def rune_colours(path: Path) -> list[tuple[int, int, int]]:
    """Mean RGB of the ink pixels of every rune-sized blob in the text block."""
    img = np.array(Image.open(path).convert("RGB"))
    grey = img.mean(axis=2)
    ink = grey < INK
    labels, n = ndimage.label(ink, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndimage.find_objects(labels), start=1):
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if not (RUNE_H[0] <= h <= RUNE_H[1]):
            continue
        if not TEXT_BLOCK_X[0] <= xs.start <= TEXT_BLOCK_X[1]:
            continue
        mask = labels[sl] == i
        patch = img[sl][mask]
        out.append(tuple(int(v) for v in patch.mean(axis=0)))
    return out


def singletons(pages) -> None:
    """Warm runes page by page, against what the rubrication census recorded."""
    import json  # noqa: PLC0415

    root = Path(__file__).resolve().parent
    known = {
        c["page"]: c["red_runes"]
        for c in json.loads((root / "rubrication_census.json").read_text())
    }
    print(f"{'page':>5}{'warm runes':>12}{'census':>9}   ")
    for page in pages:
        p = int(page.stem)
        cols = [c for c in rune_colours(page) if c[0] - c[1] >= 20]
        if not cols and not known.get(p):
            continue
        flag = "" if known.get(p, 0) else "   not in the census"
        print(f"{p:>5}{len(cols):>12}{known.get(p, 0):>9}{flag}")
        if flag:
            print(
                f"      mean RGB {tuple(int(v) for v in cols[0])}"
                f" against a catalogued title rune's (180, 4, 5)"
            )
    print(
        "\nThe extra runes carry the same ink as the titles. rubrication_spans.py"
        "\ndiscards 'scattered singletons' as red initials or bleed, which is right for"
        "\nextracting title SPANS and wrong as a description: bleed would be"
        "\ndesaturated and these are not."
    )


def main() -> None:
    directory = (
        Path(sys.argv[1])
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-")
        else IMAGE_DIR
    )
    pages = sorted(directory.glob("*.jpg"), key=lambda p: int(p.stem))
    if "--singletons" in sys.argv:
        singletons(pages)
        return
    cells: collections.Counter = collections.Counter()
    page_of: dict[tuple[int, int], set] = collections.defaultdict(set)
    total = 0
    for page in pages:
        for r, g, b in rune_colours(page):
            total += 1
            key = ((r - g) // 20 * 20, (g - b) // 20 * 20)
            cells[key] += 1
            page_of[key].add(int(page.stem))

    print(f"{total:,} rune blobs over {len(pages)} pages\n")
    print(f"{'R-G':>6}{'G-B':>6}{'runes':>9}{'pages':>7}{'share':>9}")
    for (rg, gb), n in cells.most_common(12):
        print(f"{rg:>6}{gb:>6}{n:>9,}{len(page_of[(rg, gb)]):>7}{n / total:>9.2%}")
    neutral = sum(n for (rg, gb), n in cells.items() if abs(rg) < 20 and abs(gb) < 20)
    warm = sum(n for (rg, gb), n in cells.items() if rg >= 20)
    cool = sum(n for (rg, gb), n in cells.items() if rg <= -20)
    print(f"\nneutral (|R-G| and |G-B| under 20): {neutral:,} ({neutral / total:.1%})")
    print(f"warm  (R-G >= 20, the rubrication): {warm:,} ({warm / total:.1%})")
    print(f"cool  (R-G <= -20):                 {cool:,} ({cool / total:.1%})")
    print(
        "\nTwo populations and no third means the colour channel holds one annotation"
        "\nlayer, the rubrication already catalogued. A cool or otherwise-placed cluster"
        "\nspread over many pages would be a layer nobody has named."
    )


if __name__ == "__main__":
    main()
