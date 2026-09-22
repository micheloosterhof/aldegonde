# ABOUTME: Separates merging short words from omitting them, using the upper tail of the
# ABOUTME: block-length histogram, which the two models move in opposite directions.
"""Two ways to lose function words, and they leave different histograms.

`block-lengths-have-a-hole-at-two.md` establishes the body's 2-rune fraction at 0.1588
where twenty-two English registers run 0.1840 to 0.2950, and fits the deficit with
**merging**: units of two runes or less joined into a neighbour at q ~ 0.40.

There is a second way to lose them, never separated from merging on this statistic. The
plaintext could **omit** them -- a telegraphic register, a list, an index, notes -- in
which case the short words were never written rather than absorbed.
`word-length-keystream-and-boundaries.md` compares merge-39% against drop-39% and finds
them indistinguishable **on the autocorrelation**, which is where they genuinely do agree.
On the histogram they do not:

- **merging** moves a short word's runes into its neighbour, so the rune total is
  preserved and the 5-to-9 classes gain;
- **omitting** deletes the runes, so the rune total falls and the upper classes are
  untouched.

That difference lives in the upper tail, and the body has 2,928 blocks to test it with.

## Why it matters beyond the histogram

A telegraphic body would explain several standing anomalies at once and without any of the
machinery currently carrying them: no sentence-final lengthening because there are no
sentences (`sentences-do-not-end-long.md`), no phrase repetition
(`do_length_patterns_repeat.py`), a flat length autocorrelation, and marks that divide
groups rather than clauses. It is the cheapest rival to the joining model and deserves a
direct test.

## How each model is fitted

Each is tuned so its 2-rune fraction lands on the body's exactly -- one parameter, fixed
by one cell. **Every other cell is then a prediction**, which makes this a test and not a
fit. The author's own words are the register-matched base; ten Gutenberg registers are
carried alongside so the verdict does not rest on his 723.

## Result: the fork is real, the tail behaves as predicted, and register swamps it

| base text | model | fitted rate | mean | chi2 vs body |
|---|---|---|---|---|
| the author | merging | 0.38 | 4.45 | **32.8** |
| the author | omitting | 0.44 | 4.30 | 67.0 |
| pg1342 | merging | 0.33 | 4.57 | 19.3 |
| pg1342 | omitting | 0.38 | 4.45 | **15.9** |
| pg205 | merging | 0.39 | 4.48 | **27.0** |
| pg205 | omitting | 0.46 | 4.34 | 36.3 |
| pg16643 | merging | 0.46 | 4.66 | 60.2 |
| pg16643 | omitting | 0.53 | 4.49 | **48.2** |
| pg2945 | merging | 0.45 | 4.73 | 66.8 |
| pg2945 | omitting | 0.50 | 4.56 | **36.6** |

Median over the bases: merging 32.8, omitting 36.6, on about ten degrees of freedom.

**The ranking flips with the base text.** The author and pg205 favour merging, the other
three favour omitting, and the spread across bases (15.9 to 66.8) is far wider than the
gap between models. So this does not decide anything, for the reason that has caught
several statistics here: the between-register variation exceeds the effect.

**The tail does discriminate, as designed.** Predicted share, author base:

| length | the body | merging | omitting |
|---|---|---|---|
| 5 | 0.1095 | 0.0864 | 0.0884 |
| 8 | **0.0539** | 0.0456 | 0.0379 |
| 11+ | **0.0197** | 0.0190 | 0.0126 |

Merging predicts a heavier tail than omitting at every class above 7, which is the
mechanism working: absorbed runes have to go somewhere. **The body's tail is heavier than
both**, so what lean there is favours merging -- and the body out-runs even the merging
model, which neither explains.

## The by-product worth keeping

`block-lengths-have-a-hole-at-two.md` records that the best of twenty-two raw registers
gives chi2 **105.2** against the body. Adding one merge-or-omit parameter brings that to
**15.9 to 66.8**. So the deficit model earns most of the distance and still does not reach
a fit: at 15.9 on ten degrees of freedom the best case is P = 0.10, and the
register-matched author base is P = 0.0003.

Something beyond a single short-unit rule is shaping the body's length histogram, and this
file does not identify it.

    python merged_or_telegraphic.py
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
CELLS = tuple(range(1, 12))
THRESHOLD = 2


def histogram(lengths) -> np.ndarray:
    a = np.array(lengths, float)
    counts = np.array([float((a == k).sum()) for k in CELLS])
    counts[-1] += float((a > CELLS[-1]).sum())
    return counts / counts.sum()


def merge(words, q, rng):
    """A short unit's runes are added to the next; the rune total is preserved."""
    out, i = list(words), 0
    while i < len(out) - 1:
        if out[i] <= THRESHOLD and rng.random() < q:
            out[i + 1] += out[i]
            out.pop(i)
            continue
        i += 1
    return out


