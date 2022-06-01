from collections import Counter

from ..structures import alphabet, sequence


def ioc(runes: sequence.Sequence) -> float:
    """
    Monographic Index of Coincidence: ΔIC

    Input is a list of integers, from 0 to MAX-1
    Output is the Index of Coincidence formatted as a float

    This output is not normalized to alphabet size
    """
    N = len(runes)
    if N < 2:
        return 0.0
    freqs = Counter(runes)
    freqsum = 0.0
    for rune in range(0, N):
        freqsum += freqs[rune] * (freqs[rune] - 1)
    IC = freqsum / (N * (N - 1))
    return IC


def normalized_ioc(runes: sequence.Sequence) -> float:
    """
    Like ioc() but normalized by alphabet size.
    """
    return ioc(runes) * len(runes.alphabet)


def ioc2(runes: sequence.Sequence, cut: int = 0) -> float:
    """
    Digraphic Index of Coincidence: ΔIC

    Input is a list of integers, with values from 0 to MAX-1
    Output is the Index of Coincidence formatted as a float

    Specify `cut=0` and it operates on sliding blocks of 2 runes: AB, BC, CD, DE
    Specify `cut=1` and it operates on non-overlapping blocks of 2 runes: AB, CD, EF
    Specify `cut=2` and it operates on non-overlapping blocks of 2 runes: BC, DE, FG
    """
    N = len(runes)
    if N < 3:
        return 0.0
    l: list = []
    if cut == 0:
        for i in range(0, N - 1):
            l.append(f"{runes[i]}-{runes[i+1]}")
    elif cut == 1 or cut == 2:
        for i in range(cut - 1, N - 1, 2):
            l.append(f"{runes[i]}-{runes[i+1]}")
    else:
        raise Exception
    freqs = Counter(l)
    freqsum = 0.0
    for r in freqs.keys():
        freqsum += freqs[r] * (freqs[r] - 1)
    try:
        IC = freqsum / (len(l) * (len(l) - 1))
    except ZeroDivisionError:
        IC = 0.0
    return IC


def normalized_ioc2(runes: sequence.Sequence, cut: int = 0) -> float:
    """
    Like ioc2() but normalized by alphabet size.
    """
    return ioc2(runes, cut=cut) * pow(len(runes.alphabet), 2)


def ioc3(runes: sequence.Sequence, cut: int = 0) -> float:
    """
    Trigraphic Index of Coincidence: ΔIC

    Input is a list of integers, with values from 0 to MAX-1
    Output is the Index of Coincidence formatted as a float, normalized to to alphabet size

    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 runes: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 runes: BCD, EFG, ...
    Specify `cut=3` and it operates on non-overlapping blocks of 3 runes: CDE, FGH, ...
    """
    N = len(runes)
    if N < 4:
        return 0.0
    l: list = []
    if cut == 0:
        for i in range(0, N - 2):
            l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}")
    elif cut == 1 or cut == 2 or cut == 3:
        for i in range(cut - 1, N - 2, 3):
            l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}")
    else:
        raise Exception
    freqs = Counter(l)
    freqsum = 0.0
    for r in freqs.keys():
        freqsum += freqs[r] * (freqs[r] - 1)
    try:
        IC = freqsum / (len(l) * (len(l) - 1))
    except ZeroDivisionError:
        IC = 0.0
    return IC


def normalized_ioc3(runes: sequence.Sequence, cut: int = 0) -> float:
    """
    Like ioc3() but normalized by alphabet size.
    """
    return ioc3(runes, cut=cut) * pow(len(runes.alphabet), 3)


def ioc4(runes: sequence.Sequence, cut: int = 0) -> float:
    """
    Tetragraphic Index of Coincidence: ΔIC

    Input is a list of integers, with values from 0 to MAX-1
    Output is the Index of Coincidence formatted as a float, normalized to to alphabet size

    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABCD, BCDE, CDEF, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 4 runes: ABCD, EFGH, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 4 runes: BCDE, FGHI, ...
    Specify `cut=3` and it operates on non-overlapping blocks of 4 runes: CDEF, GHIJ, ...
    Specify `cut=4` and it operates on non-overlapping blocks of 4 runes: DEFG, HIJK, ...
    """
    N = len(runes)
    if N < 6:
        return 0.0
    l: list = []
    if cut == 0:
        for i in range(0, N - 3):
            l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}-{runes[i+3]}")
    elif cut == 1 or cut == 2 or cut == 3 or cut == 4:
        for i in range(cut - 1, N - 3, 4):
            l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}-{runes[i+3]}")
    else:
        raise Exception
    freqs = Counter(l)
    freqsum = 0.0
    for r in freqs.keys():
        freqsum += freqs[r] * (freqs[r] - 1)
    IC = freqsum / (len(l) * (len(l) - 1))
    return IC


def normalized_ioc4(runes: sequence.Sequence, cut: int = 0) -> float:
    """
    Like ioc4() but normalized by alphabet size.
    """
    return ioc4(runes, cut=cut) * pow(len(runes.alphabet), 4)
