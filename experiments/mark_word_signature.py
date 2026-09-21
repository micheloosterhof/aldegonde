# ABOUTME: Splits the mark word-length signature by glyph, using the solved pages to
# ABOUTME: calibrate what a real clause boundary does before asking whether 4-dot does it.
"""Does any single mark glyph carry the word-length signature of a clause boundary?

`word-length-keystream-and-boundaries.md` tests the pooled '.' mark for a
sentence-final word-length signature and finds none (z = -1.21). That test pooled the
glyphs, and `marks-are-not-clause-punctuation.md` shows the glyphs are not one thing:
4-dot and 13-dot depart from random placement in opposite directions, and 13-dot sits
at a line end half the time. Pooling a linguistic glyph with a layout glyph dilutes
whatever the first one carries.

So ask again per glyph, and calibrate first. The solved pages (0-14) use '.' at known
English clause boundaries, so they say how big the effect should be and whether a
sample of 139 could see it. Without that step a null here would mean nothing, which is
the trap the pooled test fell into.

Two statistics, both permutation-tested by reassigning which boundaries carry a mark
while holding each page's mark count fixed:

  before   length of the word immediately preceding the mark
  after    length of the word immediately following it

    python mark_word_signature.py [--draws 20000]
"""

from __future__ import annotations

import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
DRAWS = 20_000


def parse(page: str) -> tuple[list[int], list[str]]:
    """Word lengths on a page, and the boundary glyph that follows each word.

    A word is a maximal run of runes. The glyph recorded for a word is the first
    boundary character after it, so a mark is attached to the word it follows.
    """
    lengths: list[int] = []
    glyphs: list[str] = []
    run = 0
    pending = True
    for ch in page:
        if RUNE.match(ch):
            run += 1
            pending = True
            continue
        if run:
            lengths.append(run)
            glyphs.append(ch)
            run = 0
            pending = False
        elif not pending and glyphs and glyphs[-1] not in ".④⑩⑬" and ch in ".④⑩⑬":
            glyphs[-1] = ch
    if run:
        lengths.append(run)
        glyphs.append("")
    return lengths, glyphs


def observed(group: list[str], marks: set[str]) -> tuple[float, float, int, float]:
    """Mean word length before and after a mark, the mark count, and the page mean."""
    before: list[int] = []
    after: list[int] = []
    allw: list[int] = []
    for page in group:
        lengths, glyphs = parse(page)
        allw += lengths
        for i, g in enumerate(glyphs):
            if g in marks:
                before.append(lengths[i])
                if i + 1 < len(lengths):
                    after.append(lengths[i + 1])
    return (
        statistics.mean(before) if before else 0.0,
        statistics.mean(after) if after else 0.0,
        len(before),
        statistics.mean(allw),
    )


def permute(
    group: list[str], marks: set[str], rng: random.Random
) -> tuple[float, float]:
    """The same counts of marks, reassigned to random boundaries on each page."""
    before: list[int] = []
    after: list[int] = []
    for page in group:
        lengths, glyphs = parse(page)
        n = sum(1 for g in glyphs if g in marks)
        if not n or len(lengths) < 2:
            continue
        spots = rng.sample(range(len(lengths)), min(n, len(lengths)))
        for i in spots:
            before.append(lengths[i])
            if i + 1 < len(lengths):
                after.append(lengths[i + 1])
    return (
        statistics.mean(before) if before else 0.0,
        statistics.mean(after) if after else 0.0,
    )


def report(
    name: str,
    group: list[str],
    marks: set[str],
    rng: random.Random,
    draws: int,
    calibration: tuple[float, float] | None = None,
) -> tuple[float, float] | None:
    """One row. With `calibration`, also the z a solved-sized effect would have given.

    The null column is what makes a null result mean anything: the solved pages fix
    how large a real clause-boundary effect is, so the same effect can be projected
    onto this group's sample size and compared against what was actually seen.
    """
    b, a, n, mean = observed(group, marks)
    if not n:
        print(f"{name:<26} no marks")
        return None
    nb = []
    na = []
    for _ in range(draws):
        pb, pa = permute(group, marks, rng)
        nb.append(pb)
        na.append(pa)
    sd_b = statistics.pstdev(nb) or 1
    zb = (b - statistics.mean(nb)) / sd_b
    za = (a - statistics.mean(na)) / (statistics.pstdev(na) or 1)
    want = ""
    if calibration:
        effect, _ = calibration
        want = f"{effect / sd_b:>+12.1f}"
    print(f"{name:<26}{n:>6}{mean:>8.2f}{b:>9.2f}{zb:>+8.2f}{a:>9.2f}{za:>+8.2f}{want}")
    return (b - mean, a - mean)


def main() -> None:
    draws = DRAWS
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    allp = MASTER.read_text().split("%")
    solved = [p for p in allp if "." in p]
    unsolved = [p for p in allp if any(c in p for c in "④⑩⑬")]

    rng = random.Random(3301)
    print(
        "word length at a mark, against reassigning the same marks to random boundaries\n"
    )
    print(
        f"{'group':<26}{'marks':>6}{'corpus':>8}{'before':>9}{'z':>8}{'after':>9}{'z':>8}"
        f"{'z if real':>12}"
    )
    cal = report("solved '.' (calibration)", solved, {"."}, rng, draws)
    report("unsolved, pooled", unsolved, {"④", "⑩", "⑬"}, rng, draws, cal)
    report("unsolved, 4-dot", unsolved, {"④"}, rng, draws, cal)
    report("unsolved, 13-dot", unsolved, {"⑬"}, rng, draws, cal)
    print(
        "\n'z if real' is the z this group would have shown had the solved pages'"
        f"\nclause-final effect (+{cal[0] if cal else 0.0:.2f} runes) been present at its own sample size."
    )


if __name__ == "__main__":
    main()
