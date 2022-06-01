#!/usr/bin/env python

from .sequence import *
from .alphabet import *
from .cicada3301 import *


def test_welcome():
    seq1 = Sequence(text="ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ", alphabet=CICADA_ALPHABET)
    assert seq1 == Sequence(
        data=[1, 28, 21, 15, 12, 0, 5, 4, 12, 1, 6, 13, 28, 28, 0, 7, 14, 16],
        alphabet=CICADA_ALPHABET,
    )
    assert str(seq1) == "ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ"
    assert seq1[1] == 28
