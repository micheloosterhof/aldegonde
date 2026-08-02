# ABOUTME: Chi-square tests packaged with a z effect size: uniformity,
# ABOUTME: exposure-weighted rate uniformity, and lag contingency tables.
"""Chi-square tests with a standardized effect size.

Every test returns a ChiSquare carrying the statistic, its degrees of
freedom, the Wilson-Hilferty z (a normal-scale effect size comparable across
tests with different df), and the survival p-value. The z answers "how far
from null", the p answers "how surprising"; when a test is one of many in a
scan, correct the p with `stats.multitest` before believing it.

Tests included:

    uniformity            symbol counts against a flat distribution
    goodness_of_fit       counts against arbitrary expected weights
    rate_uniformity       event rates across bins with unequal exposure
    lag_contingency       (x[i], x[i+lag]) table against independence,
                          optionally masking the diagonal
"""

from __future__ import annotations

from math import sqrt
from typing import TYPE_CHECKING, NamedTuple, TypeVar

from scipy.stats import chi2 as _chi2_dist

from aldegonde.exceptions import InsufficientDataError, InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

T = TypeVar("T")
K = TypeVar("K")


class ChiSquare(NamedTuple):
    """A chi-square statistic with its normal-scale effect size.

    Attributes:
        chi2: The chi-square statistic
        df: Degrees of freedom
        z: Wilson-Hilferty standardized value; positive means more structure
            than the null expects
        p: Survival probability of chi2 at df degrees of freedom
    """

    chi2: float
    df: int
    z: float
    p: float


def wilson_hilferty(chi2: float, df: int) -> float:
    """Map a chi-square value to an approximate standard normal z.

    The Wilson-Hilferty cube-root transform: the z is comparable across
    tests with different degrees of freedom, which raw chi-square values are
    not.

    Args:
        chi2: The chi-square statistic
        df: Degrees of freedom

    Returns:
        The approximate standard normal deviate

    Raises:
        InvalidInputError: If df < 1 or chi2 is negative
    """
    if df < 1:
        msg = f"degrees of freedom must be at least 1, got {df}"
        raise InvalidInputError(msg)
    if chi2 < 0:
        msg = f"chi-square must be non-negative, got {chi2}"
        raise InvalidInputError(msg)
    variance = 2.0 / (9.0 * df)
    cube_root = float((chi2 / df) ** (1.0 / 3.0))
    return (cube_root - (1.0 - variance)) / sqrt(variance)


def _package(chi2: float, df: int) -> ChiSquare:
    return ChiSquare(
        chi2=chi2,
        df=df,
        z=wilson_hilferty(chi2, df),
        p=float(_chi2_dist.sf(chi2, df)),
    )


def uniformity(counts: Sequence[int]) -> ChiSquare:
    """Test whether counts over categories are uniform.

    Args:
        counts: Observed count per category, including zero-count categories

    Returns:
        The chi-square against the flat expectation, df = categories - 1

    Raises:
        InsufficientDataError: If there are fewer than 2 categories or no
            observations
    """
    if len(counts) < 2:
        msg = "uniformity needs at least 2 categories"
        raise InsufficientDataError(msg, 2, len(counts))
    total = sum(counts)
    if total == 0:
        msg = "uniformity needs at least one observation"
        raise InsufficientDataError(msg, 1, 0)
    expected = total / len(counts)
    statistic = sum((count - expected) ** 2 / expected for count in counts)
    return _package(statistic, len(counts) - 1)


def goodness_of_fit(counts: Sequence[int], weights: Sequence[float]) -> ChiSquare:
    """Test counts against expected weights.

    The weights need not sum to anything in particular; they are scaled to
    the observed total. Categories with zero weight must have zero count.

    Args:
        counts: Observed count per category
        weights: Expected relative weight per category

    Returns:
        The chi-square against the scaled weights, df = categories - 1

    Raises:
        InvalidInputError: If lengths differ, a weight is negative, or a
            zero-weight category has observations
        InsufficientDataError: If there are fewer than 2 categories or no
            observations
    """
    if len(counts) != len(weights):
        msg = f"{len(counts)} counts but {len(weights)} weights"
        raise InvalidInputError(msg)
    if len(counts) < 2:
        msg = "goodness_of_fit needs at least 2 categories"
        raise InsufficientDataError(msg, 2, len(counts))
    if any(weight < 0 for weight in weights):
        msg = "weights must be non-negative"
        raise InvalidInputError(msg)
    total = sum(counts)
    weight_total = sum(weights)
    if total == 0 or weight_total == 0:
        msg = "goodness_of_fit needs observations and positive total weight"
        raise InsufficientDataError(msg, 1, 0)
    statistic = 0.0
    for count, weight in zip(counts, weights):
        expected = total * weight / weight_total
        if expected == 0:
            if count:
                msg = "a zero-weight category has observations"
                raise InvalidInputError(msg)
            continue
        statistic += (count - expected) ** 2 / expected
    return _package(statistic, len(counts) - 1)


