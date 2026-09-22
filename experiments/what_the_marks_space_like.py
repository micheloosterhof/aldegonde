# ABOUTME: Tests whether the gaps between sentence marks are spaced like English
# ABOUTME: sentences or like a memoryless process, and finds them over-dispersed.
"""The marks are not spaced mechanically. Whether they are spaced like sentences is open.

`the-cipher-does-not-restart.md` showed the marks mean nothing to the cipher, so they are
the scribe's. That leaves the question of what the scribe was marking, and the gaps
between marks answer it better than anything at the gap's edges.

Three models, each predicting a different dispersion of span length:

| model | coefficient of variation |
|---|---|
| mechanical -- a mark every k blocks | 0 |
| English sentence ends | ~0.77 |
| a memoryless process -- marks placed at random on block boundaries | ~0.97 |

**Mechanical is dead**: the body reads 0.972 +- 0.145 against 0, at 6.7 sigma. That much
is settled.

Between the other two the body sits exactly on random and 1.4 sigma from English, and
the strength of that depends on which statistic and which reference is used. This file
reports the range rather than the best number in it.

## The correction this makes

`sentences-do-not-end-long.md` reported that the marks "partition the body at ordinary
prose sentence density -- 17.2 units a span against 17.5 for joined Austen" and called it
the strongest evidence the marks are sentence-scale. **That claim carries no evidence.**
Random placement matches any mean by construction, because the density is its one free
parameter. Only the SHAPE discriminates, and the shape is what this file measures. (The
figure also moves to 19.6 under the corrected parser here, which restores the page-break
markers that a line filter had been dropping.)

## What the shape says, and its one real weakness

Mean-normalised, so no model gets credit for fitting the density, scored against both
alternatives rather than one:

| reference | P(D >= body) under the reference | under random | ratio |
|---|---|---|---|
| Pride and Prejudice, 5,361 sentences | 0.028 | 0.943 | **33 : 1 for random** |
| the LP author's own 92 sentences | 0.793 | 0.890 | **1.1 : 1 -- no power** |

The 33:1 rests entirely on Austen standing in for the LP's plaintext register. The
book's own author is the register-matched control and his 92 sentences cannot resolve
anything. What he does support is the reference value itself: his dispersion is
0.738 +- 0.049 against Austen's 0.771 +- 0.010, so the ~0.77 figure is not peculiar to
one novel.

A section mixture would inflate dispersion without any randomness, and does not: only
9.2% of the variance is between the book's nine sections, and the within-section figure
is 0.956 against the pooled 0.972.

    python what_the_marks_space_like.py
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

from does_the_cipher_restart import body_blocks  # noqa: E402
from profile_around_a_mark import author_spans  # noqa: E402
from sentences_do_not_end_long import (  # noqa: E402
    SENTENCE_MARKS,
    join,
    prose_sentences,
)

DRAWS = 600


def body_spans() -> tuple[np.ndarray, int]:
    """Blocks per run between consecutive sentence marks, and the total block count."""
    blocks = body_blocks(SENTENCE_MARKS)
    spans, current = [], []
    for _, follows_mark in blocks:
        if follows_mark and current:
            spans.append(current)
            current = []
        current.append(1)
    if current:
        spans.append(current)
    return np.array([len(s) for s in spans], float), len(blocks)


def cv(v) -> float:
    return float(v.std(ddof=1) / v.mean())


def cv_jackknife(v) -> tuple[float, float]:
    """Spans are the independent unit, and pages here are heterogeneous, so jackknife."""
    n = len(v)
    drop = np.array([cv(np.delete(v, k)) for k in range(n)])
    return cv(v), math.sqrt((n - 1) / n * ((drop - drop.mean()) ** 2).sum())


def random_spans(rng, n_blocks: int, n_marks: int) -> np.ndarray:
    """Marks dropped uniformly at random on block boundaries."""
    cuts = sorted(rng.sample(range(1, n_blocks), n_marks - 1))
    out, previous = [], 0
    for c in cuts:
        out.append(c - previous)
        previous = c
    out.append(n_blocks - previous)
    return np.array(out, float)


def english_spans(rng) -> np.ndarray:
    """Austen's sentences in blocks, with the body's own joining model applied."""
    return np.array(
        [len(join(s, 0.40, rng, forward=True)) for s in prose_sentences()], float
    )


def shape_distance(v, reference) -> float:
    """KS distance after dividing out the mean, so density is not part of the test."""
    return float(stats.ks_2samp(v / v.mean(), reference / reference.mean()).statistic)


def two_armed(observed, reference, n, n_blocks, n_marks, label) -> None:
    """Score the body's shape under BOTH models, never a single tail."""
    under_ref = np.array(
        [
            shape_distance(
                np.array(random.Random(i).choices(list(reference), k=n), float),
                reference,
            )
            for i in range(DRAWS)
        ]
    )
    under_random = np.array(
        [
            shape_distance(
                random_spans(random.Random(9000 + i), n_blocks, n_marks), reference
            )
            for i in range(DRAWS)
        ]
    )
    p_ref = max(float((under_ref >= observed).mean()), 1 / DRAWS)
    p_random = max(float((under_random >= observed).mean()), 1 / DRAWS)
    print(
        f"{label:<38}{observed:>8.3f}{p_ref:>12.3f}{p_random:>12.3f}"
        f"{f'{p_random / p_ref:.1f} : 1':>14}"
    )


