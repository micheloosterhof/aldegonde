# ABOUTME: Four-point coincidence statistics with closed-form nulls, the
# ABOUTME: signature class that pairwise and single-symbol tests cannot see.
"""Four-point coincidence statistics.

Some ciphers — transposition composed with homophonic substitution, the
Zodiac-340 family — leave no first- or second-order signature at all, yet
constrain quadruples of positions: four positions in a fixed geometric
relation coincide in a pattern more (or less) often than chance. This
module counts the canonical four-point template and compares it to its
closed-form expectation under independence.

For a template of position offsets, the statistic counts the windows in
which the two pairs (positions 0,1) and (2,3) each hold equal symbols. Under
a uniform-independent null each pair matches with probability 1/N, so both
match with probability 1/N^2 and the expected count is the window count over
N^2. A scan over the template's spacing is a family of tests: read the peak
against the whole family with a look-elsewhere correction, never a single
cell.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, TypeVar

from aldegonde.exceptions import InsufficientDataError, InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


class FourPointCount(NamedTuple):
    """A four-point coincidence count against its chance expectation.

    Attributes:
        observed: Windows where both configured pairs hold equal symbols
        expected: Windows expected under a uniform-independent null
        windows: Windows examined
        z: Poisson standard score of the count against expectation
    """

    observed: int
    expected: float
    windows: int
    z: float


def fourpoint_coincidence(
    text: Sequence[T],
    offsets: tuple[int, int, int, int],
    alphabetsize: int,
) -> FourPointCount:
    """Count windows where two configured position pairs both coincide.

    For each window start i the four positions i+offsets[k] are read; the
    window counts when the symbols at the first pair (offsets 0 and 1) are
    equal and the symbols at the second pair (offsets 2 and 3) are equal.
    The expectation under a uniform-independent null is the window count
    over alphabetsize squared, and the count is standardized as a Poisson
    score. This is the four-point generalization of the coincidence tests:
    it registers structure that leaves every one- and two-point statistic at
    chance.

    Args:
        text: Sequence to analyze
        offsets: Four position offsets; the pairs (0,1) and (2,3) are tested
            for equality
        alphabetsize: Alphabet size fixing the chance rate

    Returns:
        The observed count, its expectation, the window count, and the z

    Raises:
        InvalidInputError: If alphabetsize < 2 or the offsets are negative
        InsufficientDataError: If no window fits the offsets
    """
    if alphabetsize < 2:
        msg = f"alphabetsize must be at least 2, got {alphabetsize}"
        raise InvalidInputError(msg)
    if any(offset < 0 for offset in offsets):
        msg = f"offsets must be non-negative, got {offsets}"
        raise InvalidInputError(msg)
    span = max(offsets)
    windows = len(text) - span
    if windows < 1:
        msg = f"text of length {len(text)} has no window for offsets {offsets}"
        raise InsufficientDataError(msg, span + 1, len(text))
    a, b, c, d = offsets
    observed = 0
    for i in range(windows):
        if text[i + a] == text[i + b] and text[i + c] == text[i + d]:
            observed += 1
    expected = windows / (alphabetsize * alphabetsize)
    sd = expected**0.5
    z = (observed - expected) / sd if sd > 0 else 0.0
    return FourPointCount(
        observed=observed,
        expected=expected,
        windows=windows,
        z=z,
    )
