# ABOUTME: Splits the four-dots by whether the scribe broke his line at them, and asks
# ABOUTME: whether that subset carries the sentence-final lengthening the others lack.
"""The scribe treated a minority of four-dots specially. Are those the real sentence ends?

A correction this session reversed the layout reading. With the separator baseline cleaned
of annotation hyphens, the four-dot takes a line break **10.6% of the time against a word
separator's 3.9%** (+4.02 sigma), and its gap is in the one-dot distribution's top 5% at
2.8 times the expected rate. Both are minority effects: the scribe gave roughly one
four-dot in six some special physical treatment and the rest none.

That suggests a **mixture**. If some four-dots mark real sentence ends and others do not,
the pooled sentence-final gap of -0.24 +- 0.20 is an average over both, and the marks the
scribe physically set apart are the candidates for the real ones.

**This is the first proposal in the session that could locate sentence ends rather than
only exclude places they are not.**

## The test

Split the body's four-dots by whether a rune follows them on their written line. For each
subset, the mean length of the block the mark closes, against the span interior.

- **a mixture**: the line-end subset lengthens towards English's +1.2 and the rest do not;
- **one kind of mark**: both subsets read alike, near the pooled -0.24.

## The control that decides whether a difference means anything

The author's own clause marks get the same split. If his line-end periods lengthen more
than his mid-line ones, then line-end status selects for long preceding words **in
general** -- a scribe breaks after a long word because it fills the measure -- and the
body's split would show the same thing for a reason that has nothing to do with sentences.

That control has to come first, because the artifact is entirely plausible: justified text
breaks where a word happens to end, and long words end lines more often.

## Result: the control passes, the test is underpowered, and the second arm is poisoned

**The control is clean.** The author's clause marks lengthen the same whether or not he
broke his line at them:

| the author, '.' marks | marks | final gap |
|---|---|---|
| closed at a line end | 21 | +1.06 +- 0.51 |
| closed mid-line | 49 | +0.98 +- 0.31 |
| difference | | +0.08 +- 0.60 |

So line-end status does not select for long preceding words by itself, and the artifact
that would have invalidated this test is absent. The method is sound.

**The body cannot answer.**

| the body, four-dot marks | marks | final gap |
|---|---|---|
| closed at a line end | **14** | +0.41 +- 0.82 |
| closed mid-line | 119 | -0.05 +- 0.19 |
| difference | | +0.45 +- 0.85, z = +0.54 |

Fourteen marks. A full mixture -- the line-end subset at English's +1.2 and the rest at
zero -- would show at only 1.5 sigma here, so +0.45 +- 0.85 is equally consistent with a
mixture and with none. Reaching three sigma needs the line-end subset at about 36 marks,
which at a 10.6% line-end rate means roughly **2.4 times the corpus**.

**The gap-width arm is worse: it is poisoned by a known artifact.** Splitting the
image-measured four-dots at their median whitespace:

    interior word length (one-dot)              4.01
    four-dot, WIDE gap      n = 39              3.13
    four-dot, narrow gap    n = 21              3.90
    difference                           -0.78 +- 0.40   z = -1.93

The wide-gap subset has *shorter* preceding words, which is the wrong direction for a
sentence end and the right direction for the failure mode
`do_wide_gaps_mark_sentence_ends.py` names in advance: **a missed rune merges two words
and widens their gap**, so the reader manufactures short words beside wide gaps. That arm
measures its own detection errors, not the text.

## Status

The mixture reading -- that some four-dots are real sentence ends and the pooled -0.24 is
an average over two kinds -- is **untested**, not refuted. It is the first proposal here
that could locate sentence ends rather than only exclude them, and the corpus is about
half the size needed to try.

    python are_some_four_dots_real.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
MARKS = set("④⑬③⑩㉓.")
SEPARATORS = set("①-")
BODY = range(15, 71)
FRONT = range(15)
MIN_SPAN = 3


def blocks(chunks):
    """(length, closing glyph, at a line end) for every block, annotation lines dropped."""
    text = MASTER.read_text().split("%")
    out = []
    for ci in chunks:
        if ci >= len(text):
            continue
        for line in re.split(r"[/\n]", text[ci]):
            if not RUNE.search(line):
                continue
            n = 0
            for i, ch in enumerate(line):
                if RUNE.match(ch):
                    n += 1
                elif (ch in MARKS or ch in SEPARATORS) and n:
                    out.append((n, ch, not RUNE.search(line[i + 1 :])))
                    n = 0
            if n:
                out.append((n, "", False))
    return out


def cells(rows, closer):
    """Blocks closed by `closer`, split by line-end status, plus the span interior."""
    at_end, mid, interior, since = [], [], [], 0
    for length, glyph, line_end in rows:
        if glyph in closer:
            if since >= MIN_SPAN - 1:
                (at_end if line_end else mid).append(length)
            since = 0
        else:
            if glyph in SEPARATORS:
                interior.append(length)
            since += 1
    return at_end, mid, interior


def gap(sample, interior):
    a, b = np.array(sample, float), np.array(interior, float)
    if len(a) < 4:
        return float("nan"), float("nan"), len(a)
    se = math.hypot(a.std(ddof=1) / math.sqrt(len(a)), b.std(ddof=1) / math.sqrt(len(b)))
    return float(a.mean() - b.mean()), se, len(a)


def report(label, rows, closer):
    at_end, mid, interior = cells(rows, closer)
    print(f"\n{label}   interior mean {np.mean(interior):.2f} on {len(interior):,} blocks\n")
    print(f"{'subset':<34}{'marks':>7}{'final gap':>18}")
    out = {}
    for name, sample in (("closed AT a line end", at_end), ("closed mid-line", mid)):
        g, se, n = gap(sample, interior)
        out[name] = (g, se, n)
        cell = "too few" if math.isnan(g) else f"{g:+.2f} +- {se:.2f}"
        print(f"{name:<34}{n:>7}{cell:>18}")
    a, b = out["closed AT a line end"], out["closed mid-line"]
    if not (math.isnan(a[0]) or math.isnan(b[0])):
        d = a[0] - b[0]
        se = math.hypot(a[1], b[1])
        print(f"{'difference':<34}{'':>7}{f'{d:+.2f} +- {se:.2f}':>18}   z = {d / se:+.2f}")
    return out


def main() -> None:
    print("CONTROL FIRST. The author's own clause marks, split the same way.")
    print("If his line-end periods lengthen more, the split is a layout artifact.")
    report("the author, '.' marks", blocks(FRONT), {"."})

    print("\n\nTHE BODY.")
    report("the body, four-dot marks", blocks(BODY), {"④"})

    print(
        "\n\nRead the control before the body. A scribe breaks his line where a word"
        "\nhappens to end, and long words end lines more often, so a positive difference"
        "\nin the body means nothing unless the author's is flat."
    )


if __name__ == "__main__":
    main()
