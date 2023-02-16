"""
Code to analyse doublets, triplets, etc
"""

import math

from scipy.stats import poisson

from ..structures import sequence


def print_doublets_statistics(runes: sequence.Sequence, skip: int = 1) -> None:
    """
    find the number of doublets. doublet is X followed by X for any X
    """
    MAX: int = len(runes.alphabet)
    N: int = len(runes)
    dbls: list[int] = []
    for index in range(0, N - skip):
        if runes[index] == runes[index + skip]:
            dbls.append(index)
    l: int = len(dbls)
    mu = N / MAX
    mean, var = poisson.stats(mu, loc=0, moments="mv")
    sigmage: float = abs(l - mean) / math.sqrt(var)
    print(f"doublets={l} (skip={skip}) expected={mean:.2f} S={sigmage:.2f}σ")


def doublets(runes: sequence.Sequence, skip: int = 1, trace: bool = False) -> list[int]:
    """
    find number of doublets. doublet is X followed by X for any X
    """
    N = len(runes)
    dbls: list[int] = []
    for index in range(0, N - skip):
        if runes[index] == runes[index + skip]:
            dbls.append(index)
            if trace:
                print(
                    f"doublet at {index}: {runes[index-1]}-{runes[index]}-{runes[index+1]}-{runes[index+2]}"
                )
    return dbls


def triplets(runes: sequence.Sequence) -> int:
    """
    find number of triplet. triplet is X followed by XX for any X
    """
    N = len(runes)
    trpl: int = 0
    for index in range(0, N - 2):
        if runes[index] == runes[index + 1] and runes[index] == runes[index + 2]:
            trpl += 1
    # expected = N / MAX / MAX
    return trpl
