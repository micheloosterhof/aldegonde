#!/usr/bin/env python

from .alphabet import a2i, i2a


def test_a2i() -> None:
    assert a2i("HYDRAULIC") == [7, 24, 3, 17, 0, 20, 11, 8, 2]


def test_i2a() -> None:
    assert i2a([7, 24, 3, 17, 0, 20, 11, 8, 2]) == "HYDRAULIC"
