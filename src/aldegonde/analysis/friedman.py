"""Friedman test to detect use of the same alphabet at regular intervals."""

from collections.abc import Sequence
from statistics import mean, median
from typing import TypeVar

from aldegonde.stats.ioc import ioc

T = TypeVar("T")


# assume fixed length key. find period
def friedman_test(
    ciphertext: Sequence[T],
    minperiod: int = 1,
    maxperiod: int = 20,
    *,
    trace: bool = False,
) -> None:
    """Print the friedman test
    https://crypto.stackexchange.com/questions/40066/finding-length-of-a-key-for-a-given-vigenere-cipher-using-index-of-coincidence.
    """
    # avgioc contains the key length as key. as value it's the avgioc
    # delta is the difference between the avgioc and the max of avgioc of all lower values
    avgioc: dict[int, float] = {}
    medioc: dict[int, float] = {}
    deltas: dict[int, float] = {}

    if trace is True:
        print("Testing for periodicity using friedman test")

    for period in range(minperiod, maxperiod + 1):
        iocs: list[float] = []
        for k in range(0, period):
            v = ciphertext[slice(k, len(ciphertext), period)]
            ic: float = ioc(v)  # note, perviously was normalized
            iocs.append(ic)
            if trace is True:
                print(f"ioc of slice {k}/{period} = {ic:.3f}")
        medioc[period] = median(iocs)
        avgioc[period] = mean(iocs)
        deltas[period] = avgioc[period] - max(avgioc.values())
        print(
            f"friedman: period {period:02d} medioc: {medioc[period]:.3f} avgioc: {avgioc[period]:.3f} delta: {deltas[period]:+.4f}",
            end="",
        )

        if abs(deltas[period]) < 0.001:
            print(" <===")
        else:
            print()
