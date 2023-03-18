#!/usr/bin/env python

from aldegonde.stats.dist import dist, ngram_positions

abc = "ABC"
nz = "NOPQRSTUVWXYZ"
a = "A"


def test_dist() -> None:
    assert dist(abc) == {"A": 1, "B": 1, "C": 1}


def test_dist_positions() -> None:
    assert ngram_positions(abc) == {"A": [0], "B": [1], "C": [2]}
