"""module description."""

from collections.abc import Sequence
from math import sqrt
from typing import TypeVar

from scipy.stats import poisson

T = TypeVar("T")


def doublets(
    runes: Sequence[T],
    skip: int = 1,
    *,
    trace: bool = False,
) -> tuple[list[int], int]:
    """Find number of doublets. doublet is X followed by X for any X."""
    positions: list[int] = []
    if len(runes) == skip:
        return ([], 0)
    for index in range(len(runes) - skip):
        if runes[index] == runes[index + skip]:
            positions.append(index)
            if trace:
                print(
                    f"doublet at {index}: {runes[index-1]}-{runes[index]}-{runes[index+1]}-{runes[index+2]}",
                )
    return (positions, len(runes) - skip)


def kappa(runes: Sequence[T], skip: int = 1, *, trace: bool = False) -> float:
    dbl, length = doublets(runes, skip=skip)
    return len(dbl) / length


# def doublets(
#    inp: Iterator[T], skip: int = 1, *, trace: bool = False
# ) -> tuple[list[int], int]:
#    """Find number of doublets. doublet is X followed by X for any X.
#    returns the positions of the doublets as a list plus the length of the input"""
#    positions: list[int] = []
#    buffer: list[T] = []
#    index = 0
#
#    for item in inp:
#        buffer.append(item)
#        if len(buffer) > skip:
#            buffer.pop(0)
#        if len(buffer) == skip and buffer[0] == buffer[-1]:
#            positions.append(index - skip)
#            if trace:
#                print(f"doublet at {index - skip}: {buffer[0]}-{buffer[1]}")
#        index += 1
#
#    return (positions, index - skip)


def triplets(runes: Sequence[T]) -> int:
    """Find number of triplet. triplet is X followed by XX for any X."""
    N = len(runes)
    trpl: int = 0
    for index in range(N - 2):
        if runes[index] == runes[index + 1] and runes[index] == runes[index + 2]:
            trpl += 1
    # expected = N / MAX / MAX
    return trpl


def print_kappa(
    ciphertext: Sequence[T],
    alphabetsize: int = 0,
    minimum: int = 1,
    maximum: int = 51,
    threshold: float = 1.3,
    *,
    trace: bool = False,
) -> None:
    """Kappa test for a range. if alphabet size is 0, it will determine this based on unique characters in ciphertext"""
    assert maximum >= 0
    assert minimum >= 1
    if alphabetsize == 0:
        alphabetsize = len(set(ciphertext))
    if maximum == 0:
        maximum = int(len(ciphertext) / 2)
    elif maximum > len(ciphertext):
        maximum = len(ciphertext)
    for keylen in range(minimum, maximum):
        dbl, length = doublets(ciphertext, skip=keylen)
        l = len(dbl)
        ioc = alphabetsize * l / length
        mu = length / alphabetsize
        mean, var = poisson.stats(mu, loc=0, moments="mv")
        sigmage: float = abs(l - mean) / sqrt(var)
        print(
            f"kappa/doublets: skip={keylen:<2d} count={l:<3d} expected={mean:<3.2f} S={sigmage:.2f}σ ioc={ioc:1.3f}",
        )
        # if k > threshold or trace is True:
        #    print(f"kappa: keylen={keylen:02d}," + f"ioc={k:.3f} ")
    print()
