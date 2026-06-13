import random
from collections import Counter

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.nulls import (
    estimate_transitions,
    from_transition_matrix,
    markov1,
    no_doublet_shuffle,
    shuffle,
    unigram_distribution,
)

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_shuffle_preserves_multiset() -> None:
    data = "AABBBCCCC"
    out = shuffle(data, random.Random(0))
    assert Counter(out) == Counter(data)
    assert len(out) == len(data)


def test_shuffle_is_deterministic_with_seed() -> None:
    data = list(ABC) * 4
    assert shuffle(data, random.Random(7)) == shuffle(data, random.Random(7))


def test_shuffle_varies_with_seed() -> None:
    data = list(ABC) * 4
    assert shuffle(data, random.Random(1)) != shuffle(data, random.Random(2))


def test_no_doublet_shuffle_has_no_adjacent_equal() -> None:
    data = "AABBBCCCCDDDD"
    out = no_doublet_shuffle(data, random.Random(0))
    assert Counter(out) == Counter(data)
    assert all(a != b for a, b in zip(out, out[1:]))


def test_no_doublet_shuffle_raises_when_infeasible() -> None:
    # 'A' occurs 3 times in length 4; ceil(4/2) = 2, so no arrangement exists
    with pytest.raises(InvalidInputError):
        no_doublet_shuffle("AAAB", random.Random(0))


def test_no_doublet_shuffle_boundary_feasible() -> None:
    # 'A' occurs exactly ceil(5/2) = 3 times: feasible as A_A_A
    out = no_doublet_shuffle("AABBA"[:0] + "AAABB", random.Random(0))
    assert all(a != b for a, b in zip(out, out[1:]))


def test_estimate_transitions_rows_sum_to_one() -> None:
    matrix = estimate_transitions("ABCABCAB", alphabet="ABC")
    assert len(matrix) == 3
    for row in matrix:
        assert abs(sum(row) - 1.0) < 1e-9


def test_estimate_transitions_counts() -> None:
    # ABAB: A->B twice, B->A once; row A = [0, 1], row B = [1, 0]
    matrix = estimate_transitions("ABAB", alphabet="AB")
    assert matrix[0] == [0.0, 1.0]
    assert matrix[1] == [1.0, 0.0]


def test_estimate_transitions_smoothing_moves_toward_uniform() -> None:
    matrix = estimate_transitions("ABAB", alphabet="AB", smoothing=1.0)
    # A->A now nonzero because of the pseudo-count
    assert matrix[0][0] > 0.0
    assert matrix[0][0] < matrix[0][1]


def test_from_transition_matrix_length_and_alphabet() -> None:
    model = from_transition_matrix("AB", [[0.0, 1.0], [1.0, 0.0]], [1.0, 0.0])
    out = model("....." , random.Random(0))
    assert len(out) == 5
    assert set(out) <= set("AB")


def test_from_transition_matrix_forced_chain_is_deterministic() -> None:
    # start at A, A->B->A->B... regardless of rng
    model = from_transition_matrix("AB", [[0.0, 1.0], [1.0, 0.0]], [1.0, 0.0])
    assert model("xxxx", random.Random(99)) == ["A", "B", "A", "B"]


def test_markov1_preserves_length_and_alphabet() -> None:
    data = "ABCABCABCABC"
    out = markov1("ABC")(data, random.Random(0))
    assert len(out) == len(data)
    assert set(out) <= set("ABC")


def test_unigram_distribution_sums_to_one() -> None:
    dist = unigram_distribution("AABBC", alphabet="ABC")
    assert abs(sum(dist) - 1.0) < 1e-9
    assert dist == [pytest.approx(0.4), pytest.approx(0.4), pytest.approx(0.2)]
