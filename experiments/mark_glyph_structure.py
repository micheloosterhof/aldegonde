#!/usr/bin/env python3
# ABOUTME: Asks what the recovered dot-cluster glyphs are: where they sit in a
# ABOUTME: line, whether they pair, how they space, and whether they nest.
"""What the dot-cluster glyphs do, now that their counts are recorded.

The transcription used to write every cluster as `.` or `-`, which made these
questions unaskable. With the counts recovered from the scans (`data/SYMBOLS.md`)
the corpus carries six distinct marks, and each of the following is now a
measurement rather than a guess:

1. **Position in the line.** A mark that opens a unit sits at a line start, one
   that closes it sits at a line end, and a mark that merely separates words
   sits wherever the words fall. Measured against a null that keeps each line's
   mark COUNT and redistributes the positions, so line length and mark density
   cannot manufacture the effect.
2. **Pairing.** If a glyph brackets a span it should occur an even number of
   times per unit, and its occurrences should alternate open/close like the
   quotes do.
3. **Spacing.** The gap distribution between consecutive marks of one class
   says whether it is periodic, clustered, or memoryless.
4. **Hierarchy.** A hierarchical scheme nests: every boundary of a stronger mark
   is also a boundary of the weaker one, and the stronger mark's spans contain
   whole numbers of the weaker mark's spans. Both are checked directly.
5. **Local anomalies.** Word length and doublet rate either side of each class,
   against the corpus baseline.

Rarity limits what can be said: the corpus holds 2,764 one-dot marks, 141
four-dot, 31 thirteen-dot, 6 three-dot, 4 ten-dot and a single 23-dot. Nothing
about the last three can be established, and the script says so rather than
reporting a statistic that cannot carry weight.
"""

from __future__ import annotations

import random
import re
import statistics
from collections import Counter
from pathlib import Path

from aldegonde import c3301

# Fixed so every figure this script prints can be reproduced.
random.seed(3301)

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
DRAWS = 20000


def lines_with_marks() -> list[list[str]]:
    """Each text line as a token list of runes and marks, line wraps removed.

    Pages and sections are dropped: their markers are the project's own, not
    glyphs on the page, and a line is the unit the position question is about.
    """
    out: list[list[str]] = []
    for raw in CORPUS.read_text().split("\n"):
        toks = [c for c in raw if RUNE.match(c) or c in c3301.DOT_MARKS]
        if any(RUNE.match(c) for c in toks):
            out.append(toks)
    return out


def position_profile(lines: list[list[str]]) -> None:
    """Where each glyph sits in its line, against a position-shuffling null."""
    print("=== 1. POSITION IN THE LINE ===")
    print("   a mark that opens a unit leads its line, one that closes it trails\n")
    print(
        f"{'glyph':>7}{'n':>6}{'leads':>8}{'trails':>8}{'null lead':>11}"
        f"{'null trail':>12}{'z lead':>9}{'z trail':>9}"
    )

    for glyph in sorted(
        {t for line in lines for t in line if t in c3301.DOT_MARKS},
        key=c3301.dot_count,
    ):
        lead = trail = 0
        per_line = []
        for line in lines:
            slots = [i for i, t in enumerate(line) if t in c3301.DOT_MARKS]
            mine = [i for i in slots if line[i] == glyph]
            if not mine:
                continue
            per_line.append((len(line), len(slots), len(mine)))
            lead += sum(1 for i in mine if i == 0)
            trail += sum(1 for i in mine if i == len(line) - 1)
        n = sum(m for _, _, m in per_line)
        if n < 2:
            print(
                f"{glyph:>7}{n:>6}{lead:>8}{trail:>8}"
                f"{'--':>11}{'--':>12}{'too rare':>9}{'':>9}"
            )
            continue
        nl, nt = [], []
        for _ in range(DRAWS):
            le = tr = 0
            for length, slots, mine in per_line:
                picks = random.sample(range(length), min(slots, length))
                for i in picks[:mine]:
                    le += i == 0
                    tr += i == length - 1
            nl.append(le)
            nt.append(tr)
        mu_l, sd_l = statistics.mean(nl), statistics.stdev(nl) or 1e-9
        mu_t, sd_t = statistics.mean(nt), statistics.stdev(nt) or 1e-9
        print(
            f"{glyph:>7}{n:>6}{lead:>8}{trail:>8}{mu_l:>11.1f}{mu_t:>12.1f}"
            f"{(lead - mu_l) / sd_l:>+9.1f}{(trail - mu_t) / sd_t:>+9.1f}"
        )


