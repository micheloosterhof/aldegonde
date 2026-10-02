# ABOUTME: Tests pair tables inside words, the relation rate of a permutation, and
# ABOUTME: the exact extremes of that rate over all permutations.
from __future__ import annotations

from itertools import permutations

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.maths import permutation
from aldegonde.stats.pairs import extremal_relation_rate, pair_counts, relation_rate


def test_pair_counts_adjacent_pairs() -> None:
    # pairs in AABAB: AA, AB, BA, AB
    assert pair_counts([[0, 0, 1, 0, 1]], 2).tolist() == [[1, 2], [1, 0]]


def test_pair_counts_at_a_lag() -> None:
    # pairs at lag 3 in ABCABC: AA, BB, CC
    assert pair_counts([[0, 1, 2, 0, 1, 2]], 3, lag=3).tolist() == np.eye(3).tolist()


def test_pair_counts_do_not_cross_word_boundaries() -> None:
    whole = pair_counts([[0, 1, 1, 0]], 2)
    split = pair_counts([[0, 1], [1, 0]], 2)
    assert whole.sum() == 3
    assert split.sum() == 2
    assert split.tolist() == [[0, 1], [1, 0]]


def test_pair_counts_skip_words_shorter_than_the_lag() -> None:
    assert pair_counts([[0], [1, 2], []], 3, lag=2).sum() == 0


@pytest.mark.parametrize(
    ("words", "size", "lag"), [([[0, 3]], 3, 1), ([[0, -1]], 3, 1), ([[0, 1]], 3, 0)]
)
def test_pair_counts_reject_bad_input(
    words: list[list[int]], size: int, lag: int
) -> None:
    with pytest.raises(InvalidInputError):
        pair_counts(words, size, lag)


def test_relation_rate_of_the_identity_is_the_doublet_rate() -> None:
    table = pair_counts([[0, 0, 1, 0, 1]], 2)
    assert relation_rate(table, [0, 1]) == pytest.approx(0.25)


def test_relation_rate_counts_pairs_whose_first_symbol_is_the_image_of_the_second() -> (
    None
):
    # the only pair is (0, 1): first 0, second 1
    table = pair_counts([[0, 1]], 2)
    assert relation_rate(table, [1, 0]) == 1.0  # perm[1] == 0
    assert relation_rate(table, [0, 1]) == 0.0


def test_relation_rate_is_zero_for_an_empty_table() -> None:
    assert relation_rate([[0, 0], [0, 0]], [0, 1]) == 0.0


@pytest.mark.parametrize("perm", [[0, 1, 2], [0, 0], [0, 2]])
def test_relation_rate_rejects_a_mismatched_permutation(perm: list[int]) -> None:
    with pytest.raises(InvalidInputError):
        relation_rate([[1, 0], [0, 1]], perm)


@given(
    st.lists(
        st.lists(st.integers(0, 3), min_size=2, max_size=8), min_size=1, max_size=6
    )
)
def test_extremes_bracket_every_permutation(words: list[list[int]]) -> None:
    table = pair_counts(words, 4)
    if table.sum() == 0:
        return
    floor = extremal_relation_rate(table)
    ceiling = extremal_relation_rate(table, maximize=True)
    rates = [relation_rate(table, list(p)) for p in permutations(range(4))]
    assert floor.rate == pytest.approx(min(rates))
    assert ceiling.rate == pytest.approx(max(rates))
    assert relation_rate(table, floor.perm) == pytest.approx(floor.rate)
    assert relation_rate(table, ceiling.perm) == pytest.approx(ceiling.rate)
    assert permutation.cycle_type(floor.perm)  # a valid permutation


def test_an_alternating_language_has_a_zero_floor() -> None:
    table = pair_counts([[0, 1] * 20], 2)
    assert extremal_relation_rate(table).rate == 0.0


def test_extremal_rejects_empty_or_massless_tables() -> None:
    with pytest.raises(InsufficientDataError):
        extremal_relation_rate([])
    with pytest.raises(InsufficientDataError):
        extremal_relation_rate([[0, 0], [0, 0]])
    with pytest.raises(InvalidInputError):
        extremal_relation_rate([[1, 2, 3]])
