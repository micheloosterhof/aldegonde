# ABOUTME: Multiple-comparison corrections for scan statistics: Bonferroni,
# ABOUTME: Sidak, the expected-max z threshold, and the multiplicity budget.
"""Multiple-testing corrections for scans over lags, periods, and offsets.

Any statistic scanned over a family of keys (every lag, every period, every
offset) will produce impressive-looking extremes by chance alone; the
corrections here price that look-elsewhere effect analytically. They are the
cheap complement to the empirical route in `stats.resample.family_pvalue`,
which resamples the maximum itself: use Bonferroni or Sidak when the per-test
null is known and trials are expensive, and the resampled family-wise p-value
when it is not.

The expected-max threshold and the multiplicity budget are coarser
instruments for reading a whole z-spectrum at once: the largest of n
independent standard normals sits near sqrt(2 ln n), so a spectrum whose peak
merely reaches that level is unremarkable, and a spectrum with more
|z| >= t entries than the budget predicts is structured even if no single
entry survives correction.
"""

from __future__ import annotations

from math import erfc, log, sqrt
from typing import TYPE_CHECKING, NamedTuple

from aldegonde.exceptions import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Iterable


def _validate_tests(tests: int) -> None:
    if tests < 1:
        msg = f"number of tests must be at least 1, got {tests}"
        raise InvalidInputError(msg)


def _validate_probability(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        msg = f"{name} must be in [0, 1], got {value}"
        raise InvalidInputError(msg)


def bonferroni(p_value: float, tests: int) -> float:
    """Return the Bonferroni-corrected p-value, capped at 1.

    Args:
        p_value: Uncorrected per-test p-value
        tests: Number of tests in the family

    Returns:
        min(1, p_value * tests)

    Raises:
        InvalidInputError: If p_value is outside [0, 1] or tests < 1
    """
    _validate_probability(p_value, "p_value")
    _validate_tests(tests)
    return min(1.0, p_value * tests)


def sidak(p_value: float, tests: int) -> float:
    """Return the Sidak-corrected p-value.

    Exact for independent tests and slightly less conservative than
    Bonferroni; for correlated tests it is approximate.

    Args:
        p_value: Uncorrected per-test p-value
        tests: Number of tests in the family

    Returns:
        1 - (1 - p_value) ** tests

    Raises:
        InvalidInputError: If p_value is outside [0, 1] or tests < 1
    """
    _validate_probability(p_value, "p_value")
    _validate_tests(tests)
    return 1.0 - (1.0 - p_value) ** tests


def bonferroni_threshold(alpha: float, tests: int) -> float:
    """Return the per-test alpha giving family-wise level alpha under Bonferroni.

    Args:
        alpha: Desired family-wise significance level
        tests: Number of tests in the family

    Returns:
        alpha / tests

    Raises:
        InvalidInputError: If alpha is outside [0, 1] or tests < 1
    """
    _validate_probability(alpha, "alpha")
    _validate_tests(tests)
    return alpha / tests


def sidak_threshold(alpha: float, tests: int) -> float:
    """Return the per-test alpha giving family-wise level alpha under Sidak.

    Args:
        alpha: Desired family-wise significance level
        tests: Number of tests in the family

    Returns:
        1 - (1 - alpha) ** (1 / tests)

    Raises:
        InvalidInputError: If alpha is outside [0, 1] or tests < 1
    """
    _validate_probability(alpha, "alpha")
    _validate_tests(tests)
    return 1.0 - float((1.0 - alpha) ** (1.0 / tests))


def expected_max_z(tests: int) -> float:
    """Return the expected peak of n independent standard normal draws.

    The maximum of n independent |z| values concentrates near sqrt(2 ln n).
    A scan whose best peak merely reaches this level has found nothing; a
    peak well above it deserves a proper corrected p-value.

    Args:
        tests: Number of tests in the family

    Returns:
        sqrt(2 * ln(tests)), or 0.0 for a single test

    Raises:
        InvalidInputError: If tests < 1
    """
    _validate_tests(tests)
    return sqrt(2.0 * log(tests))


class MultiplicityBudget(NamedTuple):
    """Observed versus expected count of extreme z-scores in a spectrum.

    Attributes:
        observed: How many z-scores meet the threshold
        expected: How many would meet it by chance under the standard normal
        tests: Number of z-scores examined
    """

    observed: int
    expected: float
    tests: int


def multiplicity_budget(
    zscores: Iterable[float],
    threshold: float,
    *,
    two_sided: bool = True,
) -> MultiplicityBudget:
    """Count z-scores past a threshold against the chance expectation.

    Reads a whole z-spectrum at once: even when no single entry survives
    correction, an observed count well above the expected one means the
    spectrum as a whole is structured. Under a skewed or correlated null the
    expectation is only indicative.

    Args:
        zscores: The z-scores of the scan
        threshold: The cut at which a z-score counts as extreme
        two_sided: Count |z| >= threshold; if False, count z >= threshold

    Returns:
        The observed count, the expected count under the standard normal,
        and the number of tests

    Raises:
        InvalidInputError: If threshold is negative
    """
    if threshold < 0:
        msg = f"threshold must be non-negative, got {threshold}"
        raise InvalidInputError(msg)
    values = list(zscores)
    tail = erfc(threshold / sqrt(2.0))
    per_test = tail if two_sided else tail / 2.0
    observed = sum(1 for z in values if (abs(z) if two_sided else z) >= threshold)
    return MultiplicityBudget(
        observed=observed,
        expected=per_test * len(values),
        tests=len(values),
    )
