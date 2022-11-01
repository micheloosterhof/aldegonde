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
            f"repeats length {length}: observed={num:d} expected={expected:.2f} S1={sigmage:.2f}σ"
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
        for k, v in f.items():
            if v > 1:
                sequences[k] = v

    return sequences


def repeat2(
    ciphertext: sequence.Sequence, minimum: int = 2, maximum: int = 10
) -> dict[str, list[int]]:
    """
    Find repeating sequences in the list, up to `maximum`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and
    as value the list of starting positions of that substring
    """
    sequences = {}
    for length in range(minimum, maximum + 1):
        l: dict[str, list[int]] = {}
        for index in range(0, len(ciphertext) - length + 1):
            k = "-".join([str(x) for x in ciphertext[index : index + length]])
            if k in l:
                l[k].append(index)
            else:
                l[k] = [index]

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
        rep = repeat2(ciphertext, minimum=length, maximum=length)
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
