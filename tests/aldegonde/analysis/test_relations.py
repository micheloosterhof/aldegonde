import random

import pytest

from aldegonde.analysis.relations import (
    linear_relation_scan,
    positional_relation_scan,
)
from aldegonde.exceptions import InvalidInputError

ABC = "ABCDE"


def test_additive_progression_detected() -> None:
    # x[i+1] = x[i] + 1 mod 5, so x[i+1] + 4*x[i] = constant + 5*x[i] is
    # degenerate at coefficient N-1 (the subtractive relation)
    text = [ABC[i % 5] for i in range(300)]
    scan = linear_relation_scan(text, ABC, lags=[1])
    assert scan[(1, 4)].p < 1e-9


def test_random_text_scan_is_flat() -> None:
    rng = random.Random(17)
    text = [rng.choice(ABC) for _ in range(3000)]
    scan = linear_relation_scan(text, ABC, lags=[1, 2, 3])
    # 12 cells scanned; nothing should be extreme beyond a Bonferroni cut
    assert all(result.p > 1e-4 for result in scan.values())


def test_scan_covers_requested_grid() -> None:
    text = [random.Random(1).choice(ABC) for _ in range(100)]
    scan = linear_relation_scan(text, ABC, lags=[1, 2], coefficients=[1, 2])
    assert set(scan) == {(1, 1), (1, 2), (2, 1), (2, 2)}


def test_short_text_omits_impossible_lags() -> None:
    scan = linear_relation_scan("ABAB", "AB", lags=[1, 10], coefficients=[1])
    assert (1, 1) in scan
    assert all(lag != 10 for lag, _ in scan)


def test_invalid_inputs_raise() -> None:
    with pytest.raises(InvalidInputError):
        linear_relation_scan("ABAB", "AB", lags=[0], coefficients=[1])
    with pytest.raises(InvalidInputError):
        linear_relation_scan("ABX", "AB", lags=[1])


def test_positional_drift_detected() -> None:
    # x[i] = -2*i mod 5: adding 2*i makes the stream constant
    text = [ABC[(-2 * i) % 5] for i in range(300)]
    scan = positional_relation_scan(text, ABC)
    assert scan[2].p < 1e-9
    assert scan[1].p > 1e-4


def test_positional_scan_flat_on_random_text() -> None:
    rng = random.Random(23)
    text = [rng.choice(ABC) for _ in range(3000)]
    scan = positional_relation_scan(text, ABC)
    assert all(result.p > 1e-4 for result in scan.values())
