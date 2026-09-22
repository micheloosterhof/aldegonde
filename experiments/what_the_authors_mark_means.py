# ABOUTME: Aligns the author's runic koan against an independent English transcription to
# ABOUTME: verify directly what his dot mark corresponds to in ordinary punctuation.
"""The author's mark is the reference for everything here. Nobody had checked it.

Every result about the four-dot compares it with the author's own `.` mark: the
sentence-final lengthening of +1.39, the line-end rate of 0.471, the rank lift of +4.93.
All of it assumes his `.` is a sentence mark, which is reasonable and has never been
verified against anything outside the transcription.

It can be. `~/src/cicada-2014/stage06/index.transcribed` holds the koan of master pages
4-7 as **ordinary English with ordinary punctuation** -- periods, commas, question marks,
quotation marks and line breaks. The runic version of the same passage is recoverable:
those pages are Atbash-plus-three (`break_the_front_matter_pages.py`). So the two can be
aligned letter by letter and the marks read off.

## The alignment needs the digraph expansion

A rune maps to one English letter or **two** -- TH, EO, NG, AE, IA, EA. Indexing the
decrypted text one letter per rune drifts, and drifts further the more digraphs a passage
holds. On this passage it loses 35 letters over 813, enough to put every mark past the
first in the wrong place: the first attempt at this scored 17 of 22 marks as landing on no
punctuation at all.

Expanding each rune to its full English spelling and aligning the two letter streams with
a longest-matching-block match gives 99% coverage.

## Result: it is a sentence mark, and it is not a comma

| what the dot mark sits at | count |
|---|---|
| **a sentence end** | **18** |
| a line break | 4 |
| a comma | **0** |

| the converse | |
|---|---|
| English sentence ends carrying a dot mark | **18 of 21** |
| commas carrying one | **0 of 6** |

**The author's mark is a sentence mark.** Eighteen of his twenty-two marks sit at a period
or question mark, eighteen of the twenty-one sentence ends in the passage carry one, and
**not one of the six commas does**. The four at line breaks are the dialogue turns in the
koan, where the English transcription breaks the line rather than punctuating.

## What this underwrites

The author's `.` is the reference for every statement about the four-dot in this
directory -- the sentence-final lift of +1.39, the line-end rate of 0.471, the rank lift
of +4.93 -- and until now the claim that it marks sentences rested on it being a plausible
reading of an undeciphered convention. It is now checked against a source outside the
transcription entirely.

It also settles a question that was answered statistically.
`what_punctuation_class_is_the_four_dot.py` compares the four-dot against English
punctuation classes and finds the comma the **worst** fit of four, at -4.66 sigma. That
was a statistical argument about lengths; this is the convention itself. The author does
not mark commas, so a comma-level reading of the four-dot needs him to have changed
convention as well as everything else.

## Limits

One passage, 22 marks. The koan is dialogue, which is why four marks fall at line breaks;
a continuous prose passage might place them differently. And the check covers the author's
`.` on the ASCII-convention pages, not the body's circled numerals -- those are a different
section with no plaintext anywhere.

    python what_the_authors_mark_means.py
"""

from __future__ import annotations

import difflib
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from break_the_front_matter_pages import best_affine, runes_of  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TRANSCRIBED = Path.home() / "src" / "cicada-2014" / "stage06" / "index.transcribed"
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
KOAN_PAGES = (4, 5, 6, 7)
STRUCTURAL = '.,?!;:"\n'
WINDOW = 2


def runic_stream():
    """The decrypted koan as English letters, with the position of each dot mark."""
    chunks = MASTER.read_text().split("%")
    stream, marks = "", []
    for page in KOAN_PAGES:
        runes = runes_of(page)
        _, _, plain = best_affine(runes)[0]
        at = 0
        for ch in chunks[page]:
            if RUNE.match(ch):
                stream += ENGLISH[plain[at]]
                at += 1
            elif ch == ".":
                marks.append(len(stream))
    return stream, marks


def english_stream():
    text = TRANSCRIBED.read_text(errors="ignore").upper()
    stream, punctuation = "", {}
    for ch in text:
        if ch.isalpha():
            stream += ch
        elif ch in STRUCTURAL:
            punctuation.setdefault(len(stream), set()).add("NL" if ch == "\n" else ch)
    return stream, punctuation


def main() -> None:
    runic, marks = runic_stream()
    english, punctuation = english_stream()
    matcher = difflib.SequenceMatcher(None, runic, english, autojunk=False)
    mapping = {}
    for a, b, size in matcher.get_matching_blocks():
        for k in range(size):
            mapping[a + k] = b + k
    print(
        f"{len(runic)} decrypted letters against {len(english)} English letters;"
        f" {100 * len(mapping) / len(runic):.0f}% aligned.\n"
        f"{len(marks)} dot marks in the runic text.\n"
    )

    def nearby(at):
        found = set()
        for d in range(-WINDOW, WINDOW + 1):
            found |= punctuation.get(at + d, set())
        return found

    table = Counter()
    for position in marks:
        at = mapping.get(position, mapping.get(position - 1, mapping.get(position + 1)))
        if at is None:
            table["unaligned"] += 1
            continue
        found = nearby(at)
        table[
            "a sentence end" if found & set(".?!")
            else "a line break" if "NL" in found
            else "a quotation mark" if '"' in found
            else "a comma" if "," in found
            else "nothing"
        ] += 1
    print(f"{'what the dot mark sits at':<26}{'count':>7}")
    for label, count in table.most_common():
        print(f"{label:<26}{count:>7}")

    covered = set()
    for position in marks:
        at = mapping.get(position, mapping.get(position - 1, mapping.get(position + 1)))
        if at is not None:
            covered.update(range(at - WINDOW, at + WINDOW + 1))
    ends = [p for p, s in punctuation.items() if s & set(".?!")]
    commas = [p for p, s in punctuation.items() if s == {","}]
    print(
        f"\nthe converse: {sum(1 for p in ends if p in covered)} of {len(ends)}"
        f" English sentence ends carry a dot mark"
    )
    print(
        f"              {sum(1 for p in commas if p in covered)} of {len(commas)}"
        f" commas carry one"
    )


if __name__ == "__main__":
    main()
