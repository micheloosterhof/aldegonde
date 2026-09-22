# ABOUTME: Tests the most attractive form of the mixture -- that the four-dots the scribe
# ABOUTME: set apart physically are the genuine sentence ends -- with the rank statistic.
"""If some four-dots are real, the ones the scribe noticed are the candidates.

`the_rank_of_the_last_block.py` bounds the mixture globally: at most a sixth of four-dots
can be genuine sentence ends, f < 0.17 at two sigma. That leaves a small mixture alive,
and the physical evidence points at roughly that size -- the four-dot takes a line break
10.6% of the time against a word separator's 3.9%, +4.02 sigma
(`the-four-dot-is-not-layout-coupled.md`).

The attractive reading is that these are the same marks: **the scribe broke his line at
the four-dots that really do end a sentence.** That is directly testable and it is the
version worth killing or keeping, because it would name which marks to trust.

## The instrument

The rank of a span's last block among that span's own blocks. Reference-free -- the span's
multiset is its own control -- and the only statistic here sensitive to a minority. A
genuine sentence end reads 0.647 on the author's pages against 0.500 for a random block.

Three outcomes, and they are far apart:

- **all fourteen line-end four-dots are real**: mean rank near 0.647;
- **none are**: 0.500;
- something between: proportionally between.

## Result: they are not

| subset | n | mean rank | a random block of the same spans | z |
|---|---|---|---|---|
| the author, all spans | 68 | **0.647** | 0.500 +- 0.030 | **+4.93** |
| **closed AT a line end** | 14 | **0.501** | 0.500 +- 0.068 | **+0.01** |
| closed mid-line | 110 | 0.490 | 0.500 +- 0.024 | -0.41 |

**The line-end subset is dead uniform.** If all fourteen were genuine sentence ends the
subset would read 0.647; it reads 0.501, **2.17 sigma away**, a likelihood ratio of about
**10 to 1 for "none of them" over "all of them"**.

## What this costs the mixture

The global bound leaves a small mixture alive (f < 0.17), and the obvious way to find it
was to follow the scribe: the marks he set apart physically are the ones he noticed, so
they are the candidates. **That version is now disfavoured at 10 to 1.**

Whatever makes him break his line at a four-dot, it is not that the four-dot ends a heavy
word. The coupling is real -- 10.6% against a separator's 3.9%, +4.02 sigma -- and it does
not track sentence-final lengthening.

## What survives

A mixture that the scribe's layout does **not** flag. Nothing in this corpus identifies
which marks those would be, so it is unfalsifiable with what is here rather than refuted:
the global bound still allows one four-dot in six, and no channel can point at them.

## Limits

Fourteen marks. The test separates "all" from "none" at 2.17 sigma and cannot resolve
anything between: a subset in which half were real would read 0.574 and sit one sigma from
both hypotheses. Ruling out the intermediate cases needs the same 2.4x corpus every other
route to this question has needed.

    python are_the_special_four_dots_the_real_ones.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, blocks  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

MIN_SPAN = 4
CLOSERS = "④⑬③⑩㉓"
DRAWS = 3000


def scaled_rank(span, value) -> float:
    below = sum(1 for x in span if x < value)
    equal = sum(1 for x in span if x == value)
    return (below + (equal + 1) / 2) / (len(span) + 1)


def four_dot_spans():
    """(span, closing mark at a line end?) for spans closed by a four-dot."""
    out, cur = [], []
    for n, glyph, line_end in blocks(BODY):
        cur.append(n)
        if glyph in CLOSERS:
            if len(cur) >= MIN_SPAN and glyph == "④":
                out.append((cur, line_end))
            cur = []
    return out


def rank_lift(spans, rng):
    """Mean rank of the last block, against a block drawn from the same spans."""
    observed = float(np.mean([scaled_rank(s, s[-1]) for s in spans]))
    null = np.array(
        [
            np.mean([scaled_rank(s, s[rng.integers(len(s))]) for s in spans])
            for _ in range(DRAWS)
        ]
    )
    return observed, float(null.mean()), float(null.std(ddof=1))


def main() -> None:
    rng = np.random.default_rng(3301)
    spans = four_dot_spans()
    at_end = [s for s, le in spans if le]
    mid = [s for s, le in spans if not le]
    author = [s for s in author_spans() if len(s) >= MIN_SPAN]

    print(f"{len(at_end)} four-dot spans closed at a line end, {len(mid)} mid-line.\n")
    print(f"{'subset':<26}{'n':>5}{'mean rank':>11}{'a random block':>20}{'z':>8}")
    cells = {}
    for label, group in (
        ("the author, all spans", author),
        ("closed AT a line end", at_end),
        ("closed mid-line", mid),
    ):
        obs, mean, sd = rank_lift(group, rng)
        cells[label] = (obs, mean, sd, len(group))
        print(
            f"{label:<26}{len(group):>5}{obs:>11.3f}"
            f"{f'{mean:.3f} +- {sd:.3f}':>20}{(obs - mean) / sd:>8.2f}"
        )

    a_obs, a_mean, _, _ = cells["the author, all spans"]
    lift = a_obs - a_mean
    obs, mean, sd, n = cells["closed AT a line end"]
    predicted = mean + lift
    z = (predicted - obs) / sd
    print(
        f"\nIf every one of the {n} line-end four-dots were a real sentence end, the"
        f"\nsubset would read {predicted:.3f}. It reads {obs:.3f}, which is"
        f" {z:.2f} sigma away."
        f"\n\n  likelihood ratio for 'none of them' over 'all of them':"
        f" {math.exp(z * z / 2):.0f} to 1"
    )
    print(
        "\nSo whatever makes the scribe break his line at a four-dot, it is not that the"
        "\nfour-dot ends a heavy word. The line-break coupling is real and it does not"
        "\ntrack sentence-final lengthening."
    )


if __name__ == "__main__":
    main()
