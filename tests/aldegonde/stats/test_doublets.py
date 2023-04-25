"""tests for doublets.py."""

from aldegonde.stats.doublets import doublets, triplets

uniq = "ABCDEFGH"
dobl = "AABBCCDDEEFFGGHH"
trpl = "AAABBBCCCDDDEEEFFFGGGHHH"


def test_doublets() -> None:
    assert doublets(dobl) == [0, 2, 4, 6, 8, 10, 12, 14]
    assert doublets(uniq) == []
    assert doublets(trpl) == [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22]


def test_triplets() -> None:
    assert triplets(dobl) == 0
    assert triplets(uniq) == 0
    assert triplets(trpl) == 8
