"""tests for doublets.py."""

from aldegonde.stats.isomorph import isomorph, isomorph_distribution


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
