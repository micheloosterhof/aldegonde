#!/usr/bin/env python

from ..structures import alphabet, sequence

from .ngrams import ngrams, iterngrams

uniq = sequence.Sequence(data=list(range(0, 5)), alphabet=alphabet.UPPERCASE_ALPHABET)


def test_ngram_unique():
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
    assert [x for x in iterngrams(uniq, length=4, cut=4)] == []
