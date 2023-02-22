"""Friedman test to detect use of the same alphabet at regular intervals"""

from aldegonde.structures.sequence import Sequence
from aldegonde.analysis.split import split_by_slice
from aldegonde.stats.ioc import ioc

# assume fixed length key. find period
def friedman_test(
    ciphertext: Sequence,
    minkeysize: int = 1,
    maxkeysize: int = 20,
    trace: bool = False,
) -> None:
    """
    this is the friedman test
    https://crypto.stackexchange.com/questions/40066/finding-length-of-a-key-for-a-given-vigenere-cipher-using-index-of-coincidence
    """
    # avgioc contains the key length as key. as value it's the avgioc
    # delta is the difference between the avgioc and the max of avgioc of all lower values
    avgioc: dict[int, float] = {}
    deltas: dict[int, float] = {}

    if trace is True:
        print("Testing for periodicity using friedman test")
    print("Candidates:")
    for period in range(minkeysize, maxkeysize + 1):
        slices = split_by_slice(ciphertext, period)
        iocsum: float = 0.0
        for k, v in slices.items():
            ic = ioc(v)[1]
            iocsum += ic
            if trace is True:
                print(f"ioc of runes {k}/{period} = {ic:.3f}")
        avgioc[period] = iocsum / period
        deltas[period] = avgioc[period] - max(avgioc.values())
        print(
            f"period {period:02d} avgioc: {avgioc[period]:.3f} delta: {deltas[period]:.3f}"
        )
