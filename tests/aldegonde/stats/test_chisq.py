import random

import pytest

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.stats.chisq import (
    goodness_of_fit,
    lag_contingency,
    rate_uniformity,
    uniformity,
    wilson_hilferty,
)


def test_wilson_hilferty_centers_near_zero_at_df() -> None:
    # chi2 equal to its df is unremarkable: |z| should be small
    assert abs(wilson_hilferty(10.0, 10)) < 0.5
    # far above df: strongly positive
    assert wilson_hilferty(50.0, 10) > 4.5


def test_wilson_hilferty_invalid_inputs() -> None:
    with pytest.raises(InvalidInputError):
        wilson_hilferty(1.0, 0)
    with pytest.raises(InvalidInputError):
        wilson_hilferty(-1.0, 5)


def test_uniformity_flat_counts_not_significant() -> None:
    result = uniformity([100, 101, 99, 100])
    assert result.df == 3
    assert result.p > 0.9


def test_uniformity_skewed_counts_significant() -> None:
    result = uniformity([200, 10, 10, 10])
    assert result.p < 1e-6
    assert result.z > 3.0


def test_uniformity_needs_data() -> None:
    with pytest.raises(InsufficientDataError):
        uniformity([5])
    with pytest.raises(InsufficientDataError):
        uniformity([0, 0, 0])


def test_goodness_of_fit_matches_uniformity_for_flat_weights() -> None:
    counts = [30, 50, 20]
    assert goodness_of_fit(counts, [1.0, 1.0, 1.0]).chi2 == pytest.approx(
        uniformity(counts).chi2
    )


def test_goodness_of_fit_perfect_fit() -> None:
    result = goodness_of_fit([30, 60, 10], [3.0, 6.0, 1.0])
    assert result.chi2 == pytest.approx(0.0)
    assert result.p == pytest.approx(1.0)


def test_goodness_of_fit_zero_weight_with_count_raises() -> None:
    with pytest.raises(InvalidInputError):
        goodness_of_fit([5, 5], [1.0, 0.0])


def test_goodness_of_fit_length_mismatch_raises() -> None:
    with pytest.raises(InvalidInputError):
        goodness_of_fit([5, 5], [1.0])


def test_rate_uniformity_flat_rate_not_significant() -> None:
    # same 5% rate everywhere despite very different exposures
    result = rate_uniformity({"a": (1000, 50), "b": (100, 5), "c": (400, 20)})
    assert result.p > 0.9


def test_rate_uniformity_detects_rate_difference() -> None:
    # equal event counts would fool a frequency test; the rates differ 10x
    result = rate_uniformity({"a": (1000, 20), "b": (100, 20)})
    assert result.p < 1e-6


def test_rate_uniformity_invalid_bins() -> None:
    with pytest.raises(InvalidInputError):
        rate_uniformity({"a": (10, 20), "b": (10, 1)})
    with pytest.raises(InsufficientDataError):
        rate_uniformity({"a": (10, 1)})
    with pytest.raises(InsufficientDataError):
        rate_uniformity({"a": (10, 0), "b": (10, 0)})


def test_lag_contingency_detects_dependence() -> None:
    # strictly alternating text: symbol at i+1 is determined by symbol at i
    result = lag_contingency("AB" * 100, 1)
    assert result.p < 1e-6


def test_lag_contingency_independent_text_not_significant() -> None:
    rng = random.Random(7)
    text = [rng.choice("ABCD") for _ in range(2000)]
    result = lag_contingency(text, 1)
    assert result.p > 0.01


def test_lag_contingency_off_diagonal_masks_doublet_structure() -> None:
    # text whose only structure is never repeating: full table is significant,
    # the off-diagonal table is not
    rng = random.Random(3)
    alphabet = "ABCDE"
    text = ["A"]
    for _ in range(3000):
        text.append(rng.choice([s for s in alphabet if s != text[-1]]))
    assert lag_contingency(text, 1).p < 1e-6
    masked = lag_contingency(text, 1, off_diagonal=True)
    assert masked.p > 0.01
    assert masked.df == (5 - 1) * (5 - 1) - 5


def test_lag_contingency_invalid_inputs() -> None:
    with pytest.raises(InvalidInputError):
        lag_contingency("ABAB", 0)
    with pytest.raises(InsufficientDataError):
        lag_contingency("AB", 5)
    with pytest.raises(InsufficientDataError):
        lag_contingency("AAAA", 1)