def main() -> None:
    spans, n_blocks = body_spans()
    n_marks = len(spans)
    rng = random.Random(3301)
    english = english_spans(rng)
    author = np.array([len(s) for s in author_spans()], float)
    simulated = np.array(
        [cv(random_spans(random.Random(i), n_blocks, n_marks)) for i in range(DRAWS)]
    )

    print(
        "Dispersion of the gap between marks. Each reference carries its own error.\n"
    )
    print(f"{'text':<44}{'spans':>7}{'mean':>8}{'CV':>18}")
    for label, v in (
        ("the LP body, between sentence marks", spans),
        ("the LP author's own pages, between periods", author),
        ("Pride and Prejudice, joined q=0.40", english),
    ):
        c, se = cv_jackknife(v)
        print(f"{label:<44}{len(v):>7}{v.mean():>8.1f}{f'{c:.3f} +- {se:.3f}':>18}")
    print(
        f"{'marks placed at random (simulated)':<44}{n_marks:>7}"
        f"{n_blocks / n_marks:>8.1f}"
        f"{f'{simulated.mean():.3f} +- {simulated.std(ddof=1):.3f}':>18}"
    )
    print(
        f"{'mechanical, a mark every 19.6 blocks':<44}{n_marks:>7}"
        f"{n_blocks / n_marks:>8.1f}{'0.000':>18}"
    )

    body_cv, body_se = cv_jackknife(spans)
    print()
    for label, v in (
        ("the author's own pages", author),
        ("Pride and Prejudice", english),
    ):
        c, se = cv_jackknife(v)
        print(
            f"  body vs {label:<30} z = {(body_cv - c) / math.hypot(body_se, se):+.2f}"
        )
    print(
        f"  body vs {'random placement':<30} z = "
        f"{(body_cv - simulated.mean()) / math.hypot(body_se, simulated.std(ddof=1)):+.2f}"
    )
    print(f"  body vs {'mechanical placement':<30} z = {body_cv / body_se:+.2f}")

    print("\nShape, with the mean divided out so density is not part of the test.\n")
    print(f"{'reference':<38}{'body D':>8}{'P|ref':>12}{'P|random':>12}{'ratio':>14}")
    two_armed(
        shape_distance(spans, english),
        english,
        n_marks,
        n_blocks,
        n_marks,
        "Pride and Prejudice, 5,361 sentences",
    )
    two_armed(
        shape_distance(spans, author),
        author,
        n_marks,
        n_blocks,
        n_marks,
        "the LP author's own 92 sentences",
    )

    print(
        "\nMechanical placement is dead. Between sentences and a memoryless process the"
        "\nbody sits on the memoryless one, but the number that says so loudly depends on"
        "\nAusten standing in for the LP's register, and the register-matched control is"
        "\ntoo small to confirm it. Read this as leaning, not settled."
    )


if __name__ == "__main__":
    main()
