import random

import pytest

from aldegonde.analysis.spectral import (
    crosscorrelation_coincidence,
    multiplier_dft,
)
from aldegonde.exceptions import InsufficientDataError, InvalidInputError

A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012"[:29]


def test_crosscorrelation_finds_known_shift() -> None:
    rng = random.Random(1)
    n = 400
    s = [A[rng.randrange(29)] for _ in range(n)]
    shift = 7
    # second[i] = s[(i - shift) mod n]; first[i] aligns second[i + shift]
    second = s[-shift:] + s[:-shift]
    peak = crosscorrelation_coincidence(s, second, A)
    assert peak.shift == shift
    assert peak.coincidences == n
    assert peak.z > 10.0


def test_crosscorrelation_negative_shift() -> None:
    rng = random.Random(2)
    n = 200
    s = [A[rng.randrange(29)] for _ in range(n)]
    shift = 5
    # rotate the other way: second[i] = s[(i + shift) mod n]
    second = s[shift:] + s[:shift]
    peak = crosscorrelation_coincidence(s, second, A)
    assert peak.shift == -shift


def test_crosscorrelation_unrelated_streams_low_z() -> None:
    rng = random.Random(3)
    a = [A[rng.randrange(29)] for _ in range(400)]
    b = [A[rng.randrange(29)] for _ in range(400)]
    peak = crosscorrelation_coincidence(a, b, A)
    assert peak.z < 6.0


def test_crosscorrelation_validation() -> None:
    with pytest.raises(InvalidInputError):
        crosscorrelation_coincidence("ABC", "AB", A)
    with pytest.raises(InsufficientDataError):
        crosscorrelation_coincidence([], [], A)
    with pytest.raises(InvalidInputError):
        crosscorrelation_coincidence("AZ", "AB", "AB")


def test_multiplier_dft_detects_periodic_component() -> None:
    text = [A[(3 * i) % 29] for i in range(300)]
    peak = multiplier_dft(text, A)
    assert peak.power > peak.threshold


def test_multiplier_dft_random_below_threshold() -> None:
    rng = random.Random(5)
    text = [A[rng.randrange(29)] for _ in range(300)]
    peak = multiplier_dft(text, A)
    assert peak.power < peak.threshold


def test_multiplier_dft_threshold_covers_multiplier_scan() -> None:
    # the threshold must grow with the number of multipliers scanned
    text = [A[(3 * i) % 29] for i in range(300)]
    wide = multiplier_dft(text, A)
    narrow = multiplier_dft(text, A, multipliers=[3])
    assert wide.threshold > narrow.threshold


def test_multiplier_dft_validation() -> None:
    with pytest.raises(InsufficientDataError):
        multiplier_dft("A", A)
    with pytest.raises(InvalidInputError):
        multiplier_dft("XY", "AB")
