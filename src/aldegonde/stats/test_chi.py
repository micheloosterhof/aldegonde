#!/usr/bin/env python

from aldegonde.stats.chi import chi

am = "ABCDEFGHIJKLM"
nz = "NOPQRSTUVWXYZ"
a = "A"


def test_chi() -> None:
    assert chi(am, nz) == 0.0
    assert chi(a, a) == 1.0
