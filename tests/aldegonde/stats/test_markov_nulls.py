import random
from collections import Counter

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.nulls import doublet_markov, fitted_markov, markov_model

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _doublet_rate(seq: list[str]) -> float:
    return sum(1 for a, b in zip(seq, seq[1:]) if a == b) / (len(seq) - 1)


def test_markov_model_matches_length_only() -> None:
    null = markov_model("AB", {"A": [0.0, 1.0], "B": [1.0, 0.0]})
    out = null(list("AAAAAA"), random.Random(0))
    assert len(out) == 6
    # deterministic alternating chain: no two adjacent symbols equal
    assert all(a != b for a, b in zip(out, out[1:]))


def test_markov_model_is_seeded_and_varies() -> None:
    null = markov_model("ABC", {s: [1.0, 1.0, 1.0] for s in "ABC"})
    data = list("A" * 50)
    assert null(data, random.Random(5)) == null(data, random.Random(5))
    assert null(data, random.Random(5)) != null(data, random.Random(6))


def test_markov_model_respects_initial_distribution() -> None:
    null = markov_model("AB", {"A": [1.0, 1.0], "B": [1.0, 1.0]}, initial=[1.0, 0.0])
    for seed in range(20):
        assert null(["A"], random.Random(seed))[0] == "A"


def test_markov_model_validation() -> None:
    with pytest.raises(InvalidInputError):
        markov_model("", {})
    with pytest.raises(InvalidInputError):
        markov_model("AB", {"A": [1.0, 1.0]})  # row missing for B
    with pytest.raises(InvalidInputError):
        markov_model("AB", {"A": [1.0], "B": [1.0, 1.0]})  # wrong size
    with pytest.raises(InvalidInputError):
        markov_model("AB", {"A": [0.0, 0.0], "B": [1.0, 1.0]})  # zero row
    with pytest.raises(InvalidInputError):
        markov_model("AB", {"A": [-1.0, 2.0], "B": [1.0, 1.0]})  # negative


def test_doublet_markov_hits_target_rate() -> None:
    target = 0.02
    null = doublet_markov(list(ABC), target)
    surrogate = null(["A"] * 20000, random.Random(1))
    assert _doublet_rate(list(surrogate)) == pytest.approx(target, abs=0.005)


def test_doublet_markov_zero_rate_forbids_doublets() -> None:
    null = doublet_markov("ABCDE", 0.0)
    surrogate = null(["A"] * 2000, random.Random(2))
    assert _doublet_rate(list(surrogate)) == 0.0


def test_doublet_markov_marginals_roughly_uniform() -> None:
    null = doublet_markov("ABCD", 0.01)
    counts = Counter(null(["A"] * 20000, random.Random(3)))
    for symbol in "ABCD":
        assert counts[symbol] == pytest.approx(5000, rel=0.1)


def test_doublet_markov_validation() -> None:
    with pytest.raises(InvalidInputError):
        doublet_markov("A", 0.1)
    with pytest.raises(InvalidInputError):
        doublet_markov("AB", 1.5)


def test_fitted_markov_reproduces_transition_bias() -> None:
    # data where A is nearly always followed by B
    data = list("AB" * 500)
    null = fitted_markov("AB", smoothing=0.5)
    surrogate = null(data, random.Random(4))
    follows_b = sum(
        1 for a, b in zip(surrogate, surrogate[1:]) if a == "A" and b == "B"
    )
    a_count = sum(1 for s in surrogate[:-1] if s == "A")
    assert a_count > 0
    assert follows_b / a_count > 0.9


def test_fitted_markov_validation() -> None:
    with pytest.raises(InvalidInputError):
        fitted_markov("")
    with pytest.raises(InvalidInputError):
        fitted_markov("AB", smoothing=-1.0)
