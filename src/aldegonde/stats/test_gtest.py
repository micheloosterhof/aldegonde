#!/usr/bin/env python

from aldegonde.stats.gtest import gtest

am = "ABCDEFGHIJKLM"
nz = "NOPQRSTUVWXYZ"
a = "A"


def test_gtest() -> None:
    assert gtest(am, nz) == 0.0
    assert gtest(a, a) == 1.0
