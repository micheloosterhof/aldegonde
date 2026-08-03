import random

import pytest

from aldegonde.analysis.fingerprint import compare, fingerprint
from aldegonde.exceptions import InsufficientDataError


def test_fingerprint_has_expected_keys() -> None:
    fp = fingerprint("ABCD" * 30, alphabetsize=4, lags=(1, 2, 3))
    assert set(fp) == {"nioc", "doublet_rate", "kappa_z_1", "kappa_z_2", "kappa_z_3"}


def test_fingerprint_doublet_rate() -> None:
    fp = fingerprint("AABB" * 25, alphabetsize=2)
    # AABB repeated: doublets at the AA and BB joins, 1 in every 2 adjacencies
    assert fp["doublet_rate"] == pytest.approx(0.5, abs=0.02)


def test_fingerprint_periodic_text_peaks_at_period() -> None:
    fp = fingerprint("ABCDE" * 40, alphabetsize=5, lags=(1, 5))
    assert fp["kappa_z_5"] > 5.0
    assert fp["kappa_z_1"] < 0.0


def test_compare_self_distance_is_zero() -> None:
    fp = fingerprint("ABCDABCD" * 20, alphabetsize=4)
    assert compare(fp, fp) == 0.0


def test_compare_ranks_closer_fingerprint_lower() -> None:
    rng = random.Random(5)
    observed = fingerprint([rng.randrange(5) for _ in range(1000)], alphabetsize=5)
    near = fingerprint([rng.randrange(5) for _ in range(1000)], alphabetsize=5)
    far = fingerprint("ABCDE" * 200, alphabetsize=5)
    assert compare(observed, near) < compare(observed, far)


def test_compare_uses_scales() -> None:
    a = {"x": 0.0}
    b = {"x": 2.0}
    assert compare(a, b) == pytest.approx(4.0)
    assert compare(a, b, scales={"x": 2.0}) == pytest.approx(1.0)


def test_compare_no_shared_keys_raises() -> None:
    with pytest.raises(InsufficientDataError):
        compare({"a": 1.0}, {"b": 2.0})


def test_fingerprint_too_short_raises() -> None:
    with pytest.raises(InsufficientDataError):
        fingerprint("A")
