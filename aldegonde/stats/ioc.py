"""IOC calculation
"""

from collections import Counter
from math import sqrt
from typing import NamedTuple

from ..structures import sequence
from .ngrams import ngrams


def ioc(
    runes: sequence.Sequence, length: int = 1, cut: int = 0
) -> tuple[float, float, float]:
    """Multigraphic Index of Coincidence: ΔIC
    Args:
        runes: Sequence
        length: size of ngram
        cut: where to start ngrams

    Yields:
        Output is the Index of Coincidence formatted as a float,
        normalized to to alphabet size, and the number of standard
        deviations away from random data (sigmage)

    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 runes: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 runes: BCD, EFG, ...
    """
    C = pow(len(runes.alphabet), length)  # size of alphabet
    items: list[str] = []
    for g in ngrams(runes, length=length, cut=cut):
        items.append("-".join([str(x) for x in g]))

    # L is the number of items we have counted
    L = len(items)
    if L < 2:
        return (0.0, 0.0, 0.0)

    freqs = Counter(items)
    freqsum: float = 0.0
    for v in freqs.values():
        freqsum += v * (v - 1)

    ic = freqsum / (L * (L - 1))
    nic = C * ic
    sd = sqrt(2 * (C - 1)) / sqrt(L * (L - 1))
    sigmage = abs(nic - 1.0) / sd

    Ioc = NamedTuple("Ioc", [("ioc", float), ("nioc", float), ("sigmage", float)])
    return Ioc(ioc=ic, nioc=nic, sigmage=sigmage)


def print_ioc_statistics(runes: sequence.Sequence) -> None:
    """
    print IOC statistics
    """
    for length in range(1, 6):
        for cut in range(0, length + 1):
            if length==1 and cut==1: 
                continue
            _, nioc, sigmage = ioc(runes, length=length, cut=cut)
            print(f"ΔIC{length} (cut={cut}) = {nioc:.3f} S={sigmage:.3f}σ ", end="| ")
        print()


def sliding_window_ioc(runes: sequence.Sequence, window: int = 100) -> list[float]:
    """
    calculate sliding window IOC of a large data set
    """
    C = len(runes.alphabet)
    output: list[float] = []
    for i in range(0, len(runes) - window):
        output.append(C * ioc(runes[i : i + window])[1])
    return output


def ioc2(runes: sequence.Sequence, cut: int = 0) -> tuple[float, float, float]:
    """Multigraphic Index of Coincidence: ΔIC"""
    return ioc(runes, cut=cut, length=2)


def ioc3(runes: sequence.Sequence, cut: int = 0) -> tuple[float, float, float]:
    """Multigraphic Index of Coincidence: ΔIC"""
    return ioc(runes, cut=cut, length=3)


def ioc4(runes: sequence.Sequence, cut: int = 0) -> tuple[float, float, float]:
    """Multigraphic Index of Coincidence: ΔIC"""
    return ioc(runes, cut=cut, length=4)
