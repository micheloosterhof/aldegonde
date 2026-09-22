# ABOUTME: Audits the two transcriptions to show the solved pages' mark and the body's
# ABOUTME: are the same glyph family, and splits the sentence-final anomaly per glyph.
"""The solved pages' `.` and the body's ④ are the same mark, recorded two ways.

Every result in `sentences-do-not-end-long.md` compares the author's marks on pages
0-14 against the body's on pages 15-56. The mark is written `.` on the first set and
④⑬③⑩ on the second, and the split is exact: **pages 0-14 carry 87 `.` and no circled
numeral; pages 15-72 carry 182 circled numerals and no `.`**. That is precisely the
boundary of the solved section, which is the kind of coincidence that usually means a
convention changed rather than the book did.

It did. The repository holds two transcriptions of the same pages, and they are
identical except in how they record this one mark:

| page | master | marks file |
|---|---|---|
| 0-14 | `.` | `.` |
| 16 | ④ ×5 | `.` ×5 |
| 19 | ④ ×4 | `.` ×4 |
| 55 | ④ ×5 | ④ ×1, `.` ×4 |

So `.` does not name a distinct glyph. It means **"a dot mark whose count was not
recorded"**, and ④ means "confirmed four dots" -- page 55 carries both in the same file,
which rules out `.` being a pooled rendering of ④. The master resolved dot counts on
pages 15+ and left pages 0-14 unresolved. ⑬, ③, ⑩ and `"` agree between the two files
everywhere.

**What this settles, and it is more than expected.** Every one of the 46 disagreements
is a clean ④ ↔ `.` swap; ④ plus `.` totals 228 in both files; and ⑬, ③, ⑩ agree exactly
everywhere. So `.` and ④ are one glyph class, and the other three are genuinely
distinct marks both transcribers saw the same way.

Pages 0-14 therefore carry **87 marks of the ④ class and not one ⑬, ③ or ⑩**. The author
reference is not a mixture at all -- it is pure four-dot. That makes the body's ④ row the
exact like-for-like comparison:

    the author, 87 marks of the ④ class     +1.28 +- 0.28
    the body,  136 blocks before a ④        -0.32 +- 0.20
                                             z = -4.65

Same glyph class, same book, same statistic. The anomaly survives the strictest
comparison available, which is a stronger footing than it had.

## Two things that fall out, neither needing a register proxy

**The mark rate differs by a factor of 2.3.** The author's pages carry a mark every 32
runes and the body one every 74. That is a 5σ difference between two stretches of the
same book. It is consistent with the body being written in longer sentences and equally
consistent with the mark meaning something else there, so it decides nothing on its own
-- but it is a plain fact about the book that nothing had recorded.

**Within the body the glyphs disagree**, which earlier work on the
dot-counts predicted. Four-dot carries the whole sentence-final
anomaly; thirteen-dot is neutral, on a quarter of the sample.

    python what_the_marks_are.py
"""

from __future__ import annotations

import collections
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_cipher_restart import ANNOTATION, RUNE, STANDALONE  # noqa: E402
from sentences_do_not_end_long import BODY  # noqa: E402

from aldegonde import c3301  # noqa: E402

MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
MARKS_FILE = ROOT / "data" / "liber-primus__transcription--master.marks.txt"
DOT_MARKS = ".④⑬③⑩"
SOLVED_PAGES = range(15)  # every page the master leaves unresolved


def page_marks(path: Path) -> list[collections.Counter]:
    return [
        collections.Counter(ch for ch in page if ch in DOT_MARKS)
        for page in path.read_text().split("%")
    ]


