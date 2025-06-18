from collections.abc import Sequence
from math import sqrt
from typing import NamedTuple

from aldegonde.stats.ngrams import ngram_distribution

# --- Mutual Index of Coincidence (MIOC) Implementation ---


class MiocTuple(NamedTuple):
    """NamedTuple for storing MIOC calculation results."""

    mioc: float
    nmioc: float
    sigmage: float


def mioc(
    text1: Sequence[object],
    text2: Sequence[object],
    length: int = 1,
    cut: int = 0,
) -> float:
    """Mutual Index of Coincidence (MIOC).

    Calculates the MIOC between two sequences for specified ngram length and cut.

    Args:
        text1: The first sequence of objects.
        text2: The second sequence of objects.
        length: The size of the ngram.
        cut: The starting offset for ngrams (0 for sliding, >0 for non-overlapping).

    Returns:
        The Mutual Index of Coincidence as a float.
    """
    freqs1: dict[str, int] = ngram_distribution(text1, length=length, cut=cut)
    freqs2: dict[str, int] = ngram_distribution(text2, length=length, cut=cut)

    L1: int = sum(freqs1.values())
    L2: int = sum(freqs2.values())

    # Return 0.0 if either text has insufficient data for meaningful statistics
    if L1 < 2 or L2 < 2:
        return 0.0

    sum_prod: float = 0.0
    # Iterate over the union of keys to ensure all ngrams present in either text are considered
    all_ngrams: set[str] = freqs1.keys() | freqs2.keys()
    for ngram in all_ngrams:
        sum_prod += freqs1.get(ngram, 0) * freqs2.get(ngram, 0)

    # The denominator L1 * L2 will not be zero due to the L1 < 2 or L2 < 2 check above.
    return sum_prod / (L1 * L2)


def nmioc(
    text1: Sequence[object],
    text2: Sequence[object],
    alphabetsize: int,
    length: int = 1,
    cut: int = 0,
) -> MiocTuple:
    """Normalized Mutual Index of Coincidence (NMIOC) and statistical significance.

    Args:
        text1: The first sequence of objects.
        text2: The second sequence of objects.
        alphabetsize: The size of the underlying alphabet (e.g., 26 for English letters).
        length: The size of the ngram.
        cut: The starting offset for ngrams.

    Returns:
        A MiocTuple containing:
        - mioc: The raw Mutual Index of Coincidence.
        - nmioc: The Normalized Mutual Index of Coincidence.
        - sigmage: The number of standard deviations away from random data.
    """
    raw_mioc_value = mioc(text1, text2, length=length, cut=cut)

    # Re-calculate lengths for ngrams as they are needed for statistical significance
    freqs1: dict[str, int] = ngram_distribution(text1, length=length, cut=cut)
    freqs2: dict[str, int] = ngram_distribution(text2, length=length, cut=cut)
    L1: int = sum(freqs1.values())
    L2: int = sum(freqs2.values())

    if L1 < 2 or L2 < 2:
        return MiocTuple(mioc=0.0, nmioc=0.0, sigmage=0.0)

    C = pow(alphabetsize, length)  # Size of the ngram alphabet

    normalized_mioc_value = C * raw_mioc_value

    # Standard deviation for NMIOC for random data.
    # Formula: sqrt((C-1)/(L1*L2))
    # This approximates the standard deviation of NMIOC under the assumption of random data,
    # where the expected NMIOC is 1.0.
    sd = float("inf") if C <= 1 or L1 * L2 == 0 else sqrt((C - 1) / (L1 * L2))

    # Calculate sigmage (number of standard deviations from the random expectation of 1.0)
    if sd == 0.0:
        sigmage = float("inf") if normalized_mioc_value != 1.0 else 0.0
    else:
        sigmage = abs(normalized_mioc_value - 1.0) / sd

    return MiocTuple(mioc=raw_mioc_value, nmioc=normalized_mioc_value, sigmage=sigmage)


def print_mioc_statistics(
    text1: Sequence[object],
    text2: Sequence[object],
    alphabetsize: int,
) -> None:
    """Print MIOC statistics for various ngram lengths and cuts.

    This function iterates through common ngram lengths (1 to 5) and cut
    parameters to provide a comprehensive overview of the Mutual Index
    of Coincidence between two texts.

    Args:
        text1: The first sequence of objects.
        text2: The second sequence of objects.
        alphabetsize: The size of the underlying alphabet (e.g., 26 for English letters).
    """
    print("\n--- Mutual Index of Coincidence Statistics ---")
    for length in range(1, 6):
        for cut in range(length + 1):
            # Skip cut=1 for length=1 to align with original print_ioc_statistics behavior
            if length == 1 and cut == 1:
                continue

            mioc_result = nmioc(
                text1,
                text2,
                alphabetsize=alphabetsize,
                length=length,
                cut=cut,
            )
            print(
                f"MIOC{length} (cut={cut}) = {mioc_result.nmioc:.3f} S={mioc_result.sigmage:.3f}σ ",
                end="| ",
            )
        print()
