#!/usr/bin/env p

from ..structures import sequence, alphabet
from .hamming import hamming_distance

karolin = sequence.Sequence("karolin", alphabet=alphabet.LOWERCASE_ALPHABET)
kathrin = sequence.Sequence("kathrin", alphabet=alphabet.LOWERCASE_ALPHABET)
kerstin = sequence.Sequence("kerstin", alphabet=alphabet.LOWERCASE_ALPHABET)


def test_hamming():
    assert hamming_distance(karolin, kathrin) == 3
    assert hamming_distance(karolin, kerstin) == 3
    assert hamming_distance(kathrin, kerstin) == 4
