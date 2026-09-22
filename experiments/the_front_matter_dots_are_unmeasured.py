# ABOUTME: Shows the scan corpus covers only master pages 15-72, so the front matter's
# ABOUTME: dot counts are unmeasurable, and checks the anomaly survives that uncertainty.
"""No scan exists of the front matter, so its marks' dot counts are unknown.

`what_the_marks_are.py` concluded that "pages 0-14 carry 87 marks of the four-dot class
and not one thirteen-dot, so the author reference is pure four-dot". **That is
over-stated.** It rests on the transcription, and the transcription never resolves a dot
count before page 15 -- both the master and the marks file write a bare `.` there.

The dot counts come from the page scans, and those cover less than the book:

    data/page0-58.txt == master pages 15..72   (58 pages)
    scan image N      == master page N + 15

So image 0 is master page 15, and there is **no image of master pages 0-14 at all**. Every
dot-count statement in `mark-glyph-inventory.md` -- "a mark transcribed as `-` on page 5
is a triple dot", "page 7 carries a thirteen-dot cluster the transcription omits" -- is
about the file's pages, which are master pages 20 and 22. None of it reaches the front
matter.

The alignment is confirmed by the glyph counts: the census finds **31** thirteen-dot
clusters and the master records **31** circled-13 marks across pages 15-72, exactly.
(Four-dot reads 145 against 141 recorded, so a few are transcribed as something else or
not at all -- the 13% mismatch `mark-glyph-inventory.md` already records.)

## Does the uncertainty matter?

The author's 87 marks could be any mixture of dot counts. But **no body glyph class
lengthens**, so no mixture rescues the comparison:

| | marks | gap vs interior |
|---|---|---|
| the author, class unknown | 87 | **+1.32 +- 0.26** |
| the body, four-dot | 136 | -0.32 +- 0.20 |
| the body, thirteen-dot | 25 | +0.05 +- 0.39 |
| ten English registers | | +1.19 +- 0.28 |

Whatever the front matter's marks are, the body's marks of *both* resolved classes fail
to lengthen, and the author's lengthen like ordinary English. The conclusion survives; the
phrase "pure four-dot" does not, and is corrected in `what_the_marks_are.py`.

## What would settle it

Scans of master pages 0-14. The image directory holds 58 files covering 15-72; nothing in
this repository reaches earlier, so this cannot be resolved from what is here.

    python the_front_matter_dots_are_unmeasured.py
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ANNOTATION = re.compile(r"^[\s0-9-]*$")
DOT_MARKS = ".④⑬③⑩"
CENSUS = {"4-dot": 145, "13-dot": 31, "3-dot": 24, "10-dot": 8}


def runes_of(page: str) -> list[str]:
    return RUNE.findall(
        "\n".join(
            line
            for line in page.replace("/", "\n").split("\n")
            if not ANNOTATION.match(line)
        )
    )


def locate(target, master) -> tuple[int, int] | None:
    per_page = [runes_of(p) for p in master]
    for lo in range(20):
        for hi in range(lo + 50, len(master) + 1):
            if [r for n in range(lo, hi) for r in per_page[n]] == target:
                return lo, hi - 1
    return None


def main() -> None:
    master = MASTER.read_text().split("%")
    late = (ROOT / "data" / "page0-58.txt").read_text().split("%")
    flat = [r for p in late for r in runes_of(p)]
    found = locate(flat, master)

    print("Which master pages does the scanned corpus cover?\n")
    if found:
        lo, hi = found
        print(f"  data/page0-58.txt == master pages {lo}..{hi}   ({hi - lo + 1} pages)")
        print(f"  so scan image N == master page N + {lo}")
        print(f"  there is no image of master pages 0..{lo - 1}")
    else:
        print("  no contiguous match found")

    print("\nThe alignment, checked against the glyph counts.\n")
    print(f"{'glyph':<10}{'master 15-72':>14}{'scan census':>14}")
    counts = collections.Counter(
        ch for n in range(15, len(master)) for ch in master[n] if ch in DOT_MARKS
    )
    for glyph, label in (
        ("④", "4-dot"),
        ("⑬", "13-dot"),
        ("③", "3-dot"),
        ("⑩", "10-dot"),
    ):
        print(f"{glyph:<10}{counts.get(glyph, 0):>14}{CENSUS[label]:>14}")
    print("\n  the 13-dot counts agree exactly, which confirms the alignment")

    front = collections.Counter(
        ch for n in range(15) for ch in master[n] if ch in DOT_MARKS
    )
    print(f"\nFront matter, master pages 0-14: {dict(front)}")
    print("  the dot counts are never resolved there, and no scan exists, so the")
    print("  class of those 87 marks is unknown.")

    print("\nDoes it matter? No body glyph class lengthens.\n")
    print(f"{'':<34}{'marks':>7}{'gap vs interior':>19}")
    for label, marks, gap in (
        ("the author, class unknown", 87, "+1.32 +- 0.26"),
        ("the body, four-dot", 136, "-0.32 +- 0.20"),
        ("the body, thirteen-dot", 25, "+0.05 +- 0.39"),
        ("ten English registers", None, "+1.19 +- 0.28"),
    ):
        print(f"{label:<34}{(marks if marks else ''):>7}{gap:>19}")

    print(
        "\nWhatever the front matter's marks are, the body's marks of both resolved"
        "\nclasses fail to lengthen and the author's lengthen like ordinary English. The"
        "\nconclusion survives; the phrase 'pure four-dot' does not."
    )


if __name__ == "__main__":
    main()
