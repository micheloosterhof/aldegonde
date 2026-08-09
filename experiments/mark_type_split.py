# ABOUTME: Splits the transcription's '.' marks into the two glyphs the scans
# ABOUTME: show (4-dot and 13-dot) and re-runs the sentence-final test on each.
"""The '.' marks are two different symbols, collapsed.

`dot_cluster_census.py` finds the page scans carry 145 four-dot clusters and 31
thirteen-dot clusters, and per page the transcription's `.` count matches their
SUM, not the four-dot count alone. So the transcription records two visually
distinct glyphs with one character.

That matters because the mark semantics are the corpus's one unexplained
observation. `word-length-keystream-and-boundaries.md` shows the '.' marks lack
the English sentence-final signature — solved pages put long content words
before a mark (z = +7.06), the unsolved marks do not (z = -1.21) — and proposes
the marks may be a MIXTURE of genuine sentence ends and something else. It
looked for that mixture by line position. The scans say the mixture is by glyph.

If one glyph carries the English signature and the other does not, the puzzle
resolves: the corpus has real sentence marks diluted by a second symbol that
was never a sentence mark.

Method: align each page's glyph sequence to its transcription line
(`locate_marks`), which fixes which transcribed `.` corresponds to which
cluster on the page, then measure the word before each mark by glyph type.
Only lines whose sequences agree exactly are used, so an unalignable line costs
coverage rather than correctness.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter, defaultdict

import numpy as np
from PIL import Image
from scipy import ndimage, stats

from experiments.locate_marks import (
    CORPUS,
    IMAGE_DIR,
    LINE_GAP,
    RUNE_HEIGHT,
    TEXT_BLOCK,
    TICK_HEIGHT,
    TICK_WIDTH,
)

RUNE = re.compile(r"[ᚠ-᛿]")
PAGES = range(58)
DOT_MAX = 16
LINK = 45
BIG = 8            # clusters with at least this many dots are the second glyph


def page_glyphs(page: int):
    """Runes, ticks and dot CLUSTERS (carrying their dot count) on one page."""
    ink = np.array(Image.open(IMAGE_DIR / f"{page}.jpg").convert("L")) < 128
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    runes, ticks, dots = [], [], []
    for ys, xs in ndimage.find_objects(labels):
        y, x = ys.start, xs.start
        h, w = ys.stop - y, xs.stop - x
        if not TEXT_BLOCK[0] <= x <= TEXT_BLOCK[1]:
            continue
        if RUNE_HEIGHT[0] <= h <= RUNE_HEIGHT[1]:
            runes.append(("R", y, x, 0))
        elif TICK_HEIGHT[0] <= h <= TICK_HEIGHT[1] and TICK_WIDTH[0] <= w <= TICK_WIDTH[1]:
            ticks.append(("t", y, x, 0))
        elif h <= DOT_MAX and w <= DOT_MAX:
            dots.append((y + h // 2, x + w // 2))

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
    for i, p in enumerate(dots):
        groups[find(i)].append(p)
    marks = [("m", min(p[0] for p in g), min(p[1] for p in g), len(g))
             for g in groups.values()]
    return runes + ticks + marks


def line_bands(gs, want: int):
    found = []
    for g in sorted(x for x in gs if x[0] == "R"):
        if found and abs(g[1] - found[-1][0]) < LINE_GAP:
            found[-1][1].append(g)
        else:
            found.append((g[1], [g]))
    found = [b for b in found if len(b[1]) >= 2]
    while len(found) > want:
        found.pop(0 if len(found[0][1]) < len(found[-1][1]) else -1)
    out = []
    for _, members in found:
        lo = min(m[1] for m in members) - 30
        hi = max(m[1] for m in members) + 150
        out.append(sorted([g for g in gs if lo <= g[1] <= hi], key=lambda g: g[2]))
    return out


def line_tokens(line):
    """Reading-order tokens. Marks are just 'M' carrying their dot count, so
    alignment does not assume the transcription's mark TYPE is right — which is
    the thing under test."""
    out = []
    for kind, _, _, size in line:
        if kind == "R":
            out.append(("R", 0))
        elif kind != "t":
            out.append(("M", size))
    return out


def main() -> None:
    blocks = CORPUS.read_text().split("%")
    inventory: list[tuple[int, int]] = []      # (dot count, length of preceding word)
    skipped = 0

    for page in PAGES:
        lines = [line for line in blocks[page].split("\n") if RUNE.search(line)]
        gs = page_glyphs(page)
        bands = line_bands(gs, len(lines))
        if len(bands) != len(lines):
            skipped += len(lines)
            continue
        for band, text in zip(bands, lines):
            img = line_tokens(band)
            txt = [("R", c) if RUNE.match(c) else ("M", c)
                   for c in text if RUNE.match(c) or c in "-."]
            if [t[0] for t in img] != [t[0] for t in txt]:
                skipped += 1
                continue
            run = 0
            for (kind, char), (_, size) in zip(txt, img):
                if kind == "R":
                    run += 1
                    continue
                inventory.append((size, run, char))
                run = 0

    print(f"aligned marks: {len(inventory)}  ({skipped} lines skipped)\n")
    print("what the page shows against what the transcription recorded\n")
    print(f"{'dots on page':>14}{'as -':>8}{'as .':>8}{'total':>8}")
    cross: Counter[tuple[int, str]] = Counter((s, c) for s, _, c in inventory)
    for n in sorted({s for s, _, _ in inventory}):
        dash, dot = cross[(n, "-")], cross[(n, ".")]
        print(f"{n:>14}{dash:>8}{dot:>8}{dash + dot:>8}")

    # Only marks the transcription calls '.' enter the sentence-final statistic,
    # so split those by the glyph actually on the page.
    dots_only = [(s, w) for s, w, c in inventory if c == "."]
    small = [w for s, w in dots_only if s < BIG and w]
    large = [w for s, w in dots_only if s >= BIG and w]
    allw = [w for _, w in dots_only if w]
    print("\nword length before the mark, by glyph")
    print(f"{'glyph':>18}{'n':>6}{'mean':>8}{'1-2 runes':>12}")
    for name, sample in ((f"small (<{BIG} dots)", small), (f"large (>={BIG} dots)", large),
                         ("pooled", allw)):
        if not sample:
            continue
        short = sum(1 for v in sample if v <= 2) / len(sample)
        print(f"{name:>18}{len(sample):>6}{statistics.mean(sample):>8.2f}{short:>12.1%}")

    if small and large:
        t = stats.ttest_ind(small, large, equal_var=False)
        print(f"\n   small vs large: t = {t.statistic:+.2f}, p = {t.pvalue:.3f}")
    print("\n   solved pages put 5.56 runes before a mark against a 4.01 baseline")
    print("   (z = +7.06); the unsolved pooled figure is 4.19 against 4.42.")
    print("   A glyph carrying the English signature would show a HIGH mean here.")


if __name__ == "__main__":
    main()
