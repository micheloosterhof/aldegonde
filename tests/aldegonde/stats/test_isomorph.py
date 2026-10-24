"""tests for doublets.py."""

import random

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.isomorphs import (
    isomorph,
    isomorph_distribution,
    random_isomorph_statistics,
)


def test_isomorph() -> None:
    assert isomorph("ATTACK") == isomorph("EFFECT")
    assert isomorph("ATTACK") == "ABBACD"
    assert isomorph("ATTA") == "ABBA"
    assert isomorph([0, 0, 0, 0]) == "AAAA"


def test_all_isomorphs() -> None:
    # ATTA -> ABBA
    # TTAC -> AABC
    # TACK -> ABCD
    assert isomorph_distribution("ATTACK", length=4) == {
        "ABBA": 1,
        "AABC": 1,
        "ABCD": 1,
    }


def test_random_isomorph_statistics_is_reproducible() -> None:
    """The null must not change between runs, or no figure quoting it is stable."""
    first = random_isomorph_statistics(200, 4, samples=5)
    second = random_isomorph_statistics(200, 4, samples=5)
    assert first == second


def test_random_isomorph_statistics_takes_an_injected_source() -> None:
    """A caller supplying its own seeded source controls the draw."""
    a = random_isomorph_statistics(200, 4, samples=5, rng=random.Random(7))
    b = random_isomorph_statistics(200, 4, samples=5, rng=random.Random(7))
    c = random_isomorph_statistics(200, 4, samples=5, rng=random.Random(8))
    assert a == b
    assert a != c


def test_random_isomorph_statistics_takes_a_null_resampler() -> None:
    """A resampler that returns the observed sequence gives zero spread."""

    observed = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 4, 5, 6, 7] * 10

    def identity(data, rng):  # noqa: ANN001, ANN202
        return list(data)

    mean_d, sd_d, mean_dup, sd_dup = random_isomorph_statistics(
        len(observed), 4, samples=5, null=identity, observed=observed
    )
    assert sd_d == 0 and sd_dup == 0
    with pytest.raises(InvalidInputError):
        random_isomorph_statistics(16, 4, samples=5, null=identity)
