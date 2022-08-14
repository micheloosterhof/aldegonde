"""
https://en.wikipedia.org/wiki/G-test
use scipy.stats.power_divergence with lambda_=0
"""

import scipy.stats.power_divergence

from ..structures import sequence


def gtest(text1: sequence.Sequence, text2: sequence.Sequence) -> float:
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

    freqs1 = Counter(text1)
    freqs2 = Counter(text2)
    return scipy.stats.power_divergence(f_obs=freqs1, f_exp=freqs2, lambda_=0)
