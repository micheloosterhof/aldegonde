import math

from scipy.stats import poisson

from ..structures import alphabet, sequence


def print_doublets_statistics(runes: sequence.Sequence, skip: int = 1) -> None:
    """
    find the number of doublets. doublet is X followed by X for any X
    """
    MAX = len(runes.alphabet)
    N = len(runes)
    doublets: list[int] = []
    for index in range(0, N - skip):
        if runes[index] == runes[index + skip]:
            doublets.append(index)
    l: int = len(doublets)
    mu = N / MAX
    mean, var = poisson.stats(mu, loc=0, moments="mv")
    sigmage: float = abs(l - mean) / math.sqrt(var)
    print(f"doublets={l} expected={mean:.2f} S={sigmage:.2f}σ")


def doublets(runes: sequence.Sequence, skip: int = 1, trace: bool = False) -> list[int]:
    """
    find number of doublets. doublet is X followed by X for any X
    """
    MAX = len(runes.alphabet)
    N = len(runes)
    doublets: list[int] = []
    for index in range(0, N - skip):
        if runes[index] == runes[index + skip]:
            doublets.append(index)
            if trace:
                print(
                    f"doublet at {index}: {runes[index-1]}-{runes[index]}-{runes[index+1]}-{runes[index+2]}"
                )
    return doublets


def triplets(runes: sequence.Sequence) -> int:
    """
    find number of triplet. triplet is X followed by XX for any X
    """
    MAX = len(runes.alphabet)
    N = len(runes)
    triplets: int = 0
    for index in range(0, N - 2):
        if runes[index] == runes[index + 1] and runes[index] == runes[index + 2]:
            triplets += 1
    # expected = N / MAX / MAX
    return triplets