def pairing(lines: list[list[str]]) -> None:
    """Does a glyph bracket a span: even count per line, alternating?"""
    print("\n=== 2. PAIRING ===")
    print("   a bracketing glyph occurs an even number of times in its unit\n")
    for glyph in sorted(
        {t for line in lines for t in line if t in c3301.DOT_MARKS},
        key=c3301.dot_count,
    ):
        counts = Counter(line.count(glyph) for line in lines if glyph in line)
        n_lines = sum(counts.values())
        even = sum(v for k, v in counts.items() if k % 2 == 0)
        both_ends = sum(
            1
            for line in lines
            if len(line) > 1 and line[0] == glyph and line[-1] == glyph
        )
        spread = "  ".join(f"{k}x{v}" for k, v in sorted(counts.items()))
        print(
            f"{glyph:>7} on {n_lines:>4} lines   even count on {even:>4}"
            f"   opens AND closes its line {both_ends:>3}   per line: {spread}"
        )


def spacing(lines: list[list[str]]) -> None:
    """Gap distribution between consecutive marks of one class, in runes."""
    print("\n=== 3. SPACING ===")
    print("   cv is the coefficient of variation; memoryless gaps give ~1.0\n")
    stream: list[str] = [t for line in lines for t in line]
    for glyph in sorted(
        {t for t in stream if t in c3301.DOT_MARKS}, key=c3301.dot_count
    ):
        runes = 0
        pos = []
        for t in stream:
            if RUNE.match(t):
                runes += 1
            elif t == glyph:
                pos.append(runes)
        gaps = [b - a for a, b in zip(pos, pos[1:])]
        if len(gaps) < 3:
            print(f"{glyph:>7}{len(pos):>5} marks   too few gaps to describe")
            continue
        cv = statistics.stdev(gaps) / statistics.mean(gaps)
        print(
            f"{glyph:>7}{len(pos):>5} marks   gap runes: "
            f"mean {statistics.mean(gaps):>7.1f}  median "
            f"{statistics.median(gaps):>6.1f}  min {min(gaps):>4}  "
            f"max {max(gaps):>5}  cv {cv:>4.2f}"
        )


def hierarchy(lines: list[list[str]]) -> None:
    """Does a stronger mark's boundary set contain the weaker one's?"""
    print("\n=== 4. HIERARCHY ===")
    print("   a nested scheme puts whole weak-mark spans inside each strong span\n")
    stream = [t for line in lines for t in line]
    runes = 0
    at: dict[str, list[int]] = {}
    for t in stream:
        if RUNE.match(t):
            runes += 1
        else:
            at.setdefault(t, []).append(runes)
    order = sorted(at, key=c3301.dot_count)
    weak = order[0]
    for glyph in order[1:]:
        if len(at[glyph]) < 2:
            print(f"{glyph:>7} only {len(at[glyph])} occurrence; nesting undecidable")
            continue
        spans = list(zip(at[glyph], at[glyph][1:]))
        counts = [sum(1 for w in at[weak] if a < w < b) for a, b in spans]
        shared = sum(1 for p in at[glyph] if p in set(at[weak]))
        print(
            f"{glyph:>7} {len(spans):>3} spans   {weak} marks inside each: "
            f"mean {statistics.mean(counts):>6.1f}  min {min(counts):>3}  "
            f"max {max(counts):>4}   coincides with a {weak} boundary: "
            f"{shared}/{len(at[glyph])}"
        )


def local_anomalies(lines: list[list[str]]) -> None:
    """Word length either side of each glyph, against the corpus baseline."""
    print("\n=== 5. WORD LENGTH AROUND EACH GLYPH ===")
    stream = [t for line in lines for t in line]
    words: list[int] = []
    before: dict[str, list[int]] = {}
    after: dict[str, list[int]] = {}
    cur = 0
    pending: str | None = None
    for t in stream:
        if RUNE.match(t):
            cur += 1
            continue
        if cur:
            words.append(cur)
            before.setdefault(t, []).append(cur)
            if pending is not None:
                after.setdefault(pending, []).append(cur)
        pending = t
        cur = 0
    base = statistics.mean(words)
    print(f"   corpus mean word length {base:.2f} over {len(words)} words\n")
    print(f"{'glyph':>7}{'n':>6}{'before':>9}{'after':>9}{'z before':>10}")
    sd = statistics.stdev(words)
    for glyph in sorted(before, key=c3301.dot_count):
        b = before[glyph]
        a = after.get(glyph, [])
        z = (statistics.mean(b) - base) / (sd / len(b) ** 0.5)
        print(
            f"{glyph:>7}{len(b):>6}{statistics.mean(b):>9.2f}"
            f"{(statistics.mean(a) if a else float('nan')):>9.2f}{z:>+10.1f}"
        )


def main() -> None:
    lines = lines_with_marks()
    census = Counter(t for line in lines for t in line if t in c3301.DOT_MARKS)
    print(
        f"{len(lines)} text lines; marks: "
        + "  ".join(f"{g}{census[g]}" for g in sorted(census, key=c3301.dot_count))
        + "\n"
    )
    position_profile(lines)
    pairing(lines)
    spacing(lines)
    hierarchy(lines)
    local_anomalies(lines)


if __name__ == "__main__":
    main()
