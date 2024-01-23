"""Functions around comparing texts or distributions in texts."""

from collections import defaultdict
from collections.abc import Callable, Sequence
from importlib.resources import files
from math import log10
from typing import TypeVar

from scipy.stats import chisquare, power_divergence

from aldegonde.stats.ngrams import iterngrams, ngram_distribution

T = TypeVar("T")


def loadgrams(module: str, filename: str) -> dict[str, int]:
    """Load quadgrams from text file"""
    grams: dict[str, int] = {}
    with files(module).joinpath(filename).open() as f:
        #    with importlib.resources.open_text(module, filename) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("#"):
                continue
            items = line.split()
            grams[items[0]] = int(items[1])
    return grams


def frequency_to_probability(
    frequency_map: dict[str, int],
    decorator: Callable = lambda f: f,
) -> defaultdict[str, float]:
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
    return defaultdict(
        float,
        {k: decorator(v / total) for k, v in frequency_map.items()},
    )


unigrams = loadgrams("aldegonde.data.ngrams.english", "unigrams.txt")
bigrams = loadgrams("aldegonde.data.ngrams.english", "bigrams.txt")
trigrams = loadgrams("aldegonde.data.ngrams.english", "trigrams.txt")
quadgrams = loadgrams("aldegonde.data.ngrams.english", "quadgrams.txt")


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
    keys = set(list(d1.keys()) + list(d2.keys()))
    for key in keys:
        total += d1[key] * d2[key]
    return total / (len(text1) * len(text2))


def gtest(text1: Sequence[T], text2: Sequence[T], length: int = 1) -> float:
    """https://en.wikipedia.org/wiki/G-test
    use scipy.stats.power_divergence with lambda_=0
    Calculate another comparison of 2 texts.
    """
    d1 = frequency_to_probability(ngram_distribution(text1, length=length))
    d2 = frequency_to_probability(ngram_distribution(text2, length=length))

    keys = set(list(d1.keys()) + list(d2.keys()))
    obs: list[float] = [d1[k] for k in keys]
    exp: list[float] = [d2[k] for k in keys]
    # print(power_divergence(f_obs=obs, f_exp=exp, lambda_=0))
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


def NgramScorer(frequency_map: dict[str, int]) -> Callable[[str], float]:
    """Compute the score of a text by using the frequencies of ngrams.

    Example:
    -------
        >>> fitness = NgramScore(english.unigrams)
        >>> fitness("ABC")
        -4.3622319742618245
    Args:
        frequency_map (dict): ngram to frequency mapping

    http://practicalcryptography.com/media/cryptanalysis/files/ngram_score_1.py
    """
    length = len(next(iter(frequency_map)))
    # 0.01 is a magic number. Needs to be better than that.
    floor: float = log10(0.01 / sum(frequency_map.values()))
    ngrams: dict[str, float] = defaultdict(
        lambda: floor,
        frequency_to_probability(frequency_map, decorator=log10),
    )

    def inner(text: str) -> float:
        gen = (ngrams[str(ngram)] for ngram in iterngrams(text, length))
        return sum(gen)

    return inner


quadgramscore = NgramScorer(quadgrams)
trigramscore = NgramScorer(trigrams)
bigramscore = NgramScorer(bigrams)
