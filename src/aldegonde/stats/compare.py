"""Functions around comparing texts or distributions in texts."""

from collections.abc import Sequence
import importlib.resources
from math import log10
from typing import TypeVar

from scipy.stats import power_divergence, chisquare

from aldegonde.stats.ngrams import ngram_distribution, iterngrams
from aldegonde.data.ngrams.english import trigrams


T = TypeVar("T")


def loadquadgrams() -> dict[str, int]:
    """load quadgrams from text file"""
    quadgrams: dict[str, int] = {}
    with importlib.resources.open_text(
        "aldegonde.data.ngrams.english", "quadgrams.txt"
    ) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("#"):
                continue
            items = line.split()
            quadgrams[items[0]] = int(items[1])
    return quadgrams


def frequency_to_probability(frequency_map, decorator=lambda f: f):
    """Transform a ``frequency_map`` into a map of probability using the sum of all frequencies as the total.

    Example:
    -------
        >>> frequency_to_probability({'a': 2, 'b': 2})
        {'a': 0.5, 'b': 0.5}

    Args:
    ----
        frequency_map (dict): The dictionary to transform
        decorator (function): A function to manipulate the probability

    Returns:
    -------
        Dictionary of ngrams to probability
    """
    total = sum(frequency_map.values())
    return {k: decorator(v / total) for k, v in frequency_map.items()}


quadgrams = loadquadgrams()
quadgrams_prob = frequency_to_probability(quadgrams, decorator=log10)
quadgrams_floor = log10(0.001 / sum(quadgrams.values()))


# use scipy.stats.chisquare?
def mychisquare(text1: Sequence[T], text2: Sequence[T], length: int = 1) -> float:
    """Calculate chi^2 test of 2 texts.

    It's calculated by multiplying the frequency count of one letter
    in the first string by the frequency count of the same letter
    in the second string, and then doing the same for all the other
    letters, and summing the result. This is divided by the product
    of the total number of letters in each string.
    """
    total: float = 0.0
    d1 = ngram_distribution(text1, length=length)
    d2 = ngram_distribution(text2, length=length)
    for key in d1:
        if key in d2:
            total += d1[key] * d2[key]
    return total / (len(d1.keys()) * len(d2.keys()))


def gtest(text1: Sequence[T], text2: Sequence[T], length: int = 1) -> float:
    """https://en.wikipedia.org/wiki/G-test
    use scipy.stats.power_divergence with lambda_=0
    Calculate another comparison of 2 texts.
    """
    d1 = ngram_distribution(text1, length=length)
    d2 = ngram_distribution(text2, length=length)

    obs: list[float] = []
    exp: list[float] = []
    for k in d2:
        obs.append(d1[k])
        exp.append(d2[k])
    print(power_divergence(f_obs=obs, f_exp=exp, lambda_=0))
    return float(power_divergence(f_obs=obs, f_exp=exp, lambda_=0).statistic)


def logdist(text1: Sequence[T], text2: Sequence[T], length: int = 1) -> float:
    """Scoring using log of frequency."""
    d1 = ngram_distribution(text1, length=length)
    d2 = ngram_distribution(text2, length=length)
    total: float = 0.0
    for key in d1:
        if key in d2:
            total += log10(d1[key])
    return total


def chisquarescipy(text: Sequence[T], length: int = 4) -> float:
    """ """
    floor = 0.01
    frequency_map = quadgrams
    ngrams = frequency_to_probability(frequency_map)
    d1 = ngram_distribution(text, length=length)
    d2 = [ngrams.get(ngram, floor) for ngram in d1]
    return float(chisquare(f_obs=d1, f_exp=d2))


def quadgramscore(text: Sequence[T], length: int = 4) -> float:
    """Quadgram score against test corpus."""
    # frequency_map = quadgrams
    # ngrams = frequency_to_probability(frequency_map, decorator=log10)
    # floor = log10(0.001 / sum(frequency_map.values()))
    # return float(sum(ngrams.get(ngram, floor) for ngram in iterngrams(text, length)))
    return float(
        sum(
            quadgrams_prob.get(ngram, quadgrams_floor)
            for ngram in iterngrams(text, length)
        )
    )


def trigramscore(text: Sequence[T], length: int = 3) -> float:
    """Trigram score against test corpus."""
    frequency_map = trigrams.trigrams
    ngrams = frequency_to_probability(frequency_map, decorator=log10)
    floor = log10(0.001 / sum(frequency_map.values()))
    return float(sum(ngrams.get(ngram, floor) for ngram in iterngrams(text, length)))


# def NgramScorer(frequency_map):


# def NgramScorer(frequency_map):
#     """Compute the score of a text by using the frequencies of ngrams.
#
#     Example:
#         >>> fitness = NgramScore(english.unigrams)
#         >>> fitness("ABC")
#         -4.3622319742618245
#
#     Args:
#         frequency_map (dict): ngram to frequency mapping
#     """
#     # Calculate the log probability
#     length = len(next(iter(frequency_map)))
#     # TODO: 0.01 is a magic number. Needs to be better than that.
#     floor = math.log10(0.01 / sum(frequency_map.values()))
#     ngrams = frequency.frequency_to_probability(frequency_map, decorator=math.log10)
#
#     def inner(text):
#         # I dont like this, it is only for the .upper() to work,
#         # But I feel as though this can be removed in later refactoring
#         text = "".join(text)
#         text = remove(text.upper(), string.whitespace + string.punctuation)
#         return sum(ngrams.get(ngram, floor) for ngram in iterate_ngrams(text, length))
#
#     return inner
