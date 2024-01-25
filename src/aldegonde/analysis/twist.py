"""Twist method (2015) by Barr and Simoson to detect use of the
   same alphabet at regular intervals."""

from collections import Counter
from typing import TypeVar

from aldegonde.analysis.split import split_by_slice, split_by_slice_interrupted
from aldegonde.stats.compare import frequency_to_probability, unigrams

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
    ciphertext: str,
    minperiod: int = 1,
    maxperiod: int = 20,
    *,
    trace: bool = False,
) -> None:
    """Print the twist test"""
    if trace is True:
        print("Testing for periodicity using twist test")

    twists: dict[int, float] = {}

    for period in range(minperiod, maxperiod + 1):
        slices = split_by_slice(ciphertext, period)
        probs: list[float] = [0.0] * 26

        for sl in slices.values():
            prob = sorted(frequency_to_probability(dict(Counter(sl))).values())
            padded = [0.0] * (26 - len(prob)) + prob
            for x in range(len(probs)):
                probs[x] += padded[x] / period

        english = sorted(frequency_to_probability(unigrams).values())
        # tw = twist(english, probs)
        twists[period] = twist(english, probs)

        # print(f"twist: period={period:02} twist={tw:0.5f}")

    highest = 0.0
    highestpp = 0.0
    for period in range(minperiod + 1, maxperiod):
        print(f"twist: period: {period:02} twist: {twists[period]:0.5f}", end="")
        if twists[period] > highest:
            print(" <-")
            highest = twists[period]
        else:
            print("")
        twistplusplus = twists[period] - (twists[period - 1] + twists[period + 1]) / 2
        print(f"twist: period: {period:02} twist++: {twistplusplus:0.5f}", end="")
        if twistplusplus > highestpp:
            print(" <=")
            highestpp = twistplusplus
        else:
            print("")


def twist_test_with_interrupter(
    ciphertext: str,
    alphabet: str,
    minperiod: int = 1,
    maxperiod: int = 20,
    *,
    trace: bool = False,
) -> None:
    """Print the twist test"""
    if trace is True:
        print("Testing for periodicity using twist test")

    for interrupter in alphabet:
        twists: dict[int, float] = {}
        for period in range(minperiod, maxperiod + 1):
            slices = split_by_slice_interrupted(ciphertext, period, interrupter)
            probs: list[float] = [0.0] * 26

            for sl in slices.values():
                prob = sorted(frequency_to_probability(dict(Counter(sl))).values())
                padded = [0.0] * (26 - len(prob)) + prob
                for x in range(len(probs)):
                    probs[x] += padded[x] / period

            english = sorted(frequency_to_probability(unigrams).values())
            twists[period] = twist(english, probs)

        for period in range(minperiod + 1, maxperiod):
            print(f"twist: period: {period:02} twist: {twists[period]:0.5f}")
            twistplusplus = (
                twists[period] - (twists[period - 1] + twists[period + 1]) / 2
            )
            print(f"twist: period: {period:02} twist++: {twistplusplus:0.5f}")
