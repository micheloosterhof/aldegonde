"""tests for doublets.py"""

from aldegonde.stats.isomorph import isomorph, all_isomorphs


def test_isomorph():
    assert isomorph("ATTACK") == isomorph("EFFECT")


def test_all_isomorphs():
    assert all_isomorphs("ATTACK", length=4) == {"ABBA": [0], "AABC": [1]}
