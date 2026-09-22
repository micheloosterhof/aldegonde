# ABOUTME: Tests the mixture reading with the rank of a span's last block among its own
# ABOUTME: blocks, which is reference-free and sensitive to a minority where a mean is not.
"""A mean cannot see a minority. A rank distribution can.

The mixture reading (`are_some_four_dots_real.py`) says some four-dots are real sentence
ends and some are not, so the pooled gap is an average over two kinds. Every test of it so
far has used a **mean**, and a mean is the wrong instrument: if one span in five ends on a
genuinely heavy word and the rest end anywhere, the mean moves by a fifth of the effect
and drowns.

The rank does not. For each span, take the rank of its **last** block among that span's own
blocks, scaled to [0, 1]. Under no positional structure the rank is uniform by
construction -- the span's multiset is its own reference, so this needs no English, no
joining model and no matched register, the problem that has capped almost everything here.

Under a mixture, the fraction of spans that really do end on their heaviest word piles up
at the top of the distribution while the rest stay uniform. That is a spike in one cell,
which a mean smears across all of them.

## The cell I first chose was wrong, and the control said so

The obvious statistic is the share of spans whose last block lands in the **top tenth** of
its own span's ranks. It does not work, and the author shows why: his span-final block is
1.17 runes above a random block of the same span, yet only **0.044** of his spans put it in
the top tenth. Block lengths tie constantly -- a span of fourteen blocks holds perhaps six
distinct lengths -- so a midrank rarely reaches 0.9 however heavy the block is. His mass
sits in the 0.8 decile at 0.31.

A cell the positive control cannot fill is not a test. The **mean rank** is the statistic
that works.

## Result: at most a sixth of the four-dots can be sentence ends

Each corpus scored against its own spans: the mean rank of the last block, against the
mean rank of a block drawn uniformly from the same spans.

| corpus | spans | mean rank of the last block | a random block | z |
|---|---|---|---|---|
| **the author** | 68 | **0.647** | 0.500 +- 0.030 | **+4.97** |
| **the body** | 129 | **0.481** | 0.500 +- 0.023 | **-0.86** |

Taking the author's lift as what one genuine sentence end contributes, the body's lift
divided by his is the fraction of four-dots that could be real:

    f = -0.135 +- 0.153      f < 0.17 at two sigma,  f < 0.32 at three

**This is the first quantitative bound on the mixture.** Every earlier attempt used a mean
and returned +-0.85 on fourteen marks, which excluded nothing.

## What the bound leaves standing

A **large** mixture is dead: more than a sixth of the four-dots being genuine sentence ends
is excluded at two sigma.

A **small** one is not, and the physical evidence points at roughly that size. The four-dot
takes a line break 10.6% of the time against a separator's 3.9%
(`the-four-dot-is-not-layout-coupled.md`) and gets extra space in about one occurrence in
six. A mixture of one in ten would produce that coupling and sit comfortably inside
f < 0.17.

So the two lines of evidence are consistent rather than in tension, which they appeared to
be: **a minority of four-dots may be real sentence ends, and it is a minority small enough
that no length statistic in this corpus can confirm it.**

## Calibration

    python the_rank_of_the_last_block.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import spans  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

MIN_SPAN = 4
DECILES = 10


def ranks(rows):
    """Scaled rank of each span's last block among its own blocks, ties at midrank."""
    out = []
    for s in rows:
        if len(s) < MIN_SPAN:
            continue
        last = s[-1]
        below = sum(1 for x in s if x < last)
        equal = sum(1 for x in s if x == last)
        out.append((below + (equal + 1) / 2) / (len(s) + 1))
    return np.array(out, float)


def report(label, rows):
    r = ranks(rows)
    top = float((r >= 0.9).mean())
    expected = 0.1
    se = np.sqrt(expected * (1 - expected) / len(r))
    ks = stats.kstest(r, "uniform")
    print(
        f"{label:<22}{len(r):>7}{r.mean():>9.3f}{top:>12.3f}"
        f"{(top - expected) / se:>+9.2f}{ks.pvalue:>12.2e}"
    )
    return r


def main() -> None:
    body = spans({"④"}, minimum=MIN_SPAN)
    author = [s for s in author_spans() if len(s) >= MIN_SPAN]

    print("Rank of a span's last block among its own blocks, scaled to [0,1].")
    print("Uniform mean is 0.500 and the top tenth holds 0.100 by construction.\n")
    print(
        f"{'corpus':<22}{'spans':>7}{'mean rank':>9}{'top tenth':>12}"
        f"{'z':>9}{'KS P':>12}"
    )
    ra = report("the author", author)
    rb = report("the body", body)

    print("\nWhere each distribution puts its mass, by decile:\n")
    print(f"{'decile':<10}" + "".join(f"{i / 10:>6.1f}" for i in range(10)))
    for label, r in (("the author", ra), ("the body", rb)):
        counts = np.histogram(r, bins=10, range=(0, 1))[0] / len(r)
        print(f"{label:<10}" + "".join(f"{v:>6.2f}" for v in counts))

    top_b = int((rb >= 0.9).sum())
    n_b = len(rb)
    print(
        f"\nThe mixture predicts a spike in the top decile. The body has {top_b} spans"
        f" there\nof {n_b}, against {0.1 * n_b:.1f} expected."
    )
    for f in (0.1, 0.2, 0.3):
        predicted = 0.1 * n_b * (1 - f) + f * n_b
        z = (predicted - 0.1 * n_b) / np.sqrt(0.1 * 0.9 * n_b)
        print(
            f"  a mixture with {f:.0%} real sentence ends predicts about"
            f" {predicted:.0f} ({z:+.1f} sigma)"
        )


if __name__ == "__main__":
    main()
