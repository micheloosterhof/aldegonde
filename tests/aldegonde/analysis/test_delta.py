"""Tests for the delta (DELT) horizontal difference/sum transform."""

import pytest

from aldegonde.analysis.delta import DeltaOp, delta, delta2

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PRIME = "ABCDE"  # size 5, prime modulus for DIV


def test_delta_sub() -> None:
    # ACE -> [0,2,4]; (2-0)=2 C, (4-2)=2 C
    assert delta("ACE", ALPHA) == list("CC")
    assert delta("ACE", ALPHA, op=DeltaOp.SUB) == list("CC")


def test_delta_sub_wraparound() -> None:
    # CA -> [2,0]; (0-2)%26 = 24 -> Y
    assert delta("CA", ALPHA) == list("Y")


def test_delta_add() -> None:
    # ACE -> [0,2,4]; (2+0)=2 C, (4+2)=6 G
    assert delta("ACE", ALPHA, op=DeltaOp.ADD) == list("CG")


def test_delta_mul() -> None:
    # BCD -> [1,2,3]; (2*1)=2 C, (3*2)=6 G
    assert delta("BCD", ALPHA, op=DeltaOp.MUL) == list("CG")


def test_delta_rsub() -> None:
    # ACE -> [0,2,4]; (0-2)%26 = 24 Y, (2-4)%26 = 24 Y -- negation of SUB
    assert delta("ACE", ALPHA, op=DeltaOp.RSUB) == list("YY")


def test_delta_div() -> None:
    # DC -> [3,2] over prime mod 5; 2 * inverse(3) = 2*2 = 4 -> E
    assert delta("DC", PRIME, op=DeltaOp.DIV) == list("E")


def test_delta_rdiv() -> None:
    # BD -> [1,3] over prime mod 5; a/b = 1 * inverse(3) = 1*2 = 2 -> C
    # (DIV would give b/a = 3 -> D, so this distinguishes direction)
    assert delta("BD", PRIME, op=DeltaOp.RDIV) == list("C")


def test_delta_rdiv_by_zero_raises() -> None:
    # CA -> divisor is c[i+skip] = index 0 ('A'), no inverse
    with pytest.raises(ValueError):
        delta("CA", PRIME, op=DeltaOp.RDIV)


def test_delta_div_by_zero_raises() -> None:
    # AC -> divisor is index 0 ('A'), no inverse
    with pytest.raises(ValueError):
        delta("AC", PRIME, op=DeltaOp.DIV)


def test_delta_skip() -> None:
    # ABCDE skip=2 -> compare i with i+2; each gap is 2 -> CCC
    assert delta("ABCDE", ALPHA, skip=2) == list("CCC")


def test_delta_length() -> None:
    assert len(delta("ABCDEFG", ALPHA)) == 6
    assert len(delta("ABCDEFG", ALPHA, skip=3)) == 4


def test_delta2() -> None:
    # ABDH -> [0,1,3,7]; first delta -> [1,2,4] BCE; second -> [1,2] BC
    assert delta2("ABDH", ALPHA) == list("BC")