def blocks_with(mark: str | set[str]) -> list[tuple[int, bool, bool]]:
    """(length, follows the mark, precedes the mark) for the body's blocks."""
    wanted = {mark} if isinstance(mark, str) else mark
    text = "\n".join(
        line
        for line in BODY.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    out: list[tuple[int, bool, bool]] = []
    length, initial = 0, False
    for ch in text:
        if RUNE.match(ch):
            length += 1
        elif ch == "\n":
            continue
        elif ch in STANDALONE:
            if not length:
                initial = False
        elif ch in c3301.WORD_BOUNDARY:
            if length:
                out.append((length, initial, ch in wanted))
                length = 0
            initial = ch in wanted
    if length:
        out.append((length, initial, False))
    return out


def final_gap(mark) -> tuple[int, float, float]:
    """Mean length of the block before this mark, against the body's interior."""
    rows = blocks_with(mark)
    before = np.array([n for n, i, f in rows if f and not i], float)
    interior = np.array([n for n, i, f in rows if not f and not i], float)
    if len(before) < 4:
        return len(before), float("nan"), float("nan")
    se = math.hypot(
        before.std(ddof=1) / math.sqrt(len(before)),
        interior.std(ddof=1) / math.sqrt(len(interior)),
    )
    return len(before), float(before.mean() - interior.mean()), se


def main() -> None:
    master, marks = page_marks(MASTER), page_marks(MARKS_FILE)
    print("The same mark, recorded two ways. Pages where the files disagree.\n")
    print(f"{'page':>6}{'master':>28}{'marks file':>28}")
    shown = 0
    for n, (a, b) in enumerate(zip(master, marks)):
        if a != b and shown < 8:
            print(f"{n:>6}{str(dict(a)):>28}{str(dict(b)):>28}")
            shown += 1
    agree = sum(1 for a, b in zip(master, marks) if a == b and a)
    differ = sum(1 for a, b in zip(master, marks) if a != b)
    unclean = [
        n
        for n, (a, b) in enumerate(zip(master, marks))
        if a != b
        and (
            a.get("④", 0) - b.get("④", 0) != b.get(".", 0) - a.get(".", 0)
            or any(a.get(g, 0) != b.get(g, 0) for g in "⑬③⑩")
        )
    ]
    four = (
        sum(c.get("④", 0) + c.get(".", 0) for c in master),
        sum(c.get("④", 0) + c.get(".", 0) for c in marks),
    )
    print(f"\n{agree} pages agree exactly and {differ} differ. Of those differences,")
    print(f"{len(unclean)} is anything but a clean ④ <-> '.' swap.")
    print(
        f"  ④ plus '.' totals {four[0]} and {four[1]}: "
        f"{'identical' if four[0] == four[1] else 'DIFFERENT'}"
    )
    print(
        "  "
        + ", ".join(
            f"{g} {sum(c.get(g, 0) for c in master)} vs {sum(c.get(g, 0) for c in marks)}"
            for g in "⑬③⑩"
        )
        + "   the other glyphs agree exactly"
    )

    text = MASTER.read_text().split("%")
    solved = collections.Counter(
        ch for n in SOLVED_PAGES for ch in text[n] if ch in DOT_MARKS
    )
    body = collections.Counter(
        ch for n in range(15, len(text)) for ch in text[n] if ch in DOT_MARKS
    )
    print(f"\npages 0-14 : {dict(solved)}")
    print(f"pages 15+  : {dict(body)}")
    print("Complementary, and the split is exactly the solved section's boundary.")

    runes_solved = sum(len(RUNE.findall(text[n])) for n in SOLVED_PAGES)
    runes_body = sum(len(RUNE.findall(text[n])) for n in range(15, len(text)))
    n_solved, n_body = sum(solved.values()), sum(body.values())
    p1, p2 = n_solved / runes_solved, n_body / runes_body
    se = math.hypot(
        math.sqrt(p1 * (1 - p1) / runes_solved), math.sqrt(p2 * (1 - p2) / runes_body)
    )
    print("\nMark rate, which needs no reference text at all.\n")
    print(
        f"  pages 0-14  {n_solved:>4} marks in {runes_solved:>6,} runes"
        f"   one every {1 / p1:5.1f}"
    )
    print(
        f"  pages 15+   {n_body:>4} marks in {runes_body:>6,} runes"
        f"   one every {1 / p2:5.1f}"
    )
    print(f"  difference {p1 - p2:+.5f} +- {se:.5f}   z = {(p1 - p2) / se:+.2f}")

    print("\nThe sentence-final gap, one glyph at a time.\n")
    print(
        f"{'glyph':>6}{'in the body':>13}{'blocks before':>15}{'gap vs interior':>19}"
        f"{'vs +0.75 predicted':>21}"
    )
    for glyph in "④⑬③⑩":
        n, gap, se_gap = final_gap(glyph)
        if math.isnan(gap):
            print(f"{glyph:>6}{body.get(glyph, 0):>13}{n:>15}{'too few':>19}")
            continue
        z = (gap - 0.75) / math.hypot(se_gap, 0.04)
        print(
            f"{glyph:>6}{body.get(glyph, 0):>13}{n:>15}"
            f"{f'{gap:+.2f} +- {se_gap:.2f}':>19}{z:>+21.2f}"
        )
    n, gap, se_gap = final_gap(set("④⑬③⑩"))
    print(
        f"{'all':>6}{n_body:>13}{n:>15}{f'{gap:+.2f} +- {se_gap:.2f}':>19}"
        f"{(gap - 0.75) / math.hypot(se_gap, 0.04):>+21.2f}"
    )

    print(
        "\nFour-dot carries the anomaly. Thirteen-dot is neutral but has a quarter of"
        "\nthe sample and still sits 1.8 sigma below the prediction, so it is not a"
        "\ncounter-example -- only an unresolved cell. The pooled row is the one that"
        "\nmatches the author's pooled +1.28, and the comparison is like for like."
    )


if __name__ == "__main__":
    main()
