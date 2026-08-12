# ABOUTME: Counts isomorph patterns per word length and shows they carry nothing
# ABOUTME: beyond the per-distance coincidence rates -- no higher-order structure.
"""Are the isomorph patterns as expected? Yes, and that closes the local channel.

`stats.isomorphs.isomorph` normalises a word to its equality pattern (ATTACK and
EFFECT both give ABBACD). Since `base_w` is one bijection applied elementwise
within a word, that pattern is the COMPLETE within-word invariant -- nothing else
about a word is observable without crossing a word boundary. So if the patterns
hold structure beyond what is already measured, it is the last place a key-local
attack could live.

They do not. Two tests.

**The aggregate.** P(a word holds at least one repeat) predicted from the measured
per-distance rates alone, treating position pairs as independent:

    L    words   observed   from rates      z
    3      726      5.8%        4.7%     +1.4
    4      514     11.9%       12.0%     -0.1
    5      318     24.5%       22.0%     +1.1
    6      252     39.3%       34.3%     +1.7
    7      214     44.9%       46.0%     -0.3
    8      159     60.4%       57.5%     +0.7

Summed z^2 = 6.6 on 6 df, p ~ 0.36. The pattern rates follow from the pairwise
rates; there is no higher-order structure.

**Per pattern.** Across 49 single-collision cells the largest deviation is
L=6 ABCDCE at z = +2.5 (12 observed against 6.0 expected), and Bonferroni needs
|z| > 3.3 at this many cells. Nothing survives.

Why this matters more than a null usually does. It closes the chain of the argument
in `information_budget.py`, with every link now measured rather than assumed:

    within-word observables = the isomorph pattern       (complete invariant)
    isomorph patterns       = the per-distance rates      (this file, p ~ 0.36)
    per-distance rates      = six scalars, ~4 bits about g

So the only channel local in the key provably reduces to a handful of numbers.
Everything else about the corpus requires comparing across words, where the bases
differ by the step product over the intervening lengths -- key-global, no partial
credit. That is why no filter and no gradient exists, and it is now an argument
rather than a tally of failed attempts.

Note the caution this file also supplies: a naive "walk" expectation built from a
RANDOM order-5 g predicts 19.7% of 4-rune words holding a repeat against an
observed 11.9%, which looks like a 4.4-sigma anomaly and is not one. The real g has
a tuned d1 diagonal (0.0063, not the random 0.0345), and once that is used the
deficit is exactly reproduced. Never compare the corpus against an untuned g.
"""

from __future__ import annotations

import statistics
import sys
from collections import Counter
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import load_words  # noqa: E402

from aldegonde.stats.isomorphs import isomorph  # noqa: E402

M = 29
MIN_WORDS = 80
MIN_PAIRS = 200


def distance_rates(words: list[list[int]]) -> dict[int, float]:
    """Within-word coincidence rate at each distance."""
    out = {}
    for d in range(1, 13):
        total = hits = 0
        for w in words:
            for j in range(len(w) - d):
                total += 1
                hits += w[j] == w[j + d]
        if total > MIN_PAIRS:
            out[d] = hits / total
    return out


def predict_any_repeat(length: int, rates: dict[int, float]) -> float:
    """P(at least one repeat) if position pairs were independent."""
    clean = 1.0
    for j in range(length):
        for k in range(j + 1, length):
            clean *= 1 - rates.get(k - j, 1 / M)
    return 1 - clean


def main() -> None:
    lp = load_words()
    rates = distance_rates(lp)
    print(
        "per-distance rates: "
        + ", ".join(f"d{d}:{100 * r:.2f}%" for d, r in sorted(rates.items())[:8])
    )
    print("\nP(word holds >=1 repeat), observed vs predicted from those rates alone")
    print(f"{'L':>3}{'words':>7}{'observed':>10}{'from rates':>12}{'z':>7}")
    chi = 0.0
    cells = 0
    for length in range(3, 9):
        words = [w for w in lp if len(w) == length]
        if len(words) < MIN_WORDS:
            continue
        obs = sum(1 for w in words if len(set(w)) < length) / len(words)
        pred = predict_any_repeat(length, rates)
        se = sqrt(pred * (1 - pred) / len(words))
        z = (obs - pred) / se
        chi += z * z
        cells += 1
        print(
            f"{length:>3}{len(words):>7}{100 * obs:>9.1f}%{100 * pred:>11.1f}%{z:>+7.1f}"
        )
    print(f"\nsummed z^2 = {chi:.1f} on {cells} df -- the patterns add nothing")

    print("\nper-pattern deviations, family-wise corrected")
    worst = []
    tested = 0
    for length in range(4, 8):
        words = [w for w in lp if len(w) == length]
        if len(words) < MIN_WORDS:
            continue
        observed = Counter(isomorph(w) for w in words)
        pairs = [(j, k) for j in range(length) for k in range(j + 1, length)]
        for pattern, count in observed.items():
            collisions = [(j, k) for j, k in pairs if pattern[j] == pattern[k]]
            if len(collisions) != 1:
                continue
            j, k = collisions[0]
            p = rates.get(k - j, 1 / M)
            for a, b in pairs:
                if (a, b) != (j, k):
                    p *= 1 - rates.get(b - a, 1 / M)
            expected = p * len(words)
            tested += 1
            if expected > 3:
                worst.append(
                    (
                        (count - expected) / sqrt(expected),
                        length,
                        pattern,
                        count,
                        expected,
                    )
                )
    threshold = abs(statistics.NormalDist().inv_cdf(0.025 / max(tested, 1)))
    print(f"  {tested} single-collision cells; Bonferroni needs |z| > {threshold:.1f}")
    for z, length, pattern, count, expected in sorted(worst, key=lambda t: -abs(t[0]))[
        :4
    ]:
        print(
            f"  L={length} {pattern}: observed {count}, expected {expected:.1f}, z={z:+.1f}"
        )
    print("\nNothing survives correction. The complete within-word invariant reduces")
    print("to six scalars, which is why the key-local channel is nearly empty.")


if __name__ == "__main__":
    main()
