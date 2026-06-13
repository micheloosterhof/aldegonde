# ABOUTME: Monte Carlo comparison of an observed statistic against a null model,
# ABOUTME: reporting effect size and directional empirical p-values.
"""Resampling-based significance testing.

Given a statistic (a pure function of a sequence) and a null model (a
resampler), these harnesses evaluate the statistic on the observed sequence and
on many surrogates, then summarize where the observed value falls in the null
distribution. The statistic and the null model are both injected, so the same
harness serves every test and any null.

Randomness is reproducible and trial-independent by construction: trial i uses
random.Random(seed + i), so a run is deterministic given the seed and trials
may be evaluated in any order or in parallel.

Empirical p-values use the (count + 1) / (trials + 1) convention, which is
never zero and is conservative under ties. Both one-sided tails are reported so
the caller chooses direction at report time: doublet suppression is a lower-tail
question, periodicity an upper-tail one, and the right tail differs per test.
The z field is a standardized effect size, not the inferential quantity; under
a skewed null it is only indicative, and the p-values are authoritative.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from math import sqrt
from typing import TYPE_CHECKING, TypeVar

from aldegonde.stats.zscore import z_score

if TYPE_CHECKING:
    from aldegonde.stats.nulls import NullModel

T = TypeVar("T")

Statistic = Callable[[Sequence[T]], float]
"""A scalar statistic: a pure function from a sequence to a number."""

KeyedStatistic = Callable[[Sequence[T]], Mapping[int, float]]
"""A vector statistic keyed by an integer lag, period, or separation."""


@dataclass(frozen=True)
class NullComparison:
    """Where an observed value falls in a null distribution.

    Attributes:
        observed: The statistic on the observed sequence
        null_mean: Mean of the statistic over the surrogates
        null_sd: Standard deviation over the surrogates
        z: Standardized effect size (observed - null_mean) / null_sd; rough if
            the null distribution is skewed
        p_upper: (#{surrogate >= observed} + 1) / (trials + 1)
        p_lower: (#{surrogate <= observed} + 1) / (trials + 1)
    """

    observed: float
    null_mean: float
    null_sd: float
    z: float
    p_upper: float
    p_lower: float

    @property
    def p_two_sided(self) -> float:
        """Two-sided p-value, capped at 1.0."""
        return min(1.0, 2.0 * min(self.p_upper, self.p_lower))


@dataclass(frozen=True)
class FamilyResult:
    """A family-wise comparison of a reduced statistic over a key set.

    Attributes:
        observed: The reduced observed statistic (e.g. the max over keys)
        key: The key attaining the extremum under the default max reduction,
            else None
        p_value: (#{reduced surrogate >= observed} + 1) / (trials + 1); the
            family-wise significance of the strongest peak, correcting for the
            scan over keys
    """

    observed: float
    key: int | None
    p_value: float


class _Accumulator:
    """Running mean, sample sd, and tail counts against a fixed observed value."""

    __slots__ = ("count", "mean", "m2", "at_or_above", "at_or_below")

    def __init__(self) -> None:
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.at_or_above = 0
        self.at_or_below = 0

    def update(self, value: float, observed: float) -> None:
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        self.m2 += delta * (value - self.mean)
        if value >= observed:
            self.at_or_above += 1
        if value <= observed:
            self.at_or_below += 1

    def finalize(self, observed: float, trials: int) -> NullComparison:
        sd = sqrt(self.m2 / (self.count - 1)) if self.count > 1 else 0.0
        return NullComparison(
            observed=observed,
            null_mean=self.mean,
            null_sd=sd,
            z=z_score(observed, self.mean, sd),
            p_upper=(self.at_or_above + 1) / (trials + 1),
            p_lower=(self.at_or_below + 1) / (trials + 1),
        )


def _max_over_keys(values: Mapping[int, float]) -> float:
    """Default family reduction: the largest value across the key set."""
    return max(values.values())


def monte_carlo(
    statistic: Statistic[T],
    null_model: NullModel[T],
    observed: Sequence[T],
    *,
    trials: int = 1000,
    seed: int = 0,
) -> NullComparison:
    """Compare a scalar statistic against a null model by resampling.

    Args:
        statistic: The scalar statistic to evaluate
        null_model: The resampler producing surrogate sequences
        observed: The observed sequence
        trials: Number of surrogates to draw
        seed: Base seed; trial i uses random.Random(seed + i)

    Returns:
        A NullComparison locating the observed value in the null distribution
    """
    observed_value = statistic(observed)
    accumulator = _Accumulator()
    for trial in range(trials):
        rng = random.Random(seed + trial)
        accumulator.update(statistic(null_model(observed, rng)), observed_value)
    return accumulator.finalize(observed_value, trials)


def monte_carlo_map(
    statistic: KeyedStatistic[T],
    null_model: NullModel[T],
    observed: Sequence[T],
    *,
    keys: Sequence[int],
    trials: int = 1000,
    seed: int = 0,
) -> dict[int, NullComparison]:
    """Compare a keyed statistic against a null model, key by key.

    The key set is pinned by the caller so the observed and surrogate
    statistics are compared over the same domain; a surrogate that would yield
    a different set of valid keys cannot silently misalign the comparison.

    Args:
        statistic: The keyed statistic to evaluate
        null_model: The resampler producing surrogate sequences
        observed: The observed sequence
        keys: The fixed set of keys to compare
        trials: Number of surrogates to draw
        seed: Base seed; trial i uses random.Random(seed + i)

    Returns:
        A NullComparison per key
    """
    observed_values = statistic(observed)
    accumulators = {key: _Accumulator() for key in keys}
    for trial in range(trials):
        rng = random.Random(seed + trial)
        surrogate_values = statistic(null_model(observed, rng))
        for key in keys:
            accumulators[key].update(
                surrogate_values.get(key, 0.0),
                observed_values.get(key, 0.0),
            )
    return {
        key: accumulators[key].finalize(observed_values.get(key, 0.0), trials)
        for key in keys
    }


def family_pvalue(
    statistic: KeyedStatistic[T],
    null_model: NullModel[T],
    observed: Sequence[T],
    *,
    keys: Sequence[int],
    reduce: Callable[[Mapping[int, float]], float] = _max_over_keys,
    trials: int = 1000,
    seed: int = 0,
) -> FamilyResult:
    """Test the strongest peak across a key set with one family-wise p-value.

    Reduces the keyed statistic to a single value (by default the maximum over
    keys) on the observed sequence and on every surrogate, then reports how
    often the surrogate reduction reaches the observed one. This is the correct
    significance for "is the best period real" when scanning many candidates,
    which per-key p-values cannot give.

    Args:
        statistic: The keyed statistic to evaluate
        null_model: The resampler producing surrogate sequences
        observed: The observed sequence
        keys: The fixed set of keys to scan
        reduce: Maps the keyed values to a single statistic; defaults to the
            maximum over keys
        trials: Number of surrogates to draw
        seed: Base seed; trial i uses random.Random(seed + i)

    Returns:
        A FamilyResult with the observed reduction, its key, and the
        family-wise p-value
    """
    observed_stat = statistic(observed)
    observed_values = {key: observed_stat.get(key, 0.0) for key in keys}
    observed_reduced = reduce(observed_values)
    key = (
        max(observed_values, key=observed_values.__getitem__)
        if reduce is _max_over_keys
        else None
    )
    at_or_above = 0
    for trial in range(trials):
        rng = random.Random(seed + trial)
        surrogate_stat = statistic(null_model(observed, rng))
        surrogate_reduced = reduce({k: surrogate_stat.get(k, 0.0) for k in keys})
        if surrogate_reduced >= observed_reduced:
            at_or_above += 1
    return FamilyResult(
        observed=observed_reduced,
        key=key,
        p_value=(at_or_above + 1) / (trials + 1),
    )
