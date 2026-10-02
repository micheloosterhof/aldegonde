# ABOUTME: Tests permutation algebra on integer sequences: composition, inverse,
# ABOUTME: powers, cycle structure, conjugation and random generation.
from __future__ import annotations

import random

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from aldegonde import masc
from aldegonde.exceptions import InvalidInputError
from aldegonde.maths import permutation

SIZE = 29
permutations = st.permutations(range(SIZE))


def test_identity_maps_each_point_to_itself() -> None:
    assert permutation.identity(4) == [0, 1, 2, 3]


def test_compose_applies_the_right_operand_first() -> None:
    a, b = [1, 2, 0], [0, 2, 1]
    assert permutation.compose(a, b) == [a[b[x]] for x in range(3)]
    assert permutation.compose(a, b) == [1, 0, 2]


@given(permutations, permutations, permutations)
def test_compose_is_associative(a: list[int], b: list[int], c: list[int]) -> None:
    left = permutation.compose(permutation.compose(a, b), c)
    right = permutation.compose(a, permutation.compose(b, c))
    assert left == right


@given(permutations)
def test_inverse_undoes_the_permutation(p: list[int]) -> None:
    identity = permutation.identity(SIZE)
    assert permutation.compose(p, permutation.inverse(p)) == identity
    assert permutation.compose(permutation.inverse(p), p) == identity


def test_power_small_exponents() -> None:
    p = [1, 0, 2, 4, 5, 3]
    assert permutation.power(p, 0) == permutation.identity(6)
    assert permutation.power(p, 1) == p
    assert permutation.power(p, 2) == permutation.compose(p, p)
    assert permutation.power(p, -1) == permutation.inverse(p)


@given(permutations, st.integers(-50, 50), st.integers(-50, 50))
def test_power_adds_exponents(p: list[int], j: int, k: int) -> None:
    assert permutation.power(p, j + k) == permutation.compose(
        permutation.power(p, j), permutation.power(p, k)
    )


