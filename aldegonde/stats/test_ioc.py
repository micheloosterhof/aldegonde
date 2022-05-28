#!/usr/bin/env p

from . ioc import ioc, ioc2, ioc3, ioc4

MAX = 29

nils = [0] * 300
ones = [1] * 300
rand = range(0, MAX + 1)


def test_ioc_random():
    assert ioc(rand) == 0.0


def test_ioc_uniform():
    assert ioc(ones) == 1.0
    assert ioc(nils) == 1.0


def test_ioc2_random():
    assert ioc2(rand) == 0.0


def test_ioc2_uniform():
    assert ioc2(nils) == 1.0
    assert ioc2(ones) == 1.0
    assert ioc2(ones, cut=0) == 1.0
    assert ioc2(nils, cut=0) == 1.0
    assert ioc2(ones, cut=1) == 1.0
    assert ioc2(nils, cut=1) == 1.0
    assert ioc2(ones, cut=2) == 1.0
    assert ioc2(nils, cut=2) == 1.0


def test_ioc2_random_cut1():
    assert ioc2(rand) == 0.0
    assert ioc2(rand, cut=0) == 0.0
    assert ioc2(rand, cut=1) == 0.0
    assert ioc2(rand, cut=2) == 0.0


def test_ioc3_random():
    assert ioc3(rand) == 0.0


def test_ioc3_uniform():
    assert ioc3(ones) == 1.0
