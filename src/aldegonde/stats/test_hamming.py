#!/usr/bin/env p

from ..structures import sequence, alphabet
from .hamming import hamming_distance

karolin = sequence.Sequence.fromstr("karolin", alphabet=alphabet.LOWERCASE_ALPHABET)
kathrin = sequence.Sequence.fromstr("kathrin", alphabet=alphabet.LOWERCASE_ALPHABET)
kerstin = sequence.Sequence.fromstr("kerstin", alphabet=alphabet.LOWERCASE_ALPHABET)


def test_hamming() -> None:
    assert hamming_distance(karolin, kathrin) == 3
    assert hamming_distance(karolin, kerstin) == 3
    assert hamming_distance(kathrin, kerstin) == 4
