import math
from collections import Counter
from collections.abc import Sequence
from typing import TypeVar

from scipy.stats import poisson

from aldegonde.stats.ngrams import iterngrams, ngram_distribution, ngram_positions

T = TypeVar("T")


def print_repeat_statistics(
    ciphertext: Sequence[T],
    minimum: int = 4,
    maximum: int = 10,
    cut: int = 0,
    alphabetsize: int = 26,
    *,
    trace: bool = False,
) -> None:
    """Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the number of occurences
    The expected formula works best for length 3 or larger.
    """
    MAX = alphabetsize
    for length in range(minimum, maximum + 1):
        l = []
        num = 0
        for g in iterngrams(ciphertext, length=length, cut=cut):
            l.append(str(g))
        for v in Counter(l).values():
            if v > 1:
                num = num + 1

        # first method, poisson distribution
        mu: float = len(ciphertext) / pow(MAX, length)
        expected = pow(MAX, length) * poisson.sf(k=1, mu=mu, loc=0)
        var = poisson.stats(mu, loc=0, moments="v") * pow(MAX, length)
        sigmage: float = abs(num - expected) / math.sqrt(var)
        # sigmage: float = abs(num - expected1) / poisson.std(mu)
        print(
            f"repeats length {length}: observed={num:d} expected={expected:.2f} S={sigmage:.2f}σ",
        )


def repeat_distribution(
    ciphertext: Sequence[T],
    length: int = 2,
    cut: int = 0,
) -> dict[str, int]:
    """Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the number of occurences.
    """
    return {
        k: v
        for k, v in ngram_distribution(ciphertext, length=length, cut=cut).items()
        if v > 1
    }


def print_repeat_positions(
    ciphertext: Sequence[T],
    minimum: int = 2,
    maximum: int = 10,
) -> None:
    """Print repeating sequences in the list, up to `maximum`. Max defaults to 10."""
    for length in range(minimum, maximum + 1):
        pos = repeat_positions(ciphertext, length=length)
        print(f"repeats length {length}: {pos}")


def repeat_positions(
    ciphertext: Sequence[T],
    length: int,
    cut: int = 0,
) -> dict[str, list[int]]:
    """Repeat positions are just ngrams where each list has at least 2 entries."""
    return {
        k: v
        for k, v in ngram_positions(ciphertext, length=length, cut=cut).items()
        if len(v) > 1
    }


def odd_spaced_repeats(
    ciphertext: Sequence[T],
    minimum: int = 3,
    maximum: int = 6,
) -> None:
    """ROD = percentage of odd-spaced repeats to all repeats."""
    d = []
    for length in range(minimum, maximum + 1):
        rep = repeat_positions(ciphertext, length=length)
        for v in rep.values():
            for l in range(1, len(v)):
                d.append(v[l] - v[l - 1])

    even = 0
    odd = 0
    for x in d:
        if x / 2 == int(x / 2):
            even += 1
        else:
            odd += 1
    if even + odd > 0:
        print(f"even {even:3d} odd {odd:3d}  percentage: {100*odd/(even+odd):02f}")
