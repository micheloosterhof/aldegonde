"""Code to analyse doublets, triplets, etc."""

from collections.abc import Sequence
from math import sqrt
from typing import TypeVar

from scipy.stats import poisson

T = TypeVar("T")


def print_doublets_statistics(
    runes: Sequence[T], alphabetsize: int, skip: int = 1
) -> None:
    """Find the number of doublets. doublet is X followed by X for any X."""
    dbls: list[int] = doublets(runes, skip=skip)
    l: int = len(dbls)
    mu = len(runes) / alphabetsize
    mean, var = poisson.stats(mu, loc=0, moments="mv")
    sigmage: float = abs(l - mean) / sqrt(var)
    print(f"doublets={l} (skip={skip}) expected={mean:.2f} S={sigmage:.2f}σ")


def doublets(runes: Sequence[T], skip: int = 1, trace: bool = False) -> list[int]:
    """Find number of doublets. doublet is X followed by X for any X."""
    positions: list[int] = []
    for index in range(0, len(runes) - skip):
        if runes[index] == runes[index + skip]:
            positions.append(index)
            if trace:
                print(
                    f"doublet at {index}: {runes[index-1]}-{runes[index]}-{runes[index+1]}-{runes[index+2]}"
                )
    return positions


def triplets(runes: Sequence[T]) -> int:
    """Find number of triplet. triplet is X followed by XX for any X."""
    N = len(runes)
    trpl: int = 0
    for index in range(0, N - 2):
        if runes[index] == runes[index + 1] and runes[index] == runes[index + 2]:
            trpl += 1
    # expected = N / MAX / MAX
    return trpl
