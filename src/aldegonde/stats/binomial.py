# ABOUTME: Binomial helpers used across coincidence tests: coincidence z,
# ABOUTME: the Wilson score interval, and the two-proportion z test.
"""Binomial inference for coincidence and rate comparisons.

Small, exact helpers that recur throughout coincidence analysis and are
easy to get subtly wrong when re-derived inline:

`coincidence_z` standardizes a count of matches among a number of
opportunities against the chance rate 1/alphabetsize — the binomial z
behind kappa, boundary coincidence, and alignment tests.

`wilson_interval` is the Wilson score confidence interval for a proportion,
which behaves well for small counts and rates near 0 or 1 where the normal
approximation fails, and needs no special-casing of zero counts.

`two_proportion_z` tests whether two rates differ, pooling their counts
under the null — the standard "does this effect respect the boundary"
comparison of a within-group rate against an across-group rate.
"""

from __future__ import annotations

from math import sqrt
from typing import NamedTuple

from aldegonde.exceptions import InvalidInputError


def coincidence_z(hits: int, opportunities: int, alphabetsize: int) -> float:
    """Standardize a coincidence count against the chance rate 1/alphabetsize.

    Treats each of `opportunities` comparisons as a Bernoulli trial with
    success probability 1/alphabetsize and returns the standard score of the
    observed `hits`. Positive means more coincidences than chance.

    Args:
        hits: Observed matching comparisons
        opportunities: Total comparisons made
        alphabetsize: Alphabet size fixing the chance rate

    Returns:
        The binomial standard score, 0.0 when no opportunities

    Raises:
        InvalidInputError: If alphabetsize < 2, counts are negative, or hits
            exceed opportunities
    """
    if alphabetsize < 2:
        msg = f"alphabetsize must be at least 2, got {alphabetsize}"
        raise InvalidInputError(msg)
    if hits < 0 or opportunities < 0:
        msg = "hits and opportunities must be non-negative"
        raise InvalidInputError(msg)
    if hits > opportunities:
        msg = f"hits {hits} exceed opportunities {opportunities}"
        raise InvalidInputError(msg)
    if opportunities == 0:
        return 0.0
    rate = 1.0 / alphabetsize
    expected = opportunities * rate
    sd = sqrt(opportunities * rate * (1.0 - rate))
    return (hits - expected) / sd if sd > 0 else 0.0


class WilsonInterval(NamedTuple):
    """A Wilson score interval for a proportion.

    Attributes:
        estimate: The observed proportion hits / trials
        low: Lower confidence bound
        high: Upper confidence bound
    """

    estimate: float
    low: float
    high: float


def wilson_interval(
    hits: int,
    trials: int,
    z: float = 1.959963984540054,
) -> WilsonInterval:
    """Return the Wilson score confidence interval for a proportion.

    Well-behaved for small samples and for rates near 0 or 1, where the
    normal-approximation interval can leave [0, 1] or collapse to zero
    width; requires no dependency beyond the standard library.

    Args:
        hits: Observed successes
        trials: Total trials
        z: Standard-normal quantile for the confidence level; the default is
            the two-sided 95% value

    Returns:
        The point estimate and the lower and upper bounds

    Raises:
        InvalidInputError: If trials < 1, hits is out of range, or z is
            negative
    """
    if trials < 1:
        msg = f"trials must be at least 1, got {trials}"
        raise InvalidInputError(msg)
    if not 0 <= hits <= trials:
        msg = f"hits {hits} out of range for {trials} trials"
        raise InvalidInputError(msg)
    if z < 0:
        msg = f"z must be non-negative, got {z}"
        raise InvalidInputError(msg)
    phat = hits / trials
    denominator = 1.0 + z * z / trials
    center = (phat + z * z / (2 * trials)) / denominator
    half = (
        z
        * sqrt(phat * (1.0 - phat) / trials + z * z / (4 * trials * trials))
        / denominator
    )
    return WilsonInterval(
        estimate=phat,
        low=max(0.0, center - half),
        high=min(1.0, center + half),
    )


def two_proportion_z(
    hits1: int,
    trials1: int,
    hits2: int,
    trials2: int,
) -> float:
    """Test whether two proportions differ, pooling counts under the null.

    Returns the standard score of the difference in rates, using the pooled
    rate for the standard error as the null hypothesis of equal rates
    requires. The classic use is a within-group rate against an across-group
    rate: a large z means the effect does not respect the grouping.

    Args:
        hits1: Successes in the first group
        trials1: Trials in the first group
        hits2: Successes in the second group
        trials2: Trials in the second group

    Returns:
        The two-proportion standard score; positive means group 1's rate is
        higher

    Raises:
        InvalidInputError: If a group has no trials, or a hit count is out of
            range
    """
    if trials1 < 1 or trials2 < 1:
        msg = "both groups need at least one trial"
        raise InvalidInputError(msg)
    if not (0 <= hits1 <= trials1 and 0 <= hits2 <= trials2):
        msg = "hit counts must lie within their trial counts"
        raise InvalidInputError(msg)
    rate1 = hits1 / trials1
    rate2 = hits2 / trials2
    pooled = (hits1 + hits2) / (trials1 + trials2)
    se = sqrt(pooled * (1.0 - pooled) * (1.0 / trials1 + 1.0 / trials2))
    return (rate1 - rate2) / se if se > 0 else 0.0
