# ABOUTME: Searches the page images for unusually wide word breaks and asks whether the
# ABOUTME: word before one is long, which would locate sentence ends without any glyph.
"""If the scribe paused at sentence ends, the ink says where they are.

`does_the_scribe_leave_extra_space.py` measures the physical whitespace at every
separator and finds the four-dot spaced exactly like an ordinary word break -- median
1.000 against 1.000. It leaves one thing unlooked-at: the **ordinary** breaks. If some of
them are wider than the rest, and the word before a wide one runs long, then the spacing
locates sentence ends independently of any mark.

That would be a locator of a kind this corpus has never had. Every test of the four-dot so
far had to assume where the boundaries are; `what_would_it_take.py` shows the length
channel cannot settle it at any corpus size, because both surviving readings predict an
ordinary interior block at the span end.

## Measured entirely in the image

No alignment to the transcription is needed. Word lengths are counted from the runes
themselves, so this is one self-contained measurement:

- connected components give runes (ink 80-180 px tall) and dot clusters (blobs <= 16 px);
- runes are grouped into written lines, then into words by the one-dot separators;
- each word's closing gap gets a whitespace value, normalised by its line's median.

**The first and last word of every line are dropped.** Words wrap across lines, so those
two are truncated and their lengths are wrong.

## The artifact that would fake the opposite result

A missed rune merges two words and leaves a huge gap. That makes wide gaps follow
*shorter* apparent words, which pushes the correlation negative. So a positive result is
conservative, and a null could be a missed-rune effect masking a real signal. The
diagnostic is the word *after* the gap: a missed rune shortens the words on both sides of
it, a sentence end lengthens the one before and shortens the one after.

## Result: nothing, and the reader is too lossy to call it a clean null

| whitespace band | breaks | word before | word after |
|---|---|---|---|
| all one-dot breaks | 877 | 3.85 | 3.86 |
| top 50% (>= 1.00) | 577 | -0.03 +- 0.14 | -0.08 |
| top 25% (>= 1.09) | 233 | **-0.26 +- 0.14** | -0.14 |
| top 10% (>= 1.18) | 117 | -0.10 +- 0.19 | -0.16 |
| top 5% (>= 1.27) | 45 | **+0.27 +- 0.32** | -0.21 |

Correlation of whitespace with the word before: **+0.071 +- 0.034**; with the word after,
-0.041. The signs are what a sentence end predicts and the size is not, and the bands
contradict each other -- the top quarter reads -0.26 and the top twentieth +0.27. That is
noise.

**The reader recovers 877 usable breaks from the body's 2,392**, and its mean word length
is 3.85 against the transcription's 4.42. Dropping the first and last word of every line
costs most of that, and undercounted runes cost the rest. So this is not a clean null: a
+0.07 correlation on a lossy reader with a known negative artifact cannot exclude a real
effect of the size English would give.

**What would make it decisive:** aligning the image words to the transcription, so the
true block lengths are used instead of counted blobs, and the line-edge words are
recovered. `page_alignment.py` already matches pages by word-length sequence and could be
extended to within-page alignment.

    python do_wide_gaps_mark_sentence_ends.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_scribe_leave_extra_space import glyphs, lines_of  # noqa: E402

PAGES = range(58)
DECILES = (0.50, 0.75, 0.90, 0.95)


def words_of_page(page: int):
    """(word length, whitespace of its closing gap) for interior words of each line."""
    runes, marks = glyphs(page)
    rows = []
    for line in lines_of(runes):
        top = np.median([r[0] for r in line])
        here = [m for m in marks if abs(m[0] - top) < 150]
        gaps = []
        for a, b in zip(line, line[1:]):
            left, right = a[1] + a[2], b[1]
            gap = right - left
            if gap <= 0 or gap > 400:
                gaps.append(None)
                continue
            inside = [m for m in here if left <= m[1] and m[2] <= right]
            if len(inside) > 1:
                gaps.append(None)
                continue
            count = inside[0][3] if inside else 0
            width = (inside[0][2] - inside[0][1]) if inside else 0
            gaps.append((count, gap - width))
        base = [w for g in gaps if g and g[0] == 1 for w in (g[1],)]
        if len(base) < 3:
            continue
        scale = float(np.median(base))
        if scale <= 0:
            continue
        words, length = [], 1
        for g in gaps:
            if g is None:
                words.append(None)
                length = 1
                continue
            if g[0] == 0:
                length += 1
                continue
            words.append((length, g[0], g[1] / scale))
            length = 1
        clean = [w for w in words[1:-1] if w is not None]
        for i, (n, count, white) in enumerate(clean):
            after = clean[i + 1][0] if i + 1 < len(clean) else None
            rows.append((n, count, white, after))
    return rows


def main() -> None:
    rows = []
    for page in PAGES:
        try:
            rows.extend(words_of_page(page))
        except FileNotFoundError:
            continue
    ordinary = [r for r in rows if r[1] == 1 and r[3] is not None]
    print(f"{len(rows):,} interior words read from the images,")
    print(f"{len(ordinary):,} of them closed by an ordinary one-dot break.\n")

    lengths = np.array([r[0] for r in ordinary], float)
    white = np.array([r[2] for r in ordinary], float)
    after = np.array([r[3] for r in ordinary], float)
    print(f"mean word length from the images: {lengths.mean():.2f} runes")
    print("  (the transcription gives 4.42 for the body, so the reader is close)\n")

    print(f"{'whitespace band':<26}{'breaks':>8}{'word before':>15}{'word after':>14}")
    print(
        f"{'all one-dot breaks':<26}{len(lengths):>8}{lengths.mean():>15.2f}{after.mean():>14.2f}"
    )
    for q in DECILES:
        cut = float(np.quantile(white, q))
        sel = white >= cut
        if sel.sum() < 20:
            continue
        rest = ~sel
        d = lengths[sel].mean() - lengths[rest].mean()
        se = math.hypot(
            lengths[sel].std(ddof=1) / math.sqrt(sel.sum()),
            lengths[rest].std(ddof=1) / math.sqrt(rest.sum()),
        )
        da = after[sel].mean() - after[rest].mean()
        print(
            f"{f'top {1 - q:.0%} (>= {cut:.2f})':<26}{int(sel.sum()):>8}"
            f"{f'{d:+.2f} +- {se:.2f}':>15}{f'{da:+.2f}':>14}"
        )

    r = float(np.corrcoef(white, lengths)[0, 1])
    ra = float(np.corrcoef(white, after)[0, 1])
    n = len(white)
    print(
        f"\ncorrelation of whitespace with the word before: {r:+.3f}"
        f"  (se {1 / math.sqrt(n):.3f})"
        f"\ncorrelation of whitespace with the word after:  {ra:+.3f}"
    )
    print(
        "\nA sentence end would raise the word before and lower the word after."
        "\nA missed rune lowers both, because it merges two words into one gap."
    )


if __name__ == "__main__":
    main()
