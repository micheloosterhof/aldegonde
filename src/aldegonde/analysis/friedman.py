"""Friedman test to detect use of the same alphabet at regular intervals."""

from collections.abc import Sequence
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
    deltas: dict[int, float] = {}

    if trace is True:
        print("Testing for periodicity using friedman test")

    print("Candidates:")
    for period in range(minperiod, maxperiod + 1):
        iocsum: float = 0.0
        for k in range(0, period):
            v = ciphertext[slice(k, len(ciphertext), period)]
            ic: float = ioc(v)  # note, perviously was normalized
            iocsum += ic
            if trace is True:
                print(f"ioc of slice {k}/{period} = {ic:.3f}")
        avgioc[period] = iocsum / period
        deltas[period] = avgioc[period] - max(avgioc.values())
        print(
            f"friedman: period {period:02d} avgioc: {avgioc[period]:.3f} delta: {deltas[period]:+.4f}",
            end="",
        )
        if abs(deltas[period]) < 0.001:
            print(" <===")
        else:
            print()
