#!/usr/bin/env python

from .sequence import Sequence
from .cicada3301 import CICADA_ALPHABET


def test_welcome() -> None:
    seq1 = Sequence.fromstr(text="ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ", alphabet=CICADA_ALPHABET)
    assert seq1 == Sequence.fromlist(
        data=[1, 28, 21, 15, 12, 0, 5, 4, 12, 1, 6, 13, 28, 28, 0, 7, 14, 16],
        alphabet=CICADA_ALPHABET,
    )
    assert str(seq1) == "ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ"
    assert seq1[1] == 28
