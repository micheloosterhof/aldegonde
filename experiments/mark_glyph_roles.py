# ABOUTME: Identifies what each mark glyph marks by testing co-location with the
# ABOUTME: transcription's own paragraph delimiter; 13-dot is paragraph-associated, 4-dot is not.
"""What are the 4-dot and 13-dot marks actually marking?

`marks-are-not-clause-punctuation.md` establishes that the two glyphs are not one
thing -- they depart from random placement in opposite directions, only the 13-dot
mark clusters and sits at line ends, and only the 13-dot mark's per-section rate is
inhomogeneous. That says they differ without saying what either one is.

The transcription carries an independent structural delimiter, `&` for paragraph, put
there by the transcriber from the page layout rather than from any cipher reading. If
a mark glyph is structural it should track `&`; if it belongs to the cipher or the
clause system it should not.

Two measurements, the second a sharpening of the first:

  distance   rune distance from each mark to the nearest '&' on its page, against
             the same count of marks placed at random rune positions on that page
  adjacency  how often a mark is the immediate neighbour of a '&' in the character
             stream, against the '&' share of all boundaries

    python mark_glyph_roles.py [--draws 4000]
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
GLYPHS = "④⑬"
DRAWS = 4000


def unsolved_pages() -> list[str]:
    return [p for p in MASTER.read_text().split("%") if any(c in p for c in GLYPHS)]


def positions(page: str, glyph: str) -> tuple[list[int], list[int], int]:
    """Rune index of each `glyph`, of each '&', and the page's rune count."""
    marks: list[int] = []
    amps: list[int] = []
    n = 0
    for ch in page:
        if RUNE.match(ch):
            n += 1
        elif ch == glyph:
            marks.append(n)
        elif ch == "&":
            amps.append(n)
    return marks, amps, n


def distance_test(pages: list[str], glyph: str, rng: random.Random, draws: int):
    """Median distance to the nearest paragraph delimiter, and its null."""
    observed: list[int] = []
    for page in pages:
        marks, amps, _n = positions(page, glyph)
        if not amps:
            continue
        observed += [min(abs(m - a) for a in amps) for m in marks]
    if not observed:
        return None
    nulls = []
    for _ in range(draws):
        drawn: list[int] = []
        for page in pages:
            marks, amps, n = positions(page, glyph)
            if not amps or not marks or n < 2:
                continue
            drawn += [
                min(abs(rng.randrange(n) - a) for a in amps) for _ in range(len(marks))
            ]
        if drawn:
            nulls.append(statistics.median(drawn))
    obs = statistics.median(observed)
    p = (sum(1 for x in nulls if x <= obs) + 1) / (len(nulls) + 1)
    return len(observed), obs, statistics.median(nulls), p


def adjacency(text: str, glyph: str) -> tuple[int, int]:
    """How often `glyph` is the immediate neighbour of a '&', ignoring layout chars."""
    chars = [c for c in text if c not in "\n/"]
    hits = total = 0
    for i, ch in enumerate(chars):
        if ch != glyph:
            continue
        total += 1
        left = chars[i - 1] if i else ""
        right = chars[i + 1] if i + 1 < len(chars) else ""
        if "&" in (left, right):
            hits += 1
    return hits, total


def main() -> None:
    draws = DRAWS
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    text = MASTER.read_text()
    pages = unsolved_pages()
    rng = random.Random(3301)

    print("distance to the nearest paragraph delimiter '&'\n")
    print(f"{'glyph':<8}{'marks':>7}{'median':>9}{'null':>9}{'p':>9}")
    for glyph in GLYPHS:
        got = distance_test(pages, glyph, rng, draws)
        if got:
            n, obs, null, p = got
            print(f"{glyph:<8}{n:>7}{obs:>9.1f}{null:>9.1f}{p:>9.4f}")

    boundaries = sum(1 for c in text if c in "①②③-.④⑩⑬&")
    share = text.count("&") / boundaries
    print(f"\nimmediate adjacency to '&'  ('&' is {share:.1%} of all boundaries)\n")
    print(f"{'glyph':<8}{'beside &':>10}{'total':>7}{'rate':>8}{'expected':>10}")
    for glyph in GLYPHS:
        hits, total = adjacency(text, glyph)
        print(
            f"{glyph:<8}{hits:>10}{total:>7}{hits / total:>8.0%}{total * share:>10.1f}"
        )
    amps = text.count("&")
    hits, _ = adjacency(text, "⑬")
    print(
        f"\n{hits} of the {amps} '&' delimiters carry a 13-dot mark ({hits / amps:.0%})"
    )


if __name__ == "__main__":
    main()
