# ABOUTME: Splits the marks' line-end clustering by glyph, to ask whether the four-dot is
# ABOUTME: layout-coupled like a section break or text-coupled like ordinary punctuation.
"""The marks cluster at line ends. The ink now says which glyph should, and which should not.

`mark_forensics.py` reports the pooled result: a mark sits at a line end 17.8% of the time
against 3.7% for the ordinary word separator, z = +9.67, and the solved pages show the same
(26.7% against 5.5%, z = +8.62). Pooled, it settles nothing -- genuine punctuation clusters
at line ends too, because a scribe setting justified text will break a line where the text
breaks.

`do_the_marks_bound_the_titles.py` changed what the pooled figure is worth. ⑬ is a section
boundary confirmed from red ink, and a section boundary has an obvious reason to fall at a
line end: the next section starts a new line. ④ has no such reason if it is punctuation.
So the pooled clustering should be **carried by ⑬ and absent from ④** if ④ is a sentence
mark, and present in both if ④ is a layout device of some kind.

That is a fork the pooled number cannot show, and it needs no reference corpus: the
ordinary word separator on the same pages is the baseline, and the solved pages' own
punctuation is the control.

## The control that matters

`marks-are-not-clause-punctuation.md` records that only six of the fifteen ASCII-convention
pages (3, 8, 9, 10, 11, 14) are plaintext; the other nine are still enciphered. Their `.`
is the author's genuine clause punctuation and is the right thing to hold ④ against.

    python which_mark_is_layout_coupled.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
SEPARATOR = {"①", "-"}
PLAIN_PAGES = (3, 8, 9, 10, 11, 14)
ASCII_PAGES = range(15)
BODY_PAGES = range(15, 73)


def lines_of(chunk: str) -> list[str]:
    """Written lines that actually carry runes.

    Lines with no rune are annotation -- page numbers, and the number grids on chunks 30
    and 64 whose rows read `3258-3222-3152-3038`. Their delimiters are not word
    separators, and because nothing follows them on the line every one counts as
    line-final. Including them put 236 such hyphens into the body's separator baseline,
    all at rate 1.000, and inflated it from 0.039 to 0.115.
    """
    return [ln for ln in re.split(r"[/\n]", chunk) if RUNE.search(ln)]


def line_end_rates(pages) -> dict[str, tuple[int, int]]:
    """{glyph: (at a line end, total)} for every separator glyph on these pages."""
    chunks = MASTER.read_text().split("%")
    counts: dict[str, list[int]] = {}
    for n in pages:
        if n >= len(chunks):
            continue
        for line in lines_of(chunks[n]):
            for i, ch in enumerate(line):
                if ch not in c3301.WORD_BOUNDARY or RUNE.match(ch):
                    continue
                rest = line[i + 1 :]
                cell = counts.setdefault(ch, [0, 0])
                cell[1] += 1
                cell[0] += not RUNE.search(rest)
    return {g: (a, b) for g, (a, b) in counts.items()}


def show(label, rates, baseline_glyphs):
    base_hits = sum(rates.get(g, (0, 0))[0] for g in baseline_glyphs)
    base_all = sum(rates.get(g, (0, 0))[1] for g in baseline_glyphs)
    if not base_all:
        return
    p0 = base_hits / base_all
    print(f"\n{label}   the word separator sits at a line end {p0:.3f} of the time"
          f" ({base_hits}/{base_all})\n")
    print(f"{'glyph':>6}{'count':>8}{'at a line end':>16}{'rate':>9}{'vs separator':>14}")
    for glyph, (hits, total) in sorted(rates.items(), key=lambda kv: -kv[1][1]):
        if glyph in baseline_glyphs or total < 4:
            continue
        p = hits / total
        se = math.sqrt(p0 * (1 - p0) * (1 / total + 1 / base_all))
        print(
            f"{glyph:>6}{total:>8}{hits:>16}{p:>9.3f}"
            f"{f'{(p - p0) / se:+.2f}':>14}"
        )


def main() -> None:
    print("A mark 'sits at a line end' when no rune follows it on that written line.")
    show("THE BODY, pages 15-72.", line_end_rates(BODY_PAGES), SEPARATOR)
    show(
        "THE AUTHOR'S PLAINTEXT pages 3, 8, 9, 10, 11, 14.",
        line_end_rates(PLAIN_PAGES),
        SEPARATOR,
    )
    show(
        "The other ASCII-convention pages, still enciphered.",
        line_end_rates([n for n in ASCII_PAGES if n not in PLAIN_PAGES]),
        SEPARATOR,
    )

    body = line_end_rates(BODY_PAGES)
    plain = line_end_rates(PLAIN_PAGES)
    four = body.get("④", (0, 0))
    dot = plain.get(".", (0, 0))
    if four[1] and dot[1]:
        p1, p2 = four[0] / four[1], dot[0] / dot[1]
        se = math.hypot(
            math.sqrt(p1 * (1 - p1) / four[1]), math.sqrt(p2 * (1 - p2) / dot[1])
        )
        print(
            f"\nThe four-dot against the author's own clause punctuation:"
            f"\n  ④ {p1:.3f} ({four[0]}/{four[1]})   '.' {p2:.3f} ({dot[0]}/{dot[1]})"
            f"   difference {p1 - p2:+.3f} +- {se:.3f}   z = {(p1 - p2) / se:+.2f}"
        )


if __name__ == "__main__":
    main()
