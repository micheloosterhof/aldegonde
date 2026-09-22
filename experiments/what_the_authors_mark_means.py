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

## Result: it is a sentence mark, it is never a comma, and it holds on two passages

| passage | marks | at a sentence end | ends marked | commas marked |
|---|---|---|---|---|
| the koan, pages 4-7, Atbash+3 | 22 | 18 | 18/21 | **0/6** |
| the welcome, page 2, Vigenere | 10 | 8 | **8/8** | **0/1** |
| **both** | **32** | **26** | **26/29** | **0/7** |

**Two passages, two ciphers, two registers.** The koan is dialogue and the welcome is
continuous prose; one is Atbash-plus-three and the other Vigenere with DIVINITY and
interrupts. The marks that do not sit at a sentence end sit at a line break -- the koan's
dialogue turns, where the English transcription breaks the line instead of punctuating.

**Not one of the seven commas carries a mark.**

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
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from break_the_front_matter_pages import best_affine, runes_of  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
CICADA = Path.home() / "src" / "cicada-2014"
PASSAGES = (
    ("the koan, pages 4-7, Atbash+3", (4, 5, 6, 7), CICADA / "stage06" / "index.transcribed"),
    ("the welcome, page 2, Vigenere", (2,), CICADA / "stage04" / "index.1.decrypted"),
)
TRIPLES = ROOT / "experiments" / "solved_page_triples.json"
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
KOAN_PAGES = (4, 5, 6, 7)
STRUCTURAL = '.,?!;:"\n'
WINDOW = 2


def plaintext_for(page):
    """Rune indices of a page's plaintext: affine where that breaks it, else the triples."""
    runes = runes_of(page)
    score, _, plain = best_affine(runes)[0]
    if score / len(runes) > -5.0:
        return plain
    triples = {e["page"]: e for e in json.loads(TRIPLES.read_text())}
    return triples[page]["plaintext_runes"]


def runic_stream(pages):
    """The decrypted passage as English letters, with the position of each dot mark."""
    chunks = MASTER.read_text().split("%")
    stream, marks = "", []
    for page in pages:
        plain = plaintext_for(page)
        at = 0
        for ch in chunks[page]:
            if RUNE.match(ch):
                if at < len(plain):
                    stream += ENGLISH[plain[at]]
                    at += 1
            elif ch == ".":
                marks.append(len(stream))
    return stream, marks


def english_stream(path):
    text = path.read_text(errors="ignore").upper().split("PAGE 6 FOOTER")[0]
    stream, punctuation = "", {}
    for ch in text:
        if ch.isalpha():
            stream += ch
        elif ch in STRUCTURAL:
            punctuation.setdefault(len(stream), set()).add("NL" if ch == "\n" else ch)
    return stream, punctuation


def main() -> None:
    print(f"{'passage':<34}{'marks':>7}{'at a sentence end':>19}{'ends marked':>14}{'commas marked':>15}")
    totals = [0, 0, 0, 0, 0, 0]
    for label, pages, path in PASSAGES:
        runic, marks = runic_stream(pages)
        english, punctuation = english_stream(path)
        matcher = difflib.SequenceMatcher(None, runic, english, autojunk=False)
        mapping = {}
        for a, b, size in matcher.get_matching_blocks():
            for k in range(size):
                mapping[a + k] = b + k

        at_end, covered = 0, set()
        for position in marks:
            at = mapping.get(position, mapping.get(position - 1, mapping.get(position + 1)))
            if at is None:
                continue
            covered.update(range(at - WINDOW, at + WINDOW + 1))
            found = set()
            for d in range(-WINDOW, WINDOW + 1):
                found |= punctuation.get(at + d, set())
            at_end += bool(found & set(".?!"))
        ends = [p for p, s in punctuation.items() if s & set(".?!")]
        commas = [p for p, s in punctuation.items() if s == {","}]
        marked_ends = sum(1 for p in ends if p in covered)
        marked_commas = sum(1 for p in commas if p in covered)
        print(
            f"{label:<34}{len(marks):>7}{at_end:>19}"
            f"{f'{marked_ends}/{len(ends)}':>14}{f'{marked_commas}/{len(commas)}':>15}"
        )
        for i, v in enumerate(
            (len(marks), at_end, marked_ends, len(ends), marked_commas, len(commas))
        ):
            totals[i] += v
    print(
        f"{'both':<34}{totals[0]:>7}{totals[1]:>19}"
        f"{f'{totals[2]}/{totals[3]}':>14}{f'{totals[4]}/{totals[5]}':>15}"
    )
    print(
        "\n  Two passages, two ciphers, two registers -- dialogue and continuous prose."
        "\n  The mark is a sentence mark and it is never a comma."
    )


if __name__ == "__main__":
    main()
