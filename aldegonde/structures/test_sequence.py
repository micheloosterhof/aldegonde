#!/usr/bin/env python

from .sequence import *
from .alphabet import *


def test_sequence_init():
    assert Sequence(text="ABCDEFG", alphabet=UPPERCASE_ALPHABET) == Sequence(
        data=[0, 1, 2, 3, 4, 5, 6], alphabet=UPPERCASE_ALPHABET
    )
