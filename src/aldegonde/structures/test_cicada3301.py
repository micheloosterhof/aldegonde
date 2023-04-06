#!/usr/bin/env python

from aldegonde.structures.cicada3301 import CICADA_ALPHABET


def test_welcome() -> None:
    data=[1, 28, 21, 15, 12, 0, 5, 4, 12, 1, 6, 13, 28, 28, 0, 7, 14, 16]
    seq = "".join([CICADA_ALPHABET[e] for e in data])
    assert seq == "ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ"
