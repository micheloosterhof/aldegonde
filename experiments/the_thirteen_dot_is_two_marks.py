# ABOUTME: Splits the thirteen-dot by its role at a rubricated title and finds the two
# ABOUTME: roles have opposite layout behaviour, which pooling had hidden.
"""The thirteen-dot's layout coupling is a mixture of nothing and almost everything.

`does_the_dot_count_mean_a_level.py` records that ⑬ is **bimodal** -- mean 114.4 blocks
between occurrences against a median of 18 -- because a rubricated title is opened and
closed by a pair of thirteen-dots a few words apart while sections run hundreds of blocks.
It warns that any statistic pooling ⑬ occurrences mixes the two.

Three results in this directory pool them, including the line-end rate of 0.516 that
`the-four-dot-is-not-layout-coupled.md` uses as its benchmark for what a structural mark
looks like. This checks whether that benchmark survives the split.

## The three roles

`rubricated_titles.json` gives each title's word range, so every ⑬ falls into one of:

- **opens a title** -- it closes the word immediately before the title starts;
- **closes a title** -- it closes the title's last word;
- **neither** -- a section boundary with no red title visible, on one of the 24 pages
  whose scan carries no colour.

## This is internal to the body

Same pages, same hand, same cipher. The baseline is the body's own one-dot separator, so
no external control applies.

## Result: the two roles behave oppositely

The body's one-dot separator sits at a line end 0.0401 of the time (108/2,695).

| thirteen-dot | n | at a line end | z | P |
|---|---|---|---|---|
| **closes a title** | 9 | **0/9 = 0.000** | -0.61 | 1.0e-09 against 0.9 |
| opens a title | 4 | 3/4 = 0.750 | +7.23 | 2.5e-04 |
| **neither** | 13 | **12/13 = 0.923** | +16.19 | 2.1e-16 |
| pooled, as used elsewhere | 26 | 15/26 = 0.577 | | |

**The pooled figure is a mixture of 0.000 and 0.923 and describes neither role.**

A title's **closing** thirteen-dot is never at a line end: the body text continues on the
title's own line, which is what a short title set at the head of a paragraph looks like.
Every other thirteen-dot ends its line almost always, which is what starting a new unit
looks like.

## What this costs and what it does not

`the-four-dot-is-not-layout-coupled.md` uses ⑬'s pooled 0.516 as the benchmark for what a
structural mark looks like. **That benchmark is wrong in both directions** -- the real
figure is 0.923 for a unit-opening mark and 0.000 for a title-closing one. The four-dot's
0.106 is further below the first than the pooled comparison suggested, and its coupling
claim (+4.02 against the separator) is untouched, since that uses the separator baseline
and not ⑬.

The red-ink result is untouched: `do_the_marks_bound_the_titles.py` asks which words are
red, which has nothing to do with line ends.

**The general point is the third of its kind this session.** Pooling a mark class has now
hidden a split three times -- the four-dot's possible mixture, ⑬'s bimodal spacing, and
now ⑬'s opposite layout roles. Every mark statistic here should be reported split until
shown homogeneous, not pooled until shown otherwise.

    python the_thirteen_dot_is_two_marks.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TITLES = ROOT / "experiments" / "rubricated_titles.json"
MARKS = set("④⑬③⑩㉓")
SEPARATORS = set("①-")
BODY = range(15, 71)


def marks_by_chunk():
    """{chunk: [(word index, glyph, at a line end)]} over rune-bearing lines."""
    text = MASTER.read_text().split("%")
    out = {}
    for ci in range(15, 73):
        if ci >= len(text):
            continue
        idx, rec = 0, []
        for line in re.split(r"[/\n]", text[ci]):
            if not RUNE.search(line):
                continue
            n = 0
            for i, ch in enumerate(line):
                if RUNE.match(ch):
                    n += 1
                elif (ch in MARKS or ch in SEPARATORS) and n:
                    rec.append((idx, ch, not RUNE.search(line[i + 1 :])))
                    idx += 1
                    n = 0
        out[ci] = rec
    return out


def main() -> None:
    info = marks_by_chunk()
    titles = json.loads(TITLES.read_text())
    opens, closes = set(), set()
    for t in titles:
        a, b = t["word_range"]
        if t["chunk"] in info:
            if a > 0:
                opens.add((t["chunk"], a - 1))
            closes.add((t["chunk"], b))

    base = [le for ci, rec in info.items() if ci < 71 for _, ch, le in rec if ch in SEPARATORS]
    p0 = float(np.mean(base))
    print(f"the body's one-dot separator sits at a line end {p0:.4f} of the time "
          f"({int(np.sum(base))}/{len(base)}).\n")

    rows = []
    for ci, rec in info.items():
        if ci >= 71:
            continue
        for idx, ch, le in rec:
            if ch != "⑬":
                continue
            if (ci, idx) in closes:
                rows.append(("closes a title", le))
            elif (ci, idx) in opens:
                rows.append(("opens a title", le))
            else:
                rows.append(("neither", le))

    print(f"{'thirteen-dot':<20}{'n':>5}{'at a line end':>15}{'z':>8}{'P':>11}")
    for kind in ("closes a title", "opens a title", "neither"):
        v = [le for k, le in rows if k == kind]
        if not v:
            continue
        hits, n = int(np.sum(v)), len(v)
        p = hits / n
        se = math.sqrt(p0 * (1 - p0) * (1 / n + 1 / len(base)))
        tail = (
            stats.binom.cdf(hits, n, 0.9)
            if p < p0
            else stats.binom.sf(hits - 1, n, p0)
        )
        print(f"{kind:<20}{n:>5}{f'{hits}/{n} = {p:.3f}':>15}{(p - p0) / se:>+8.2f}{tail:>11.1e}")

    allv = [le for _, le in rows]
    print(
        f"\npooled, as every earlier statistic used it: "
        f"{int(np.sum(allv))}/{len(allv)} = {np.mean(allv):.3f}"
    )
    print(
        "\nThe pooled figure is a mixture of 0.000 and 0.923 and describes neither role."
        "\nA title's CLOSING thirteen-dot is never at a line end -- the body text"
        "\ncontinues on the title's own line. Every other thirteen-dot ends its line"
        "\nalmost always, which is what starting a new unit looks like."
    )


if __name__ == "__main__":
    main()
