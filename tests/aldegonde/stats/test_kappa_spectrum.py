# ABOUTME: Tests the kappa spectrum: doublet counts at every skip, standardized
# ABOUTME: against the frequency-matched chance rate.
from __future__ import annotations

import random

import pytest

from aldegonde.exceptions import InsufficientDataError
from aldegonde.stats.kappa_test import KappaZ, kappa_spectrum


def test_periodic_text_peaks_at_multiples_of_the_period() -> None:
    spectrum = kappa_spectrum("ABCDE" * 40, range(1, 11))
    for skip in (5, 10):
        assert spectrum[skip].z > 5.0
    for skip in (1, 2, 3, 4, 6, 7, 8, 9):
        assert spectrum[skip].z < 0.0


def test_random_text_gives_a_flat_spectrum() -> None:
    rng = random.Random(11)
    text = [rng.choice("ABCDEFGH") for _ in range(4000)]
    spectrum = kappa_spectrum(text, range(1, 21))
    assert all(abs(result.z) < 4.0 for result in spectrum.values())


def test_the_frequency_matched_rate_absorbs_skew() -> None:
    # skewed frequencies inflate coincidences at every skip; that is not periodicity
    rng = random.Random(13)
    text = rng.choices("AB", weights=[9, 1], k=5000)
    spectrum = kappa_spectrum(text, range(1, 11))
    assert all(abs(result.z) < 4.0 for result in spectrum.values())


def test_expected_count_uses_the_frequency_rate() -> None:
    # AA and BB repeat in every block: 200 doublets over 399 comparisons at rate 1/2
    result = kappa_spectrum("AABB" * 100, [1])[1]
    assert result == KappaZ(observed=200, comparisons=399, expected=199.5, z=result.z)
    assert result.z == pytest.approx((200 - 199.5) / (399 * 0.25) ** 0.5)


def test_digraphic_spectrum() -> None:
    spectrum = kappa_spectrum("ABCABC" * 30, [3, 4], length=2)
    assert spectrum[3].z > 5.0
    assert spectrum[4].z < 0.0


def test_skips_beyond_the_text_are_left_out() -> None:
    spectrum = kappa_spectrum("ABCD", [1, 10])
    assert 1 in spectrum
    assert 10 not in spectrum


def test_empty_text_is_rejected() -> None:
    with pytest.raises(InsufficientDataError):
        kappa_spectrum([], [1])
