#!/usr/bin/env python

from aldegonde.structures import alphabet, sequence

from aldegonde.stats.repeats import repeat_distribution, repeat_positions

uniq = sequence.Sequence.fromstr(text="ABCABC", alphabet=alphabet.UPPERCASE_ALPHABET)


def test_ngram_unique() -> None:
    assert repeat_distribution(uniq, length=2) == {
        "[0, 1]": 2,
        "[1, 2]": 2,
    }
    assert repeat_distribution(uniq, length=3) == {"[0, 1, 2]": 2}
    assert repeat_positions(uniq, length=2) == {
        "[0, 1]": [0, 3],
        "[1, 2]": [1, 4],
    }
    assert repeat_positions(uniq, length=3) == {
        "[0, 1, 2]": [0, 3],
    }
