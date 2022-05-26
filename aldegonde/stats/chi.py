from collections import Counter


def chi(text1: list[int], text2: list[int]) -> float:
    """
    Calculate chi test of 2 texts

    It's calculated by multiplying the frequency count of one letter
    in the first string by the frequency count of the same letter
    in the second string, and then doing the same for all the other
    letters, and summing the result. This is divided by the product
    of the total number of letters in each string.
    """
    N1 = len(text1)
    N2 = len(text2)
    freqs1 = Counter(text1)
    freqs2 = Counter(text2)
    sum: float = 0.0
    for rune in range(0, MAX):
        sum += freqs1[rune] * freqs2[rune] / (N1 * N2)
    return sum
