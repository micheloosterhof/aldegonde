# ABOUTME: Stratifies the sentence-final length gap by how long a span the mark closes,
# ABOUTME: and shows the pooled anomaly is substantially a composition effect.
"""The author's marks close short units far more often than the body's, and that is most
of the gap between them.

`sentences-do-not-end-long.md` reports that the author's mark-preceding words run
+1.28 runes above his interior while the body's run -0.32, a like-for-like difference of
-4.65 sigma on one glyph class. This file stratifies that by the length of the span the
mark closes, and the effect turns out to depend on it strongly in both texts -- in
opposite directions.

Reading the solved pages with their plaintext spliced back into their own separator
layout shows why. The author's mark is a period, and it closes titles and exclamations
as readily as sentences:

    A WARNNG . BELIEUE NOTHNG FROM THIS BOOC . EXCEPT WHAT YOU CNOW TO BE TRUE .
    WELCOME . WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THNGS .
    SOME WISDOM . THE PRIMES ARE SACRED .

"A WARNNG." and "WELCOME." are one- and two-block spans whose final word is necessarily
a content word, and they carry a gap of **+2.78**. Long spans carry **+0.20**. One fifth
of the author's marks close a span of two blocks or less; **one thirty-fifth** of the
body's do.

## What survives and what does not

| stratum | share: author / body | author | the body | difference |
|---|---|---|---|---|
| 1-2 blocks | 20.2% / 2.9% | +2.78 +- 0.61 | -1.49 +- 0.71 | n = 4, ignore |
| 3-6 | 31.9% / 18.2% | +2.20 +- 0.42 | -0.81 +- 0.33 | **-5.6 sigma** |
| 7-14 | 38.3% / 29.2% | +0.90 +- 0.34 | -0.19 +- 0.36 | **-2.2 sigma** |
| 15+ | 9.6% / 49.6% | +0.20 +- 0.53 | -0.17 +- 0.30 | **-0.6 sigma** |

So the difference is real in the strata where both texts have data, and **vanishes in the
stratum holding half the body's spans**. The author has only 9 spans there, so that cell
settles nothing on its own -- but it is the cell the body mostly lives in, and the pooled
-4.65 sigma leans on a composition mismatch rather than on matched evidence.

## A second retraction, about the reference

Austen's profile runs the **opposite way** to the author's: +0.35 at 3-6 blocks rising to
+1.08 at 15+, where the author falls from +2.20 to +0.20. Since every "predicted +0.75"
in this thread is Austen's pooled figure, and Austen's composition happens to match the
body's while its shape does not match the author's, that benchmark is doing less work
than it appeared to. The author's own long spans (+0.20 +- 0.53) sit 1.7 sigma BELOW
Austen's (+1.08 +- 0.05), which is the wrong direction for treating Austen as the
register model.

    python the_gap_depends_on_span_length.py
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402
from sentences_do_not_end_long import join, prose_sentences  # noqa: E402
from what_the_marks_are import blocks_with  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
STRATA = ((1, 2, "1-2 blocks"), (3, 6, "3-6"), (7, 14, "7-14"), (15, 10**6, "15+"))


def solved_pages() -> list[int]:
    return sorted(
        set(PLAIN_PAGES) | {t["page"] for t in json.loads(TRIPLES.read_text())}
    )


def author_spans() -> list[list[int]]:
    """Block lengths grouped into the runs the author's period closes."""
    pages = MASTER.read_text().split("%")
    spans: list[list[int]] = []
    current: list[int] = []
    length = 0
    for n in solved_pages():
        for ch in pages[n]:
            if RUNE.match(ch):
                length += 1
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY:
                if length:
                    current.append(length)
                    length = 0
                if ch == "." and current:
                    spans.append(current)
                    current = []
        if current:
            spans.append(current)
            current = []
    return spans


def body_spans() -> list[list[int]]:
    """The same, closed by a four-dot mark."""
    spans: list[list[int]] = []
    current: list[int] = []
    for length, _, closes in blocks_with("④"):
        current.append(length)
        if closes:
            spans.append(current)
            current = []
    if current:
        spans.append(current)
    return spans


