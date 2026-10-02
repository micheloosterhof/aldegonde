# ABOUTME: Chi-square tests that return the statistic with its degrees of freedom,
# ABOUTME: tail probability and a normal-scale z, for counts, rates and pair tables.
"""Chi-square tests with a standardized effect size.

Every test returns a ChiSquare holding the statistic, its degrees of freedom,
the Wilson-Hilferty z, and the tail probability. The z puts tests with
different degrees of freedom on one scale; the p says how surprising the
value is. A test that is one of many in a scan needs its p corrected before
it is believed.

    uniformity        counts over categories against a flat expectation
    goodness_of_fit   counts against stated expected weights
    rate_uniformity   an event rate across bins of unequal exposure
    independence      a pair table against the product of its margins,
                      with the diagonal optionally set aside
"""

from __future__ import annotations

from math import sqrt
from typing import TYPE_CHECKING, NamedTuple, TypeVar

import numpy as np
from scipy.stats import chi2 as chi2_distribution

from aldegonde.exceptions import InsufficientDataError, InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

K = TypeVar("K")


class ChiSquare(NamedTuple):
    """A chi-square statistic with its tail probability and normal-scale z.

    Attributes:
        chi2: The statistic
        df: Degrees of freedom
        z: Wilson-Hilferty standardized value; positive means more departure
            from the null than expected
        p: Probability of a value at least this large under the null
    """

    chi2: float
    df: int
    z: float
    p: float


def wilson_hilferty(chi2: float, df: int) -> float:
    """Map a chi-square value to an approximate standard normal z.

    Args:
        chi2: The statistic, non-negative
        df: Degrees of freedom, at least 1

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
    """Attach the z and the tail probability to a statistic."""
    return ChiSquare(
        chi2=chi2,
        df=df,
        z=wilson_hilferty(chi2, df),
        p=float(chi2_distribution.sf(chi2, df)),
    )


def uniformity(counts: Sequence[int]) -> ChiSquare:
    """Test whether counts over categories are flat.

    Args:
        counts: Observed count per category, zero-count categories included

    Returns:
        The chi-square against the flat expectation, df = categories - 1

    Raises:
        InsufficientDataError: If there are fewer than 2 categories or no
            observations
    """
    return goodness_of_fit(counts, [1.0] * len(counts))


def goodness_of_fit(counts: Sequence[int], weights: Sequence[float]) -> ChiSquare:
    """Test counts against expected weights.

    The weights are scaled to the observed total, so any positive scale works.
    A category with zero weight must have a zero count.

    Args:
        counts: Observed count per category
        weights: Expected relative weight per category

    Returns:
        The chi-square against the scaled weights, df = categories - 1

    Raises:
        InvalidInputError: If the lengths differ, a weight is negative, or a
            zero-weight category has observations
        InsufficientDataError: If there are fewer than 2 categories, no
            observations, or no positive weight
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
    """Test whether an event rate is the same across bins of unequal exposure.

    Each bin carries (exposure, events): the opportunities it offered and the
    events that occurred. The null is one shared rate, total events over
    total exposure, so a significant result means the rate depends on the
    bin, not that large bins hold more events.

    Args:
        bins: Maps a bin label to (exposure, events)

    Returns:
        The chi-square over bins with positive exposure, df = such bins - 1

    Raises:
        InvalidInputError: If a bin has a negative exposure or event count,
            or more events than exposure
        InsufficientDataError: If fewer than 2 bins have exposure, or no
            events occurred
    """
    exposed: list[tuple[int, int]] = []
    for label, (exposure, events) in bins.items():
        if exposure < 0 or events < 0 or events > exposure:
            msg = f"bin {label!r} has (exposure, events) = ({exposure}, {events})"
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


def independence(
    table: Sequence[Sequence[float]],
    *,
    off_diagonal: bool = False,
) -> ChiSquare:
    """Test a pair table against the product of its margins.

    This sees any relation between the two symbols of a pair, not only
    equality, which is all a coincidence rate measures. With off_diagonal the
    diagonal cells are set aside and the remaining expectations are rescaled
    to the off-diagonal mass, so a doublet excess or deficit alone scores
    zero and only structure beyond it registers. That masked form is a quasi
    chi-square with df = (n - 1)^2 - n; treat it as indicative and confirm it
    against a resampled null.

    Rows and columns with no mass are left out of the degrees of freedom.

    Args:
        table: Square pair table, as from `pair_counts`
        off_diagonal: Set the diagonal aside

    Returns:
        The chi-square against independence

    Raises:
        InvalidInputError: If the table is not square or holds a negative
            entry
        InsufficientDataError: If fewer than 2 rows and columns carry mass, or
            no mass or no degrees of freedom remain
    """
    weights = np.asarray(table, dtype=float)
    if weights.ndim != 2 or weights.shape[0] != weights.shape[1]:
        msg = f"pair table must be square, got shape {weights.shape}"
        raise InvalidInputError(msg)
    if (weights < 0).any():
        msg = "pair table holds a negative entry"
        raise InvalidInputError(msg)
    rows = weights.sum(axis=1)
    columns = weights.sum(axis=0)
    keep = (rows > 0) & (columns > 0)
    weights = weights[np.ix_(keep, keep)]
    n = int(keep.sum())
    if n < 2:
        msg = "independence needs at least 2 symbols with mass"
        raise InsufficientDataError(msg, 2, n)
    total = float(weights.sum())
    expected = np.outer(weights.sum(axis=1), weights.sum(axis=0)) / total
    cells = np.ones_like(weights, dtype=bool)
    if off_diagonal:
        cells &= ~np.eye(n, dtype=bool)
        observed_mass = float(weights[cells].sum())
        expected_mass = float(expected[cells].sum())
        if observed_mass == 0 or expected_mass == 0:
            msg = "setting the diagonal aside leaves no off-diagonal mass"
            raise InsufficientDataError(msg, 1, 0)
        expected = expected * (observed_mass / expected_mass)
    cells &= expected > 0
    statistic = float(((weights[cells] - expected[cells]) ** 2 / expected[cells]).sum())
    df = (n - 1) * (n - 1) - (n if off_diagonal else 0)
    if df < 1:
        msg = "setting the diagonal aside leaves no degrees of freedom"
        raise InsufficientDataError(msg, 1, df)
    return _package(statistic, df)
