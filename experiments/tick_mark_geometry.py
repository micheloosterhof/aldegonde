# ABOUTME: Measures whether the dot-cluster marks beside quote ticks differ geometrically
# ABOUTME: from free-standing ones, settling whether the tick+mark pairing is one glyph.
"""Is the mark beside a quote tick part of the quote, or a separate clause mark?

`quote-span-boundaries.md` measures that 8 of the 14 quote ticks sit immediately beside
a 4-dot mark, P = 2.2e-6, and leaves two readings open. Either the clustering is
linguistic -- a closing quote, a clause mark, an opening quote, as printed English does
-- or the LP writes a quotation mark as a tick PLUS a dot cluster and the transcriber
recorded one glyph as two.

The transcription cannot separate those, because it has already collapsed the glyphs it
saw into characters. The page images can. If the tick-adjacent clusters differ from
free-standing ones in how far they sit from the tick, in their vertical placement, or in
their internal dot spacing, they belong to the quote glyph. If they are
indistinguishable, the clustering is linguistic.

Detection reuses `apostrophe_census.py`: ticks are ink blobs 38-42 px tall and 10-13
wide inside the text block, where a rune is ~114 px tall and a mark dot is ~9-10.

    python tick_mark_geometry.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from apostrophe_census import IMAGE_DIR, TEXT_BLOCK_X, components, ticks  # noqa: E402

DOT = (6, 14)  # a mark dot's height and width both fall in this range
CLUSTER_GAP = 30  # px: dots closer than this belong to one mark
NEAR_TICK = 120  # px: how far from a tick a mark counts as adjacent


def dots(path: Path) -> list[tuple[int, int]]:
    """Centres of blobs the size of a mark dot, inside the text block."""
    out = []
    for y, x, h, w in components(path):
        if (
            DOT[0] <= h <= DOT[1]
            and DOT[0] <= w <= DOT[1]
            and TEXT_BLOCK_X[0] <= x <= TEXT_BLOCK_X[1]
        ):
            out.append((y + h // 2, x + w // 2))
    return sorted(out)


def cluster(points: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Group dots into marks by simple single-link proximity."""
    groups: list[list[tuple[int, int]]] = []
    for pt in points:
        for g in groups:
            if any(
                abs(pt[0] - q[0]) <= CLUSTER_GAP and abs(pt[1] - q[1]) <= CLUSTER_GAP
                for q in g
            ):
                g.append(pt)
                break
        else:
            groups.append([pt])
    merged = True
    while merged:
        merged = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if any(
                    abs(a[0] - b[0]) <= CLUSTER_GAP and abs(a[1] - b[1]) <= CLUSTER_GAP
                    for a in groups[i]
                    for b in groups[j]
                ):
                    groups[i] += groups.pop(j)
                    merged = True
                    break
            if merged:
                break
    return groups


def main() -> None:
    pages = sorted(IMAGE_DIR.glob("*.jpg"), key=lambda p: int(p.stem))
    near, far = [], []
    print(f"{'page':>5}{'ticks':>7}{'marks':>7}  tick-adjacent cluster sizes")
    for path in pages:
        t = ticks(path)
        if not t:
            continue
        groups = cluster(dots(path))
        sizes = []
        for g in groups:
            cy = statistics.mean(p[0] for p in g)
            cx = statistics.mean(p[1] for p in g)
            d = min((abs(cy - ty) + abs(cx - tx)) for ty, tx in t)
            rec = {
                "n": len(g),
                "cy": cy,
                "cx": cx,
                "dist": d,
                "spread": max(p[1] for p in g) - min(p[1] for p in g),
            }
            if d <= NEAR_TICK:
                near.append(rec)
                sizes.append(len(g))
            else:
                far.append(rec)
        print(f"{int(path.stem):>5}{len(t):>7}{len(groups):>7}  {sorted(sizes)}")

    print(f"\ntick-adjacent clusters {len(near)}, free-standing {len(far)}\n")
    print(f"{'group':<20}{'n':>5}{'mean dots':>11}{'mean spread px':>16}")
    for label, rows in (("adjacent to a tick", near), ("free-standing", far)):
        if not rows:
            continue
        print(
            f"{label:<20}{len(rows):>5}"
            f"{statistics.mean(r['n'] for r in rows):>11.2f}"
            f"{statistics.mean(r['spread'] for r in rows):>16.1f}"
        )
    if near:
        print(
            f"\ndistance from tick to its cluster: "
            f"{sorted(round(r['dist']) for r in near)}"
        )


if __name__ == "__main__":
    main()
