# ABOUTME: Tests whether the unsolved pages' clause marks space like genuine punctuation
# ABOUTME: by comparing words-between-marks against the LP's own SOLVED pages and a random null.
"""Are the '.' marks plaintext punctuation, or cipher machinery?

Two files here disagree and cannot both be right.

`quote-span-boundaries.md` measures that quoted spans align to the marks (8 of 14
edges, p = 1.5e-7) and are depleted inside them: the PLAINTEXT respects the marks.
`thirty-symbol-disk.md` reads the marks as machinery -- a 30th cell of a
size-mismatched disk -- and supports it with per-section homogeneity, uniform rune
contexts and near-exponential gaps. A content-independent machine cannot align with
quoted speech, so one of the two readings is wrong.

The gap evidence was measured in RUNES (`mark_thirty_symbol.py`, cv 0.91 against
1.0 for exponential). That test has little power: word lengths vary by a factor of
several, so rune gaps inherit that variance and drift toward cv 1 whatever the
underlying process does. Measured in WORDS the two readings separate cleanly:

  machinery     marks fall independently on word boundaries, so the number of words
                between marks is geometric -- mode at 1, cv ~ 1, many 1-2 word gaps
  punctuation   clause lengths in words, which are not geometric in any natural
                language: few very short clauses, cv well under 1

The reference is the LP's own solved pages. The transcription splits cleanly by
convention -- pages 0-14 use '.' for the clause delimiter, pages 15+ use the 4/10/13
dot glyphs, and NO page uses both -- and pages 0-14 are the solved section, where the
marks are known to sit at genuine English clause boundaries. Same book, same scribe,
same delimiter semantics, so the register objection that has bitten this project
before does not apply.

Registered before running:

  if the unsolved pages match the solved pages and both reject the random null,
      the marks are punctuation and `thirty-symbol-disk.md`'s machinery reading fails
  if the unsolved pages match the random null while the solved pages do not,
      the marks are machinery and the quote alignment needs another explanation
  if both match the random null,
      the test has no power and says nothing about either reading

    python mark_clause_lengths.py [--draws 20000]
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
CLAUSE = set(".④⑩⑬")
DRAWS = 20_000


def pages() -> list[str]:
    return MASTER.read_text().split("%")


def segments(page: str, clause: set[str] = CLAUSE) -> tuple[list[int], int]:
    """Words between clause marks on one page, and the page's word count.

    A word is a maximal run of runes, so every non-rune character ends one; that
    matches `lp_corpus.load_clean`'s tokenization. The run of words after the last
    mark is censored by the page end and is dropped rather than counted short.
    """
    out: list[int] = []
    words = held = 0
    in_word = False
    for ch in page:
        if RUNE.match(ch):
            in_word = True
            continue
        if in_word:
            words += 1
            held += 1
            in_word = False
        if ch in clause:
            out.append(held)
            held = 0
    if in_word:
        words += 1
    return out, words


def collect(group: list[str], clause: set[str] = CLAUSE) -> tuple[list[int], int, int]:
    """Segments, total words and total marks over a group of pages."""
    segs: list[int] = []
    words = marks = 0
    for p in group:
        s, w = segments(p, clause)
        segs += s
        words += w
        marks += len(s)
    return segs, words, marks


def describe(name: str, segs: list[int]) -> None:
    if not segs:
        print(f"{name:<24} no segments")
        return
    mean = statistics.mean(segs)
    sd = statistics.pstdev(segs)
    short = sum(1 for x in segs if x <= 2) / len(segs)
    print(
        f"{name:<24}{len(segs):>7}{mean:>9.2f}{statistics.median(segs):>9.1f}"
        f"{sd:>9.2f}{sd / mean if mean else 0:>8.2f}{short:>10.1%}"
    )


def random_null(
    group: list[str], rng: random.Random, clause: set[str] = CLAUSE
) -> list[int]:
    """The machinery reading: the same marks scattered over the same word boundaries.

    Each page keeps its own word count and mark count, so page structure and the
    overall rate are held fixed and only the PLACEMENT is randomised.
    """
    segs: list[int] = []
    for p in group:
        s, w = segments(p, clause)
        if not s or w < 2:
            continue
        cuts = sorted(rng.sample(range(1, w), min(len(s), w - 1)))
        previous = 0
        for c in cuts:
            segs.append(c - previous)
            previous = c
    return segs


def main() -> None:
    draws = DRAWS
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    allp = pages()
    solved = [p for p in allp if "." in p]
    unsolved = [p for p in allp if any(c in p for c in "④⑩⑬")]
    print(f"solved pages {len(solved)}, unsolved pages {len(unsolved)}\n")

    s_seg, s_words, s_marks = collect(solved)
    u_seg, u_words, u_marks = collect(unsolved)
    print(
        f"solved:   {s_words:,} words, {s_marks} marks, 1 per {s_words / s_marks:.1f} words"
    )
    print(
        f"unsolved: {u_words:,} words, {u_marks} marks, 1 per {u_words / u_marks:.1f} words\n"
    )

    rng = random.Random(3301)
    print(
        f"{'group':<24}{'n':>7}{'mean':>9}{'median':>9}{'sd':>9}{'cv':>8}{'<=2 wd':>10}"
    )
    describe("solved (known English)", s_seg)
    describe("unsolved", u_seg)
    describe("random null, solved", random_null(solved, rng))
    describe("random null, unsolved", random_null(unsolved, rng))

    print("\npermutation tests, cv and the short-segment fraction as statistics:")
    for name, group, segs in (
        ("solved", solved, s_seg),
        ("unsolved", unsolved, u_seg),
    ):
        obs_cv = statistics.pstdev(segs) / statistics.mean(segs)
        obs_short = sum(1 for x in segs if x <= 2) / len(segs)
        cv_hits = short_hits = 0
        for _ in range(draws):
            null = random_null(group, rng)
            if statistics.pstdev(null) / statistics.mean(null) <= obs_cv:
                cv_hits += 1
            if sum(1 for x in null if x <= 2) / len(null) <= obs_short:
                short_hits += 1
        print(
            f"  {name:<10} cv {obs_cv:.2f}  p(cv this low or lower) "
            f"{(cv_hits + 1) / (draws + 1):.4f}"
            f"   short {obs_short:.1%}  p {(short_hits + 1) / (draws + 1):.4f}"
        )

    print("\nper glyph, unsolved pages (are the three marks one thing?):")
    for glyph in "④⑩⑬":
        describe(f"  only {glyph}", collect(unsolved, {glyph})[0])


if __name__ == "__main__":
    main()
