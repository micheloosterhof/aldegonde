"""In-depth coincidence test: detect a shared keystream by aligning units.

When several messages or text units are enciphered with the same keystream
starting from a common reset point, the symbols in corresponding column
positions coincide far more often than chance. This is the classical
detection of "messages in depth". Stacking the units aligned at their start
(or their end) and counting column-wise coincidences across every pair of
units gives a coincidence count; comparing it to the chance expectation of
1/alphabetsize as a binomial z-score reveals a shared or restarting keystream.

The z-score treats every column comparison as an independent Bernoulli trial
with success probability 1/alphabetsize, the same approximation used by the
kappa test. Because a unit takes part in several pairs the trials are not
strictly independent, so the z-score is indicative rather than exact.

All functions work on arbitrary alphabets (runes, integers, letters).
"""

from collections.abc import Sequence
from dataclasses import dataclass
from math import sqrt
from typing import TypeVar

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.validation import validate_positive_integer

T = TypeVar("T")


@dataclass(frozen=True)
class AlignmentResult:
    """Outcome of an in-depth alignment coincidence test.

    Attributes:
        hits: Number of coinciding column comparisons across all unit pairs
        opportunities: Total number of column comparisons made
        expected: Coincidences expected by chance (opportunities / alphabetsize)
        z_score: Standardized excess of hits over the chance expectation
    """

    hits: int
    opportunities: int
    expected: float
    z_score: float


def alignment_coincidence(
    units: Sequence[Sequence[T]],
    alphabetsize: int = 0,
    *,
    align: str = "left",
    min_length: int = 1,
) -> AlignmentResult:
    """Count column coincidences between units aligned at a common boundary.

    Every pair of units is overlaid and compared column by column over the
    length of the shorter unit. With align="left" the units share position 0;
    with align="right" they share their final position. A coincidence count
    well above the chance expectation (large positive z) indicates that the
    units were produced with the same keystream from the alignment boundary.

    Args:
        units: The text units to overlay (words, lines, pages, messages)
        alphabetsize: Size of the alphabet; 0 auto-detects from the symbols
        align: "left" to align at the start, "right" to align at the end
        min_length: Units shorter than this are ignored

    Returns:
        An AlignmentResult with the hit count, opportunities, chance
        expectation, and z-score

    Raises:
        InvalidInputError: If align is not "left" or "right", or if
            alphabetsize or min_length is invalid
        InsufficientDataError: If fewer than two units meet min_length
    """
    if align not in ("left", "right"):
        msg = f"align must be 'left' or 'right', got {align!r}"
        raise InvalidInputError(msg, input_value=align)
    validate_positive_integer(min_length, "min_length")
    if alphabetsize != 0:
        validate_positive_integer(alphabetsize, "alphabetsize")

    kept = [u for u in units if len(u) >= min_length]
    if len(kept) < 2:
        msg = f"need at least two units of length >= {min_length}, got {len(kept)}"
        raise InsufficientDataError(msg, required_length=2, actual_length=len(kept))

    if alphabetsize == 0:
        alphabetsize = len({symbol for unit in kept for symbol in unit})

    hits = 0
    opportunities = 0
    for i, first in enumerate(kept):
        for second in kept[i + 1 :]:
            overlap = min(len(first), len(second))
            opportunities += overlap
            if align == "left":
                hits += sum(first[k] == second[k] for k in range(overlap))
            else:
                hits += sum(
                    first[-1 - k] == second[-1 - k] for k in range(overlap)
                )

    probability = 1 / alphabetsize
    expected = opportunities * probability
    sd = sqrt(opportunities * probability * (1 - probability))
    z_score = (hits - expected) / sd if sd > 0 else 0.0
    return AlignmentResult(
        hits=hits,
        opportunities=opportunities,
        expected=expected,
        z_score=z_score,
    )
