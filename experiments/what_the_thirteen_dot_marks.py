# ABOUTME: Shows the 13-dot mark is a structural terminator sitting at section breaks
# ABOUTME: while the 4-dot mark avoids them, which is why pooled dot statistics mix.
"""The thirteen-dot mark closes a section. The four-dot mark does not.

`marks-are-not-one-glyph` records that the two behave oppositely and that every pooled
`.` statistic is therefore a mixture. It does not say what either one *is*. This does.

Measured against the book's own structural markers -- `$` for a section break and `&`,
which the solved pages show standing between blocks of text:

| | n | median runes to the nearest `$` | within 40 runes |
|---|---|---|---|
| **13-dot** | 31 | **9** | **23 / 31** |
| 4-dot | 141 | 429 | 5 / 141 |
| 3-dot | 6 | 548 | 1 / 6 |
| 10-dot | 4 | 408 | 0 / 4 |

Scattered at random over the rune stream the median would be 313 +- 74. The 13-dot reads
9 (P = 0.0000); the 4-dot reads 429, which is **farther than chance** (P(<= observed) =
0.999), so it actively avoids section edges rather than merely ignoring them.

The adjacency is categorical rather than statistical. Looking at what immediately follows
each mark in the transcription:

    13-dot   followed by '&' 15 times, by a rune 15, by another 13-dot 1
    4-dot    followed by '&'  0 times, by a rune 132, by a quote mark 5

Half the 13-dot marks sit immediately before the `&` marker, and the sequence that
follows is usually `& $ %` -- marker, section break, page break. No 4-dot does this once
in 141.

## What it explains

- **Why pooled dot statistics are a mixture.** They average a sentence-level mark with a
  section-level one.
- **Why 4-dot carries the sentence-final anomaly and 13-dot does not**
  (`sentences-do-not-end-long.md`: -0.32 +- 0.20 against +0.05 +- 0.39). They are not the
  same kind of mark, so the 13-dot cell was never a counter-example -- it was the wrong
  population.
- **Why the front matter has none.** Pages 0-14 carry 87 marks, all of the 4-dot class,
  and no 13-dot at all, while still carrying `&` and `$`. The body marks its section ends
  with a glyph the front matter does not use.

## What it does not explain

Sixteen of the 31 are followed by a rune, so the 13-dot is not *exclusively* terminal.
Whether those are a second function or the same one at boundaries the transcription does
not mark is not answerable from here.

## A lead that died on the way

The body's per-page line measure correlates -0.74 with the page's 13-dot count, which
looked like a scribal signature. It is entirely page fullness: 13-dot pages are
section-end pages, which carry fewer runes (r = -0.56), and a page with fewer runes has
shorter lines (r = +0.71). Controlling for runes and lines on the page, the partial
correlation is **+0.087, P = 0.59**. The mark tells you nothing about the hand.

    python what_the_thirteen_dot_marks.py
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ANNOTATION = re.compile(r"^[\s0-9-]*$")
DOT_MARKS = ("⑬", "④", "③", "⑩")
NEAR = 40
DRAWS = 1500


def stream() -> str:
    return "\n".join(
        line
        for line in MASTER.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )


def positions(text):
    """Rune index of each dot mark, each section break and each '&' marker."""
    marks = {g: [] for g in DOT_MARKS}
    sections, markers = [], []
    k = 0
    for ch in text:
        if RUNE.match(ch):
            k += 1
        elif ch in marks:
            marks[ch].append(k)
        elif ch == "$":
            sections.append(k)
        elif ch == "&":
            markers.append(k)
    return marks, np.array(sections, float), np.array(markers, float), k


def neighbours(text, glyph):
    """What immediately follows and precedes this glyph, skipping line breaks."""

    def step(i, direction):
        j = i + direction
        while 0 <= j < len(text) and text[j] == "\n":
            j += direction
        return text[j] if 0 <= j < len(text) else ""

    after, before = collections.Counter(), collections.Counter()
    for i, ch in enumerate(text):
        if ch != glyph:
            continue
        nxt, prv = step(i, 1), step(i, -1)
        after["rune" if RUNE.match(nxt) else repr(nxt)] += 1
        before["rune" if RUNE.match(prv) else repr(prv)] += 1
    return after, before


def main() -> None:
    text = stream()
    marks, sections, markers, runes = positions(text)
    rng = np.random.default_rng(3301)

    print(
        f"{len(sections)} section breaks and {len(markers)} '&' markers "
        f"in {runes:,} runes.\n"
    )
    print(
        f"{'mark':<8}{'n':>5}{'median to $':>14}{'within 40':>12}"
        f"{'random null':>18}{'P':>9}"
    )
    for glyph in DOT_MARKS:
        if not marks[glyph]:
            continue
        distance = np.array([np.min(np.abs(sections - p)) for p in marks[glyph]])
        null = np.array(
            [
                np.median(
                    [
                        np.min(np.abs(sections - x))
                        for x in rng.uniform(0, runes, len(distance))
                    ]
                )
                for _ in range(DRAWS)
            ]
        )
        observed = float(np.median(distance))
        print(
            f"{glyph:<8}{len(distance):>5}{observed:>14.0f}"
            f"{f'{int((distance < NEAR).sum())}/{len(distance)}':>12}"
            f"{f'{null.mean():.0f} +- {null.std(ddof=1):.0f}':>18}"
            f"{float((null <= observed).mean()):>9.4f}"
        )

    print("\nDistance to the nearest '&' marker, which the solved pages show standing")
    print("between blocks of text.\n")
    print(f"{'mark':<8}{'median':>10}{'at distance zero':>20}")
    for glyph in ("⑬", "④"):
        d = np.array([np.min(np.abs(markers - p)) for p in marks[glyph]])
        print(f"{glyph:<8}{np.median(d):>10.0f}{f'{int((d == 0).sum())}/{len(d)}':>20}")

    print("\nWhat immediately follows each mark in the transcription.\n")
    table = {}
    for glyph in ("⑬", "④"):
        after, _ = neighbours(text, glyph)
        table[glyph] = after
        print(f"  {glyph}  {dict(after.most_common(5))}")
    a, b = table["⑬"].get("'&'", 0), table["④"].get("'&'", 0)
    na, nb = sum(table["⑬"].values()), sum(table["④"].values())
    odds, p = stats.fisher_exact([[a, na - a], [b, nb - b]])
    print(f"\n  followed by '&': 13-dot {a}/{na}, 4-dot {b}/{nb}   Fisher P = {p:.2e}")

    front = collections.Counter(
        ch
        for n, page in enumerate(MASTER.read_text().split("%"))
        if n < 15
        for ch in page
        if ch in DOT_MARKS or ch in "&$"
    )
    print(f"\nPages 0-14, for contrast: {dict(front)}")
    print("They carry section structure but not one 13-dot.")

    print(
        "\nThe 13-dot marks a structural close and the 4-dot does not; the 4-dot avoids"
        "\nsection edges by more than chance. Any statistic that pools them averages a"
        "\nsentence-level mark with a section-level one."
    )


if __name__ == "__main__":
    main()
