"""Higher-order coincidence statistics.

The kappa test measures second-order coincidence: how often a symbol equals
the symbol a fixed lag away. Some ciphers leave a higher-order signature
instead, where the lag-L matches themselves cluster at particular separations.
This module exposes the lag-L match indicator and counts pairs of matches at
chosen separations, the canonical fourth-order generalization of kappa.

A periodic interaction shows up as an excess of joint matches at a separation
tied to the period. Significance is best judged against a Monte Carlo null
built from shuffles of the same text, since the joint counts are not
independent; this module supplies the raw statistic, not a p-value.

All functions work on arbitrary alphabets (runes, integers, letters).
"""

from collections.abc import Sequence
from typing import TypeVar

from aldegonde.validation import validate_positive_integer, validate_text_sequence

T = TypeVar("T")


def match_indicator(text: Sequence[T], lag: int) -> list[bool]:
    """Return the lag-L match indicator of a sequence.

    Entry i is True when the symbol at position i equals the symbol lag
    positions later. This is the per-position event whose mean is the kappa
    coincidence rate.

    Args:
        text: Sequence to analyze
        lag: Distance between the compared symbols

    Returns:
        A list of booleans of length len(text) - lag

    Raises:
        InvalidInputError: If lag is not a positive integer
        InsufficientDataError: If text is no longer than lag
    """
    validate_positive_integer(lag, "lag")
    validate_text_sequence(text, min_length=lag + 1)
    return [text[i] == text[i + lag] for i in range(len(text) - lag)]


def joint_coincidence(
    text: Sequence[T],
    lag: int,
    separations: Sequence[int],
) -> dict[int, int]:
    """Count pairs of lag-L matches at each requested separation.

    For each separation s the count is the number of positions i where the
    lag-L match indicator is True at both i and i + s. An excess at a
    separation tied to a period reveals a higher-order periodic structure
    that the plain kappa test averages away.

    Args:
        text: Sequence to analyze
        lag: Lag of the match indicator
        separations: Separations between matches to count pairs for

    Returns:
        A dictionary mapping each separation to its joint match count

    Raises:
        InvalidInputError: If lag or any separation is not a positive integer
        InsufficientDataError: If text is no longer than lag
    """
    indicator = match_indicator(text, lag)
    length = len(indicator)
    counts: dict[int, int] = {}
    for separation in separations:
        validate_positive_integer(separation, "separation")
        counts[separation] = sum(
            indicator[i] and indicator[i + separation]
            for i in range(length - separation)
        )
    return counts
