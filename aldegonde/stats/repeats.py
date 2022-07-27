from collections import Counter
import math

from scipy.stats import poisson

from ..structures import sequence


# TODO: add `cut` parameter here


def print_repeat_statistics(
    ciphertext: sequence.Sequence,
    minimum: int = 4,
    maximum: int = 10,
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
        for index in range(0, len(ciphertext) - length + 1):
            k = "-".join([str(x) for x in ciphertext[index : index + length]])
            l.append(k)
        f = Counter(l)
        for k in f.keys():
            if f[k] > 1:
                num = num + 1

        # first method, poisson distribution
        mu: float = len(ciphertext) / pow(MAX, length)
        expected1 = pow(MAX, length) * poisson.pmf(2, mu)
        var = poisson.stats(mu, loc=0, moments="v") * pow(MAX, length)
        sigmage1: float = abs(num - expected1) / math.sqrt(var)
        # sigmage: float = abs(num - expected1) / poisson.std(mu)

        # second method, simple math
        expected2 = len(ciphertext) * (len(ciphertext) - 1) / (2 * pow(MAX, length))
        sigmage2: float = abs(num - expected2) / math.sqrt(var)

        print(
            f"repeats length {length}: observed={num:d} expected1={expected1:.3f} S1={sigmage1:.2f}σ expected2={expected2:.3f} S2={sigmage2:.2f}σ"
        )


def repeat(
    ciphertext: sequence.Sequence, minimum: int = 2, maximum: int = 10
) -> dict[str, int]:
    """
    Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the number of occurences
    """
    sequences = {}
    for length in range(minimum, maximum + 1):
        l = []
        for index in range(0, len(ciphertext) - length + 1):
            k = "-".join([str(x) for x in ciphertext[index : index + length]])
            l.append(k)
        f = Counter(l)
        for k in f.keys():
            if f[k] > 1:
                sequences[k] = f[k]

    return sequences


def repeat2(
    ciphertext: sequence.Sequence, minimum: int = 2, maximum: int = 10
) -> dict[str, list[int]]:
    """
    Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the list of starting positions of that substring
    """
    sequences = {}
    for length in range(minimum, maximum + 1):
        l: dict[str, list[int]] = {}
        for index in range(0, len(ciphertext) - length + 1):
            k = "-".join([str(x) for x in ciphertext[index : index + length]])
            if k in l.keys():
                l[k].append(index)
            else:
                l[k] = [index]

        for k in l.keys():
            if len(l[k]) > 1:
                sequences[k] = l[k].copy()

    return sequences
