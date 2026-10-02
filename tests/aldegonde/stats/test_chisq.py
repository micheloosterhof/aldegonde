# ABOUTME: Tests the chi-square helpers: uniformity, goodness of fit, rate
# ABOUTME: uniformity across exposures, and independence of a pair table.
from __future__ import annotations

import random

import pytest
from scipy.stats import chi2_contingency

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.stats.chisq import (
    goodness_of_fit,
    independence,
    rate_uniformity,
    uniformity,
    wilson_hilferty,
)
from aldegonde.stats.pairs import pair_counts


def test_wilson_hilferty_is_near_zero_when_chi2_equals_df() -> None:
    assert abs(wilson_hilferty(10.0, 10)) < 0.5
    assert wilson_hilferty(50.0, 10) > 4.5


def test_wilson_hilferty_matches_the_published_transform() -> None:
    # Wilson and Hilferty 1931: z = ((x/k)^(1/3) - (1 - 2/9k)) / sqrt(2/9k)
    k, x = 20, 31.41
    expected = ((x / k) ** (1 / 3) - (1 - 2 / (9 * k))) / (2 / (9 * k)) ** 0.5
    assert wilson_hilferty(x, k) == pytest.approx(expected)


def test_wilson_hilferty_rejects_bad_input() -> None:
    with pytest.raises(InvalidInputError):
        wilson_hilferty(1.0, 0)
    with pytest.raises(InvalidInputError):
        wilson_hilferty(-1.0, 5)


def test_uniformity_of_flat_counts_is_not_significant() -> None:
    result = uniformity([100, 101, 99, 100])
    assert result.df == 3
    assert result.p > 0.9


def test_uniformity_of_skewed_counts_is_significant() -> None:
    result = uniformity([200, 10, 10, 10])
    assert result.chi2 == pytest.approx(3 * (47.5**2) / 57.5 + 142.5**2 / 57.5)
    assert result.p < 1e-6
    assert result.z > 3.0


def test_uniformity_needs_categories_and_data() -> None:
    with pytest.raises(InsufficientDataError):
        uniformity([5])
    with pytest.raises(InsufficientDataError):
        uniformity([0, 0, 0])


def test_goodness_of_fit_with_flat_weights_is_uniformity() -> None:
    counts = [30, 50, 20]
    assert goodness_of_fit(counts, [1.0, 1.0, 1.0]).chi2 == pytest.approx(
        uniformity(counts).chi2
    )


def test_goodness_of_fit_of_a_perfect_fit_is_zero() -> None:
    result = goodness_of_fit([30, 60, 10], [3.0, 6.0, 1.0])
    assert result.chi2 == pytest.approx(0.0)
    assert result.p == pytest.approx(1.0)


def test_goodness_of_fit_rejects_bad_input() -> None:
    with pytest.raises(InvalidInputError):
        goodness_of_fit([5, 5], [1.0, 0.0])
    with pytest.raises(InvalidInputError):
        goodness_of_fit([5, 5], [1.0])
    with pytest.raises(InvalidInputError):
        goodness_of_fit([5, 5], [1.0, -1.0])


def test_rate_uniformity_ignores_unequal_exposure() -> None:
    # the same 5% rate everywhere despite very different exposures
    result = rate_uniformity({"a": (1000, 50), "b": (100, 5), "c": (400, 20)})
    assert result.chi2 == pytest.approx(0.0)
    assert result.p == pytest.approx(1.0)


def test_rate_uniformity_sees_a_rate_difference_behind_equal_counts() -> None:
    result = rate_uniformity({"a": (1000, 20), "b": (100, 20)})
    assert result.p < 1e-6


def test_rate_uniformity_rejects_bad_bins() -> None:
    with pytest.raises(InvalidInputError):
        rate_uniformity({"a": (10, 20), "b": (10, 1)})
    with pytest.raises(InsufficientDataError):
        rate_uniformity({"a": (10, 1)})
    with pytest.raises(InsufficientDataError):
        rate_uniformity({"a": (10, 0), "b": (10, 0)})


def test_independence_matches_scipy() -> None:
    rng = random.Random(7)
    words = [[rng.randrange(4) for _ in range(rng.randrange(2, 9))] for _ in range(300)]
    table = pair_counts(words, 4)
    result = independence(table)
    chi2, p, df, _ = chi2_contingency(table, correction=False)
    assert result.chi2 == pytest.approx(chi2)
    assert result.df == df
    assert result.p == pytest.approx(p)


def test_independence_sees_dependence() -> None:
    assert independence(pair_counts([[0, 1] * 100], 2)).p < 1e-6


def test_independence_leaves_absent_symbols_out_of_the_degrees_of_freedom() -> None:
    rng = random.Random(1)
    words = [[rng.randrange(3) for _ in range(6)] for _ in range(200)]
    assert independence(pair_counts(words, 5)).df == (3 - 1) * (3 - 1)


def test_independence_off_diagonal_masks_doublet_structure() -> None:
    # text whose only structure is never repeating: the full table is
    # significant, the off-diagonal table is not
    rng = random.Random(3)
    word = [0]
    for _ in range(3000):
        word.append(rng.choice([s for s in range(5) if s != word[-1]]))
    table = pair_counts([word], 5)
    assert independence(table).p < 1e-6
    masked = independence(table, off_diagonal=True)
    assert masked.p > 0.01
    assert masked.df == (5 - 1) * (5 - 1) - 5


def test_independence_rejects_bad_tables() -> None:
    with pytest.raises(InvalidInputError):
        independence([[1, 2, 3]])
    with pytest.raises(InvalidInputError):
        independence([[1, -1], [1, 1]])
    with pytest.raises(InsufficientDataError):
        independence([[4, 0], [0, 0]])
    with pytest.raises(InsufficientDataError):
        independence([[0, 3], [3, 0]], off_diagonal=True)
