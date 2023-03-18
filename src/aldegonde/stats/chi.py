"""
Functions around chi^2
"""

from collections.abc import Sequence
from typing import TypeVar

from aldegonde.stats.ngrams import ngram_distribution

T = TypeVar("T")


def chi(text1: Sequence[T], text2: Sequence[T], length: int = 1) -> float:
    """
    Calculate chi test of 2 texts

    It's calculated by multiplying the frequency count of one letter
    in the first string by the frequency count of the same letter
    in the second string, and then doing the same for all the other
    letters, and summing the result. This is divided by the product
    of the total number of letters in each string.
    """
    total: float = 0.0
    d1 = ngram_distribution(text1, length=length)
    d2 = ngram_distribution(text2, length=length)
    for key in d1.keys():
        try:
            total += d1[key] * d2[key]
        except KeyError:
            continue
    return total / (len(d1.keys()) * len(d2.keys()))
