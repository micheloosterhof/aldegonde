# ABOUTME: Tests whether the four-dot's missing final-block lengthening is uniform across
# ABOUTME: the body's sections, which is the coarsest form of the mixture question.
"""The session's central number has only ever been pooled over all 139 marks.

The body's block before a four-dot does not lengthen: -0.24 +- 0.20 where the author gives
+1.39 +- 0.27. Every statement of that result pools every four-dot in the book.

Three times this session pooling a mark class has hidden a split -- the thirteen-dot's
bimodal spacing, its opposite layout roles at a title (0.000 against 0.923), and the
four-dot's own possible mixture. The working rule that came out of it is to report mark
statistics **split until shown homogeneous**. This applies that rule to the central
number.

`is_the_body_homogeneous.py` audits five observables across the `$` sections -- 2-rune
fraction, mark rate, lag-1 doublets, lag-5 coincidences, mean block length -- and finds
all five uniform. **The final-block gap is not among them**, and it is the one every
conclusion about the four-dot rests on.

## What a split would mean

If the four-dot is a mixture of real sentence ends and something else, and the proportion
varies between sections, the per-section gaps spread wider than their own sampling error.
That is the coarsest version of the mixture question and the only one with enough marks
per cell to test: roughly fourteen four-dots per section against a gap error of 0.65.

A within-section mixture is invisible here. This can only see a mixture that tracks the
book's divisions.

## The control

A planted split -- half the sections shifted to +1.2 and half left at zero, at the observed
cell sizes -- says what the test could see. Without it a uniform result means nothing.

    python is_the_four_dot_gap_homogeneous.py
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

import numpy as np
from body_parse import blocks  # noqa: E402
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
MARKS = set("④⑬③⑩㉓")
SEPARATORS = set("①-")
BODY = range(15, 71)
MIN_MARKS = 5
DRAWS = 400


def sections():
    """Blocks per `$` section, with blocks spanning line wraps."""
    text = MASTER.read_text().split("%")
    out, current = [], []
    for ci in BODY:
        if ci >= len(text):
            continue
        if "$" in text[ci] and current:
            out.append(current)
            current = []
        current.extend((n, g) for n, g, _ in blocks([ci]))
    if current:
        out.append(current)
    return out


def gap_of(rows):
    """Final-block gap for the four-dots inside one section."""
    before = [n for n, g in rows if g == "④"]
    interior = [n for n, g in rows if g in SEPARATORS]
    if len(before) < MIN_MARKS or len(interior) < 30:
        return None
    a, b = np.array(before, float), np.array(interior, float)
    se = math.hypot(
        a.std(ddof=1) / math.sqrt(len(a)), b.std(ddof=1) / math.sqrt(len(b))
    )
    return float(a.mean() - b.mean()), se, len(a)


def heterogeneity(cells):
    g = np.array([c[0] for c in cells])
    se = np.array([c[1] for c in cells])
    w = 1 / se**2
    mean = float((w * g).sum() / w.sum())
    chi = float((w * (g - mean) ** 2).sum())
    return chi, len(cells) - 1, mean


def main() -> None:
    secs = sections()
    cells = [c for c in (gap_of(s) for s in secs) if c]
    print(f"{len(secs)} sections, {len(cells)} with at least {MIN_MARKS} four-dots.\n")
    print(f"{'section':>8}{'four-dots':>11}{'final gap':>18}")
    for i, (g, se, n) in enumerate(cells):
        print(f"{i:>8}{n:>11}{f'{g:+.2f} +- {se:.2f}':>18}")
    chi, df, mean = heterogeneity(cells)
    print(
        f"\npooled gap {mean:+.3f};  heterogeneity chi2 = {chi:.1f} on {df} df,"
        f" P = {stats.chi2.sf(chi, df):.3f}"
    )

    rng = random.Random(3301)
    sizes = [(c[1], c[2]) for c in cells]
    print("\nWhat the test could see, at these cell sizes.\n")
    print(f"{'planted':<34}{'median chi2':>13}{'P(detect at 0.05)':>20}")
    for label, shift in (("uniform", 0.0), ("half the sections at +1.2", 1.2)):
        hits, chis = 0, []
        for _ in range(DRAWS):
            fake = []
            for j, (se, n) in enumerate(sizes):
                offset = shift if (shift and j % 2 == 0) else 0.0
                fake.append((rng.gauss(offset, se), se, n))
            c, d, _ = heterogeneity(fake)
            chis.append(c)
            hits += stats.chi2.sf(c, d) < 0.05
        print(f"{label:<34}{np.median(chis):>13.1f}{hits / DRAWS:>20.2f}")


if __name__ == "__main__":
    main()
