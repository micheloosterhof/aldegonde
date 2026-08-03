import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.binomial import (
    coincidence_z,
    two_proportion_z,
    wilson_interval,
)


def test_coincidence_z_at_chance_is_near_zero() -> None:
    # exactly the expected count under 1/29
    z = coincidence_z(round(2900 / 29), 2900, 29)
    assert abs(z) < 0.5


def test_coincidence_z_excess_is_positive() -> None:
    assert coincidence_z(200, 2900, 29) > 5.0


def test_coincidence_z_zero_opportunities() -> None:
    assert coincidence_z(0, 0, 29) == 0.0


def test_coincidence_z_validation() -> None:
    with pytest.raises(InvalidInputError):
        coincidence_z(5, 10, 1)
    with pytest.raises(InvalidInputError):
        coincidence_z(11, 10, 5)
    with pytest.raises(InvalidInputError):
        coincidence_z(-1, 10, 5)


def test_wilson_interval_brackets_estimate() -> None:
    result = wilson_interval(5, 100)
    assert result.estimate == 0.05
    assert result.low < 0.05 < result.high
    assert result.low >= 0.0


def test_wilson_interval_handles_zero_hits() -> None:
    result = wilson_interval(0, 50)
    assert result.estimate == 0.0
    assert result.low == pytest.approx(0.0, abs=1e-12)
    assert result.high > 0.0


def test_wilson_interval_handles_all_hits() -> None:
    result = wilson_interval(50, 50)
    assert result.estimate == 1.0
    assert result.high == 1.0
    assert result.low < 1.0


def test_wilson_interval_validation() -> None:
    with pytest.raises(InvalidInputError):
        wilson_interval(5, 0)
    with pytest.raises(InvalidInputError):
        wilson_interval(11, 10)
    with pytest.raises(InvalidInputError):
        wilson_interval(5, 10, z=-1.0)


def test_two_proportion_z_detects_difference() -> None:
    # 30% vs 10% over 100 trials each
    assert two_proportion_z(30, 100, 10, 100) > 3.0


def test_two_proportion_z_equal_rates_near_zero() -> None:
    assert abs(two_proportion_z(20, 100, 40, 200)) < 0.5


def test_two_proportion_z_sign() -> None:
    assert two_proportion_z(10, 100, 30, 100) < 0.0


def test_two_proportion_z_validation() -> None:
    with pytest.raises(InvalidInputError):
        two_proportion_z(5, 0, 5, 10)
    with pytest.raises(InvalidInputError):
        two_proportion_z(11, 10, 5, 10)
