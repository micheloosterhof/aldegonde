from collections import Counter
from collections import defaultdict
from collections.abc import Sequence
import math
from typing import TypeVar

from scipy.stats import poisson

from aldegonde.structures import sequence
from aldegonde.stats.ngrams import iterngrams, ngram_distribution


T = TypeVar("T")


def print_repeat_statistics(
    ciphertext: sequence.Sequence,
    minimum: int = 4,
    maximum: int = 10,
    cut: int = 0,
    trace: bool = False,
) -> None:
    """
    Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the number of occurences
    The expected formula works best for length 3 or larger
    """
    MAX = len(ciphertext.alphabet)
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
            f"repeats length {length}: observed={num:d} expected={expected:.2f} S={sigmage:.2f}σ"
        )


def repeat(
    ciphertext: Sequence[T], minimum: int = 2, maximum: int = 10, cut: int = 0
) -> dict[str, int]:
    """
    Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the number of occurences
    """
    sequences = {}
    for length in range(minimum, maximum + 1):
        f = ngram_distribution(ciphertext, length=length, cut=cut)
        for k, v in f.items():
            if v > 1:
                sequences[k] = v
    return sequences


def repeat_positions(
    ciphertext: Sequence[T], minimum: int = 2, maximum: int = 10
) -> dict[str, list[int]]:
    """
    Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and
    as value the list of starting positions of that substring
    """
    sequences = {}
    for length in range(minimum, maximum + 1):
        l: dict[str, list[int]] = defaultdict(list)
        for index in range(0, len(ciphertext) - length + 1):
            k = str(ciphertext[index : index + length])
            l[k].append(index)
        for k, v in l.items():
            if len(v) > 1:
                sequences[k] = v.copy()

    return sequences


def odd_spaced_repeats(ciphertext: sequence.Sequence, minimum=3, maximum=6):
    """
    ROD = percentage of odd-spaced repeats to all repeats.
    """
    d = []
    for length in range(minimum, maximum + 1):
        rep = repeat_positions(ciphertext, minimum=length, maximum=length)
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
