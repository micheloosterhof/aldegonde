# ABOUTME: Tests whether the body's marks sit at the edges of the rubricated titles, which
# ABOUTME: the ink colour locates independently of the text, and finds the thirteen-dot does.
"""The red ink locates seventeen structural boundaries. The thirteen-dot mark is on them.

Two readings of the sentence-mark anomaly are still standing
(`sentences-do-not-end-long.md`): the spans between marks are transposed sentences, or
the marks are not sentence marks at all. Everything tried so far has had to infer where
the text's real boundaries are from the text itself. The rubrication does not: a section
title is written in red, and `rubrication-crib-candidates.md` reads the red runes off the
page scans and records which words each title covers. **Those are structural boundaries
fixed by ink, not by any statistic of the corpus**, and no mark was used to find them --
`rubrication_cribs.py` locates a span from the red rune count and word lengths alone.

If the marks punctuate the text, they must agree with those seventeen units.

## Result

**They do, and one glyph does nearly all of it.**

| | observed | at an ordinary boundary | P |
|---|---|---|---|
| mid-page titles closed by a thirteen-dot | 6 / 6 | 0.0098 | 9e-13 |
| mid-page titles opened by a thirteen-dot | 5 / 6 | 0.0098 | 5e-10 |
| mid-page titles bounded by any mark | 6 / 6 both sides | 0.0592 | 4e-08 |
| page-opening titles after a page ending in a mark | 11 / 11 | 13 of 57 pages | 4e-10 |

The sixth mid-page title is opened by a four-dot rather than a thirteen-dot; it is the
twelve-word span on page 53, which the census records as four adjacent red runs, so it is
the one entry where "one title" is least certain.

**Eleven of the body's thirteen page-final marks are at a title.** The mark that ends a
page is, far more often than not, there because a title starts the next one.

This is independent physical confirmation of `the-thirteen-dot-closes-a-section.md`,
which had only the text to go on.

## Why it matters to the open fork

The marks are not unrelated to the text's structure; the ink says they mark it. So the
reading "the marks fall in positions unrelated to the syntax" is damaged, and the
sentence-final anomaly gets sharper rather than softer: the block before a mark is the
block before a real boundary, and it still does not lengthen.

**But the glyph that carries the anomaly is not the glyph the titles pin.** The
thirteen-dot bounds sections and reads +0.05 +- 0.39 on the final-block gap; the four-dot
carries the whole anomaly at -0.32 +- 0.20 (`what_the_marks_are.py`). The rubrication
anchors ⑬ and says nothing about ④, so the anomaly is untouched and now better located.

## Two conventions, and the page break

`①` is the one-dot word separator, not a mark -- it appears 3,380 times. The marks are
④ ⑬ ③ ⑩ ㉓ on the circled-convention chunks and `.` on the ASCII ones. Eleven of the
seventeen titles start at word 0 of their chunk, and 46 of the 57 page breaks fall in the
middle of a word (`page-breaks-cut-blocks.md`), so for those the boundary before the title
is the end of the *previous* chunk. The two strata get different nulls, because a
chunk-final position is not an ordinary word boundary.

    python do_the_marks_bound_the_titles.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TITLES = ROOT / "experiments" / "rubricated_titles.json"
SEPARATOR = {"①", "-"}  # one dot: an ordinary word boundary, not a mark
MARKS = set("④⑬③⑩㉓.")
BODY = range(15, 73)


def chunk_words(chunk: str) -> list[tuple[int, str]]:
    """(word length, the separator that closed it) in the order the titles index.

    The titles were indexed after splitting the master on '%', so this keeps that
    convention: line breaks are not boundaries, every other separator is.
    """
    out: list[tuple[int, str]] = []
    n = 0
    for ch in chunk:
        if RUNE.match(ch):
            n += 1
        elif ch in "/\n":
            continue
        elif ch in c3301.WORD_BOUNDARY and n:
            out.append((n, ch))
            n = 0
    if n:
        out.append((n, "%"))
    return out


def preceding(chunks, chunk_id: int, index: int) -> str:
    """The separator closing the word before `index`, carried across the page break."""
    if index > 0:
        return chunks[chunk_id][index - 1][1]
    previous = chunks.get(chunk_id - 1)
    return previous[-1][1] if previous else "%"


def main() -> None:
    chunks = {i: chunk_words(c) for i, c in enumerate(MASTER.read_text().split("%"))}
    titles = json.loads(TITLES.read_text())
    print(f"{len(titles)} rubricated titles, {sum(t['words'] for t in titles)} words.\n")

    print(f"{'title':<32}{'before it':>12}{'after it':>12}{'opens a page':>15}")
    mid, initial = [], []
    for t in titles:
        a, b = t["word_range"]
        words = chunks[t["chunk"]]
        if b >= len(words):
            continue
        before, after = preceding(chunks, t["chunk"], a), words[b][1]
        (initial if a == 0 else mid).append((t, before, after))
        label = f"page {t['page']:>2}, words {a}-{b}"
        print(f"{label:<32}{before:>12}{after:>12}{'yes' if a == 0 else '':>15}")

    bounds = [s for i in BODY if chunks.get(i) for _, s in chunks[i]]
    for glyph, name in (("\u246c", "a thirteen-dot"), (None, "any mark")):
        def carries(s, glyph=glyph):
            return s == glyph if glyph else s in MARKS

        rate = sum(1 for s in bounds if carries(s)) / len(bounds)
        print(f"\n{name} at an ordinary body word boundary: {rate:.4f}")
        for label, seps in (
            ("mid-page titles opened by it", [b for _, b, _ in mid]),
            ("mid-page titles closed by it", [a for _, _, a in mid]),
        ):
            hits = sum(1 for s in seps if carries(s))
            p = stats.binom.sf(hits - 1, len(seps), rate)
            print(f"  {label}: {hits}/{len(seps)}   P = {p:.2e}")

    ends = [chunks[i][-1][1] for i in BODY if chunks.get(i)]
    marked = sum(1 for s in ends if s in MARKS)
    hits = sum(1 for _, b, _ in initial if b in MARKS)
    p = stats.hypergeom.sf(hits - 1, len(ends), marked, len(initial))
    print(
        f"\nPages whose last word carries a mark: {marked} of {len(ends)}."
        f"\n  page-opening titles preceded by one: {hits}/{len(initial)}   P = {p:.2e}"
        f"\n  so {hits} of the body's {marked} page-final marks are at a title."
    )


if __name__ == "__main__":
    main()
