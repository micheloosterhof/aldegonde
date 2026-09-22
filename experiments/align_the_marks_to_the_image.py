# ABOUTME: Matches image-detected four-dot gaps to their transcription blocks on pages
# ABOUTME: where the counts agree, giving exact lengths and removing the reader's artifact.
"""Measure the gap in the image, take the length from the transcription.

`are_some_four_dots_real.py` proposes that the four-dot is a **mixture** -- some marks are
real sentence ends, some are not -- and that the ones the scribe set apart physically are
the candidates. Both arms of that test failed:

- the line-end split is valid but has **14 marks**, where a full mixture would show at
  1.5 sigma;
- the gap-width split has more marks but measured word lengths from the image, and the
  reader's missed-rune artifact manufactures short words beside wide gaps -- the wide-gap
  subset read 3.13 against 3.90, the wrong direction for a sentence end and the right one
  for the failure mode.

The second failure is fixable. The gap width has to come from the image, because the
transcription does not record it. The **length** does not: it is in the transcription
exactly. Matching the two removes the artifact at its source rather than bounding it.

## The matching, and why it is conservative

For each page the image's four-dot gaps and the transcription's four-dot marks are both in
reading order. Rather than align sequences, this uses only pages where the **two counts
agree exactly**, and matches in order. A page where the reader missed or split a cluster
is discarded whole instead of contributing a mismatched pair.

That keeps 27 of 58 pages and **66 marks**, against the 14 the line-end split had.

## The control that decides it

Wide gaps might follow long blocks for a layout reason: justified text stretches spacing
after whatever happens to sit there. So the same correlation is measured on the **one-dot
separators of the same pages**. If it is positive there, the four-dot's is worthless.

## RETRACTED: the control that killed the channel was itself an artifact

The first version of this file reported a one-dot control at **r = +0.397 on 93 marks**
and concluded that justification confounds the gap-width channel outright. Both halves of
that are wrong.

Its transcription parser reset the rune counter at each line start, cutting every wrapped
word in two (`body_parse.py`). That mattered twice over. The block lengths were wrong --
and worse, the page-selection rule is **exact count agreement between image and
transcription**, so the pages it kept were the ones where the parser's errors happened to
cancel the image reader's. Selection by mutual error is not a sample.

With the parser corrected, genuine agreement is rarer and the one-dot control collapses
from 93 marks to **17** -- too few to read.

## The confound is real and small

Measured instead on all 1,395 one-dot gaps the image reader finds, with no
count-agreement filter:

    correlation of whitespace with the preceding word    r = +0.054 +- 0.027
    wide-gap minus narrow-gap block length               +0.05 +- 0.12

The image reader's missed-rune artifact biases this **negative**, so +0.054 is a lower
bound. Either way it is a tenth of the +0.397 first reported, and it does not rule the
channel out.

## What the channel actually gives

| mark | marks | wide-gap subset | narrow | difference | r |
|---|---|---|---|---|---|
| four-dot, aligned | 41 | 4.19 | 3.80 | +0.39 +- 0.63 | -0.128 |

Forty-one marks and a standard error of 0.63 against an effect that would be about +1.2
under a full mixture. **The channel is underpowered, not confounded** -- which is the same
verdict the line-end split reached, and for the same reason.

## What is worth keeping

The alignment. Matching image gaps to transcription blocks gives 41 four-dots with exact
lengths and removes the missed-rune artifact at its source. The count-agreement rule is
the limiting factor and now rejects more pages than it did, because it is no longer
accepting cancelled errors.

    python align_the_marks_to_the_image.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_scribe_leave_extra_space import glyphs, lines_of  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
PAGES = range(58)
OFFSET = 15


def image_gaps(page: int):
    """(dot count, normalised whitespace) in reading order, mid-line gaps only."""
    runes, marks = glyphs(page)
    out = []
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
                continue
            count = inside[0][3] if inside else 0
            width = (inside[0][2] - inside[0][1]) if inside else 0
            cells.append((count, gap - width))
        base = [w for c, w in cells if c == 1]
        if len(base) < 3:
            continue
        scale = float(np.median(base))
        if scale > 0:
            out.extend((c, w / scale) for c, w in cells if c)
    return out


def transcription_marks(chunk: int):
    """(glyph, preceding block length) in reading order, mid-line marks only."""
    text = MASTER.read_text().split("%")
    out = []
    for line in re.split(r"[/\n]", text[chunk]):
        if not RUNE.search(line):
            continue
        n = 0
        for i, ch in enumerate(line):
            if RUNE.match(ch):
                n += 1
            elif ch in "①④⑬③⑩" and n:
                if RUNE.search(line[i + 1 :]):
                    out.append((ch, n))
                n = 0
    return out


def paired(count: int, glyph: str):
    """(whitespace, block length) on pages where the two counts agree exactly."""
    text = MASTER.read_text().split("%")
    out, pages = [], 0
    for page in PAGES:
        chunk = page + OFFSET
        if chunk >= len(text):
            continue
        try:
            img = [w for c, w in image_gaps(page) if c == count]
        except FileNotFoundError:
            continue
        txt = [n for g, n in transcription_marks(chunk) if g == glyph]
        if img and len(img) == len(txt):
            pages += 1
            out.extend(zip(img, txt))
    return out, pages


def correlate(rows):
    w = np.array([a for a, _ in rows], float)
    n = np.array([b for _, b in rows], float)
    r = float(np.corrcoef(w, n)[0, 1])
    return r, 1 / math.sqrt(len(rows) - 3), len(rows)


def split(rows):
    w = np.array([a for a, _ in rows], float)
    n = np.array([b for _, b in rows], float)
    cut = float(np.median(w))
    hi, lo = n[w >= cut], n[w < cut]
    se = math.hypot(hi.std(ddof=1) / math.sqrt(len(hi)), lo.std(ddof=1) / math.sqrt(len(lo)))
    return hi.mean(), lo.mean(), hi.mean() - lo.mean(), se, len(hi), len(lo)


def main() -> None:
    four, pages4 = paired(4, "④")
    one, pages1 = paired(1, "①")
    print(
        f"four-dots: {len(four)} marks on {pages4} pages where image and transcription"
        f" agree.\none-dots:  {len(one)} on {pages1} pages, as the layout control.\n"
    )
    print(f"{'mark':<12}{'n':>6}{'wide gap':>11}{'narrow':>9}{'difference':>18}{'r':>9}")
    for label, rows in (("four-dot", four), ("one-dot", one)):
        if len(rows) < 20:
            print(f"{label:<12}{len(rows):>6}   too few")
            continue
        hi, lo, d, se, nh, nl = split(rows)
        r, rse, n = correlate(rows)
        print(
            f"{label:<12}{n:>6}{hi:>11.2f}{lo:>9.2f}"
            f"{f'{d:+.2f} +- {se:.2f}':>18}{f'{r:+.3f}':>9}"
        )

    print(
        "\n  'wide gap' and 'narrow' are the mean length of the block the mark closes,"
        "\n  split at that mark class's own median whitespace."
        "\n\n  A mixture predicts the four-dot's wide-gap subset to run about 1.2 runes"
        "\n  longer. The one-dot row must be flat, or justification explains everything."
    )


if __name__ == "__main__":
    main()
