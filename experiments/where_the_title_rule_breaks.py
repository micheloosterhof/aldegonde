# ABOUTME: Audits every rubricated title against the thirteen-dot bracket rule and turns
# ABOUTME: the rule's three exceptions into predictions checkable against the scans.
"""The bracket rule read backwards: does every title carry its marks?

`the_thirteen_dot_brackets_a_title.py` reads from the marks outward -- 24 of 26
thirteen-dots sit at a title edge or close a chunk. That direction can be satisfied by a
rule that fires rarely. This file reads the other way, from the red ink outward, and asks
whether every title is marked.

## Result

    chunk    range  words   closer   before   text
       15   (0, 1)      2        ⑬   ^chunk   SHEOGMIAF SYENGC
       18   (0, 2)      3        ⑬   ^chunk   LJ EOHNGCTHTAEJTXH TUOE
       18 (22, 22)      1        ⑬        ⑬   PDTH
       21 (15, 18)      4        ⑬        ⑬   ATXB M GIASB XEO
       22 (45, 49)      5        ⑬        ⑬   DO OETTHAE CWJ XEA GEAM
       23   (0, 1)      2        ①   ^chunk   XIXM UXMCTHPOB
       30   (0, 4)      5        ⑬   ^chunk   FULM AEAYOEA LUNGN CU BNTFNG
       38   (0, 3)      4        ⑬   ^chunk   UA WNGGXDG IBI EOTBIY
       42   (0, 2)      3        ⑬   ^chunk   MPY LSOAAEHLEEOIML LSCP
       48   (0, 1)      2        ⑬   ^chunk   DEO XCFIAWHG
       48 (23, 24)      2        ⑬        ⑬   NGTHEO IFCOEEO
       54 (26, 26)      1        ⑬        ⑬   IACS
       55   (0, 1)      2        ①   ^chunk   FNM YGDAEH
       68 (28, 39)     12        ⑬        ④   TPWEOS WBEOTH NHGJ RIADIATHAIEOAEX...
       69   (0, 0)      1        ①   ^chunk   A

**Twelve of fifteen body titles are closed by a thirteen-dot.** All six titles that begin
mid-chunk are closed by one, and five of those six are opened by one as well.

## The three exceptions have one shape

Every title the rule misses begins a chunk and runs one or two words: chunks 23, 55 and
69. Chunks 23 and 55 carry no thirteen-dot anywhere, so there the mark is absent from the
whole page rather than from the title. Chunk 69 does carry one, at word 1, which is the
stray the next section is about.

## Two predictions about the red ink, not about the ciphertext

The bracket rule leaves exactly two thirteen-dots unexplained, and each implies a specific
correction to the title record. Both are checkable against the scans and neither is
checked here.

- **Chunk 69.** The title is recorded as word 0 alone and the thirteen-dot sits at word 1.
  If the rule holds, the red ink runs to word 1 and the record is one word short.
- **Chunk 30.** The title is recorded as words 0-4, closed by a thirteen-dot at word 4,
  and a second thirteen-dot sits at word 1 *inside* it. If the rule holds, this is two
  titles -- words 0-1 and 2-4 -- not one.

Either confirmation strengthens the rule to 26 of 26. A refutation -- red ink that
genuinely spans a thirteen-dot -- breaks it, because a mark inside a title is not a
bracket.

## What this does not show

Nothing about the four-dot. Chunk 68's title is preceded by a four-dot, which is the only
four-dot adjacent to a title edge in the book, and one instance is not a pattern.

    python where_the_title_rule_breaks.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, MASTER, chunk_blocks  # noqa: E402

TITLES = ROOT / "experiments" / "rubricated_titles.json"


def rows_for(chunk_index, text):
    return chunk_blocks(text[chunk_index])


def main() -> None:
    titles = sorted(json.loads(TITLES.read_text()), key=lambda t: t["chunk"])
    text = MASTER.read_text().split("%")

    print(f"{'chunk':>6}{'range':>10}{'words':>7}{'closer':>9}{'before':>9}   text")
    closed, opened, mid, unmarked = 0, 0, 0, []
    for t in titles:
        ci = t["chunk"]
        if ci not in BODY:
            continue
        rows = rows_for(ci, text)
        start, end = t["word_range"]
        closer = rows[end][1] if end < len(rows) else "?"
        before = rows[start - 1][1] if start > 0 else "^chunk"
        print(
            f"{ci:>6}{str((start, end)):>10}{t['words']:>7}{closer:>9}{before:>9}"
            f"   {t['text'][:34]}"
        )
        closed += closer == "⑬"
        if start > 0:
            mid += 1
            opened += before == "⑬"
        if closer != "⑬":
            unmarked.append((ci, (start, end), t["words"]))

    total = sum(1 for t in titles if t["chunk"] in BODY)
    print(f"\n{closed} of {total} body titles are closed by a thirteen-dot.")
    print(f"{opened} of the {mid} that begin mid-chunk are opened by one as well.\n")
    print("The exceptions:")
    for ci, span, words in unmarked:
        marks = [
            i for i, (_, glyph, _) in enumerate(rows_for(ci, text)) if glyph == "⑬"
        ]
        print(
            f"  chunk {ci}, words {span}, {words} word(s), begins the chunk;"
            f" thirteen-dots in that chunk: {marks or 'none'}"
        )
    print(
        "\nEvery exception begins a chunk and runs one or two words. Two of the three"
        "\nsit on a page with no thirteen-dot at all, so there the mark is missing from"
        "\nthe page rather than from the title. The third, chunk 69, has one at word 1."
    )


if __name__ == "__main__":
    main()
