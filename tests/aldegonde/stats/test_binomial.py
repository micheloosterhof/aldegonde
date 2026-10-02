# ABOUTME: Tests the binomial helpers: the standard score against a stated rate,
# ABOUTME: the Wilson interval, and the two-proportion test.
from __future__ import annotations

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.binomial import binomial_z, two_proportion_z, wilson_interval


def test_binomial_z_at_the_rate_is_zero() -> None:
    assert binomial_z(100, 2900, 1 / 29) == pytest.approx(0.0)


def test_binomial_z_matches_the_formula() -> None:
    # 104 hits of 2,105 pairs against chance 1/29: the body's lag-5 cell. The
    # binomial spread gives 3.75; dividing by sqrt(expected) instead gives 3.69.
    expected = (104 - 2105 / 29) / (2105 * (1 / 29) * (28 / 29)) ** 0.5
    assert binomial_z(104, 2105, 1 / 29) == pytest.approx(expected)
    assert binomial_z(104, 2105, 1 / 29) == pytest.approx(3.75, abs=0.01)


def test_binomial_z_takes_the_rate_the_caller_states() -> None:
    assert binomial_z(104, 2105, 0.0568) < 0 < binomial_z(104, 2105, 1 / 29)


def test_binomial_z_is_zero_without_spread() -> None:
    assert binomial_z(0, 0, 0.5) == 0.0
    assert binomial_z(10, 10, 1.0) == 0.0
    assert binomial_z(0, 10, 0.0) == 0.0


@pytest.mark.parametrize(
    ("hits", "trials", "rate"), [(11, 10, 0.5), (-1, 10, 0.5), (5, 10, 1.5)]
)
def test_binomial_z_rejects_bad_input(hits: int, trials: int, rate: float) -> None:
    with pytest.raises(InvalidInputError):
        binomial_z(hits, trials, rate)


def test_wilson_interval_brackets_the_estimate() -> None:
    result = wilson_interval(5, 100)
    assert result.estimate == 0.05
    assert result.low < 0.05 < result.high
    assert result.low >= 0.0


def test_wilson_interval_matches_a_published_value() -> None:
    # Wilson 95% interval for 5 of 100 is 0.0215 to 0.1118
    result = wilson_interval(5, 100)
    assert result.low == pytest.approx(0.0215, abs=0.0001)
    assert result.high == pytest.approx(0.1118, abs=0.0001)


def test_wilson_interval_handles_zero_and_all_hits() -> None:
    none = wilson_interval(0, 50)
    assert none.estimate == 0.0
    assert none.low == pytest.approx(0.0, abs=1e-12)
    assert none.high > 0.0
    every = wilson_interval(50, 50)
    assert every.estimate == 1.0
    assert every.high == 1.0
    assert every.low < 1.0


@pytest.mark.parametrize(
    ("hits", "trials", "z"), [(5, 0, 1.96), (11, 10, 1.96), (5, 10, -1.0)]
)
def test_wilson_interval_rejects_bad_input(hits: int, trials: int, z: float) -> None:
    with pytest.raises(InvalidInputError):
        wilson_interval(hits, trials, z=z)


def test_two_proportion_z_detects_a_difference() -> None:
    assert two_proportion_z(30, 100, 10, 100) > 3.0


def test_two_proportion_z_is_near_zero_for_equal_rates() -> None:
    assert abs(two_proportion_z(20, 100, 40, 200)) < 1e-9


def test_two_proportion_z_sign_follows_the_first_group() -> None:
    assert two_proportion_z(10, 100, 30, 100) < 0.0


def test_two_proportion_z_is_zero_without_spread() -> None:
    assert two_proportion_z(0, 10, 0, 10) == 0.0


@pytest.mark.parametrize(
    ("hits1", "trials1", "hits2", "trials2"), [(5, 0, 5, 10), (11, 10, 5, 10)]
)
def test_two_proportion_z_rejects_bad_input(
    hits1: int, trials1: int, hits2: int, trials2: int
) -> None:
    with pytest.raises(InvalidInputError):
        two_proportion_z(hits1, trials1, hits2, trials2)
