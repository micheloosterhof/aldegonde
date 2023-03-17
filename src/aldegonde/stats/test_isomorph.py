"""tests for doublets.py"""

from aldegonde.stats.isomorph import isomorph


def test_isomorphs():
    assert isomorph("ATTACK") == isomorph("EFFECT")
