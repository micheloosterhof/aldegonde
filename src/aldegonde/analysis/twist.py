"""Twist test to detect use of the same alphabet at regular intervals."""

from collections import Counter, defaultdict
from collections.abc import Sequence
from statistics import mean, median
from typing import TypeVar

from aldegonde.analysis.split import split_by_slice
from aldegonde.stats.compare import unigrams, frequency_to_probability

T = TypeVar("T")


def twist(afreqs: list[float], bfreqs: list[float]) -> float:
    """
    barr simoson twist
    input is a list of letter frequencies
    """
    assert len(afreqs) == 26
    assert len(bfreqs) == 26
    safreqs = sorted(afreqs)
    sbfreqs = sorted(bfreqs)
    twist: float = 0.0
    for r in range(13):
        twist += safreqs[r] - sbfreqs[r]
    for r in range(13, 26):
        twist += sbfreqs[r] - safreqs[r]
    return twist


def twist_test(
    ciphertext: Sequence[T],
    minperiod: int = 1,
    maxperiod: int = 20,
    *,
    trace: bool = False,
) -> None:
    """Print the twist test"""
    if trace is True:
        print("Testing for periodicity using twist test")

    for period in range(minperiod, maxperiod + 1):
        slices = split_by_slice(ciphertext, period)
        probs: list[float] = [0.0] * 26

        for sl in slices.values():
            prob = sorted(frequency_to_probability(dict(Counter(sl))).values())
            padded = [0.0] * (26 - len(prob)) + prob
            for x in range(len(probs)):
                probs[x] += padded[x] / period

        english = sorted(frequency_to_probability(unigrams).values())
        tw = twist(english, probs)

        print(f"period {period} TWIST:{tw}")
