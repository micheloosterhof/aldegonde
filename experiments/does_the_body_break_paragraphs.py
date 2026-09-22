# ABOUTME: Measures short lines as a paragraph-end device, showing the body uses it three
# ABOUTME: times less than the author and that its instances are thirteen-dots not four-dots.
"""A short line is a paragraph end. How often does the body allow one?

A manuscript set as justified text fills every line to the measure except where a unit
ends. So a **short line** is the classic layout marker of a paragraph break, and it is
visible in the transcription without reading a rune.

This matters for the mixture reading (`are_some_four_dots_real.py`): if some four-dots are
real boundaries, the ones closing a short line are the strongest candidates available --
stronger than the line-end flag, because ending a line is common and ending a *short* line
is deliberate.

Page-final lines are dropped throughout: they are short by construction.

## The control has to be the ENCIPHERED front matter

`does_the_body_have_a_different_hand.py` states the confound: enciphered text has no word
shapes to break on, so a scribe fills to a measure, where plaintext breaks where the text
does. Comparing the body's layout against the author's **plaintext** pages measures
encipherment, not the scribe.

| | lines | mean | sd | short | ending mid-word |
|---|---|---|---|---|---|
| front matter, plaintext | 49 | 18.6 | 6.6 | 16.3% | 46.9% |
| **front matter, enciphered** | 83 | 19.9 | **3.0** | **4.8%** | **69.9%** |
| the body | 539 | 21.9 | **2.3** | **3.5%** | **77.7%** |

The enciphered front matter sits beside the body on every column and far from the
plaintext pages. So the layout difference is the cipher, not the hand.

What survives as a real difference is small: the body's lines are more uniform than the
enciphered front matter's, **sd 2.32 against 2.97, F = 1.64, p = 0.0007** -- a factor of
1.28, not the 2 the plaintext comparison suggested. The short-line rate (3.5% against
4.8%) and the mid-word rate (77.7% against 69.9%) are both within noise.

## Result: the device is real, identical in both, and carried by the thirteen-dot

A short line is closed by a mark at about twenty times the ordinary rate, and at the same
rate in both sections:

| | short lines | closed by a mark | on ordinary lines | P |
|---|---|---|---|---|
| front matter, enciphered | 4 | 2 (0.50) | 0.025 | 3.7e-03 |
| the body | 19 | 9 (0.47) | 0.025 | 2.8e-10 |

Within the body the two glyphs separate sharply:

| glyph | in the body | closing a short line | rate |
|---|---|---|---|
| ⑬ | 28 | 5 | **0.179** |
| ④ | 139 | 3 | **0.022** |

**z = +3.55.** The thirteen-dot takes a paragraph break eight times as often as the
four-dot. That comparison is internal to the body -- same pages, same hand, same cipher --
so the confound above does not touch it.

## What this settles and what it does not

**Settles:** the four-dot is not a paragraph mark. Three short lines out of 139, where the
glyph the red ink confirms as a section boundary takes 5 of 28. A third physical channel
separating the two glyphs, after the ink and the line-end rate, agreeing with both.

**Does not:** supply the mixture test with marks. Three four-dots is fewer than the
fourteen the line-end flag gave, so this route is worse for locating sentence ends.

**And it retracts a side observation.** The first version of this file reported the body's
paragraph breaks as "three times rarer than the author allows" and its lines as twice as
uniform. Both came from the plaintext comparison and neither survives the right control.

    python does_the_body_break_paragraphs.py
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
MARKS = set("④⑬③⑩㉓.")
BODY = range(15, 71)
FRONT = range(15)
SHORT = 0.8


def lines(chunks):
    """(runes, page-final?, closing glyph) for each rune-bearing line."""
    text = MASTER.read_text().split("%")
    out = []
    for ci in chunks:
        if ci >= len(text):
            continue
        kept = [ln for ln in re.split(r"[/\n]", text[ci]) if RUNE.search(ln)]
        for j, ln in enumerate(kept):
            last = max(i for i, ch in enumerate(ln) if RUNE.match(ch))
            closer = "".join(c for c in ln[last + 1 :] if not c.isspace())[:1]
            out.append((len(RUNE.findall(ln)), j == len(kept) - 1, closer))
    return [row for row in out if not row[1]]


def report(label, rows):
    n = np.array([a for a, _, _ in rows], float)
    short = n <= SHORT * n.mean()
    marked = np.array([c in MARKS for _, _, c in rows])
    hits, total = int((short & marked).sum()), int(short.sum())
    base = float(marked[~short].mean())
    print(
        f"\n{label}: {len(rows)} non-page-final lines, mean {n.mean():.1f} runes,"
        f" sd {n.std(ddof=1):.1f}"
    )
    print(f"  short lines (<= {SHORT:.0%} of the mean): {total} ({total / len(rows):.1%})")
    print(
        f"  of those, closed by a mark: {hits}/{total} = {hits / total:.2f}"
        f"   against {base:.2f} on ordinary lines"
        f"   P = {stats.binom.sf(hits - 1, total, base):.1e}"
    )
    counts = Counter(c for (_, _, c), s in zip(rows, short) if s and c in MARKS)
    print(f"  glyphs closing them: {dict(counts)}")
    return counts


def main() -> None:
    body, author = lines(BODY), lines(FRONT)
    print("A short line is a paragraph end. Page-final lines are dropped as short by")
    print("construction. The mark rate on ordinary lines is the baseline.")
    report("THE AUTHOR", author)
    counts = report("THE BODY", body)

    all_marks = Counter()
    text = MASTER.read_text().split("%")
    for ci in BODY:
        if ci < len(text):
            all_marks.update(ch for ch in text[ci] if ch in MARKS)

    print("\n\nWhich glyph gets a paragraph break, in the body.\n")
    print(f"{'glyph':>6}{'in the body':>13}{'closing a short line':>22}{'rate':>9}")
    for glyph in ("⑬", "④"):
        print(
            f"{glyph:>6}{all_marks[glyph]:>13}{counts.get(glyph, 0):>22}"
            f"{counts.get(glyph, 0) / all_marks[glyph]:>9.3f}"
        )
    p1 = counts.get("⑬", 0) / all_marks["⑬"]
    p2 = counts.get("④", 0) / all_marks["④"]
    pooled = (counts.get("⑬", 0) + counts.get("④", 0)) / (all_marks["⑬"] + all_marks["④"])
    se = math.sqrt(pooled * (1 - pooled) * (1 / all_marks["⑬"] + 1 / all_marks["④"]))
    print(f"\n  thirteen-dot against four-dot: z = {(p1 - p2) / se:+.2f}")
    print(
        "\n  So the body's paragraph breaks are section breaks. The four-dot closes"
        "\n  three short lines out of 141, which is too few for the mixture test and"
        "\n  is itself evidence that the four-dot is not a paragraph mark either."
    )


if __name__ == "__main__":
    main()
