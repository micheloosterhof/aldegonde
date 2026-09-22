# ABOUTME: Prices every channel tried against the four-dot question, giving the corpus
# ABOUTME: multiple each would need to separate the surviving readings at three sigma.
"""Nine statistics have been tried on one question. This prices them all at once.

Three readings of the four-dot survive (`sentences-do-not-end-long.md`):

1. **not a sentence mark** -- it divides the text somewhere other than at sentence ends;
2. **the words are transposed** within each span before encipherment;
3. **a variably displaced stop** -- written a block or two off the true sentence end.

All three predict a flat profile at the mark, which is why test after test has come back
empty. What has not been done is to ask, for each channel, **how much corpus would be
needed** rather than whether this corpus suffices. That turns a series of null results
into one decision: keep pushing, or stop.

## Two different jobs

A channel can do either of two things and they need separating:

- **Detect the anomaly**: tell reading 1, 2 or 3 apart from "ordinary English at the
  mark". Several channels do this comfortably.
- **Separate the readings**: tell 2 or 3 apart from 1. This is the open question and no
  channel has managed it.

For each channel the script computes the two arms from the data, the body's own standard
error, and the corpus multiple `N` at which the arms would be three sigma apart, on the
assumption that the error falls as the square root of the corpus.

## Result

**Job 1, detecting the anomaly.** Author against body:

| channel | order intact | the body | sigma | N for 3s |
|---|---|---|---|---|
| span-final mean lift | +1.320 +- 0.265 | -0.291 +- 0.199 | **-4.86** | 0.38 |
| span-final 7+ share | +0.140 +- 0.052 | -0.036 +- 0.033 | **-2.86** | 1.10 |
| length lag-1 correlation | -0.029 +- 0.030 | -0.009 +- 0.019 | +0.57 | 25 |

The first two work and carry every result about the four-dot.

**Job 2, separating the readings.** Each corpus scored against its own within-span
shuffle, which is exactly what the transposition reading predicts:

| corpus | span length | observed | its own shuffle | excess | sigma |
|---|---|---|---|---|---|
| the body | 21.1 | -0.0087 | +0.0058 +- 0.0180 | -0.0145 | -0.81 |
| the joined author | 8.4 | -0.0271 | -0.0051 +- 0.0393 | -0.0220 | -0.56 |

**The reference cannot be told from a full shuffle.** The author's own excess is 0.56
sigma. So the arm separation is not merely smaller than the body's error; it is
unmeasured. Taking his -0.0220 as the gap, three sigma needs about 6 times this corpus,
and establishing the gap itself needs 29 times his solved pages.

The body's excess is -0.0145 +- 0.0180: consistent with a full rearrangement and equally
consistent with the author's value.

## Two errors this file had to fix first

**A single JOINING draw is not a measurement either**, and this one was caught by
re-running the file rather than by inspection. The joining is stochastic and the author
has only 94 spans, so one draw is worth +-0.030 on his lag-1 -- over 200 draws it runs
-0.029 +- 0.030, from -0.110 to +0.061. An unrelated edit that changed how much the shared
random stream had been consumed flipped the reported value from -0.046 to +0.042 and its
excess from -0.029 to +0.047, reversing the sign. The author's side is now averaged over
120 joining draws.

**A single shuffle is not an arm.** The first version drew one within-span shuffle and
read -0.085 off it. The shuffle distribution has sd 0.039, so that was a two-sigma draw
reported as a measurement.

**The shuffle baseline depends on span length.** A random permutation of a span of length
L has expected lag-1 correlation -1/(L-1): about -0.05 for the body's 21-block spans and
-0.14 for the author's 8-block ones. Comparing the body against an arm built on the
author's shorter spans mixes that bias into the answer. Scoring each corpus against its
own shuffle removes it.

This also supersedes the 4.7x figure in `order_survives_in_the_lengths.py`, which used an
arm gap of 0.026 estimated without either correction.

## Verdict

The span-final channels detect the anomaly at 2.9 to 4.9 sigma and separate the readings
not at all, because both predict an ordinary interior block there. The lag-1 channel is
the only one that distinguishes them in principle, and neither the corpus nor the
reference is large enough to use it.

    python what_would_it_take.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from order_survives_in_the_lengths import serial  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

LONG = 7
TARGET = 3.0
SHUFFLES = 400
JOIN_DRAWS = 120
JOIN_RATE = 0.40


def shuffled(spans, rng):
    out = []
    for s in spans:
        s = list(s)
        rng.shuffle(s)
        out.append(s)
    return out


def final_mean(spans):
    kept = [s for s in spans if len(s) >= 3]
    last = np.array([s[-1] for s in kept], float)
    interior = np.array([x for s in kept for x in s[1:-1]], float)
    se = math.hypot(
        last.std(ddof=1) / math.sqrt(len(last)),
        interior.std(ddof=1) / math.sqrt(len(interior)),
    )
    return float(last.mean() - interior.mean()), se


def final_tail(spans):
    kept = [s for s in spans if len(s) >= 3]
    last = np.array([s[-1] for s in kept], float)
    interior = np.array([x for s in kept for x in s[1:-1]], float)
    pl, pi = float((last >= LONG).mean()), float((interior >= LONG).mean())
    se = math.sqrt(pl * (1 - pl) / len(last) + pi * (1 - pi) / len(interior))
    return pl - pi, se


def lag_one(spans):
    r, n = serial(spans, 1)
    return r, 1 / math.sqrt(max(n - 3, 1))


def multiple(gap, se, target=TARGET) -> float:
    """Corpus multiple at which `gap` reaches `target` sigma, error falling as sqrt(N)."""
    if gap <= 0:
        return float("inf")
    return (target * se / gap) ** 2


def main() -> None:
    rng = random.Random(3301)
    body, author = body_spans(), author_spans()
    def joined(seed):
        r = random.Random(seed)
        return [
            s
            for s in (join(list(x), JOIN_RATE, r, forward=True) for x in author)
            if len(s) >= 3
        ]

    joined_author = joined(0)

    print("JOB 1. Detect the anomaly: order intact against the body as observed.\n")
    print(
        f"{'channel':<30}{'order intact':>18}{'the body':>18}{'sigma':>8}{'N for 3s':>10}"
    )
    rows = []
    for label, fn in (
        ("span-final mean lift", final_mean),
        ("span-final 7+ share", final_tail),
    ):
        a, sa = fn(author)
        b, sb = fn(body)
        se = math.hypot(sa, sb)
        rows.append((label, a, sa, b, sb))
        print(
            f"{label:<30}{f'{a:+.3f} +- {sa:.3f}':>18}{f'{b:+.3f} +- {sb:.3f}':>18}"
            f"{(b - a) / se:>+8.2f}{multiple(abs(a - b), se):>10.2f}"
        )
    draws = np.array([serial(joined(s), 1)[0] for s in range(JOIN_DRAWS)])
    r_a, s_a = float(draws.mean()), float(draws.std(ddof=1))
    r_b, s_b = lag_one(body)
    se = math.hypot(s_a, s_b)
    print(
        f"{'length lag-1 correlation':<30}{f'{r_a:+.3f} +- {s_a:.3f}':>18}"
        f"{f'{r_b:+.3f} +- {s_b:.3f}':>18}{(r_b - r_a) / se:>+8.2f}"
        f"{multiple(abs(r_a - r_b), se):>10.2f}"
    )

    print(
        "\n  The first two already work. Every result about the four-dot rests on them."
    )

    print("\n\nJOB 2. Separate the readings: rearranged against not-a-sentence-mark.\n")
    print("Each corpus is scored against ITS OWN within-span shuffle, which is what the")
    print("transposition reading predicts exactly. That baseline matters: a random")
    print("permutation of a span of length L has expected lag-1 correlation -1/(L-1),")
    print("so an arm built on the author's 8-block spans is not comparable with the")
    print("body's 21-block ones. And it must be averaged: one shuffle has sd 0.039.\n")
    print(
        f"{'corpus':<22}{'span len':>10}{'observed':>11}{'its own shuffle':>20}"
        f"{'excess':>10}{'sigma':>8}"
    )
    excesses = {}
    for label, spans in (("the body", body), ("the joined author", joined_author)):
        if label.endswith("author"):
            # the joining is stochastic and the author has only 94 spans, so one draw
            # is worth +-0.030 on this statistic -- enough to flip its sign
            obs = float(np.mean([serial(joined(s), 1)[0] for s in range(JOIN_DRAWS)]))
            cuts = [
                serial(shuffled(joined(s), rng), 1)[0] for s in range(JOIN_DRAWS)
            ]
            draws = np.array(cuts)
        else:
            draws = np.array(
                [serial(shuffled(spans, rng), 1)[0] for _ in range(SHUFFLES)]
            )
            obs = serial(spans, 1)[0]
        excesses[label] = (obs - draws.mean(), float(draws.std(ddof=1)))
        print(
            f"{label:<22}{np.mean([len(s) for s in spans]):>10.1f}{obs:>+11.4f}"
            f"{f'{draws.mean():+.4f} +- {draws.std(ddof=1):.4f}':>20}"
            f"{obs - draws.mean():>+10.4f}"
            f"{(obs - draws.mean()) / draws.std(ddof=1):>+8.2f}"
        )

    gap, se_body = excesses["the body"]
    ref, se_ref = excesses["the joined author"]
    print(
        f"\n  The author's own excess over his shuffle is {ref:+.4f} at"
        f" {abs(ref) / se_ref:.2f} sigma."
        "\n  **The reference itself cannot be told from a full shuffle.** So the arm"
        "\n  separation is not merely larger than the body's error -- it is unmeasured."
        f"\n\n  Taking {abs(ref):.4f} as the arm gap and the body's {se_body:.4f} as its"
        f" error,\n  three-sigma separation needs {multiple(abs(ref), se_body):.0f} times"
        " this corpus. Establishing the arm\n  itself would need"
        f" {multiple(abs(ref), se_ref):.0f} times the author's solved pages."
    )
    print(
        f"\n  The body's own excess is {gap:+.4f} +- {se_body:.4f},"
        f" {abs(gap) / se_body:.2f} sigma: consistent with a"
        "\n  full rearrangement and equally consistent with the author's value."
    )

    print(
        "\n\nVERDICT. The span-final channels detect the anomaly at 2.9 to 4.9 sigma and"
        "\nseparate the readings not at all, because both predict an ordinary interior"
        "\nblock there. The lag-1 channel is the only one that distinguishes them in"
        "\nprinciple, and neither the corpus nor the reference is large enough to use it."
    )


if __name__ == "__main__":
    main()