def omit(words, q, rng):
    """A short unit is deleted; its runes are gone."""
    return [w for w in words if not (w <= THRESHOLD and rng.random() < q)]


def fit(words, model, target, rng, draws=6):
    """The rate whose 2-rune fraction lands on the target."""
    lo, hi = 0.0, 1.0
    for _ in range(14):
        mid = (lo + hi) / 2
        got = np.mean(
            [float(np.mean(np.array(model(words, mid, rng)) == 2)) for _ in range(draws)]
        )
        if got > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def chi2(observed_counts, predicted_probs) -> float:
    n = observed_counts.sum()
    expected = np.maximum(predicted_probs * n, 0.5)
    return float((((observed_counts - expected) ** 2) / expected).sum())


def main() -> None:
    rng = random.Random(3301)
    body = [x for s in body_spans() for x in s]
    author = [x for s in author_spans() for x in s]
    target = float(np.mean(np.array(body) == 2))
    counts = histogram(body) * len(body)
    print(f"body: {len(body):,} blocks, 2-rune fraction {target:.4f}, "
          f"mean {np.mean(body):.2f}")
    print(f"author: {len(author):,} words, 2-rune fraction "
          f"{np.mean(np.array(author) == 2):.4f}, mean {np.mean(author):.2f}\n")

    sources = [("the author", author)]
    for n in REGISTERS[:4]:
        p = fetch(n)
        if p is not None:
            words = [x for s in register_spans(p, rng, 0.0) for x in s]
            sources.append((f"pg{n}", words[:20000]))

    print(f"{'base text':<14}{'model':<12}{'rate':>7}{'mean':>8}{'chi2 vs body':>15}")
    scores = {"merging": [], "omitting": []}
    for label, words in sources:
        for name, model in (("merging", merge), ("omitting", omit)):
            rate = fit(words, model, target, rng)
            reps = [model(words, rate, rng) for _ in range(8)]
            probs = np.mean([histogram(r) for r in reps], axis=0)
            mean = float(np.mean([np.mean(r) for r in reps]))
            score = chi2(counts, probs)
            scores[name].append(score)
            print(f"{label:<14}{name:<12}{rate:>7.2f}{mean:>8.2f}{score:>15.1f}")

    print(f"\n{'model':<12}{'median chi2 over the bases':>30}")
    for name, v in scores.items():
        print(f"{name:<12}{np.median(v):>30.1f}")
    print("\n  11 cells, one parameter fitted, so about 10 degrees of freedom.")

    print("\nWhere they differ: predicted share in each length class, author base.\n")
    print(f"{'length':>7}{'the body':>11}{'merging':>11}{'omitting':>11}")
    best = {}
    for name, model in (("merging", merge), ("omitting", omit)):
        rate = fit(author, model, target, rng)
        best[name] = np.mean(
            [histogram(model(author, rate, rng)) for _ in range(8)], axis=0
        )
    obs = histogram(body)
    for i, k in enumerate(CELLS):
        tag = f"{k}" if k < CELLS[-1] else f"{k}+"
        print(f"{tag:>7}{obs[i]:>11.4f}{best['merging'][i]:>11.4f}{best['omitting'][i]:>11.4f}")


if __name__ == "__main__":
    main()