def english_spans(rng) -> list[list[int]]:
    return [
        s for s in (join(s, 0.40, rng, forward=True) for s in prose_sentences()) if s
    ]


def strata_gaps(spans):
    """Final-block gap against the interior, within each span-length stratum."""
    interior = np.array([x for s in spans for x in s[:-1]], float)
    out = {}
    for lo, hi, label in STRATA:
        chosen = [s for s in spans if lo <= len(s) <= hi]
        if len(chosen) < 4:
            out[label] = (len(chosen), float("nan"), float("nan"))
            continue
        final = np.array([s[-1] for s in chosen], float)
        se = math.hypot(
            final.std(ddof=1) / math.sqrt(len(final)),
            interior.std(ddof=1) / math.sqrt(len(interior)),
        )
        out[label] = (len(chosen), float(final.mean() - interior.mean()), se)
    final = np.array([s[-1] for s in spans], float)
    se = math.hypot(
        final.std(ddof=1) / math.sqrt(len(final)),
        interior.std(ddof=1) / math.sqrt(len(interior)),
    )
    out["all"] = (len(spans), float(final.mean() - interior.mean()), se)
    return out


def main() -> None:
    rng = random.Random(3301)
    texts = {
        "the author, pages 0-14": author_spans(),
        "the body, four-dot": body_spans(),
        "Austen, joined q=0.40": english_spans(rng),
    }
    gaps = {name: strata_gaps(spans) for name, spans in texts.items()}

    print(
        "Final-block gap against the interior, by the length of the span the mark closes.\n"
    )
    header = f"{'stratum':<14}"
    for name in texts:
        header += f"{name:>26}"
    print(header)
    for _, _, label in (*STRATA, (0, 0, "all")):
        row = f"{label:<14}"
        for name in texts:
            n, gap, se = gaps[name][label]
            cell = "too few" if math.isnan(gap) else f"{gap:+.2f} +- {se:.2f}  (n={n})"
            row += f"{cell:>26}"
        print(row)

    print("\nShare of spans in each stratum, which is what drives any pooled figure.\n")
    print(f"{'stratum':<14}" + "".join(f"{name:>26}" for name in texts))
    for lo, hi, label in STRATA:
        row = f"{label:<14}"
        for spans in texts.values():
            share = sum(1 for s in spans if lo <= len(s) <= hi) / len(spans)
            row += f"{share:>26.1%}"
        print(row)

    print("\nThe body against the author, stratum by stratum.\n")
    print(f"{'stratum':<14}{'author':>18}{'body':>18}{'difference':>20}{'z':>8}")
    for _, _, label in (*STRATA, (0, 0, "all")):
        na, ga, sa = gaps["the author, pages 0-14"][label]
        nb, gb, sb = gaps["the body, four-dot"][label]
        if math.isnan(ga) or math.isnan(gb):
            print(f"{label:<14}{'':>18}{'':>18}{'a cell is empty':>20}")
            continue
        se = math.hypot(sa, sb)
        note = "  n too small" if min(na, nb) < 8 else ""
        print(
            f"{label:<14}{f'{ga:+.2f} +- {sa:.2f}':>18}{f'{gb:+.2f} +- {sb:.2f}':>18}"
            f"{f'{gb - ga:+.2f} +- {se:.2f}':>20}{(gb - ga) / se:>+8.2f}{note}"
        )

    print(
        "\nThe difference is real where both texts have spans and disappears in the"
        "\nstratum holding half the body's. The pooled figure leans on the author closing"
        "\nshort units -- titles and exclamations -- five times as often as the body does."
        "\n\nAusten runs the other way, rising with span length where the author falls, so"
        "\nit is a poor model for this register and the '+0.75 predicted' benchmark built"
        "\non it should not be read as the LP's own expectation."
    )


if __name__ == "__main__":
    main()
