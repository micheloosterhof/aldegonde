"""Functions around comparing texts or distributions in texts."""

from collections import Counter, defaultdict
from collections.abc import Callable, Sequence
from importlib.resources import files
from math import log10
from typing import TypeVar

from scipy.stats import chisquare, power_divergence

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.ngram import (
    iterngrams,
    ngram_counts,
    ngram_distribution,
)

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
    decorator: Callable[[float], float] = lambda f: f,
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


def chi_test(text1: Sequence[T], text2: Sequence[T], length: int = 1) -> float:
    """Friedman's chi test: how alike two texts' symbol distributions are.

    Multiply the count of each ngram in the first text by its count in the
    second, sum over ngrams, and divide by the product of the two lengths. Two
    texts drawn from the same distribution score near the sum of squared symbol
    frequencies; unrelated texts score near 1/alphabet size.

    This is NOT a chi-square: it compares two texts to each other rather than a
    text to a reference, and it has no degrees of freedom. See `chi_square` for
    goodness of fit against a table.

    Args:
        text1: First sequence
        text2: Second sequence
        length: Size of the ngram compared

    Returns:
        The cross-product sum, normalised by both lengths
    """
    d1 = ngram_counts(text1, length=length)
    d2 = ngram_counts(text2, length=length)
    total = sum(d1[key] * d2[key] for key in set(d1) | set(d2))
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


def chi_square(
    text: Sequence[str],
    length: int = 4,
    frequency_map: dict[str, int] | None = None,
) -> float:
    """Chi-square goodness of fit of a text's ngrams against a reference table.

    Counts the text's ngrams, scales the reference frequencies to the same
    total, and measures the squared deviation. A text drawn from the same
    distribution as the reference scores low; an unrelated one scores high.

    scipy does the arithmetic when it is importable, and the same formula is
    applied directly when it is not, so the result does not depend on whether
    the optional dependency is installed.

    Args:
        text: Sequence of symbols to test
        length: Size of the ngram counted
        frequency_map: Reference ngram frequencies; the English quadgrams by
            default, which only makes sense with `length` 4

    Returns:
        The chi-square statistic; 0.0 when the text is too short to hold an ngram

    Raises:
        InvalidInputError: If the reference table is empty
    """
    reference = quadgrams if frequency_map is None else frequency_map
    if not reference:
        msg = "reference frequency map is empty"
        raise InvalidInputError(msg)

    observed = Counter("".join(gram) for gram in iterngrams(text, length=length))
    total = sum(observed.values())
    if not total:
        return 0.0

    probability = frequency_to_probability(reference)
    # an ngram absent from the reference is rare, not impossible: without a
    # floor its expected count is zero and the statistic is undefined
    floor = 0.5 / sum(reference.values())
    weights = [probability.get(gram, floor) for gram in observed]
    scale = total / sum(weights)
    expected = [w * scale for w in weights]
    counts = [observed[gram] for gram in observed]

    try:
        return float(chisquare(f_obs=counts, f_exp=expected).statistic)
    except (ImportError, ValueError, TypeError):
        # same formula, so a machine without scipy reports the same number
        return sum((o - e) ** 2 / e for o, e in zip(counts, expected))


def make_ngram_scorer(
    frequency_map: dict[str, int],
) -> Callable[[Sequence[str]], float]:
    """Compute the score of a text by using the frequencies of ngrams.

    Example:
    -------
        >>> fitness = make_ngram_scorer(english.unigrams)
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

    def inner(text: Sequence[str]) -> float:
        # join rather than str(): an ngram taken from a LIST of runes stringifies
        # to "['A', 'B', ...]", which matches no key, so every position would
        # silently fall to the floor and the score would be a constant.
        return sum(ngrams["".join(ngram)] for ngram in iterngrams(text, length))

    return inner


quadgramscore = make_ngram_scorer(quadgrams)
trigramscore = make_ngram_scorer(trigrams)
bigramscore = make_ngram_scorer(bigrams)
