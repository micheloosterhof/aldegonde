# ABOUTME: Binomial inference for coincidence counts: the standard score of a count
# ABOUTME: against a stated rate, the Wilson interval, and the two-proportion test.
"""Binomial inference for coincidence and rate comparisons.

A coincidence count is a number of hits among a number of trials. These
helpers do the three things every such count needs and that are easy to get
wrong when written inline:

`binomial_z` standardizes a count against a rate the caller states. The rate
is an argument, not a built-in 1/N, because the right baseline is usually the
model's own prediction rather than chance.

`wilson_interval` is the Wilson score interval for a proportion. It behaves
well for small counts and for rates near 0 or 1, where the normal interval
leaves [0, 1] or collapses to zero width.

`two_proportion_z` tests whether two rates differ, pooling the counts under
the null of equal rates. The usual use is a within-group rate against an
across-group rate.
"""

from __future__ import annotations

from math import sqrt
from typing import NamedTuple

from aldegonde.exceptions import InvalidInputError


def _validate_count(hits: int, trials: int) -> None:
    """Reject a hit count outside 0..trials or a negative trial count."""
    if trials < 0:
        msg = f"trials must be non-negative, got {trials}"
        raise InvalidInputError(msg)
    if not 0 <= hits <= trials:
        msg = f"hits {hits} out of range for {trials} trials"
        raise InvalidInputError(msg)


def binomial_z(hits: int, trials: int, rate: float) -> float:
    """Standardize a count of hits against a stated rate.

    Each trial is taken as a Bernoulli draw with the given success rate, and
    the result is the standard score of the observed count. Positive means
    more hits than the rate predicts.

    Args:
        hits: Observed hits
        trials: Trials made
        rate: Expected probability of a hit, between 0 and 1

    Returns:
        The standard score, or 0.0 when the spread is zero (no trials, or a
        rate of exactly 0 or 1)

    Raises:
        InvalidInputError: If the rate is outside [0, 1], a count is
            negative, or hits exceed trials
    """
    if not 0.0 <= rate <= 1.0:
        msg = f"rate must be between 0 and 1, got {rate}"
        raise InvalidInputError(msg)
    _validate_count(hits, trials)
    sd = sqrt(trials * rate * (1.0 - rate))
    return (hits - trials * rate) / sd if sd > 0 else 0.0


class WilsonInterval(NamedTuple):
    """A Wilson score interval for a proportion.

    Attributes:
        estimate: The observed proportion hits / trials
        low: Lower bound
        high: Upper bound
    """

    estimate: float
    low: float
    high: float


def wilson_interval(
    hits: int,
    trials: int,
    z: float = 1.959963984540054,
) -> WilsonInterval:
    """Return the Wilson score interval for a proportion.

    Args:
        hits: Observed hits
        trials: Trials made, at least 1
        z: Standard-normal quantile for the confidence level; the default is
            the two-sided 95% value

    Returns:
        The point estimate and the lower and upper bounds, clipped to [0, 1]

    Raises:
        InvalidInputError: If trials < 1, hits is out of range, or z is
            negative
    """
    if trials < 1:
        msg = f"trials must be at least 1, got {trials}"
        raise InvalidInputError(msg)
    _validate_count(hits, trials)
    if z < 0:
        msg = f"z must be non-negative, got {z}"
        raise InvalidInputError(msg)
    estimate = hits / trials
    denominator = 1.0 + z * z / trials
    center = (estimate + z * z / (2 * trials)) / denominator
    half = (
        z
        * sqrt(estimate * (1.0 - estimate) / trials + z * z / (4 * trials * trials))
        / denominator
    )
    return WilsonInterval(
        estimate=estimate,
        low=max(0.0, center - half),
        high=min(1.0, center + half),
    )


def two_proportion_z(
    hits1: int,
    trials1: int,
    hits2: int,
    trials2: int,
) -> float:
    """Test whether two proportions differ, pooling the counts under the null.

    Args:
        hits1: Hits in the first group
        trials1: Trials in the first group, at least 1
        hits2: Hits in the second group
        trials2: Trials in the second group, at least 1

    Returns:
        The standard score of the difference in rates; positive means the
        first group's rate is higher, and 0.0 when the pooled spread is zero

    Raises:
        InvalidInputError: If a group has no trials, or a hit count is out
            of range
    """
    if trials1 < 1 or trials2 < 1:
        msg = "both groups need at least one trial"
        raise InvalidInputError(msg)
    _validate_count(hits1, trials1)
    _validate_count(hits2, trials2)
    rate1 = hits1 / trials1
    rate2 = hits2 / trials2
    pooled = (hits1 + hits2) / (trials1 + trials2)
    se = sqrt(pooled * (1.0 - pooled) * (1.0 / trials1 + 1.0 / trials2))
    return (rate1 - rate2) / se if se > 0 else 0.0
