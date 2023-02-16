#!/usr/bin/env python

from ..structures import alphabet, sequence

from .ioc import ioc, ioc2, ioc3, ioc4

nils = sequence.Sequence.fromlist(data=[0] * 300, alphabet=alphabet.UPPERCASE_ALPHABET)
ones = sequence.Sequence.fromlist(data=[1] * 300, alphabet=alphabet.UPPERCASE_ALPHABET)
uniq = sequence.Sequence.fromlist(
    data=list(range(0, 26)), alphabet=alphabet.UPPERCASE_ALPHABET
)


def test_ioc_unique() -> None:
    assert ioc(uniq)[1] == 0.0


def test_ioc_uniform() -> None:
    assert ioc(ones)[0] == 1.0
    assert ioc(nils)[0] == 1.0


def test_ioc2_unique() -> None:
    assert ioc2(uniq)[0] == 0.0
    assert ioc2(uniq, cut=0)[0] == 0.0
    assert ioc2(uniq, cut=1)[0] == 0.0
    assert ioc2(uniq, cut=2)[0] == 0.0


def test_ioc2_uniform() -> None:
    assert ioc2(nils)[0] == 1.0
    assert ioc2(ones)[0] == 1.0
    assert ioc2(ones, cut=0)[0] == 1.0
    assert ioc2(nils, cut=0)[0] == 1.0
    assert ioc2(ones, cut=1)[0] == 1.0
    assert ioc2(nils, cut=1)[0] == 1.0
    assert ioc2(ones, cut=2)[0] == 1.0
    assert ioc2(nils, cut=2)[0] == 1.0


def test_ioc3_unique() -> None:
    assert ioc3(uniq)[0] == 0.0


def test_ioc3_uniform() -> None:
    assert ioc3(nils)[0] == 1.0
    assert ioc3(ones)[0] == 1.0
    assert ioc3(ones, cut=0)[0] == 1.0
    assert ioc3(nils, cut=0)[0] == 1.0
    assert ioc3(ones, cut=1)[0] == 1.0
    assert ioc3(nils, cut=1)[0] == 1.0
    assert ioc3(ones, cut=2)[0] == 1.0
    assert ioc3(nils, cut=2)[0] == 1.0


def test_ioc4_unique() -> None:
    assert ioc4(uniq)[0] == 0.0


def test_ioc4_uniform() -> None:
    assert ioc4(nils)[0] == 1.0
    assert ioc4(ones)[0] == 1.0
    assert ioc4(ones, cut=0)[0] == 1.0
    assert ioc4(nils, cut=0)[0] == 1.0
    assert ioc4(ones, cut=1)[0] == 1.0
    assert ioc4(nils, cut=1)[0] == 1.0
    assert ioc4(ones, cut=2)[0] == 1.0
    assert ioc4(nils, cut=2)[0] == 1.0
