"""tests for doublets.py"""

from aldegonde.structures import sequence, alphabet
from aldegonde.stats.doublets import doublets, triplets

uniq = sequence.Sequence.fromstr("ABCDEFGH", alphabet=alphabet.UPPERCASE_ALPHABET)
dobl = sequence.Sequence.fromstr(
    "AABBCCDDEEFFGGHH", alphabet=alphabet.UPPERCASE_ALPHABET
)
trpl = sequence.Sequence.fromstr(
    "AAABBBCCCDDDEEEFFFGGGHHH", alphabet=alphabet.UPPERCASE_ALPHABET
)


def test_doublets() -> None:
    assert doublets(dobl) == [0, 2, 4, 6, 8, 10, 12, 14]
    assert doublets(uniq) == []
    assert doublets(trpl) == [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22]


def test_triplets() -> None:
    assert triplets(dobl) == 0
    assert triplets(uniq) == 0
    assert triplets(trpl) == 8
