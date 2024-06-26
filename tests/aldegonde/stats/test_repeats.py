from aldegonde.stats.repeats import repeat_distribution, repeat_positions

uniq = "ABCABC"


def test_ngram_unique() -> None:
    assert repeat_distribution(uniq, length=2) == {
        "AB": 2,
        "BC": 2,
    }
    assert repeat_distribution(uniq, length=3) == {"ABC": 2}
    assert repeat_positions(uniq, length=2) == {
        "AB": [0, 3],
        "BC": [1, 4],
    }
    assert repeat_positions(uniq, length=3) == {
        "ABC": [0, 3],
    }
