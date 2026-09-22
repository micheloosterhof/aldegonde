# ABOUTME: Tests whether the body's marks are a thinned sample of true sentence ends,
# ABOUTME: which explains their rate and spacing but not the sentence-edge anomaly.
"""One parameter explains the mark rate and the span shape. It does not touch the anomaly.

Two facts about the body's marks have sat unconnected:

- the **rate** is 2.3x lower than the author's -- one mark per 72 runes against one per 32
  (`what_the_marks_are.py`);
- the **spacing** is over-dispersed for sentence ends -- CV 0.972 against 0.738 for the
  author's own pages and 0.771 for English (`what-the-marks-space-like`).

A single mechanism gives both: the transcription records only a fraction **p** of the
marks the scribe wrote. Then an observed span is a sum of Geometric(p) true spans, so the
mean scales as 1/p and the dispersion follows

    CV^2(observed) = p x CV^2(true) + (1 - p)

**p is fitted from the mean alone**, so the dispersion and the distribution shape are
predictions.

## What it predicts and gets right

Taking the author's own spacing as the truth, the mean gives **p = 0.402**.

| | predicted | observed |
|---|---|---|
| CV of the span length | 0.904 | 0.972 +- 0.145 (z = +0.47) |

The CV is a weak test -- English at 0.771 sits 1.4 sigma away and random placement at
0.970 sits on top of the observation, so it cannot separate them. The **shape** can.
Mean-normalised, against a reference built from 40 draws of each model:

| model | D from the body | P(D >= observed) |
|---|---|---|
| the author's spacing, as written | 0.115 | 0.688 |
| **under-recorded at p = 0.40** | **0.059** | **0.830** |
| English (Austen, joined at q = 0.40) | 0.118 | 0.035 |
| marks placed at random | 0.071 | 0.122 |

Under-recording is the closest of the four and English the furthest. The P column is not
comparable across rows -- each model's null has its own spread, and the author's 92 spans
resample widely -- so read the D column.

## What it does not explain, and this is the point

If the marks are a thinned sample, then a mark that **is** recorded is still a true
sentence end, so the block before it should carry the full English sentence-final
lengthening. `sentences-do-not-end-long.md` measures that at **-0.21 +- 0.20** against a
joined-English prediction of +0.75.

Under-recording predicts no dilution of that profile whatever p is. It therefore leaves
the sentence-edge anomaly exactly where it was. The hypothesis covers the rate and the
spacing and is silent on the thing that actually needs explaining.

The alternative -- that the lost marks are lost *selectively*, in a way that also flattens
the edge profile -- is not falsifiable from this corpus and is not proposed.

    python are_the_marks_under_recorded.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from profile_around_a_mark import author_spans  # noqa: E402
from what_the_marks_space_like import (  # noqa: E402
    body_spans,
    cv,
    cv_jackknife,
    english_spans,
    random_spans,
)

REFERENCE_DRAWS = 40
NULL_DRAWS = 400


def under_recorded(truth, p, rng, n):
    """Merge Geometric(p) consecutive true spans: what a thinned transcription leaves."""
    out = []
    while len(out) < n:
        total = 0
        while True:
            total += rng.choice(list(truth))
            if rng.random() < p:
                break
        out.append(total)
    return np.array(out, float)


def shape_distance(a, b) -> float:
    return float(stats.ks_2samp(a / a.mean(), b / b.mean()).statistic)


def main() -> None:
    rng = random.Random(3301)
    spans, n_blocks = body_spans()
    author = np.array([len(s) for s in author_spans()], float)
    english = english_spans(rng)
    n = len(spans)

    print(f"{'text':<34}{'spans':>7}{'mean':>8}{'CV':>18}")
    for label, v in (
        ("the body", spans),
        ("the author's pages", author),
        ("Austen, joined q=0.40", english),
    ):
        c, se = cv_jackknife(v)
        print(f"{label:<34}{len(v):>7}{v.mean():>8.2f}{f'{c:.3f} +- {se:.3f}':>18}")

    observed_cv, cv_se = cv_jackknife(spans)
    p = author.mean() / spans.mean()
    predicted = math.sqrt(p * cv(author) ** 2 + (1 - p))
    print("\nFitting p from the MEAN span alone, against the author's own spacing:\n")
    print(f"  p = {p:.3f}")
    print(
        f"  predicted CV {predicted:.3f}   observed {observed_cv:.3f} +- {cv_se:.3f}"
        f"   z = {(observed_cv - predicted) / cv_se:+.2f}"
    )
    print("  (a weak test: English at 0.771 and random placement at 0.970 both sit")
    print("   within about 1.5 sigma of the observation)")

    models = {
        "the author's spacing, as written": lambda r: np.array(
            r.choices(list(author), k=n), float
        ),
        f"under-recorded at p = {p:.2f}": lambda r: under_recorded(author, p, r, n),
        "English (Austen, joined)": lambda r: np.array(
            r.choices(list(english), k=n), float
        ),
        "marks placed at random": lambda r: random_spans(r, n_blocks, n),
    }
    print("\nMean-normalised shape, which is a prediction rather than a fit.\n")
    print(f"{'model':<36}{'D from the body':>17}{'P(D >= obs)':>14}")
    for label, generate in models.items():
        reference = np.concatenate(
            [generate(random.Random(500 + i)) for i in range(REFERENCE_DRAWS)]
        )
        observed = shape_distance(spans, reference)
        null = np.array(
            [
                shape_distance(generate(random.Random(900 + i)), reference)
                for i in range(NULL_DRAWS)
            ]
        )
        print(f"{label:<36}{observed:>17.3f}{float((null >= observed).mean()):>14.3f}")
    print("\n  The P column is not comparable across rows -- each model's null has its")
    print("  own spread, and the author's 92 spans resample widely. Read the D column.")

    print(
        "\nWhat it does not explain. If the marks are a thinned sample, a mark that IS"
        "\nrecorded is still a true sentence end, so the block before it should carry the"
        "\nfull English sentence-final lengthening. The corpus reads -0.21 +- 0.20 against"
        "\na joined-English prediction of +0.75. Under-recording predicts no dilution of"
        "\nthat profile at any p, so it leaves the sentence-edge anomaly untouched."
    )


if __name__ == "__main__":
    main()
