"""Kasiski examination: repeated n-grams at a distance.

This is the classical Kasiski examination (Friedrich Kasiski, 1863, earlier
discovered by Charles Babbage). For every rune or set of runes (n-gram) that
occurs more than once in the ciphertext, the distance between the occurrences
is recorded. In a periodic polyalphabetic cipher, repeated plaintext encrypted
with the same part of the key produces repeated ciphertext, so these distances
tend to be multiples of the key period. Counting which candidate periods
divide the observed distances reveals the most likely key length.

The single-rune (length=1) variant of the distance spectrum is equivalent to
the autocorrelation / kappa test: the number of n-gram pairs at distance d
equals the number of coincidences at shift d.

All functions work on arbitrary alphabets (runes, integers, letters).
"""

from collections import Counter, defaultdict
from collections.abc import Sequence
from math import sqrt
from typing import TypeVar

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.ngrams import iterngram_positions
from aldegonde.stats.zscore import z_score
from aldegonde.validation import validate_positive_integer, validate_text_sequence

T = TypeVar("T")


def repeat_distances(
    text: Sequence[T],
    length: int = 1,
    cut: int = 0,
    max_distance: int | None = None,
) -> dict[tuple[T, ...], list[int]]:
    """Find the distances at which each repeated n-gram recurs.

    For every n-gram that occurs more than once, the distances between all
    pairs of its occurrences are returned. For a repeated plaintext fragment
    enciphered with the same key alignment, every such distance is a multiple
    of the period. Distances are measured in source text positions, also
    for non-overlapping ngrams (cut != 0).

    Args:
        text: Sequence to analyze
        length: Size of n-gram (1 = single runes, 2 = pairs, etc.)
        cut: Passed to ngram generation; 0 = sliding window
        max_distance: Ignore occurrence pairs further apart than this;
            None keeps all pairs. A cap bounds the cost on long texts,
            where frequent n-grams otherwise produce quadratically many pairs

    Returns:
        Dictionary keyed by the repeated n-gram (as a tuple of its symbols),
        with the list of pairwise distances between its occurrences as value

    Raises:
        InvalidInputError: If length is not a positive integer
        InsufficientDataError: If text is shorter than length + 1
    """
    validate_positive_integer(length, "length")
    validate_text_sequence(text, min_length=length + 1)
    positions: dict[tuple[T, ...], list[int]] = defaultdict(list)
    for index, gram in iterngram_positions(text, length=length, cut=cut):
        positions[tuple(gram)].append(index)

    out: dict[tuple[T, ...], list[int]] = {}
    for gram, occurrences in positions.items():
        if len(occurrences) < 2:
            continue
        distances: list[int] = []
        # occurrences are ascending, so the inner loop can stop at the cap
        for i, first in enumerate(occurrences):
            for second in occurrences[i + 1 :]:
                distance = second - first
                if max_distance is not None and distance > max_distance:
                    break
                distances.append(distance)
        if distances:
            out[gram] = distances
    return out


def distance_spectrum(
    text: Sequence[T],
    length: int = 1,
    cut: int = 0,
    max_distance: int | None = None,
) -> Counter[int]:
    """Count repeated n-grams for every lag distance.

    For each distance d, the count is the number of n-gram pairs that are
    identical and exactly d positions apart. This is the full-spectrum
    equivalent of the kappa (autocorrelation) test: peaks appear at
    multiples of the cipher period.

    Args:
        text: Sequence to analyze
        length: Size of n-gram
        cut: Passed to ngram generation; 0 = sliding window
        max_distance: Ignore lags larger than this; None keeps all

    Returns:
        Counter mapping lag distance to number of repeated n-gram pairs

    Raises:
        InvalidInputError: If length is not a positive integer
        InsufficientDataError: If text is shorter than length + 1
    """
    spectrum: Counter[int] = Counter()
    for distances in repeat_distances(
        text,
        length=length,
        cut=cut,
        max_distance=max_distance,
    ).values():
        spectrum.update(distances)
    return spectrum


def _validate_bounds(minimum: int, maximum: int, name: str) -> None:
    """Validate a minimum/maximum parameter pair."""
    validate_positive_integer(minimum, f"min_{name}")
    validate_positive_integer(maximum, f"max_{name}")
    if minimum > maximum:
        msg = f"min_{name} {minimum} exceeds max_{name} {maximum}"
        raise InvalidInputError(msg, input_value=minimum)


