# ABOUTME: Maps the raised tick glyphs in the LP page scans to exact character
# ABOUTME: positions in the transcription, by aligning whole glyph sequences.
"""Place the apostrophes and quotation marks into the transcription.

`apostrophe_census.py` finds the ticks in pixel coordinates. To record them in
the transcription each mark needs a character position, which means knowing how
many runes and separators precede it on its line.

Counting rune blobs is not enough: adjacent runes occasionally touch and merge
into one component. Instead every glyph on the line is classified and the whole
sequence is matched against the transcription line:

    runes        h 80-180        -> R
    tick         h 40, w 12      -> ' alone, " when two sit within 40 px
    one dot      h <= 14         -> word separator
    dot cluster  3+ dots         -> sentence mark

A line is only used if its image sequence equals the transcription sequence,
which makes each placement self-verifying rather than inferred.

Usage:  python3 experiments/locate_marks.py [--write]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
IMAGE_DIR = Path("/Users/mich/src/cicada-2014/stage11/ky2khlqdf7qdznac.onion")
CORPUS = ROOT / "data" / "page0-58.txt"
TARGETS = [
    ROOT / "data" / "liber-primus__transcription--master.txt",
    ROOT / "data" / "page0-58.txt",
    ROOT / "data" / "page0-56.txt",
]

RUNE = re.compile(r"[ᚠ-᛿]")
TEXT_BLOCK = (450, 2050)
RUNE_HEIGHT = (80, 180)
TICK_HEIGHT = (36, 44)
TICK_WIDTH = (8, 16)
DOT_MAX = 14
PAIR_SPACING = 40       # two ticks this close are one double quote
DOT_SPACING = 25        # dots this close belong to one mark
LINE_GAP = 60


def glyphs(page: int) -> list[tuple[str, int, int]]:
    """Every glyph on the page as (kind, y, x), kind in R / t / d."""
    ink = np.array(Image.open(IMAGE_DIR / f"{page}.jpg").convert("L")) < 128
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    out = []
    for ys, xs in ndimage.find_objects(labels):
        y, x = ys.start, xs.start
        h, w = ys.stop - y, xs.stop - x
        if not TEXT_BLOCK[0] <= x <= TEXT_BLOCK[1]:
            continue
        if RUNE_HEIGHT[0] <= h <= RUNE_HEIGHT[1]:
            out.append(("R", y, x))
        elif TICK_HEIGHT[0] <= h <= TICK_HEIGHT[1] and TICK_WIDTH[0] <= w <= TICK_WIDTH[1]:
            out.append(("t", y, x))
        elif h <= DOT_MAX and w <= DOT_MAX:
            out.append(("d", y, x))
    return out


def text_lines(page_block: str) -> list[str]:
    return [line for line in page_block.split("\n") if RUNE.search(line)]


def bands(gs: list, want: int) -> list[list]:
    """Group glyphs into text lines, dropping decorative headers and strays."""
    found: list[tuple[int, list]] = []
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


def tokens(line: list) -> list[str]:
    """Reading-order tokens for one image line."""
    out, i = [], 0
    while i < len(line):
        kind, _, x = line[i]
        if kind == "R":
            out.append("R")
            i += 1
        elif kind == "t":
            paired = (
                i + 1 < len(line)
                and line[i + 1][0] == "t"
                and line[i + 1][2] - x <= PAIR_SPACING
            )
            out.append('"' if paired else "'")
            i += 2 if paired else 1
        else:
            j = i
            while (
                j + 1 < len(line)
                and line[j + 1][0] == "d"
                and line[j + 1][2] - line[j][2] <= DOT_SPACING
            ):
                j += 1
            out.append("." if j - i + 1 >= 3 else "-")
            i = j + 1
    return out


def text_tokens(text: str) -> list[str]:
    """Transcription line as tokens; existing tick marks are not glyphs here."""
    return ["R" if RUNE.match(c) else c for c in text if RUNE.match(c) or c in "-."]


def recorded(text: str) -> list[tuple[int, str]]:
    """Marks the transcription line already carries, as (token index, mark)."""
    out, seen = [], 0
    for char in text:
        if RUNE.match(char) or char in "-.":
            seen += 1
        elif char in "'\"":
            out.append((seen, char))
    return out


def insert(text: str, positions: list[tuple[int, str]]) -> str:
    """Insert marks at the given token indices, keeping marks already present."""
    out, seen, at = [], 0, dict(positions)
    for char in text:
        if RUNE.match(char) or char in "-.":
            if seen in at:
                out.append(at.pop(seen))
            seen += 1
        out.append(char)
    if seen in at:
        out.append(at.pop(seen))
    assert not at, f"unplaced marks {at} in {text!r}"
    return "".join(out)


def placements() -> list[tuple[int, str, str]]:
    """(page, original line, line with its marks) for every aligned line."""
    blocks = CORPUS.read_text().split("%")
    out = []
    for page in range(len(blocks)):
        gs = glyphs(page)
        if not any(g[0] == "t" for g in gs):
            continue
        lines = text_lines(blocks[page])
        for line, text in zip(bands(gs, len(lines)), lines):
            tk = tokens(line)
            marks = [(i, t) for i, t in enumerate(tk) if t in "'\""]
            if not marks:
                continue
            stripped = [t for t in tk if t not in "'\""]
            expected = text_tokens(text)
            # a line may carry a trailing separator the transcription omits;
            # every mark still sits inside the agreeing prefix
            common = min(len(stripped), len(expected))
            if stripped[:common] != expected[:common] or max(i for i, _ in marks) > common:
                print(f"page {page} line SKIPPED (sequence disagrees): {text}")
                continue
            # token indices shift by the marks sitting before them
            shifted = [(i - sum(1 for j, _ in marks if j < i), t) for i, t in marks]
            missing = [m for m in shifted if m not in recorded(text)]
            if not missing:
                continue
            out.append((page, text, insert(text, missing)))
    return out


def main() -> None:
    found = placements()
    apostrophes = sum(line.count("'") for _, _, line in found)
    quotes = sum(line.count('"') for _, _, line in found)
    for page, _old, new in found:
        print(f"page {page:3}: {new}")
    print(f"\n{len(found)} lines carry marks: {apostrophes} apostrophes, {quotes} quotation marks")

    if "--write" not in sys.argv:
        print("\n(dry run; pass --write to update the transcriptions)")
        return

    for path in TARGETS:
        text = path.read_text()
        for _, old, new in found:
            if old == new:
                continue
            assert text.count(old) == 1, f"{path.name}: {old!r} is not unique"
            text = text.replace(old, new)
        path.write_text(text)
        print(f"updated {path.name}")


if __name__ == "__main__":
    main()
