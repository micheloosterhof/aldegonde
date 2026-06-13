import random
import statistics
from collections.abc import Mapping, Sequence

import pytest

from aldegonde.stats.resample import (
    family_pvalue,
    monte_carlo,
    monte_carlo_map,
)


def _rng_null(data: Sequence[float], rng: random.Random) -> list[float]:
    """Surrogate carrying one fresh random draw, independent of data."""
    return [rng.random()]


def _scalar(seq: Sequence[float]) -> float:
    return float(seq[0])


def _reference_draws(trials: int, seed: int) -> list[float]:
    return [random.Random(seed + i).random() for i in range(trials)]


def test_monte_carlo_uses_seed_per_trial_for_mean_and_sd() -> None:
    res = monte_carlo(_scalar, _rng_null, [0.5], trials=200, seed=0)
    draws = _reference_draws(200, 0)
    assert res.observed == 0.5
    assert res.null_mean == pytest.approx(statistics.fmean(draws))
    assert res.null_sd == pytest.approx(statistics.stdev(draws))


def test_monte_carlo_empirical_pvalues() -> None:
    res = monte_carlo(_scalar, _rng_null, [0.5], trials=200, seed=0)
    draws = _reference_draws(200, 0)
    upper = (sum(1 for v in draws if v >= 0.5) + 1) / 201
    lower = (sum(1 for v in draws if v <= 0.5) + 1) / 201
    assert res.p_upper == pytest.approx(upper)
    assert res.p_lower == pytest.approx(lower)


def test_monte_carlo_two_sided_property() -> None:
    res = monte_carlo(_scalar, _rng_null, [0.99], trials=200, seed=0)
    assert res.p_two_sided == pytest.approx(min(1.0, 2.0 * min(res.p_upper, res.p_lower)))


def test_monte_carlo_is_deterministic() -> None:
    a = monte_carlo(_scalar, _rng_null, [0.5], trials=50, seed=3)
    b = monte_carlo(_scalar, _rng_null, [0.5], trials=50, seed=3)
    assert a == b


def test_monte_carlo_z_uses_helper_convention() -> None:
    res = monte_carlo(_scalar, _rng_null, [0.5], trials=200, seed=0)
    expected = (res.observed - res.null_mean) / res.null_sd
    assert res.z == pytest.approx(expected)


def _stat_map(seq: Sequence[float]) -> Mapping[int, float]:
    return {1: float(seq[0]), 2: 2.0 * float(seq[0])}


def test_monte_carlo_map_keys_match_scalar() -> None:
    result = monte_carlo_map(_stat_map, _rng_null, [0.5], keys=[1, 2], trials=100, seed=0)
    draws = _reference_draws(100, 0)
    assert set(result) == {1, 2}
    assert result[1].null_mean == pytest.approx(statistics.fmean(draws))
    assert result[2].null_mean == pytest.approx(statistics.fmean([2.0 * v for v in draws]))
    assert result[1].observed == 0.5
    assert result[2].observed == 1.0


def test_family_pvalue_max_reduction() -> None:
    def stat(seq: Sequence[float]) -> Mapping[int, float]:
        return {1: float(seq[0]), 2: 0.0}

    fam = family_pvalue(stat, _rng_null, [0.9], keys=[1, 2], trials=200, seed=0)
    draws = _reference_draws(200, 0)
    null_reduced = [max(v, 0.0) for v in draws]
    expected_p = (sum(1 for v in null_reduced if v >= 0.9) + 1) / 201
    assert fam.observed == 0.9
    assert fam.key == 1
    assert fam.p_value == pytest.approx(expected_p)


def test_family_pvalue_custom_reduce_has_no_key() -> None:
    def stat(seq: Sequence[float]) -> Mapping[int, float]:
        return {1: float(seq[0]), 2: 1.0}

    fam = family_pvalue(
        stat,
        _rng_null,
        [0.5],
        keys=[1, 2],
        reduce=lambda values: sum(values.values()),
        trials=50,
        seed=0,
    )
    assert fam.key is None
