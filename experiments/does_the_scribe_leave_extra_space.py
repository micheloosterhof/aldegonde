# ABOUTME: Measures the physical whitespace at each separator in the page images, asking
# ABOUTME: whether the four-dot gets a wider gap than an ordinary word break.
"""A channel in the scans that has never been read: how wide the gap actually is.

Every result about the four-dot so far uses the transcription -- block lengths, mark
glyphs, line ends. The images carry something the transcription throws away: **the
physical width of the space at each separator.** A scribe setting text by hand leaves
more room at a structural break than at a word break, and that is a signal about what the
mark means which no length statistic can reach.

`what_would_it_take.py` shows the length channel is closed on this question: both
surviving readings predict an ordinary interior block at the span end, so the arm gap is
zero at any corpus size. Layout supplied one channel outside it
(`the-four-dot-is-not-layout-coupled.md`, line-end coupling) and that is spent. This is a
second.

## What is measured

Connected components on each page: runes are ink blobs 80-180 px tall inside the text
block, dots are blobs at most 16 px, clustered into marks by proximity. For each adjacent
pair of runes on a written line:

    gap        = x(next rune) - right edge of (previous rune)
    whitespace = gap - width of the dot cluster sitting in it

**Whitespace is the statistic**, not gap: a four-dot cluster is physically wider than a
one-dot, so a raw gap comparison measures the dots rather than the spacing.

Two controls are built in.

**Justification.** The body is set as justified text, so spacing stretches line by line.
Every measurement is normalised by its own line's median word-break whitespace.

**The author's own pages.** Pages 15-72 are the body. The scans do not cover the ASCII
front matter at all (`the_front_matter_dots_are_unmeasured.py`), so the within-book
control here is the thirteen-dot, which red ink confirms is a section boundary.

## The prediction

If the four-dot is an ordinary word separator that happens to carry four dots, its
whitespace matches the one-dot's. If it is a structural break, it is wider. The
thirteen-dot, known to be a section boundary, says what a structural break looks like in
this hand.

## Result: the four-dot gets an ordinary word-break space

11,249 adjacent rune pairs across the page images.

| dots in the gap | pairs | mean | se | median | vs one dot |
|---|---|---|---|---|---|
| none (within a word) | 8,758 | 0.407 | 0.002 | 0.417 | -116.44 |
| one (a word break) | 2,392 | 1.007 | 0.005 | 1.000 | — |
| **four** | 90 | **1.230** | 0.109 | **1.000** | +2.04 |
| thirteen | 7 | 0.839 | 0.054 | 0.857 | -3.11 |

**The mean says +2.04 sigma and the median says nothing.** The four-dot's median
whitespace is 1.000, exactly a word break's; a handful of wide gaps pull the mean to
1.230. The typical four-dot is spaced like an ordinary separator.

That is the answer, and it agrees with the other physical channel: the four-dot sits at a
line end 10.6% of the time against the word separator's 11.5%
(`the-four-dot-is-not-layout-coupled.md`). **Two independent measurements off the scans,
both saying the scribe treated the four-dot as an ordinary word break.**

The thirteen-dot cell has seven usable pairs and should not be read. Most thirteen-dots
sit at a line end, where there is no following rune to measure against.

## Three detection problems, all found and fixed

**Two clusters in one gap.** Summing their dot counts created a spurious "two-dot" class
of 104 pairs with whitespace 0.248 -- narrower than within a word. Those are gaps where a
rune was missed, so the gap spans a whole word. Requiring exactly one cluster removes the
class.

**Cluster width has to be subtracted, and it is not proportional to the dot count.**
Median widths are 9 px for one dot, 40 px for four and 39 px for thirteen: a four-dot is a
horizontal row and a thirteen-dot is a compact block. A raw gap comparison would have
measured the dots.

**Marks at a line end are unmeasurable** and drop out, which costs about half the
thirteen-dots and a tenth of the four-dots. That biases the sample toward mid-line marks
and is why the thirteen-dot row is too thin to use.

## What the channel could still do

Nothing was found at positions *without* a mark: if the scribe had left extra space at
unmarked sentence ends, that would locate boundaries independently of the glyphs. The
within-word cell at 0.407 and the word-break cell at 1.007 are cleanly separated, so the
measurement is sound enough to look; a wide-gap search among the 2,392 one-dot breaks is
the obvious next step and is not done here.

    python does_the_scribe_leave_extra_space.py
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from experiments.locate_marks import IMAGE_DIR  # noqa: E402

TEXT_BLOCK = (450, 2050)
RUNE_HEIGHT = (80, 180)
DOT_MAX = 16
LINK = 40
LINE_GAP = 60
PAGES = range(58)


def glyphs(page: int):
    """Runes as (y, x, w) and dot clusters as (y, x_min, x_max, count)."""
    ink = np.array(Image.open(IMAGE_DIR / f"{page}.jpg").convert("L")) < 128
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    runes, dots = [], []
    for ys, xs in ndimage.find_objects(labels):
        y, x = ys.start, xs.start
        h, w = ys.stop - y, xs.stop - x
        if not TEXT_BLOCK[0] <= x <= TEXT_BLOCK[1]:
            continue
        if RUNE_HEIGHT[0] <= h <= RUNE_HEIGHT[1]:
            runes.append((y, x, w))
        elif h <= DOT_MAX and w <= DOT_MAX:
            dots.append((y + h // 2, x, x + w))

    parent = list(range(len(dots)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(dots):
        for j in range(i + 1, len(dots)):
            b = dots[j]
            if abs(a[0] - b[0]) <= LINK and abs(a[1] - b[1]) <= LINK:
                parent[find(i)] = find(j)
    groups = defaultdict(list)
    for i in range(len(dots)):
        groups[find(i)].append(dots[i])
    marks = [
        (
            int(np.mean([d[0] for d in g])),
            min(d[1] for d in g),
            max(d[2] for d in g),
            len(g),
        )
        for g in groups.values()
    ]
    return runes, marks


def lines_of(runes):
    """Group runes into written lines by their top edge."""
    out = []
    for r in sorted(runes):
        if out and abs(r[0] - out[-1][-1][0]) < LINE_GAP:
            out[-1].append(r)
        else:
            out.append([r])
    return [sorted(line, key=lambda r: r[1]) for line in out if len(line) >= 4]


def measure(page: int):
    """(dot count, whitespace) for every adjacent rune pair on the page."""
    runes, marks = glyphs(page)
    rows = []
    for line in lines_of(runes):
        top = np.median([r[0] for r in line])
        here = [m for m in marks if abs(m[0] - top) < 150]
        cells = []
        for a, b in zip(line, line[1:]):
            left, right = a[1] + a[2], b[1]
            gap = right - left
            if gap <= 0 or gap > 400:
                continue
            inside = [m for m in here if left <= m[1] and m[2] <= right]
            if len(inside) > 1:
                # two clusters between one pair of runes means a rune was missed;
                # the gap then spans a whole word and is not a separator measurement
                continue
            count = inside[0][3] if inside else 0
            width = (inside[0][2] - inside[0][1]) if inside else 0
            cells.append((count, gap - width))
        if not cells:
            continue
        base = [w for c, w in cells if c == 1]
        if len(base) < 3:
            continue
        scale = float(np.median(base))
        if scale <= 0:
            continue
        rows.extend((c, w / scale) for c, w in cells)
    return rows


def main() -> None:
    rows = []
    for page in PAGES:
        try:
            rows.extend(measure(page))
        except FileNotFoundError:
            continue
    print(f"{len(rows):,} adjacent rune pairs measured across the page images.")
    print("Whitespace is the gap minus the dot cluster's own width, divided by that")
    print("line's median one-dot whitespace, so justification cancels.\n")

    by_count = defaultdict(list)
    for count, w in rows:
        by_count[count].append(w)
    base = np.array(by_count.get(1, []), float)
    print(
        f"{'dots in the gap':>16}{'pairs':>9}{'mean':>9}{'se':>8}"
        f"{'median':>9}{'vs one dot':>12}"
    )
    for count in sorted(by_count):
        v = np.array(by_count[count], float)
        if len(v) < 6:
            continue
        se = v.std(ddof=1) / math.sqrt(len(v))
        z = (
            (v.mean() - base.mean())
            / math.hypot(se, base.std(ddof=1) / math.sqrt(len(base)))
            if count != 1
            else 0.0
        )
        label = "none (within a word)" if count == 0 else str(count)
        print(
            f"{label:>16}{len(v):>9}{v.mean():>9.3f}{se:>8.3f}"
            f"{np.median(v):>9.3f}{z:>+12.2f}"
        )


if __name__ == "__main__":
    main()
