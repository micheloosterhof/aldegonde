# ABOUTME: Re-runs the session's chi-squared headline results over many joining seeds to
# ABOUTME: separate their real spread from the single-draw values that were reported.
"""A single stochastic draw was reported as a measurement twice. This checks the rest.

`what_would_it_take.py` reported the LP author's lag-1 correlation from one joining draw.
The joining is stochastic and he has only 94 spans, so a draw is worth +-0.030 -- and an
unrelated edit, by changing how much of a shared random stream had been consumed, flipped
the value from -0.046 to +0.042 and reversed the sign of the conclusion. Before that,
`what_would_it_take.py` had used one within-span shuffle as an arm when its standard
deviation is 0.039.

Two headline results have the same shape. Both apply the body's joining model to the ten
reference registers **once** and read a chi-squared off the result:

- `which_structured_permutation.py`: identity word order excluded at chi2 = 38.5 on eight
  cells, P = 2e-6, which is the sentence-final anomaly in its strongest published form;
- `can_joining_alone_flatten_the_edge.py`: every joining convention rejected at
  P <= 0.001, best arm 26.2 against the transposition arm's 9.7.

If those chi-squared values swing with the joining seed, the P values are wrong.

## What is measured

Each arm is rebuilt from scratch under many independent joining seeds and its chi-squared
recorded. Reported are the median, the spread, and where the previously published
single-draw value sits in that distribution. A published value near the middle is safe; a
value in the tail was luck.

## Result: both hold, and the reason tells you where to look next time

Forty independent joining seeds per arm.

| rule | published | median | spread | range | percentile of the published value |
|---|---|---|---|---|---|
| identity | 38.5 | 39.6 | 0.6 | 38.5 to 40.9 | 0.00 |
| reverse | 28.7 | 28.1 | 0.5 | 26.9 to 29.2 | 0.90 |
| full shuffle | 8.5 | 9.7 | 0.6 | 8.2 to 10.8 | 0.05 |
| keep first, reverse rest | 7.5 | 7.6 | 0.1 | 7.5 to 8.0 | 0.03 |

| joining arm | published | median | spread | range |
|---|---|---|---|---|
| join within the span, forward, <=2 | 38.5 | 39.6 | 0.6 | 38.5 to 40.9 |
| join within the span, forward, <=3 | 26.2 | 26.5 | 0.6 | 25.5 to 28.0 |
| shuffle within the span, then join | 9.7 | 9.6 | 0.5 | 8.7 to 10.8 |

**A spread of 0.6 on a chi-squared of 39.6 does not move a P value.** Identity stays
excluded at 2e-6 and every joining convention stays rejected. Three of the four published
values sit near the bottom of their range, so the reported figures were mildly lucky in
the direction of a *smaller* gap between identity and the shuffle -- the true gap is
39.6 - 9.7 = 29.9 against the published 38.5 - 8.5 = 30.0, which is the same.

## Why these were safe and the author's lag-1 was not

The difference is the size of the reference, not the kind of statistic.

| statistic | reference | draw-to-draw spread | relative to the value |
|---|---|---|---|
| chi2 of a rule | ten registers, 30,281 sentences | 0.6 on 39.6 | **1.5%** |
| the author's lag-1 | his 94 spans | 0.030 on 0.029 | **100%** |

Pooling ten registers averages the joining noise away before the statistic is formed. The
author's 94 spans do not. **The rule is not "average over seeds" in general -- it is
"average over seeds whenever the reference is small", and the threshold is visible in
advance from the reference's size.**

    python are_the_headline_numbers_seed_stable.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from can_joining_alone_flatten_the_edge import (  # noqa: E402
    body_fingerprint,
    join_within,
    score,
    shuffle_within,
)
from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from which_structured_permutation import RULES, apply_rule  # noqa: E402
from which_structured_permutation import fingerprint as span_fingerprint  # noqa: E402

SEEDS = 40
JOIN_RATE = 0.40
WATCH = ("identity", "reverse", "full shuffle", "keep first, reverse rest")


def raw_registers(rng):
    return [
        register_spans(p, rng, join_rate=0.0)
        for p in (fetch(n) for n in REGISTERS)
        if p is not None
    ]


def chi_for(rule, raw, observed, body_se, seed):
    rng = random.Random(seed)
    prints = np.array([span_fingerprint(apply_rule(s, rule, rng)) for s in raw])
    mean, spread = prints.mean(axis=0), prints.std(axis=0, ddof=1)
    return float((((observed - mean) / np.hypot(body_se, spread)) ** 2).sum())


def main() -> None:
    raw = raw_registers(random.Random(11))
    observed, body_se = body_fingerprint()
    rules = dict(RULES)

    print(f"Each arm rebuilt under {SEEDS} independent joining seeds.\n")
    print(
        f"{'rule':<28}{'published':>11}{'median':>9}{'spread':>9}"
        f"{'range':>17}{'percentile':>12}"
    )
    published = {
        "identity": 38.5,
        "reverse": 28.7,
        "full shuffle": 8.5,
        "keep first, reverse rest": 7.5,
    }
    for name in WATCH:
        vals = np.array(
            [chi_for(rules[name], raw, observed, body_se, s) for s in range(SEEDS)]
        )
        pub = published[name]
        pct = float((vals <= pub).mean())
        print(
            f"{name:<28}{pub:>11.1f}{np.median(vals):>9.1f}{vals.std(ddof=1):>9.1f}"
            f"{f'{vals.min():.1f} to {vals.max():.1f}':>17}{pct:>12.2f}"
        )

    print("\nThe joining arms, same treatment.\n")
    print(f"{'arm':<40}{'published':>11}{'median':>9}{'spread':>9}{'range':>17}")
    arms = (
        (
            "join within the span, forward, <=2",
            lambda s, r: join_within(s, JOIN_RATE, 2, r, forward=True),
            38.5,
        ),
        (
            "join within the span, forward, <=3",
            lambda s, r: join_within(s, JOIN_RATE, 3, r, forward=True),
            26.2,
        ),
        (
            "SHUFFLE within the span, then join",
            lambda s, r: join_within(
                shuffle_within(s, r), JOIN_RATE, 2, r, forward=True
            ),
            9.7,
        ),
    )
    for label, build, pub in arms:
        vals = np.array(
            [
                score(raw, build, observed, body_se, random.Random(s))[2]
                for s in range(SEEDS)
            ]
        )
        print(
            f"{label:<40}{pub:>11.1f}{np.median(vals):>9.1f}{vals.std(ddof=1):>9.1f}"
            f"{f'{vals.min():.1f} to {vals.max():.1f}':>17}"
        )


if __name__ == "__main__":
    main()
