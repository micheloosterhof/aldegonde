"""
Functions around chi^2
"""

from collections import Counter

from ..structures import sequence


def chi(text1: sequence.Sequence, text2: sequence.Sequence) -> float:
    """
    Calculate chi test of 2 texts

    It's calculated by multiplying the frequency count of one letter
    in the first string by the frequency count of the same letter
    in the second string, and then doing the same for all the other
    letters, and summing the result. This is divided by the product
    of the total number of letters in each string.
    """
    if text1.alphabet != text2.alphabet:
        raise TypeError("Incompatible alphabet")

    N1 = len(text1)
    N2 = len(text2)
    freqs1 = Counter(text1)
    freqs2 = Counter(text2)
    total: float = 0.0
    for rune in range(0, len(text1.alphabet)):
        total += freqs1[rune] * freqs2[rune] / (N1 * N2)
    return total
