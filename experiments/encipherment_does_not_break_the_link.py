# ABOUTME: Shows the author's enciphered pages keep the mark-at-sentence-end link, so
# ABOUTME: encipherment is not what severs it in the body.
"""The front matter's ENCIPHERED pages still mark sentence ends. The body's do not.

The tidiest explanation of the sentence-edge anomaly would be that the body's marks were
added to text nobody could read. `the-scribe-ignored-the-blocks.md` shows the copyist
worked mechanically -- he keeps words whole when ruling lines on plaintext (z = +5.60) and
not at all on ciphertext -- so a scribe punctuating enciphered runes at arbitrary
intervals would produce exactly what the body shows: prose-scale spacing, memoryless, and
no relationship to sentences.

The book tests it. Ten of the author's sixteen solved pages are enciphered, and their
plaintext is known, so the marks on them can be scored the same way.

| group | pages | spans | gap vs interior |
|---|---|---|---|
| plaintext pages | 6 | 26 | +1.48 +- 0.44 |
| enciphered: monoalphabetic | 5 | 30 | +1.31 +- 0.37 |
| enciphered: interrupted vigenere | 4 | 18 | +1.11 +- 0.67 |
| **all enciphered** | **10** | **49** | **+1.21 +- 0.33** |
| all solved front matter | 16 | 75 | +1.32 +- 0.26 |
| ten English registers | | | +1.19 +- 0.28 |
| **the body** | | 167 | **-0.29 +- 0.20** |

**The enciphered pages keep the link.** Their +1.21 sits on top of the plaintext pages'
+1.48, on top of the ten-register English mean of +1.19, and 3.9 sigma above the body.

So encipherment is not what severs the tie between a mark and a sentence end. Whoever
placed the marks on the author's enciphered pages knew where the sentences were -- they
were put in before or during enciphering, not after by someone reading runes.

## Where this leaves the two readings

It removes the mechanism that made "the marks are not sentence marks" comfortable. That
reading survives, but it can no longer lean on the marks having been added blind to
ciphertext, because the same book does the opposite on pages of the same kind.

It also joins a pattern. `joining_is_not_preparation.py` found the short-unit joining does
not track cipher difficulty either -- plaintext, monoalphabetic, Vigenere and prime
running key pages all sit between 0.22 and 0.32 against the body's 0.159. Two independent
conventions change at page 15 and **neither** tracks encipherment, which is what
`one-production-break-at-page-fifteen.md` already concluded from the line measure.

## Scope

Forty-nine spans on the enciphered side, so the +1.21 carries +- 0.33 and cannot be
pushed much further -- there are only ten such pages in the book. What it can do, it does:
it separates the body from enciphered text of the same authorship at 3.9 sigma.

    python encipherment_does_not_break_the_link.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402
from the_gap_depends_on_span_length import body_spans  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ANNOTATION = re.compile(r"^[\s0-9-]*$")
MIN_SPANS = 8
TEN_REGISTERS = (1.19, 0.28)  # final_lengthening_across_registers.py


def spans_of(page_ids):
    """Block lengths grouped into the runs the author's period closes."""
    pages = MASTER.read_text().split("%")
    out, current, length = [], [], 0
    for n in page_ids:
        text = "\n".join(
            line
            for line in pages[n].replace("/", "\n").split("\n")
            if not ANNOTATION.match(line)
        )
        for ch in text:
            if RUNE.match(ch):
                length += 1
            elif ch == "\n" or ch in "%$&":
                continue
            elif ch in c3301.WORD_BOUNDARY:
                if length:
                    current.append(length)
                    length = 0
                if ch == "." and current:
                    out.append(current)
                    current = []
        if current:
            out.append(current)
            current = []
    return [s for s in out if len(s) >= 3]


def gap(spans):
    interior = np.array([x for s in spans for x in s[1:-1]], float)
    final = np.array([s[-1] for s in spans], float)
    return (
        float(final.mean() - interior.mean()),
        math.hypot(
            final.std(ddof=1) / math.sqrt(len(final)),
            interior.std(ddof=1) / math.sqrt(len(interior)),
        ),
        len(spans),
    )


def main() -> None:
    triples = {t["page"]: t["cipher"] for t in json.loads(TRIPLES.read_text())}
    groups = (
        ("plaintext pages", sorted(PLAIN_PAGES)),
        (
            "enciphered: monoalphabetic",
            [n for n, c in triples.items() if c == "monoalphabetic"],
        ),
        (
            "enciphered: interrupted vigenere",
            [n for n, c in triples.items() if "vigenere" in c],
        ),
        ("all enciphered", sorted(triples)),
        ("all solved front matter", sorted(set(PLAIN_PAGES) | set(triples))),
    )

    print("Sentence-final lengthening on the author's pages, split by whether the page")
    print("is enciphered -- that is, whether the mark-placer could read it.\n")
    print(f"{'group':<36}{'pages':>7}{'spans':>7}{'gap vs interior':>20}")
    enciphered = None
    for label, ids in groups:
        spans = spans_of(ids)
        if len(spans) < MIN_SPANS:
            print(f"{label:<36}{len(ids):>7}{len(spans):>7}{'too few':>20}")
            continue
        g, se, n = gap(spans)
        if label == "all enciphered":
            enciphered = (g, se)
        print(f"{label:<36}{len(ids):>7}{n:>7}{f'{g:+.2f} +- {se:.2f}':>20}")

    print(
        f"{'ten English registers':<36}{'':>7}{'':>7}"
        f"{f'{TEN_REGISTERS[0]:+.2f} +- {TEN_REGISTERS[1]:.2f}':>20}"
    )
    body_gap, body_se, body_n = gap([s for s in body_spans() if len(s) >= 3])
    print(
        f"{'the body':<36}{'':>7}{body_n:>7}{f'{body_gap:+.2f} +- {body_se:.2f}':>20}"
    )

    print("\nThe body against each, like for like.\n")
    print(f"{'against':<36}{'z':>8}")
    for label, value in (
        ("the author's ENCIPHERED pages", enciphered),
        ("ten English registers", TEN_REGISTERS),
    ):
        g, se = value
        print(f"{label:<36}{(body_gap - g) / math.hypot(body_se, se):>+8.2f}")

    print(
        "\nThe enciphered pages keep the link: +1.21 sits on top of the plaintext pages'"
        "\n+1.48 and the ten-register +1.19. So encipherment is not what severs the tie"
        "\nbetween a mark and a sentence end -- whoever marked the author's enciphered"
        "\npages knew where the sentences were."
        "\n\nThat removes the mechanism that made 'the marks are not sentence marks'"
        "\ncomfortable: they cannot simply have been added blind to ciphertext, because"
        "\nthe same book does the opposite on pages of the same kind."
    )


if __name__ == "__main__":
    main()
