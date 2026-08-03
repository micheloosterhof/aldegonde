from math import log, sqrt

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.multitest import (
    bonferroni,
    bonferroni_threshold,
    expected_max_z,
    multiplicity_budget,
    sidak,
    sidak_threshold,
)


def test_bonferroni_scales_and_caps() -> None:
    assert bonferroni(0.01, 5) == pytest.approx(0.05)
    assert bonferroni(0.5, 10) == 1.0


def test_bonferroni_single_test_is_identity() -> None:
    assert bonferroni(0.037, 1) == pytest.approx(0.037)


def test_sidak_less_conservative_than_bonferroni() -> None:
    assert sidak(0.01, 5) < bonferroni(0.01, 5)
    assert sidak(0.01, 5) == pytest.approx(1 - 0.99**5)


def test_thresholds_invert_corrections() -> None:
    assert bonferroni_threshold(0.05, 20) == pytest.approx(0.0025)
    # applying sidak to its own threshold recovers the family-wise level
    per_test = sidak_threshold(0.05, 20)
    assert sidak(per_test, 20) == pytest.approx(0.05)


def test_invalid_inputs_raise() -> None:
    with pytest.raises(InvalidInputError):
        bonferroni(1.5, 5)
    with pytest.raises(InvalidInputError):
        bonferroni(0.01, 0)
    with pytest.raises(InvalidInputError):
        sidak(-0.1, 5)
    with pytest.raises(InvalidInputError):
        expected_max_z(0)


def test_expected_max_z_value() -> None:
    assert expected_max_z(1) == 0.0
    assert expected_max_z(100) == pytest.approx(sqrt(2 * log(100)))


def test_multiplicity_budget_counts_two_sided() -> None:
    result = multiplicity_budget([0.1, 2.5, -3.0, 1.9], 2.0)
    assert result.observed == 2
    assert result.tests == 4
    # two-sided normal tail at 2.0 is about 4.55% per test
    assert result.expected == pytest.approx(4 * 0.0455, abs=0.001)


def test_multiplicity_budget_one_sided() -> None:
    result = multiplicity_budget([2.5, -3.0], 2.0, two_sided=False)
    assert result.observed == 1
    assert result.expected == pytest.approx(2 * 0.02275, abs=0.001)


def test_multiplicity_budget_negative_threshold_raises() -> None:
    with pytest.raises(InvalidInputError):
        multiplicity_budget([1.0], -1.0)
