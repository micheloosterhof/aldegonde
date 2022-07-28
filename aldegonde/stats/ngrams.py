"""
ngrams
"""

from ..structures import sequence


def ngrams(runes: sequence.Sequence, length: int, cut: int = 0) -> list[list[int]]:
    """
    Input is a Sequence
    Output is a list of ngrams

    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 runes: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 runes: BCD, EFG, ...
    """
    N = len(runes)  # size of sequence
    l: list[list[int]] = []
    if cut == 0:
        for i in range(0, N - length + 1):
            l.append(runes[i : i + length])
    elif cut in range(1, length + 1):
        for i in range(cut - 1, N - length + 1, length):
            l.append(runes[i : i + length])
    return l
