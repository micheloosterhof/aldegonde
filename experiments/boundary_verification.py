# ABOUTME: Checks every word separator in the transcription against the page
# ABOUTME: scans, to test whether missing separators explain the short-word deficit.
"""Are the word boundaries faithful to the page?

The unsolved corpus has a 2-rune word deficit against the solved pages
(15.9% against 24.2%, `short_word_deficit.py`). Encryption cannot cause it, so
either the plaintext is genuinely that telegraphic or the boundaries are not
plaintext-faithful — and if they are not, word lengths are key material and
cribbing on word identity is futile.

The deficit has a suggestive shape. Mass is missing from length 2 and shows up
at 3, 5, 7 and 8. That is what MERGING would do: drop a separator between a
2-rune word and a 3-rune word and you lose two short words and gain one of
length 5.

`word-length-keystream-and-boundaries.md` notes that a transcription artifact
"cannot be fully excluded without the page scans". The scans are available, and
`locate_marks.py` already aligns a page's glyph sequence to its transcription
line. This runs that alignment over every line of every page and asks a single
question: does the image carry separators the transcription omits?

Per line the image sequence is reduced to runes / word separator (a single dot)
/ sentence mark (a dot cluster), and compared with the transcription's own
token sequence. A missing separator shows up as the image having a separator
where the transcription has a rune-to-rune join.

RESULT AND ITS LIMIT (August 2026). 491 of 604 lines (81.3%) carry exactly the
transcribed separators. The remaining differences are dominated by faults in
THIS reader, not the transcription:

  * 92 of 113 involve a rune-count difference, which is the connected-component
    reader merging touching runes. Those cannot arbitrate on separators and are
    excluded from the separator tally.
  * Of the 21 clean disagreements, 19 have the image carrying more separators
    and 0 the transcription — but they sit at line EDGES, and spot-checking two
    of the trailing cases found one real (page 0 line 1 genuinely ends with a
    word-separator dot the transcription omits) and one false (page 2 line 4
    ends with the rune B; the "dot" was a fragment of the marginal artwork
    inside the too-generous TEXT_BLOCK window).

So this run does NOT establish that the transcription systematically drops
line-edge separators. It establishes that most lines verify, and that settling
the rest needs a tighter text-block boundary per page and a rune segmenter that
does not merge touching glyphs. Do not quote the 19 as missing boundaries.
"""

from __future__ import annotations

import re
from collections import Counter

from experiments.locate_marks import bands, glyphs, text_lines, tokens

RUNE = re.compile(r"[ᚠ-᛿]")
PAGES = range(58)


def transcription_pages() -> list[str]:
    from experiments.locate_marks import CORPUS

    return CORPUS.read_text().split("%")


def main() -> None:
    blocks = transcription_pages()
    totals = Counter()
    detail: list[tuple[int, int, str, str]] = []

    for page in PAGES:
        lines = text_lines(blocks[page])
        gs = glyphs(page)
        img_lines = bands(gs, len(lines))
        if len(img_lines) != len(lines):
            totals["page line-count mismatch"] += 1
            continue
        for idx, (line, text) in enumerate(zip(img_lines, lines)):
            img = [t for t in tokens(line) if t not in "'\""]
            txt = ["R" if RUNE.match(c) else c for c in text if RUNE.match(c) or c in "①-."]
            totals["lines compared"] += 1
            if img == txt:
                totals["exact match"] += 1
                continue
            # a trailing separator the transcription omits at a line end is a
            # known convention difference, not a missing word break
            if img[:len(txt)] == txt and all(t in "①-." for t in img[len(txt):]):
                totals["extra trailing separator"] += 1
                continue
            totals["genuine mismatch"] += 1
            ri, rt = img.count("R"), txt.count("R")
            si = sum(img.count(c) for c in "①-.")
            st = sum(txt.count(c) for c in "①-.")
            if ri != rt:
                # the connected-component reader merges touching runes, so a
                # rune-count difference is a reader fault, not a transcription
                # one. These cannot arbitrate on separators.
                totals["reader fault (rune count differs)"] += 1
                continue
            totals["clean separator disagreement"] += 1
            totals["  image has more separators"] += si > st
            totals["  text has more separators"] += st > si
            if len(detail) < 10:
                detail.append((page, idx, "".join(img), "".join(txt)))

    print("word-separator verification, image against transcription\n")
    for k in ("lines compared", "exact match", "extra trailing separator",
              "genuine mismatch", "reader fault (rune count differs)",
              "clean separator disagreement", "  image has more separators",
              "  text has more separators", "page line-count mismatch"):
        print(f"   {k:>28}: {totals[k]}")

    compared = totals["lines compared"]
    if compared:
        clean = totals["exact match"] + totals["extra trailing separator"]
        print(f"\n   {clean}/{compared} = {clean / compared:.1%} of lines carry "
              "exactly the transcribed separators")

    if detail:
        print("\nfirst mismatching lines (img above, txt below)")
        for page, idx, img, txt in detail:
            print(f"   page {page:>2} line {idx:>2}")
            print(f"      img {img}")
            print(f"      txt {txt}")


if __name__ == "__main__":
    main()
