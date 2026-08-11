"""tests for doublets.py."""

import random

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
