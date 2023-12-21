from aldegonde.stats.kappa import kappa, doublets, triplets

"""
"""


def test_kappa() -> None:
    assert kappa("ABCDEFGHIJKLMNOPQRSTUVWXYZ", skip=1) == 0.0
    assert kappa("ABCABC", skip=1) == 0.0
    assert kappa("ABCABC", skip=2) == 0.0
    assert kappa("ABCABC", skip=3) == 1.0
    assert kappa("ABCABCABC", skip=3) == 1.0
    assert kappa("ABCABCABCXXX", skip=3) == 2 / 3


uniq = "ABCDEFGH"
dobl = "AABBCCDDEEFFGGHH"
trpl = "AAABBBCCCDDDEEEFFFGGGHHH"


def test_doublets() -> None:
    assert doublets(uniq) == ([], 8 - 1)
    assert doublets(dobl) == ([0, 2, 4, 6, 8, 10, 12, 14], 16 - 1)
    assert doublets(trpl) == (
        [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22],
        24 - 1,
    )


def test_triplets() -> None:
    assert triplets(dobl) == 0
    assert triplets(uniq) == 0
    assert triplets(trpl) == 8
