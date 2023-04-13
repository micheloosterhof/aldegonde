"""tests for doublets.py"""

from aldegonde.stats.isomorph import isomorph, count_isomorphs


def test_isomorph() -> None:
    assert isomorph("ATTACK") == isomorph("EFFECT")
    assert isomorph("ATTACK") == "ABBACD"
    assert isomorph("ATTA") == "ABBA"
    assert isomorph([0, 0, 0, 0]) == "AAAA"


def test_all_isomorphs() -> None:
    # ATTA -> ABBA
    # TTAC -> AABC
    # TACK -> ABCD
    assert count_isomorphs("ATTACK", length=4) == {"ABBA": 1, "AABC": 1, "ABCD": 1}
