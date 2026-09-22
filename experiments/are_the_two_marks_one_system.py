# ABOUTME: Tests whether the thirteen-dot falls at a four-dot boundary or independently
# ABOUTME: inside a four-dot span, using renewal geometry and the body's own gap law.
"""Two mark systems, and the question is whether they are one.

The thirteen-dot is a section boundary, confirmed from red ink
(`do_the_marks_bound_the_titles.py`): six of six mid-page rubricated titles are closed by
one, P = 9e-13. The four-dot is not a clause terminator: no lengthening before it
(-3.35 sigma against English), no line-break coupling (0.106 against the word separator's
0.115), and no match to any English punctuation class.

If the four-dot marks *something in the text*, a section end is also one of those
somethings, and a thirteen-dot should land where a four-dot span ends. If the four-dot
marks something unrelated to the text's divisions, a thirteen-dot falls wherever the
sections happen to fall, which is somewhere inside a four-dot span.

Those two are distinguishable by renewal geometry and need no reference corpus.

## The statistic

The number of blocks from the preceding four-dot to each thirteen-dot.

- **Nested**: a thirteen-dot sits at the end of a four-dot span, so the distance is a
  whole four-dot gap, drawn from the body's own gap law.
- **Independent**: a thirteen-dot sits at a random point inside a span, so the distance is
  the *backward recurrence time* of the four-dot process. That is length-biased -- a
  random point is more likely to land in a long span -- with mean E[L^2]/(2 E[L]) rather
  than E[L].

Both arms are built from the body's measured four-dot gaps, so the comparison carries no
assumption about English or about what a sentence is.

## Result: the test has no power, and the reason closes a family

| | n | mean | se | median |
|---|---|---|---|---|
| four-dot gaps | 137 | 21.40 | 1.88 | 14.0 |
| observed: previous ④ to each ⑬ | 28 | **31.82** | 5.62 | 18.0 |
| if nested (⑬ ends a ④ span) | 20,000 | 21.27 | 0.15 | 14.0 |
| if independent (⑬ falls inside) | 20,000 | 22.54 | 0.17 | 14.0 |

**The two arms differ by 1.3 blocks out of 21.** Likelihood ratio 1.0 to 1. The test
cannot distinguish them and never could.

The reason is structural, not a matter of sample size. The backward recurrence time of a
renewal process has mean `E[L](1 + cv^2)/2`, and `mark_forensics.py` records the four-dot
gap law at **cv = 1.09** -- near-exponential. At cv = 1 that factor is exactly 1, because
an exponential is memoryless: **a random point inside a span is indistinguishable from a
span end.**

So no renewal-geometry test on the four-dot can work, whatever the sample size. That
closes a family of tests rather than returning a null, and it should have been checked
before the experiment was written: the gap cv was already on record.

## The side observation, which is weak

The observed 31.82 +- 5.62 sits **above** both arms, 1.9 sigma over the 21.3 either
predicts. Four-dots are sparser than usual in the run-up to a section end.

It is not a title artifact. Splitting on whether the thirteen-dot closes a red title:

| | n | blocks since the previous ④ | blocks since the previous mark of any kind |
|---|---|---|---|
| closing a red title | 13 | 33.4 +- 8.7 | 3.2 |
| not a title | 15 | 30.5 +- 7.6 | 17.8 |

Both subsets are elevated and neither reaches 1.5 sigma alone. At n = 28 this is
suggestive and nothing more. (The 3.2 in the last column simply records that a title is
short and opens with its own thirteen-dot.)

## What it cannot do

It cannot say what the four-dot marks. It was meant to say whether the four-dot and the
thirteen-dot divide the same thing, and it cannot do that either.

    python are_the_two_marks_one_system.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from do_the_marks_bound_the_titles import BODY, MASTER, chunk_words  # noqa: E402

FOUR, THIRTEEN = "④", "⑬"
DRAWS = 20000


def body_stream():
    chunks = {i: chunk_words(c) for i, c in enumerate(MASTER.read_text().split("%"))}
    return [sep for i in BODY for _, sep in chunks.get(i, [])]


def gaps_between(stream, glyph) -> list[int]:
    """Blocks between consecutive occurrences of a glyph."""
    at = [i for i, s in enumerate(stream) if s == glyph]
    return [b - a for a, b in zip(at, at[1:])]


def backward_distances(stream, target, source) -> list[int]:
    """Blocks from the preceding `source` mark to each `target` mark."""
    out, last = [], None
    for i, s in enumerate(stream):
        if s == source:
            last = i
        elif s == target and last is not None:
            out.append(i - last)
    return out


def nested_arm(gaps, n, rng):
    """A thirteen-dot ends a span: the distance is a whole gap."""
    return [rng.choice(gaps) for _ in range(n)]


def independent_arm(gaps, n, rng):
    """A thirteen-dot falls at a random point inside a length-biased span."""
    weights = np.cumsum(gaps, dtype=float)
    weights /= weights[-1]
    out = []
    for _ in range(n):
        span = gaps[int(np.searchsorted(weights, rng.random()))]
        out.append(rng.randint(1, span))
    return out


def summarise(label, values):
    a = np.array(values, float)
    return (
        f"{label:<34}{len(a):>7}{a.mean():>10.2f}"
        f"{a.std(ddof=1) / math.sqrt(len(a)):>9.2f}{np.median(a):>9.1f}"
    )


def main() -> None:
    stream = body_stream()
    gaps = gaps_between(stream, FOUR)
    observed = backward_distances(stream, THIRTEEN, FOUR)
    rng = random.Random(3301)
    print(
        f"{len([s for s in stream if s == FOUR])} four-dots, "
        f"{len([s for s in stream if s == THIRTEEN])} thirteen-dots, "
        f"{len(stream):,} blocks.\n"
    )
    print(f"{'':<34}{'n':>7}{'mean':>10}{'se':>9}{'median':>9}")
    print(summarise("four-dot gaps", gaps))
    print(summarise("observed: previous ④ to each ⑬", observed))
    print(
        summarise(
            "if nested (⑬ ends a ④ span)", nested_arm(gaps, 20000, rng)
        )
    )
    print(
        summarise(
            "if independent (⑬ falls inside)", independent_arm(gaps, 20000, rng)
        )
    )

    n = len(observed)
    mean = float(np.mean(observed))
    print("\nWhere the observed mean sits in each arm, over 20,000 resamples of n =", n)
    print(f"\n{'arm':<34}{'mean of the arm':>18}{'P(arm mean <= observed)':>26}")
    tails = {}
    for label, draw in (
        ("nested", nested_arm),
        ("independent", independent_arm),
    ):
        means = np.array(
            [np.mean(draw(gaps, n, rng)) for _ in range(DRAWS // 20)], float
        )
        tails[label] = float((means <= mean).mean())
        print(f"{label:<34}{means.mean():>18.2f}{tails[label]:>26.3f}")

    lo = max(min(tails.values()), 1e-4)
    hi = max(tails.values())
    two_sided = {k: 2 * min(v, 1 - v) for k, v in tails.items()}
    print(f"\nobserved mean {mean:.2f}")
    print(f"{'arm':<34}{'two-sided P':>14}")
    for k, v in two_sided.items():
        print(f"{k:<34}{v:>14.3f}")
    print(
        f"\nLikelihood ratio between the arms, on the mean alone: {hi / lo:.1f} to 1"
        f" for {max(two_sided, key=two_sided.get)}."
    )


if __name__ == "__main__":
    main()
