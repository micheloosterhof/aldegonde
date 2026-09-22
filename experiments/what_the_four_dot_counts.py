# ABOUTME: Tests whether the four-dot is clocked by runes or by blocks, using the
# ABOUTME: length bias a rune clock forces on the block it lands after.
"""A mark placed by letter count lands after long blocks more often. The four-dot does not.

Everything measured about the four-dot's *spacing* has used a rate per rune.
`is_the_four_dot_placed_per_page.py` fits its count per page to a constant per-rune rate
and gets P = 0.406; `the_four_dot_has_a_floor.py` counts its gaps in blocks. Nothing has
asked which of the two the mark actually counts, and the two models are separable without
any reference text.

## The prediction

A **rune clock** drops a mark when a letter countdown expires. The block it lands after is
therefore sampled in proportion to its length -- a size-biased draw -- so its mean exceeds
the corpus mean by exactly var/mean:

    the body's blocks      mean 4.426, var 5.347   ->   size-biased mean 5.634

A **block clock** drops a mark at a block boundary at a constant rate per boundary. It
samples blocks uniformly, so the block before a mark has the corpus mean, 4.426.

The two differ by **1.21 runes**, and the body's 139 four-dots resolve 0.20. This is the
same cell as the sentence-final lengthening statistic, read against a different model: a
rune clock predicts lengthening for a reason that has nothing to do with language.

## Result: the rune clock is excluded in the body and fits the author exactly

    corpus                    observed        rune clock        block clock
    the body's four-dot     4.165 +- 0.187   5.631  z = -4.9   4.428  z = -1.0
    the author's marks      5.426 +- 0.239   5.182  z = +0.7   4.012  z = +4.5

The body's four-dot is **not rune-clocked**. That removes the last reading in which the
mark is a production quantity measured off the page: a scribe marking every so many
letters would leave this bias, and there is none. The mark is consistent with a block
clock, sitting 1.0 sigma below it -- the short-block lean already recorded as the -0.24
sentence-final gap.

## The author's lengthening is arithmetic, not only linguistic

His marks lengthen by **+1.42** and his own size bias predicts **+1.18**. A verified
sentence mark and a letter countdown make the same prediction on his pages, and the
observed value sits 0.7 sigma from the countdown.

That is a degeneracy, not a claim that he counted letters -- `what_the_authors_mark_means.py`
verifies his mark against an English transcription outside the repository, 26 of 32 at
sentence ends. What it changes is what his +1.39 may be quoted for. **It is not evidence
that sentence marks lengthen more than an arbitrary length-proportional mark**, because
they do not. The comparison against the body survives only because the body shows neither
effect.

## What this tightens

The body's missing lengthening now excludes two models with one number, not one. It was
read as "the four-dot is not a sentence mark". It also says the four-dot is not placed by
any rule that samples blocks in proportion to their length -- letter counts, line
measures, column widths, or anything else that counts glyphs rather than words.

    python what_the_four_dot_counts.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, blocks  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

DRAWS = 4000


def rune_clocked(lengths, count, rng):
    """Mean length of the blocks a letter countdown expires inside.

    A scribe counting letters cannot mark mid-block: the mark goes at the end of the
    block the count falls in, so that block is drawn in proportion to its length.
    """
    ends = np.cumsum(lengths)
    total = float(ends[-1])
    period = total / count
    picked = []
    for _ in range(DRAWS):
        targets = (rng.random() * period) + period * np.arange(count)
        hit = np.searchsorted(ends, targets, side="left")
        picked.append(
            float(np.mean(np.asarray(lengths, float)[hit[hit < len(lengths)]]))
        )
    return np.array(picked)


def block_clocked(lengths, count, rng):
    """Mean length of `count` blocks drawn uniformly."""
    return np.array([float(np.mean(rng.sample(lengths, count))) for _ in range(DRAWS)])


def report(label, lengths, before):
    n = len(before)
    observed = float(np.mean(before))
    mean = float(np.mean(lengths))
    var = float(np.var(lengths, ddof=1))
    se = float(np.std(before, ddof=1)) / np.sqrt(n)
    print(f"\n{label}: {len(lengths):,} blocks, mean {mean:.3f}, var {var:.3f}")
    print(f"  {n} marks, the block before them averages {observed:.3f} +- {se:.3f}\n")
    print(f"  {'model':<26}{'predicted':>11}{'spread':>9}{'z':>8}")
    rng = random.Random(3301)
    for name, arm in (
        ("a rune clock", rune_clocked(lengths, n, rng)),
        ("a block clock", block_clocked(lengths, n, rng)),
    ):
        spread = float(np.hypot(arm.std(ddof=1), se))
        print(
            f"  {name:<26}{arm.mean():>11.3f}{spread:>9.3f}"
            f"{(observed - arm.mean()) / spread:>8.1f}"
        )
    return observed - mean


def main() -> None:
    rows = blocks(BODY)
    body = [n for n, _, _ in rows]
    four = [n for n, glyph, _ in rows if glyph == "④"]
    report("the body, four-dot", body, four)

    spans = author_spans()
    author = [n for s in spans for n in s]
    author_final = [s[-1] for s in spans]
    gap = report("the author, sentence marks", author, author_final)

    mean = float(np.mean(author))
    bias = float(np.var(author, ddof=1)) / mean
    print(
        f"\n  His marks lengthen by {gap:+.2f} and his size bias alone gives {bias:+.2f}."
        "\n  A sentence mark and a rune clock are degenerate wherever a mark lengthens."
        "\n  They separate only where it does not, and there both are excluded."
    )


if __name__ == "__main__":
    main()
