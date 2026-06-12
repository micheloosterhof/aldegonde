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
from typing import NamedTuple, TypeVar

from aldegonde.validation import validate_positive_integer, validate_text_sequence

T = TypeVar("T")


class JointCount(NamedTuple):
    """A joint match count alongside its chance expectation.

    Attributes:
        observed: Pairs of lag-L matches actually found at the separation
        expected: Pairs expected if the matches fell independently at the
            observed per-position rate
    """

    observed: int
    expected: float


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
) -> dict[int, JointCount]:
    """Count pairs of lag-L matches at each separation, against chance.

    For each separation s the observed count is the number of positions i
    where the lag-L match indicator is True at both i and i + s. The expected
    count is what that would be if the matches fell independently at the
    observed per-position rate: the number of available pairs times the
    squared rate. An observed count well above its expectation reveals a
    higher-order periodic structure that the plain kappa test averages away.

    Args:
        text: Sequence to analyze
        lag: Lag of the match indicator
        separations: Separations between matches to count pairs for

    Returns:
        A dictionary mapping each separation to its observed and expected
        joint match counts

    Raises:
        InvalidInputError: If lag or any separation is not a positive integer
        InsufficientDataError: If text is no longer than lag
    """
    indicator = match_indicator(text, lag)
    length = len(indicator)
    rate = sum(indicator) / length
    counts: dict[int, JointCount] = {}
    for separation in separations:
        validate_positive_integer(separation, "separation")
        observed = sum(
            indicator[i] and indicator[i + separation]
            for i in range(length - separation)
        )
        available_pairs = max(0, length - separation)
        counts[separation] = JointCount(
            observed=observed,
            expected=available_pairs * rate * rate,
        )
    return counts