def rate_uniformity(bins: Mapping[K, tuple[int, int]]) -> ChiSquare:
    """Test whether an event rate is uniform across bins with unequal exposure.

    Each bin carries (exposure, events): the number of opportunities the bin
    offered and the number of events that occurred there. The null is one
    shared rate — total events over total exposure — so a significant result
    means the rate itself depends on the bin, not merely that big bins hold
    more events. This is the correct form of "do events cluster on axis X"
    whenever bins differ in size; a plain frequency chi-square is not.

    Args:
        bins: Mapping from bin label to (exposure, events)

    Returns:
        The chi-square of events against the shared-rate expectation over
        bins with positive exposure, df = such bins - 1

    Raises:
        InvalidInputError: If a bin has negative exposure or events, or
            events exceed exposure
        InsufficientDataError: If fewer than 2 bins have exposure, or no
            events occurred anywhere
    """
    exposed: list[tuple[int, int]] = []
    for label, (exposure, events) in bins.items():
        if exposure < 0 or events < 0 or events > exposure:
            msg = (
                f"bin {label!r} has invalid (exposure, events) = ({exposure}, {events})"
            )
            raise InvalidInputError(msg)
        if exposure > 0:
            exposed.append((exposure, events))
    if len(exposed) < 2:
        msg = "rate_uniformity needs at least 2 bins with exposure"
        raise InsufficientDataError(msg, 2, len(exposed))
    total_exposure = sum(exposure for exposure, _ in exposed)
    total_events = sum(events for _, events in exposed)
    if total_events == 0:
        msg = "rate_uniformity needs at least one event"
        raise InsufficientDataError(msg, 1, 0)
    rate = total_events / total_exposure
    statistic = sum(
        (events - rate * exposure) ** 2 / (rate * exposure)
        for exposure, events in exposed
    )
    return _package(statistic, len(exposed) - 1)


def lag_contingency(
    text: Sequence[T],
    lag: int,
    *,
    off_diagonal: bool = False,
) -> ChiSquare:
    """Test the pairs (x[i], x[i+lag]) against independence.

    The omnibus second-order dependence test: it sees any relation between a
    symbol and the symbol lag positions later, not only equality, which is
    all the kappa test measures. With off_diagonal=True the diagonal cells
    are removed and the remaining expectations are renormalized to the
    off-diagonal mass, so a pure doublet suppression or enhancement scores
    zero and only structure beyond it registers. The masked form is a quasi
    chi-square with df = (n-1)^2 - n — indicative, best confirmed against a
    resampled null.

    Args:
        text: Sequence to analyze
        lag: Distance between the paired symbols
        off_diagonal: Exclude cells where both symbols are equal

    Returns:
        The chi-square of the pair table against the product of its
        marginals

    Raises:
        InvalidInputError: If lag is not positive
        InsufficientDataError: If the text offers no pairs at this lag or
            uses fewer than 2 distinct symbols
    """
    if lag < 1:
        msg = f"lag must be positive, got {lag}"
        raise InvalidInputError(msg)
    pairs = len(text) - lag
    if pairs < 1:
        msg = f"text of length {len(text)} has no pairs at lag {lag}"
        raise InsufficientDataError(msg, lag + 1, len(text))
    symbols: list[T] = []
    index: dict[T, int] = {}
    for symbol in text:
        if symbol not in index:
            index[symbol] = len(symbols)
            symbols.append(symbol)
    n = len(symbols)
    if n < 2:
        msg = "lag_contingency needs at least 2 distinct symbols"
        raise InsufficientDataError(msg, 2, n)
    table = [[0] * n for _ in range(n)]
    row_totals = [0] * n
    column_totals = [0] * n
    for i in range(pairs):
        row = index[text[i]]
        column = index[text[i + lag]]
        table[row][column] += 1
        row_totals[row] += 1
        column_totals[column] += 1
    scale = 1.0
    if off_diagonal:
        # Renormalize the independence expectations to the off-diagonal mass,
        # so removing the diagonal does not misstate every remaining cell
        observed_mass = pairs - sum(table[i][i] for i in range(n))
        expected_mass = pairs - sum(
            row_totals[i] * column_totals[i] / pairs for i in range(n)
        )
        if observed_mass == 0 or expected_mass == 0:
            msg = "masking the diagonal leaves no off-diagonal mass"
            raise InsufficientDataError(msg, 1, 0)
        scale = observed_mass / expected_mass
    statistic = 0.0
    for row in range(n):
        for column in range(n):
            if off_diagonal and row == column:
                continue
            expected = scale * row_totals[row] * column_totals[column] / pairs
            if expected > 0:
                statistic += (table[row][column] - expected) ** 2 / expected
    df = (n - 1) * (n - 1) - (n if off_diagonal else 0)
    if df < 1:
        msg = "masking the diagonal leaves no degrees of freedom"
        raise InsufficientDataError(msg, 1, df)
    return _package(statistic, df)
