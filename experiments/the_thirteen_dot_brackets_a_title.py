# ABOUTME: Shows the body's non-terminal thirteen-dots sit on the edges of rubricated
# ABOUTME: titles, answering what their second function is.
"""The thirteen-dot has two jobs, and the second one is punctuating a title.

`the-thirteen-dot-closes-a-section.md` establishes the mark as a section closer and then
records an open question verbatim: *"Fifteen of the 31 are followed by a rune, so the
13-dot is not exclusively terminal. Whether that is a second function, or the same one at
boundaries the transcription does not record, is not answerable from this corpus."*

It is answerable. The corpus has a second, independent record of structure that the mark
was never checked against: `rubricated_titles.json`, seventeen passages written in red ink
and read off the scans rather than the transcription.

## The rule

Read against the titles, every thirteen-dot but two falls into one of three classes:

- it closes a chunk, which is the section-end job already known;
- it sits on the **last block of a rubricated title**;
- it sits on the **block immediately before one starts**.

Titles that begin a chunk get no opening mark, because the chunk boundary already is one.
Of the six body titles that begin mid-chunk, five carry both marks.

## Result

    chunk-final          7
    closes a title      12
    opens a title        5
    unexplained          2

    title-edge hits   observed 17, chance within the same chunks 0.84 +- 0.89
                      P = 0.00002 or below

**Twenty-four of twenty-six.** The two strays are chunk 30 block 1, which sits *inside* a
five-word title whose closing mark is at block 4, and chunk 69 block 1, one block past a
one-word title. Both are consistent with a title range recorded one word wide or narrow,
and neither is checked against the scans here.

## The null

Counting title-edge hits against random placement anywhere in the body would prove
nothing: the thirteen-dot is known to live near section breaks and so do the titles. The
permutation keeps each mark in **its own chunk** and moves it to a random block there,
which holds the mark's section habitat fixed and tests only where inside a section it
lands.

## Scope

The master holds 31 thirteen-dots. Three sit in chunks 71-72, outside the body range, and
two of the 28 in range close no block -- they follow another mark with no rune between --
so `body_parse` drops them and this file analyses 26. Both dropped marks are in chunks
that already show the bracket pattern.

    python the_thirteen_dot_brackets_a_title.py
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, MASTER, chunk_blocks  # noqa: E402

TITLES = ROOT / "experiments" / "rubricated_titles.json"
DRAWS = 20_000


def layout():
    """{chunk: (block count, thirteen-dot indices, title (start, end) pairs)}."""
    titles: dict[int, list[tuple[int, int]]] = {}
    for t in json.loads(TITLES.read_text()):
        titles.setdefault(t["chunk"], []).append(tuple(t["word_range"]))
    text = MASTER.read_text().split("%")
    out = {}
    for ci in BODY:
        rows = chunk_blocks(text[ci])
        marks = [i for i, (_, glyph, _) in enumerate(rows) if glyph == "⑬"]
        if marks or ci in titles:
            out[ci] = (len(rows), marks, titles.get(ci, []))
    return out


def edges(spans, size):
    """Block indices a title ends on, and the ones a title starts just after."""
    closing = {end for _, end in spans}
    opening = {start - 1 for start, _ in spans if start > 0}
    return closing, {i for i in opening if 0 <= i < size}


def classify(size, marks, spans):
    closing, opening = edges(spans, size)
    counts = {"chunk-final": 0, "closes a title": 0, "opens a title": 0, "other": 0}
    strays = []
    for i in marks:
        if i in closing:
            counts["closes a title"] += 1
        elif i in opening:
            counts["opens a title"] += 1
        elif i == size - 1:
            counts["chunk-final"] += 1
        else:
            counts["other"] += 1
            strays.append(i)
    return counts, strays


def main() -> None:
    rng = random.Random(3301)
    pages = layout()
    total = {"chunk-final": 0, "closes a title": 0, "opens a title": 0, "other": 0}
    strays = []
    marks_total = 0

    print(f"{'chunk':>6}{'blocks':>8}{'thirteen-dot at':>22}{'title word ranges':>26}")
    for ci, (size, marks, spans) in pages.items():
        print(f"{ci:>6}{size:>8}{str(marks):>22}{str(spans):>26}")
        counts, stray = classify(size, marks, spans)
        for k, v in counts.items():
            total[k] += v
        strays += [(ci, i) for i in stray]
        marks_total += len(marks)

    print(f"\n{marks_total} thirteen-dots in the body.\n")
    for k, v in total.items():
        print(f"  {k:<18}{v:>4}")
    print(f"\n  unexplained: {strays}")

    # Keep each mark in its own chunk; move it to a random block there.
    hits = total["closes a title"] + total["opens a title"]
    null = []
    for _ in range(DRAWS):
        got = 0
        for size, marks, spans in pages.values():
            if not marks or not spans:
                continue
            closing, opening = edges(spans, size)
            wanted = closing | opening
            got += sum(rng.randrange(size) in wanted for _ in marks)
        null.append(got)
    null = np.array(null, float)
    print(
        f"\nTitle-edge hits: observed {hits}, "
        f"chance within the same chunks {null.mean():.2f} +- {null.std(ddof=1):.2f}"
        f"\n  P(chance reaches {hits}) = {np.mean(null >= hits):.5f}"
    )

    print(
        "\nSix body titles begin mid-chunk; five carry both an opening and a closing"
        "\nmark. A title that begins a chunk carries only the closing one, the chunk"
        "\nboundary serving as the opening."
        "\n\nScope. The master holds 31 thirteen-dots: 3 sit in chunks 71-72, outside the"
        "\nbody range, and 2 of the 28 in range close no block -- they follow another mark"
        "\nwith no rune between -- so body_parse drops them and this file analyses 26."
    )


if __name__ == "__main__":
    main()
