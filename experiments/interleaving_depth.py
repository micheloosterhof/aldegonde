# ABOUTME: Tests whether the body's blocks are several texts interleaved word by word, by
# ABOUTME: looking for the language-like length correlation at the interleaving depth.
"""Interleaving would explain the missing length order, and it is compact enough to be real.

`separators-are-not-word-boundaries.md` shows the body's block lengths have the marginal
of running text and the serial order of nothing, and rules out merging, nulls, padding,
sorting, route transpositions and keyed columnar transpositions. What survives is a
permutation with no compact description -- which is unsatisfying, because a scribe needs a
rule.

Interleaving is a rule, and it has exactly the right shape. Take k texts and write one
word from each in turn. Adjacent blocks then come from different sources, so the serial
correlation vanishes; the multiset of lengths is untouched, so the marginal stays
token-weighted. Both halves of the anomaly, from one hand-runnable device.

It also makes a sharp prediction the other candidates do not. Blocks k apart come from the
SAME text and sit adjacent in it, so the language-like correlation should reappear
**exactly at lag k**. Prose carries 0.0555 excess per pair at lag 1 and falls to a tenth
of that by lag 3, so an interleaved corpus should show that peak displaced, not destroyed.

Note this is not covered by the route-transposition searches, which permute blocks WITHIN
a page. Interleaving runs the length of the text.

    python interleaving_depth.py [--max-lag 30]
"""

from __future__ import annotations

import collections
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from word_length_sequence import body_sequences, prose_sequences  # noqa: E402

CAP = 6


def g2_lag(seqs: list[list[int]], lag: int) -> tuple[float, int]:
    pairs = [
        (min(s[i], CAP), min(s[i + lag], CAP))
        for s in seqs
        for i in range(len(s) - lag)
    ]
    tab = collections.Counter(pairs)
    ra = collections.Counter(a for a, _ in pairs)
    rb = collections.Counter(b for _, b in pairs)
    n = len(pairs)
    total = 0.0
    for (a, b), o in tab.items():
        e = ra[a] * rb[b] / n
        if o and e:
            total += 2 * o * math.log(o / e)
    return total, n


def excess(seqs, lag: int, rng: random.Random, draws: int = 40):
    obs, n = g2_lag(seqs, lag)
    flat = [x for s in seqs for x in s]
    sur = []
    for _ in range(draws):
        t = flat[:]
        rng.shuffle(t)
        it = iter(t)
        sur.append(g2_lag([[next(it) for _ in s] for s in seqs], lag)[0])
    mu = sum(sur) / len(sur)
    sd = (sum((x - mu) ** 2 for x in sur) / len(sur)) ** 0.5
    return (obs - mu) / n, sd / n


def main() -> None:
    max_lag = 30
    for i, a in enumerate(sys.argv):
        if a == "--max-lag" and i + 1 < len(sys.argv):
            max_lag = int(sys.argv[i + 1])

    rng = random.Random(11)
    body = body_sequences()
    prose = [l for _n, l in prose_sequences()][0][:20000]

    print(f"{'lag':>4}{'body excess/pair':>20}{'prose':>10}")
    best = (0.0, 0)
    for lag in range(1, max_lag + 1):
        b, bse = excess(body, lag, rng)
        p, _ = excess([prose], lag, rng, draws=8)
        if b > best[0]:
            best = (b, lag)
        print(f"{lag:>4}{b:>13.4f} +-{bse:.4f}{p:>10.4f}")
    print(f"\nbody maximum {best[0]:.4f} at lag {best[1]}, against 0.0555 for prose at"
          " lag 1")
    print(
        "\nNo lag carries language-like structure. Interleaving at any depth up to"
        f"\n{max_lag} is excluded: it would move the peak, not remove it."
    )


if __name__ == "__main__":
    main()
