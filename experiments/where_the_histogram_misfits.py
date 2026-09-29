# ABOUTME: Localises the residual between the body's block-length histogram and the best
# ABOUTME: merge model, testing whether the misfit is consistent across reference registers.
"""One short-unit rule gets most of the way and misses. Where, exactly?

`merged_or_telegraphic.py` fits merging and omitting to the body's 2-rune fraction and
scores the rest of the histogram. The best case is chi2 15.9 on about ten degrees of
freedom, P = 0.10, and the register-matched author base gives 32.8, P = 0.0003. So the
deficit model earns most of the distance from the raw registers' 105.2 and still does not
fit. That file could not say where it fails.

The residuals did not look like a smooth tail excess. Against the author base the body ran
**+0.023 at length 5, -0.016 at 6, +0.008 at 8** -- alternating rather than monotone,
which a mis-set merge rate cannot produce.

Two readings, and they are distinguishable:

- **noise.** With 2,928 blocks a cell at 0.10 has a standard error of 0.0055, so +0.023 is
  four sigma against ONE base -- but five bases give five chances at each of eleven cells,
  and the between-register spread is already known to be large.
- **structure.** If the same cells miss in the same direction against every base, the
  pattern belongs to the body and not to the choice of reference.

The test is consistency. Each base is fitted separately, and the residual is reported per
cell with the spread across bases beside it.

## Result: the structure was the reference, not the body

Six reference texts, each fitted separately to the body's 2-rune fraction.

| length | the body | mean residual | spread | sign agreement | z |
|---|---|---|---|---|---|
| 1 | 0.0287 | +0.0064 | 0.0082 | 67% | +1.40 |
| 2 | 0.1547 | -0.0004 | 0.0017 | 83% | -0.06 |
| 3 | 0.2486 | +0.0183 | 0.0190 | 83% | +1.64 |
| 4 | 0.1771 | +0.0039 | 0.0124 | 67% | +0.45 |
| **5** | 0.1095 | **-0.0013** | 0.0140 | **50%** | -0.16 |
| 6 | 0.0884 | -0.0117 | 0.0030 | **100%** | -2.17 |
| 7 | 0.0746 | +0.0042 | 0.0064 | 67% | +0.75 |
| 8 | 0.0539 | +0.0021 | 0.0066 | 67% | +0.42 |
| 9 | 0.0269 | -0.0101 | 0.0072 | **100%** | -2.41 |
| 10 | 0.0180 | -0.0044 | 0.0061 | 83% | -1.26 |
| 11+ | 0.0197 | -0.0068 | 0.0096 | 83% | -1.46 |

**No cell misses consistently.** The +0.023 at length 5 that motivated this file was
measured against the author base alone; across six bases the mean residual there is
-0.0013 and the sign agreement is **50%**, which is a coin toss. The apparent +5 / -6 / +8
alternation belonged to the choice of reference.

Two cells are the only candidates: lengths 6 and 9, both with all six references on the
same side, at z = -2.17 and -2.41, the body low in each. On eleven cells neither survives
its own multiple testing, and they are recorded as candidates rather than findings.

So the misfit that `merged_or_telegraphic.py` measured is **spread across the histogram
and register-dependent**, not localised. Identifying what shapes the body's length
distribution beyond a short-unit rule needs a reference this corpus does not have, which
is the same wall `what_would_it_take.py` reaches from the other side.

    python where_the_histogram_misfits.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from merged_or_telegraphic import CELLS, fit, histogram, merge  # noqa: E402
from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

REPS = 10
CAP = 20000


def main() -> None:
    rng = random.Random(3301)
    body = [x for s in body_spans() for x in s]
    obs = histogram(body)
    n = len(body)
    target = float(np.mean(np.array(body) == 2))

    bases = [("the author", [x for s in author_spans() for x in s])]
    for number in REGISTERS[:5]:
        p = fetch(number)
        if p is not None:
            words = [x for s in register_spans(p, rng, 0.0) for x in s]
            bases.append((f"pg{number}", words[:CAP]))

    residuals = []
    for _, words in bases:
        rate = fit(words, merge, target, rng)
        probs = np.mean(
            [histogram(merge(words, rate, rng)) for _ in range(REPS)], axis=0
        )
        residuals.append(obs - probs)
    residuals = np.array(residuals)

    print(f"{len(bases)} reference texts, each fitted to the body's 2-rune fraction.")
    print(f"The body has {n:,} blocks, so a cell near 0.10 carries +-0.0055.\n")
    print(
        f"{'length':>7}{'the body':>10}{'mean residual':>16}{'spread':>9}"
        f"{'sign agreement':>16}{'z':>8}"
    )
    flagged = []
    for i, k in enumerate(CELLS):
        column = residuals[:, i]
        mean = float(column.mean())
        spread = float(column.std(ddof=1))
        agree = max((column > 0).sum(), (column < 0).sum()) / len(column)
        se = math.hypot(
            spread / math.sqrt(len(column)), math.sqrt(obs[i] * (1 - obs[i]) / n)
        )
        z = mean / se
        tag = f"{k}" if k < CELLS[-1] else f"{k}+"
        print(
            f"{tag:>7}{obs[i]:>10.4f}{mean:>+16.4f}{spread:>9.4f}"
            f"{agree:>16.0%}{z:>+8.2f}"
        )
        if abs(z) >= 2.5 and agree == 1.0:
            flagged.append((k, mean, z))

    print(
        "\n  'sign agreement' is the share of reference texts whose residual has the"
        "\n  majority sign. A cell that is real must be near 100%."
    )
    if flagged:
        print("\nCells that miss in the same direction against every reference:\n")
        for k, mean, z in flagged:
            print(f"  length {k:<4}{mean:+.4f}   z = {z:+.2f}")
    else:
        print("\nNo cell misses consistently against every reference.")


if __name__ == "__main__":
    main()
