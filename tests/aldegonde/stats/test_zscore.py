from math import sqrt

from aldegonde.stats.zscore import z_score


def test_zscore_positive() -> None:
    assert z_score(10.0, 4.0, 2.0) == 3.0


def test_zscore_negative() -> None:
    assert z_score(1.0, 4.0, 2.0) == -1.5


def test_zscore_at_expectation() -> None:
    assert z_score(4.0, 4.0, 2.0) == 0.0


def test_zscore_zero_sd_returns_zero() -> None:
    assert z_score(10.0, 4.0, 0.0) == 0.0


def test_zscore_negative_sd_returns_zero() -> None:
    assert z_score(10.0, 4.0, -1.0) == 0.0


def test_zscore_poisson_form() -> None:
    mu = 9.0
    assert z_score(15.0, mu, sqrt(mu)) == 2.0
