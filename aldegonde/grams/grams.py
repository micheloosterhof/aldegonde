"""
Various functions to create grams
"""

from collections import Counter, defaultdict
from typing import Dict

from ..structures import sequence


def trigrams(runes: sequence.Sequence, cut: int = 0) -> list[str]:
    """
    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 runes: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 runes: BCD, EFG, ...
    Specify `cut=3` and it operates on non-overlapping blocks of 3 runes: CDE, FGH, ...
    """
    N = len(runes)
    l: list = []
    if cut == 0:
        for i in range(0, N - 2):
            try:
                l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}")
            except IndexError:
                break
    elif cut == 1 or cut == 2 or cut == 3:
        for i in range(cut - 1, N - 2, 3):
            try:
                l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}")
            except IndexError:
                break
    else:
        raise Exception

    return l


def tetragrams(runes: sequence.Sequence, cut: int = 0) -> list[str]:
    """
    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABCD, BCDE, CDEF, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 4 runes: ABCD, EFGH, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 4 runes: BCDE, FGHI, ...
    Specify `cut=3` and it operates on non-overlapping blocks of 4 runes: CDEF, GHIJ, ...
    Specify `cut=4` and it operates on non-overlapping blocks of 4 runes: DEFG, HIJK, ...
    """
    N = len(runes)
    l: list = []
    if cut == 0:
        for i in range(0, N - 2):
            try:
                l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}-{runes[i+3]}")
            except IndexError:
                break
    elif cut == 1 or cut == 2 or cut == 3 or cut == 4:
        for i in range(cut - 1, N - 3, 3):
            try:
                l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}-{runes[i+3]}")
            except IndexError:
                break
    else:
        raise Exception

    return l
