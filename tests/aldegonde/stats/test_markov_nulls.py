# ABOUTME: Tests the generative null models: surrogates drawn from a Markov model,
# ABOUTME: from a model fitted to the data, and from a pinned doublet rate.
from __future__ import annotations

import random
from collections import Counter

import pytest

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.markov import MarkovModel
from aldegonde.stats.nulls import doublet_markov, fitted_markov, markov_null

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _doublet_rate(seq: list[str]) -> float:
    return sum(1 for a, b in zip(seq, seq[1:]) if a == b) / (len(seq) - 1)


def test_markov_null_matches_the_length_only() -> None:
    model = MarkovModel(1, "AB", {("A",): {"B": 1.0}, ("B",): {"A": 1.0}})
    out = markov_null(model)(list("AAAAAA"), random.Random(0))
    assert len(out) == 6
    assert all(a != b for a, b in zip(out, out[1:]))


def test_doublet_markov_hits_the_target_rate() -> None:
    null = doublet_markov(ABC, 0.02)
    out = null(list(ABC) * 400, random.Random(1))
    assert _doublet_rate(out) == pytest.approx(0.02, abs=0.005)


def test_doublet_markov_at_zero_forbids_doublets() -> None:
    out = doublet_markov(ABC, 0.0)(list(ABC) * 50, random.Random(2))
    assert _doublet_rate(out) == 0.0


def test_doublet_markov_keeps_the_marginals_flat() -> None:
    out = doublet_markov("ABCD", 0.01)(["A"] * 20000, random.Random(3))
    counts = Counter(out)
    assert all(abs(counts[s] / 20000 - 0.25) < 0.02 for s in "ABCD")


def test_doublet_markov_rejects_bad_input() -> None:
    with pytest.raises(InvalidInputError):
        doublet_markov("A", 0.1)
    with pytest.raises(InvalidInputError):
        doublet_markov("AB", 1.5)


def test_fitted_markov_reproduces_the_transition_bias() -> None:
    rng = random.Random(4)
    data = ["A"]
    for _ in range(4000):
        data.append("A" if rng.random() < 0.9 else "B")
    out = fitted_markov(order=1, smoothing=0.0)(data, random.Random(5))
    assert len(out) == len(data)
    after_a = [b for a, b in zip(out, out[1:]) if a == "A"]
    assert after_a.count("A") / len(after_a) == pytest.approx(0.9, abs=0.03)


def test_fitted_markov_is_seeded() -> None:
    data = list("ABRACADABRA" * 10)
    null = fitted_markov()
    assert null(data, random.Random(7)) == null(data, random.Random(7))


def test_fitted_markov_rejects_bad_input() -> None:
    with pytest.raises(InvalidInputError):
        fitted_markov(order=0)
    with pytest.raises(InvalidInputError):
        fitted_markov(smoothing=-1.0)
