# ABOUTME: Precise reader for the LP page scans: per-line text bounds to exclude
# ABOUTME: artwork, and column splitting for touching runes, with mark dot counts.
"""A reader accurate enough to correct the transcription's marks.

The mark inventory is wrong (`mark-glyph-inventory.md`): at least four dot
glyphs are recorded as two characters, and line-initial ones are dropped. Fixing
that needs a reader whose disagreements with the transcription are the
transcription's fault, not its own. The first reader had two faults:

  * **Artwork.** Glyphs were selected by y-band and a global x window, so a
    marginal illustration at the same height as a line was read as a dot.
    Fixed by bounding each line to its own runes: a mark counts only if it lies
    within MARGIN of that line's leftmost and rightmost rune. Real leading and
    trailing marks sit ~40-60px out; artwork sits further.

  * **Merged runes.** Connected components join touching runes into one blob,
    losing a rune and shifting every count on the line. Fixed by measuring the
    line's own median rune width and splitting any wider blob at its
    lowest-ink columns.

Marks carry their dot count, so the four glyph classes stay distinct instead of
collapsing to `-` and `.`.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy import ndimage

from experiments.locate_marks import IMAGE_DIR

INK = 128
RUNE_HEIGHT = (80, 180)
TICK_HEIGHT, TICK_WIDTH = (36, 44), (8, 16)
DOT_MAX = 16
DOT_LINK = 45
LINE_GAP = 60
MARGIN = 120          # how far past the end runes a mark may sit
WIDE = 1.5            # only blobs this much wider than the median can split
VALLEY = 0.22         # a cut needs the column ink to fall to this fraction of mean


@dataclass
class Glyph:
    kind: str          # "R" rune, "M" dot cluster, "t" tick
    y: int
    x: int
    dots: int = 0


def _blobs(page: int) -> tuple[list, list]:
    ink = np.array(Image.open(IMAGE_DIR / f"{page}.jpg").convert("L")) < INK
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    tall, dots = [], []
    for ys, xs in ndimage.find_objects(labels):
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if RUNE_HEIGHT[0] <= h <= RUNE_HEIGHT[1]:
            tall.append((ys.start, xs.start, h, w))
        elif TICK_HEIGHT[0] <= h <= TICK_HEIGHT[1] and TICK_WIDTH[0] <= w <= TICK_WIDTH[1]:
            tall.append((ys.start, xs.start, h, w, "t"))
        elif h <= DOT_MAX and w <= DOT_MAX:
            dots.append((ys.start + h // 2, xs.start + w // 2))
    return tall, dots, ink


def _split_wide(box: tuple, ink: np.ndarray, unit: float) -> list[int]:
    """X positions of the runes inside a blob, splitting only at a real valley.

    Splitting on width alone over-splits: runes differ genuinely in width, so a
    wide glyph like D or X gets cut in half. Touching runes meet at a thin
    join, which leaves a deep minimum in the column ink profile; a single wide
    rune does not. So a cut is made only where the profile actually collapses,
    and only in blobs wide enough to hold two runes.
    """
    y, x, h, w = box[:4]
    if w < unit * WIDE:
        return [x]
    profile = ink[y:y + h, x:x + w].sum(axis=0).astype(float)
    floor = VALLEY * profile[profile > 0].mean() if (profile > 0).any() else 0
    edge = int(unit * 0.45)
    cuts = [c for c in range(edge, w - edge) if profile[c] <= floor]
    if not cuts:
        return [x]
    # keep one cut per valley
    keep, last = [], -10**9
    for c in cuts:
        if c - last > edge:
            keep.append(c)
            last = c
    starts, prev = [], 0
    for c in [*keep, w]:
        starts.append(x + prev)
        prev = c
    return starts


def read_page(page: int) -> list[list[Glyph]]:
    """Glyphs of each text line, in reading order, with artwork excluded."""
    tall, dots, ink = _blobs(page)

    runes = sorted([t for t in tall if len(t) == 4])
    bands: list[list] = []
    for r in runes:
        if bands and abs(r[0] - bands[-1][0][0]) < LINE_GAP:
            bands[-1].append(r)
        else:
            bands.append([r])
    bands = [b for b in bands if len(b) >= 2]

    # dot clusters, built once for the page
    parent = list(range(len(dots)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(dots):
        for j in range(i + 1, len(dots)):
            b = dots[j]
            if abs(a[0] - b[0]) <= DOT_LINK and abs(a[1] - b[1]) <= DOT_LINK:
                parent[find(i)] = find(j)
    groups = defaultdict(list)
    for i, p in enumerate(dots):
        groups[find(i)].append(p)
    clusters = [(min(p[0] for p in g), min(p[1] for p in g), len(g))
                for g in groups.values()]
    ticks = [t for t in tall if len(t) == 5]

    out = []
    for band in bands:
        unit = float(np.median([b[3] for b in band]))
        glyphs: list[Glyph] = []
        for b in band:
            for gx in _split_wide(b, ink, unit):
                glyphs.append(Glyph("R", b[0], gx))
        lo_y = min(b[0] for b in band) - 30
        hi_y = max(b[0] for b in band) + 140
        lo_x = min(g.x for g in glyphs) - MARGIN
        hi_x = max(g.x for g in glyphs) + MARGIN
        for cy, cx, n in clusters:
            if lo_y <= cy <= hi_y and lo_x <= cx <= hi_x:
                glyphs.append(Glyph("M", cy, cx, n))
        for ty, tx, *_ in ticks:
            if lo_y <= ty <= hi_y and lo_x <= tx <= hi_x:
                glyphs.append(Glyph("t", ty, tx))
        out.append(sorted(glyphs, key=lambda g: g.x))
    return out


def sequence(line: list[Glyph]) -> list[tuple[str, int]]:
    """Reading-order (kind, dots), ticks dropped."""
    return [(g.kind, g.dots) for g in line if g.kind != "t"]
