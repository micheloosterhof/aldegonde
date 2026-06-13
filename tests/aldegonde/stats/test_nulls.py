import random
from collections import Counter

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.nulls import no_doublet_shuffle, shuffle

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


def test_no_doublet_shuffle_preserves_multiset() -> None:
    data = "AABBBCCCCDDDD"
    out = no_doublet_shuffle(data, random.Random(0))
    assert Counter(out) == Counter(data)


def test_no_doublet_shuffle_has_no_adjacent_equal() -> None:
    data = "AABBBCCCCDDDD"
    out = no_doublet_shuffle(data, random.Random(0))
    assert all(a != b for a, b in zip(out, out[1:]))


def test_no_doublet_shuffle_raises_when_infeasible() -> None:
    # 'A' occurs 3 times in length 4; ceil(4/2) = 2, so no arrangement exists
    with pytest.raises(InvalidInputError):
        no_doublet_shuffle("AAAB", random.Random(0))


def test_no_doublet_shuffle_boundary_feasible() -> None:
    # 'A' occurs exactly ceil(5/2) = 3 times: feasible as A_A_A
    out = no_doublet_shuffle("AAABB", random.Random(0))
    assert Counter(out) == Counter("AAABB")
    assert all(a != b for a, b in zip(out, out[1:]))
