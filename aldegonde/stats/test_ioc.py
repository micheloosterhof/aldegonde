#!/usr/bin/env p

from .ioc import ioc, ioc2, ioc3, ioc4

nils = [0] * 300
ones = [1] * 300
uniq = range(0, 300)


def test_ioc_unique():
    assert ioc(uniq) == 0.0


def test_ioc_uniform():
    assert ioc(ones) == 1.0
    assert ioc(nils) == 1.0


def test_ioc2_unique():
    assert ioc2(uniq) == 0.0


def test_ioc2_uniform():
    assert ioc2(nils) == 1.0
    assert ioc2(ones) == 1.0
    assert ioc2(ones, cut=0) == 1.0
    assert ioc2(nils, cut=0) == 1.0
    assert ioc2(ones, cut=1) == 1.0
    assert ioc2(nils, cut=1) == 1.0
    assert ioc2(ones, cut=2) == 1.0
    assert ioc2(nils, cut=2) == 1.0


def test_ioc2_unique():
    assert ioc2(uniq) == 0.0
    assert ioc2(uniq, cut=0) == 0.0
    assert ioc2(uniq, cut=1) == 0.0
    assert ioc2(uniq, cut=2) == 0.0


def test_ioc3_unique():
    assert ioc3(uniq) == 0.0


def test_ioc3_uniform():
    assert ioc3(nils) == 1.0
    assert ioc3(ones) == 1.0
    assert ioc3(ones, cut=0) == 1.0
    assert ioc3(nils, cut=0) == 1.0
    assert ioc3(ones, cut=1) == 1.0
    assert ioc3(nils, cut=1) == 1.0
    assert ioc3(ones, cut=2) == 1.0
    assert ioc3(nils, cut=2) == 1.0


def test_ioc4_unique():
    assert ioc4(uniq) == 0.0


def test_ioc4_uniform():
    assert ioc4(nils) == 1.0
    assert ioc4(ones) == 1.0
    assert ioc4(ones, cut=0) == 1.0
    assert ioc4(nils, cut=0) == 1.0
    assert ioc4(ones, cut=1) == 1.0
    assert ioc4(nils, cut=1) == 1.0
    assert ioc4(ones, cut=2) == 1.0
    assert ioc4(nils, cut=2) == 1.0
