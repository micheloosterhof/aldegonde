"""
https://en.wikipedia.org/wiki/G-test
use scipy.stats.power_divergence with lambda_=0
"""

from collections.abc import Sequence
from typing import TypeVar

import scipy.stats.power_divergence

from aldegonde.stats.ngrams import ngram_distribution

T = TypeVar("T")


def gtest(text1: Sequence[T], text2: Sequence[T], length: int = 1) -> float:
    """
    Calculate chi test of 2 texts
    """
    d1 = ngram_distribution(text1, length=length)
    d2 = ngram_distribution(text2, length=length)
    return scipy.stats.power_divergence(f_obs=d1, f_exp=d2, lambda_=0)
