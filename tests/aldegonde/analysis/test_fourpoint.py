import random

import pytest

from aldegonde.analysis.fourpoint import fourpoint_coincidence
from aldegonde.exceptions import InsufficientDataError, InvalidInputError


def test_fourpoint_expectation_formula() -> None:
    result = fourpoint_coincidence("ABCDABCD" * 10, (0, 1, 2, 3), 4)
    assert result.windows == len(list("ABCDABCD" * 10)) - 3
    assert result.expected == pytest.approx(result.windows / 16)


def test_fourpoint_detects_structure() -> None:
    # ABAB.. makes positions i,i+2 always equal and i+1,i+3 always equal
    result = fourpoint_coincidence("AB" * 200, (0, 2, 1, 3), 2)
    assert result.z > 10.0


def test_fourpoint_random_text_near_chance() -> None:
    rng = random.Random(4)
    text = [rng.randrange(5) for _ in range(4000)]
    result = fourpoint_coincidence(text, (0, 1, 2, 3), 5)
    assert abs(result.z) < 5.0


def test_fourpoint_validation() -> None:
    with pytest.raises(InvalidInputError):
        fourpoint_coincidence("ABAB", (0, 1, 2, 3), 1)
    with pytest.raises(InvalidInputError):
        fourpoint_coincidence("ABAB", (0, -1, 2, 3), 2)
    with pytest.raises(InsufficientDataError):
        fourpoint_coincidence("AB", (0, 1, 2, 10), 2)