@given(permutations)
def test_power_to_the_order_is_identity(p: list[int]) -> None:
    order = permutation.order(p)
    assert permutation.power(p, order) == permutation.identity(SIZE)
    assert all(
        permutation.power(p, order // prime) != permutation.identity(SIZE)
        for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
        if order % prime == 0
    )


def test_cycle_structure() -> None:
    p = [1, 0, 2, 4, 5, 3]
    assert permutation.cycles(p) == [[0, 1], [2], [3, 4, 5]]
    assert permutation.cycle_type(p) == [3, 2, 1]
    assert permutation.order(p) == 6
    assert permutation.fixed_points(p) == [2]


def test_from_cycles_leaves_unlisted_points_fixed() -> None:
    assert permutation.from_cycles(6, [[0, 1], [3, 4, 5]]) == [1, 0, 2, 4, 5, 3]


@given(permutations)
def test_from_cycles_inverts_cycles(p: list[int]) -> None:
    assert permutation.from_cycles(SIZE, permutation.cycles(p)) == list(p)


@pytest.mark.parametrize("cycles", [[[0, 1], [1, 2]], [[0, 6]], [[0, -1]]])
def test_from_cycles_rejects_bad_points(cycles: list[list[int]]) -> None:
    with pytest.raises(InvalidInputError):
        permutation.from_cycles(6, cycles)


def test_shift_adds_modulo_size() -> None:
    assert permutation.shift(5, 2) == [2, 3, 4, 0, 1]
    assert permutation.shift(5, -1) == [4, 0, 1, 2, 3]
    assert permutation.shift(5, 7) == permutation.shift(5, 2)


def test_transposition_swaps_two_points() -> None:
    assert permutation.transposition(4, 1, 3) == [0, 3, 2, 1]


@given(permutations, permutations)
def test_conjugate_is_by_p_by_inverse(p: list[int], by: list[int]) -> None:
    expected = permutation.compose(by, permutation.compose(p, permutation.inverse(by)))
    assert permutation.conjugate(p, by) == expected


@given(permutations, permutations)
def test_conjugate_keeps_the_cycle_type(p: list[int], by: list[int]) -> None:
    conjugated = permutation.conjugate(p, by)
    assert permutation.cycle_type(conjugated) == permutation.cycle_type(p)


@given(permutations, st.integers(0, SIZE - 1))
def test_conjugated_shift_steps_along_a_mixed_alphabet(
    alphabet: list[int], delta: int
) -> None:
    position = {symbol: i for i, symbol in enumerate(alphabet)}
    expected = [alphabet[(position[x] + delta) % SIZE] for x in range(SIZE)]
    shifted = permutation.conjugate(permutation.shift(SIZE, delta), alphabet)
    assert shifted == expected


def test_random_permutation_is_a_permutation() -> None:
    p = permutation.random_permutation(SIZE, random.Random(1))
    assert sorted(p) == list(range(SIZE))


def test_random_permutation_repeats_with_the_seed() -> None:
    first = permutation.random_permutation(SIZE, random.Random(7))
    assert first == permutation.random_permutation(SIZE, random.Random(7))
    assert first != permutation.random_permutation(SIZE, random.Random(8))


def test_random_with_cycle_type_has_that_cycle_type() -> None:
    p = permutation.random_with_cycle_type(SIZE, [5] * 5, random.Random(3301))
    assert permutation.cycle_type(p) == [5, 5, 5, 5, 5, 1, 1, 1, 1]
    assert permutation.order(p) == 5


def test_random_with_cycle_type_keeps_chosen_points_fixed() -> None:
    fixed = [0, 7, 13, 28]
    for seed in range(20):
        p = permutation.random_with_cycle_type(
            SIZE, [5] * 5, random.Random(seed), fixed=fixed
        )
        assert permutation.fixed_points(p) == fixed


def test_random_with_cycle_type_repeats_with_the_seed() -> None:
    first = permutation.random_with_cycle_type(SIZE, [5, 3], random.Random(7))
    second = permutation.random_with_cycle_type(SIZE, [5, 3], random.Random(7))
    assert first == second


@pytest.mark.parametrize(
    ("lengths", "fixed"),
    [([5] * 6, []), ([5] * 5, [0, 1, 2, 3, 4]), ([0], []), ([5], [29])],
)
def test_random_with_cycle_type_rejects_what_does_not_fit(
    lengths: list[int], fixed: list[int]
) -> None:
    with pytest.raises(InvalidInputError):
        permutation.random_with_cycle_type(SIZE, lengths, random.Random(0), fixed=fixed)


@pytest.mark.parametrize("bad", [[0, 0, 1], [0, 1, 3], [0, 1, -1], []])
def test_a_sequence_that_is_not_a_permutation_is_rejected(bad: list[int]) -> None:
    with pytest.raises(InvalidInputError):
        permutation.inverse(bad)


def test_compose_rejects_different_sizes() -> None:
    with pytest.raises(InvalidInputError, match="size"):
        permutation.compose([0, 1, 2], [1, 0])


def test_numpy_arrays_are_accepted() -> None:
    a, b = np.array([1, 2, 0]), np.array([0, 2, 1])
    assert permutation.compose(a, b) == list(a[b])
    assert permutation.inverse(a) == [2, 0, 1]


def test_parity_of_a_transposition_is_odd() -> None:
    assert permutation.parity(permutation.transposition(4, 0, 1)) == -1
    assert permutation.parity(permutation.identity(4)) == 1
    assert permutation.parity(permutation.from_cycles(4, [[0, 1, 2]])) == 1


@given(permutations, permutations)
def test_parity_is_multiplicative(p: list[int], q: list[int]) -> None:
    product = permutation.compose(p, q)
    assert permutation.parity(product) == permutation.parity(p) * permutation.parity(q)


def test_from_key_reads_a_substitution_key_in_alphabet_order() -> None:
    key = masc.shiftedkey("ABCD", shift=1)
    assert permutation.from_key("ABCD", key) == [1, 2, 3, 0]


def test_to_key_inverts_from_key() -> None:
    key = masc.randomkey("ABCDEFG", rng=random.Random(5))
    perm = permutation.from_key("ABCDEFG", key)
    assert permutation.to_key("ABCDEFG", perm) == key


@given(permutations)
def test_from_key_inverts_to_key(p: list[int]) -> None:
    alphabet = [chr(0x16A0 + i) for i in range(SIZE)]
    assert permutation.from_key(alphabet, permutation.to_key(alphabet, p)) == list(p)


def test_from_key_rejects_a_key_that_is_not_a_bijection() -> None:
    with pytest.raises(InvalidInputError):
        permutation.from_key("ABC", {"A": "B", "B": "B", "C": "A"})
    with pytest.raises(InvalidInputError):
        permutation.from_key("ABC", {"A": "B", "B": "C"})


def test_to_key_rejects_a_size_mismatch() -> None:
    with pytest.raises(InvalidInputError):
        permutation.to_key("ABC", [0, 1])
