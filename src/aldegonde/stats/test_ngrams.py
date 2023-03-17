#!/usr/bin/env python

from aldegonde.structures import alphabet, sequence

from aldegonde.stats.ngrams import ngrams, iterngrams

uniq = sequence.Sequence.fromlist(
    data=list(range(0, 5)), alphabet=alphabet.UPPERCASE_ALPHABET
)

string = "ABCDEF"


def test_ngram_unique() -> None:
    assert ngrams(uniq, length=2, cut=0) == [[0, 1], [1, 2], [2, 3], [3, 4]]
    assert ngrams(uniq, length=2, cut=1) == [[0, 1], [2, 3]]
    assert ngrams(uniq, length=2, cut=2) == [[1, 2], [3, 4]]
    assert ngrams(uniq, length=3, cut=0) == [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
    assert ngrams(uniq, length=3, cut=1) == [[0, 1, 2]]
    assert ngrams(uniq, length=3, cut=2) == [[1, 2, 3]]
    assert ngrams(uniq, length=3, cut=3) == [[2, 3, 4]]
    assert ngrams(uniq, length=4, cut=0) == [[0, 1, 2, 3], [1, 2, 3, 4]]
    assert ngrams(uniq, length=4, cut=1) == [[0, 1, 2, 3]]
    assert ngrams(uniq, length=4, cut=2) == [[1, 2, 3, 4]]
    assert ngrams(uniq, length=4, cut=3) == []
    assert ngrams(uniq, length=4, cut=4) == []
    assert ngrams(string, length=4, cut=0) == ["ABCD", "BCDE", "CDEF"]
    assert ngrams(string, length=4, cut=1) == ["ABCD"]
    assert list(iterngrams(uniq, length=4, cut=4)) == []
