import pytest

from aldegonde.analysis.bounds import (
    diagonal_rate,
    extremal_diagonal_rate,
    pair_counts,
)
from aldegonde.exceptions import InsufficientDataError, InvalidInputError


def test_pair_counts_adjacent() -> None:
    matrix = pair_counts("AABAB", "AB")
    # pairs: AA, AB, BA, AB
    assert matrix == [[1, 2], [1, 0]]


def test_pair_counts_at_lag() -> None:
    matrix = pair_counts("ABCABC", "ABC", lag=3)
    # pairs at lag 3: AA, BB, CC
    assert matrix == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_pair_counts_unknown_symbol_raises() -> None:
    with pytest.raises(InvalidInputError):
        pair_counts("ABX", "AB")
    with pytest.raises(InvalidInputError):
        pair_counts("AB", "AB", lag=0)


def test_diagonal_rate_identity_counts_doublets() -> None:
    matrix = pair_counts("AABAB", "AB")
    # identity permutation: mass at (A,A) and (B,B) = 1 of 4 pairs
    assert diagonal_rate(matrix, [0, 1]) == pytest.approx(0.25)


def test_diagonal_rate_size_mismatch_raises() -> None:
    with pytest.raises(InvalidInputError):
        diagonal_rate([[1, 0], [0, 1]], [0, 1, 2])


def test_diagonal_rate_empty_matrix_is_zero() -> None:
    assert diagonal_rate([[0, 0], [0, 0]], [0, 1]) == 0.0


def test_extremal_bounds_bracket_every_permutation() -> None:
    matrix = pair_counts("AABBCCABCACB" * 5, "ABC")
    floor = extremal_diagonal_rate(matrix)
    ceiling = extremal_diagonal_rate(matrix, maximize=True)
    assert floor.rate <= ceiling.rate
    # check the bound against the whole symmetric group on 3 points
    from itertools import permutations

    for candidate in permutations(range(3)):
        rate = diagonal_rate(matrix, list(candidate))
        assert floor.rate <= rate + 1e-12
        assert rate <= ceiling.rate + 1e-12


def test_extremal_perm_attains_reported_rate() -> None:
    matrix = pair_counts("AABBCC" * 10, "ABC")
    floor = extremal_diagonal_rate(matrix)
    assert diagonal_rate(matrix, floor.perm) == pytest.approx(floor.rate)
    sorted_perm = sorted(floor.perm)
    assert sorted_perm == [0, 1, 2]


def test_language_avoiding_pairs_has_zero_floor() -> None:
    # alternating language never needs a diagonal: some permutation exposes
    # no doublets at all
    matrix = pair_counts("ABAB" * 20, "AB")
    assert extremal_diagonal_rate(matrix).rate == 0.0


def test_extremal_validation() -> None:
    with pytest.raises(InsufficientDataError):
        extremal_diagonal_rate([])
    with pytest.raises(InsufficientDataError):
        extremal_diagonal_rate([[0, 0], [0, 0]])