def _collect_distances(
    text: Sequence[T],
    min_length: int,
    max_length: int,
    max_distance: int | None,
) -> Counter[int]:
    """Pool repeat distances over all n-gram sizes in a range."""
    _validate_bounds(min_length, max_length, "length")
    validate_text_sequence(text, min_length=min_length + 1)
    distances: Counter[int] = Counter()
    for length in range(min_length, max_length + 1):
        if length + 1 > len(text):
            break
        distances.update(
            distance_spectrum(text, length=length, max_distance=max_distance),
        )
    return distances


def _count_divisible(
    distances: Counter[int],
    min_period: int,
    max_period: int,
) -> dict[int, int]:
    """Count, for each candidate period, the distances it divides."""
    return {
        period: sum(c for d, c in distances.items() if d % period == 0)
        for period in range(min_period, max_period + 1)
    }


def kasiski_examination(
    text: Sequence[T],
    min_length: int = 1,
    max_length: int = 5,
    min_period: int = 2,
    max_period: int = 20,
    max_distance: int | None = None,
) -> dict[int, float]:
    """Kasiski examination over all n-gram sizes in a range.

    Collects the distances between repeated n-grams of every size from
    min_length to max_length and scores, for each candidate period, how many
    of these distances it divides relative to chance. By chance a period p
    divides 1/p of all distances, so the score is the observed count divided
    by total/p. The true period (and its divisors) score well above 1.0.

    Note: classical Kasiski uses n-grams of length 3 and up to suppress
    coincidental repeats; including single runes (min_length=1) adds the
    autocorrelation signal but also more noise, and is quadratically more
    expensive on long texts unless max_distance is set.

    Args:
        text: Sequence to analyze
        min_length: Smallest n-gram size to examine
        max_length: Largest n-gram size to examine
        min_period: Smallest candidate period to score
        max_period: Largest candidate period to score
        max_distance: Ignore repeats further apart than this; None keeps all

    Returns:
        Dictionary mapping each candidate period to its score (observed
        divisible distances / expected by chance), sorted descending

    Raises:
        InvalidInputError: If length or period bounds are invalid
        InsufficientDataError: If text is too short for min_length
    """
    _validate_bounds(min_period, max_period, "period")
    distances = _collect_distances(text, min_length, max_length, max_distance)
    total = sum(distances.values())
    counts = _count_divisible(distances, min_period, max_period)
    scores = {
        period: count * period / total if total > 0 else 0.0
        for period, count in counts.items()
    }
    return dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))


def print_kasiski_statistics(
    text: Sequence[T],
    min_length: int = 1,
    max_length: int = 5,
    min_period: int = 2,
    max_period: int = 20,
    max_distance: int | None = None,
) -> None:
    """Print Kasiski examination results for a range of candidate periods.

    For each candidate period, prints the number of repeat distances it
    divides, the count expected by chance (total/period), the ratio (the
    same score returned by kasiski_examination), and the Poisson z-score.
    A ratio well above 1.0 marks the period and its divisors.

    Args:
        text: Sequence to analyze
        min_length: Smallest n-gram size to examine
        max_length: Largest n-gram size to examine
        min_period: Smallest candidate period to score
        max_period: Largest candidate period to score
        max_distance: Ignore repeats further apart than this; None keeps all

    Raises:
        InvalidInputError: If length or period bounds are invalid
        InsufficientDataError: If text is too short for min_length
    """
    _validate_bounds(min_period, max_period, "period")
    distances = _collect_distances(text, min_length, max_length, max_distance)
    total = sum(distances.values())
    if total == 0:
        print("kasiski: no repeated ngrams found")
        return

    print(
        "null hypothesis: no period; repeat distances fall uniformly (Poisson); "
        "z = standard deviations from this null"
    )
    for period, count in _count_divisible(distances, min_period, max_period).items():
        mu = total / period
        z = z_score(count, mu, sqrt(mu))
        print(
            f"kasiski: period={period:<3d} count={count:<6d} "
            f"expected={mu:<8.1f} ratio={count / mu:.2f} z={z:+5.2f}",
        )
