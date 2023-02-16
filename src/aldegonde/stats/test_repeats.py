#!/usr/bin/env python

from ..structures import alphabet, sequence

from .repeats import repeat, repeat2

uniq = sequence.Sequence.fromstr(text="ABCABC", alphabet=alphabet.UPPERCASE_ALPHABET)


def test_ngram_unique() -> None:
    assert repeat(uniq) == {"0-1": 2, "1-2": 2, "0-1-2": 2}
    assert repeat2(uniq) == {"0-1": [0, 3], "1-2": [1, 4], "0-1-2": [0, 3]}
