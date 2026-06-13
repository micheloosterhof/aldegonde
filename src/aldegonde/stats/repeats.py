import math
from collections import Counter
from collections.abc import Sequence
from typing import TypeVar

from scipy.stats import poisson

from aldegonde.stats.ngrams import iterngrams, ngram_distribution, ngram_positions
from aldegonde.stats.nulls import NullModel
from aldegonde.stats.resample import monte_carlo_map
from aldegonde.stats.zscore import z_score

T = TypeVar("T")


def _repeat_count(text: Sequence[object], length: int, cut: int) -> int:
    """Number of distinct n-grams of a given length that occur more than once."""
    counts = Counter(str(gram) for gram in iterngrams(text, length=length, cut=cut))
    return sum(1 for occurrences in counts.values() if occurrences > 1)


def print_repeat_statistics(
    ciphertext: Sequence[object],
    minimum: int = 4,
    maximum: int = 10,
    cut: int = 0,
    alphabetsize: int = 26,
    *,
    null: NullModel[object] | None = None,
    null_label: str | None = None,
    trials: int = 1000,
    seed: int = 0,
    trace: bool = False,
) -> None:
    """Count repeated n-grams per length with z-scores against a null hypothesis.

    By default the null is uniform random text and z is the closed-form Poisson
    standard score. Pass `null` (a resampler) to compare instead against a Monte
    Carlo null, for example one that preserves frequencies and the doublet rate;
    z and the expected count are then taken from that null's distribution, in the
    same format, and `null_label` names it in the header.
    """
    lengths = list(range(minimum, maximum + 1))
    if null is None:
        print(
            f"null hypothesis: uniform random text over {alphabetsize} symbols "
            f"(Poisson repeat counts); z = standard deviations from this null"
        )
        for length in lengths:
            num = _repeat_count(ciphertext, length, cut)
            mu: float = len(ciphertext) / pow(alphabetsize, length)
            expected = pow(alphabetsize, length) * poisson.sf(k=1, mu=mu, loc=0)
            var = poisson.stats(mu, loc=0, moments="v") * pow(alphabetsize, length)
            z = z_score(num, expected, math.sqrt(var))
            print(
                f"repeats length {length}: observed={num:d} "
                f"expected={expected:.2f} z={z:+.2f}",
            )
        return

    print(
        f"null hypothesis: {null_label or 'injected null model'}; "
        f"z = standard deviations from this null"
    )

    def statistic(sample: Sequence[object]) -> dict[int, float]:
        return {length: float(_repeat_count(sample, length, cut)) for length in lengths}

    results = monte_carlo_map(
        statistic, null, ciphertext, keys=lengths, trials=trials, seed=seed
    )
    for length in lengths:
        comparison = results[length]
        print(
            f"repeats length {length}: observed={int(comparison.observed):d} "
            f"expected={comparison.null_mean:.2f} z={comparison.z:+.2f}",
        )


def repeat_distribution(
    ciphertext: Sequence[object],
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
    ciphertext: Sequence[object],
    minimum: int = 2,
    maximum: int = 10,
) -> None:
    """Print repeating sequences in the list, up to `maximum`. Max defaults to 10."""
    for length in range(minimum, maximum + 1):
        pos = repeat_positions(ciphertext, length=length)
        print(f"repeats length {length}: {pos}")


def repeat_positions(
    ciphertext: Sequence[object],
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
    ciphertext: Sequence[object],
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
        print(
            f"even {even:3d} odd {odd:3d}  percentage: {100 * odd / (even + odd):02f}",
        )
