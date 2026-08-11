import pytest

from aldegonde import c3301
from aldegonde.stats import compare
from aldegonde.stats.compare import quadgramscore

am = "ABCDEFGHIJKLM"
nz = "NOPQRSTUVWXYZ"
a = "A"


# def test_chisquare() -> None:
#    assert chi_square(am, nz) == 0.0
#    assert chi_square(a, a) == 1.0


# def test_gtest() -> None:
#    assert gtest(am, nz) == 1.0
#    assert gtest(a, a) == 1.0


def test_quadgramscore() -> None:
    # lowercase letters are not in the corpus. floor value
    assert quadgramscore("TEST") < -3.6
    assert quadgramscore("TEST") > -3.7
    assert quadgramscore("THISISATESTOFTHEEMERGENCYBROADCASTSYSTEM") > -153.0
    assert quadgramscore("THISISATESTOFTHEEMERGENCYBROADCASTSYSTEM") < -152.0


def test_ngram_scorer_treats_a_rune_list_like_the_same_string() -> None:
    """A sequence of runes must score as the text it spells.

    `str(ngram)` on a list produced "['A', 'B', ...]", which matches no ngram, so
    every position silently fell to the floor and the score became a constant.
    """
    runes = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗ")
    assert c3301.quadgramscore(runes) == c3301.quadgramscore("".join(runes))


def test_ngram_scorer_is_not_constant_over_different_texts() -> None:
    """A degenerate scorer returns the same value for everything."""
    a = c3301.quadgramscore(list("ᚦᛖᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒ"))
    b = c3301.quadgramscore(list("ᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾ"))
    assert a != b


def test_chi_square_is_small_when_the_text_matches_the_reference() -> None:
    """Text drawn to the reference's own shape should fit it better than noise."""
    table = {"AA": 90, "AB": 10}
    like = "AA" * 90 + "AB" * 10
    unlike = "AB" * 90 + "AA" * 10
    assert compare.chi_square(like, length=2, frequency_map=table) < compare.chi_square(
        unlike, length=2, frequency_map=table
    )


def test_chi_square_falls_back_when_scipy_is_unavailable(monkeypatch) -> None:
    """The local computation must agree with scipy, not merely run."""
    table = {"AA": 90, "AB": 10}
    text = "AA" * 60 + "AB" * 40
    with_scipy = compare.chi_square(text, length=2, frequency_map=table)

    def unavailable(*args: object, **kwargs: object) -> float:
        msg = "no scipy"
        raise ImportError(msg)

    monkeypatch.setattr(compare, "chisquare", unavailable)
    without = compare.chi_square(text, length=2, frequency_map=table)
    assert without == pytest.approx(with_scipy)


def test_chi_square_scores_a_rune_list_like_the_string_it_spells() -> None:
    table = {"AA": 90, "AB": 10}
    assert compare.chi_square(list("AAAB"), length=2, frequency_map=table) == (
        compare.chi_square("AAAB", length=2, frequency_map=table)
    )
