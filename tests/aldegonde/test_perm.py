import random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from aldegonde import perm
from aldegonde.exceptions import InvalidInputError


def random_perms(max_size: int = 12) -> st.SearchStrategy[list[int]]:
    return st.integers(min_value=1, max_value=max_size).map(
        lambda n: random.Random(n).sample(range(n), n)
    )


perms = st.permutations(list(range(6)))


def test_identity() -> None:
    assert perm.identity(4) == [0, 1, 2, 3]
    assert perm.identity(0) == []


@given(perms)
def test_compose_with_inverse_is_identity(p: list[int]) -> None:
    assert perm.compose(p, perm.invert(p)) == perm.identity(len(p))
    assert perm.compose(perm.invert(p), p) == perm.identity(len(p))


def test_compose_applies_inner_first() -> None:
    f = [1, 2, 0]  # 0->1, 1->2, 2->0
    g = [0, 2, 1]  # swap 1 and 2
    assert perm.compose(f, g) == [f[g[i]] for i in range(3)]


def test_compose_size_mismatch_raises() -> None:
    with pytest.raises(InvalidInputError):
        perm.compose([0, 1], [0, 1, 2])


@given(perms, st.integers(min_value=-8, max_value=8))
def test_power_matches_repeated_composition(p: list[int], k: int) -> None:
    expected = perm.identity(len(p))
    step = p if k >= 0 else perm.invert(p)
    for _ in range(abs(k)):
        expected = perm.compose(step, expected)
    assert perm.power(p, k) == expected


@given(perms)
def test_power_at_order_is_identity(p: list[int]) -> None:
    assert perm.power(p, perm.order(p)) == perm.identity(len(p))


def test_order_is_lcm_of_cycle_lengths() -> None:
    p = perm.from_cycles([[0, 1, 2], [3, 4]], 6)
    assert perm.order(p) == 6
    assert perm.order(perm.identity(5)) == 1


def test_cycles_canonical_form() -> None:
    p = perm.from_cycles([[2, 0, 1], [4, 3]], 6)
    assert perm.cycles(p) == [[0, 1, 2], [3, 4], [5]]


def test_cycle_type_sorted_descending() -> None:
    p = perm.from_cycles([[0, 1], [2, 3, 4]], 7)
    assert perm.cycle_type(p) == (3, 2, 1, 1)


def test_parity_of_transposition_is_odd() -> None:
    assert perm.parity(perm.from_cycles([[0, 1]], 4)) == -1
    assert perm.parity(perm.identity(4)) == 1
    # a 3-cycle is even
    assert perm.parity(perm.from_cycles([[0, 1, 2]], 4)) == 1


@given(perms, perms)
def test_parity_is_multiplicative(p: list[int], q: list[int]) -> None:
    assert perm.parity(perm.compose(p, q)) == perm.parity(p) * perm.parity(q)


def test_from_cycles_rejects_repeated_point() -> None:
    with pytest.raises(InvalidInputError):
        perm.from_cycles([[0, 1], [1, 2]], 4)


def test_from_cycles_rejects_out_of_range() -> None:
    with pytest.raises(InvalidInputError):
        perm.from_cycles([[0, 5]], 4)


def test_from_cycle_type_has_requested_type() -> None:
    p = perm.from_cycle_type([3, 2], 7)
    assert perm.cycle_type(p) == (3, 2, 1, 1)


def test_from_cycle_type_overrun_raises() -> None:
    with pytest.raises(InvalidInputError):
        perm.from_cycle_type([3, 3], 5)


@given(perms, perms)
def test_conjugate_preserves_cycle_type(p: list[int], s: list[int]) -> None:
    assert perm.cycle_type(perm.conjugate(p, s)) == perm.cycle_type(p)


@given(perms)
def test_transposition_conjugate_preserves_cycle_type(p: list[int]) -> None:
    mutated = perm.transposition_conjugate(p, 0, 3)
    assert perm.cycle_type(mutated) == perm.cycle_type(p)


def test_random_permutation_is_valid_and_seeded() -> None:
    a = perm.random_permutation(10, random.Random(3))
    b = perm.random_permutation(10, random.Random(3))
    perm.validate_permutation(a)
    assert a == b


def test_key_round_trip() -> None:
    alphabet = "ABCD"
    key = {"A": "C", "B": "A", "C": "D", "D": "B"}
    p = perm.from_key(alphabet, key)
    assert perm.to_key(alphabet, p) == key


def test_from_key_rejects_non_bijection() -> None:
    with pytest.raises(InvalidInputError):
        perm.from_key("ABC", {"A": "B", "B": "B", "C": "A"})


def test_validate_permutation_rejects_duplicates() -> None:
    with pytest.raises(InvalidInputError):
        perm.validate_permutation([0, 1, 1])
