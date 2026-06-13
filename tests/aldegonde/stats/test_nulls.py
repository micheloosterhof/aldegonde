import random
import statistics
from collections import Counter

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats import kappa
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


def test_no_doublet_shuffle_has_no_long_range_structure() -> None:
    # A valid null must not inject long-range skip-dependent structure: at skip
    # >= 3 the mean kappa over surrogates must track the plain-shuffle frequency
    # baseline, not ramp with the skip. A greedy "most frequent first"
    # arrangement fails this because it builds a quasi-periodic pattern. (Skip 2
    # is excluded: a doublet-free sequence genuinely elevates skip-2 coincidence,
    # since the forbidden skip-1 matches spill one position over.)
    data = random.Random(0).choices(
        range(12), weights=[6, 5, 4, 4, 3, 3, 2, 2, 1, 1, 1, 1], k=2000
    )
    for skip in range(3, 14):
        no_doublet = statistics.fmean(
            kappa(no_doublet_shuffle(data, random.Random(t)), skip=skip)
            for t in range(30)
        )
        plain = statistics.fmean(
            kappa(shuffle(data, random.Random(t)), skip=skip) for t in range(30)
        )
        assert abs(no_doublet - plain) < 0.01, f"skip {skip}: {no_doublet} vs {plain}"
