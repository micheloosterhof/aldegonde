import random

import pytest

from aldegonde.exceptions import InsufficientDataError
from aldegonde.stats.kappa import kappa_spectrum


def test_periodic_text_peaks_at_multiples_of_period() -> None:
    spectrum = kappa_spectrum("ABCDE" * 40, range(1, 11))
    for skip in (5, 10):
        assert spectrum[skip].z > 5.0
    for skip in (1, 2, 3, 4, 6, 7, 8, 9):
        assert spectrum[skip].z < 0.0


def test_random_text_spectrum_is_flat() -> None:
    rng = random.Random(11)
    text = [rng.choice("ABCDEFGH") for _ in range(4000)]
    spectrum = kappa_spectrum(text, range(1, 21))
    assert all(abs(result.z) < 4.0 for result in spectrum.values())


def test_frequency_matched_null_absorbs_skew() -> None:
    # heavily skewed frequencies inflate coincidences at every skip; the
    # frequency-matched null must not read that as periodicity
    rng = random.Random(13)
    text = rng.choices("AB", weights=[9, 1], k=5000)
    spectrum = kappa_spectrum(text, range(1, 11))
    assert all(abs(result.z) < 4.0 for result in spectrum.values())


def test_expected_uses_frequency_rate() -> None:
    text = "AABB" * 100
    spectrum = kappa_spectrum(text, [1])
    result = spectrum[1]
    # frequencies are flat over 2 symbols: chance rate 1/2
    assert result.expected == pytest.approx(result.comparisons * 0.5)


def test_digraphic_spectrum() -> None:
    spectrum = kappa_spectrum("ABCABC" * 30, [3, 4], length=2)
    assert spectrum[3].z > 5.0
    assert spectrum[4].z < 0.0


def test_skips_beyond_text_are_omitted() -> None:
    spectrum = kappa_spectrum("ABCD", [1, 10])
    assert 1 in spectrum
    assert 10 not in spectrum


def test_empty_text_raises() -> None:
    with pytest.raises(InsufficientDataError):
        kappa_spectrum([], [1])
