# ABOUTME: Tests the Markov text model: sampling from stated weights, fitting to a
# ABOUTME: training sequence, and the validation of both.
from __future__ import annotations

import random
from collections import Counter

import pytest

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.stats.markov import MarkovModel, fit_markov


def _alternating() -> MarkovModel[str]:
    return MarkovModel(1, "AB", {("A",): {"B": 1.0}, ("B",): {"A": 1.0}})


def test_sample_follows_the_stated_transitions() -> None:
    out = _alternating().sample(50, random.Random(0))
    assert len(out) == 50
    assert all(a != b for a, b in zip(out, out[1:]))


def test_sample_repeats_with_the_seed_and_varies_without() -> None:
    model = MarkovModel(1, "ABC", {(s,): dict.fromkeys("ABC", 1.0) for s in "ABC"})
    assert model.sample(40, random.Random(5)) == model.sample(40, random.Random(5))
    assert model.sample(40, random.Random(5)) != model.sample(40, random.Random(6))


def test_sample_respects_the_start_weights() -> None:
    model = MarkovModel(
        1, "AB", {(s,): dict.fromkeys("AB", 1.0) for s in "AB"}, starts={("A",): 1.0}
    )
    assert all(model.sample(1, random.Random(seed)) == ["A"] for seed in range(20))


def test_sample_restarts_at_an_unseen_context() -> None:
    model = MarkovModel(2, "AB", {("A", "A"): {"B": 1.0}})
    out = model.sample(7, random.Random(1))
    assert out == ["A", "A", "B", "A", "A", "B", "A"]


def test_sample_of_zero_length_is_empty() -> None:
    assert _alternating().sample(0, random.Random(0)) == []
    with pytest.raises(InvalidInputError):
        _alternating().sample(-1, random.Random(0))


def test_fit_markov_learns_the_transition_bias() -> None:
    rng = random.Random(2)
    training = ["A"]
    for _ in range(5000):
        training.append("A" if rng.random() < 0.9 else "B")
    model = fit_markov(training, order=1)
    out = model.sample(5000, random.Random(3))
    after_a = [b for a, b in zip(out, out[1:]) if a == "A"]
    assert Counter(after_a)["A"] / len(after_a) == pytest.approx(0.9, abs=0.03)


def test_fit_markov_of_order_two_reproduces_a_deterministic_pattern() -> None:
    model = fit_markov("ABCABCABCABC", order=2)
    out = "".join(model.sample(30, random.Random(0)))
    assert out in ("ABC" * 10, "BCA" * 10, "CAB" * 10)


def test_fit_markov_smoothing_lets_unseen_symbols_appear() -> None:
    model = fit_markov("AAAAAAAA", order=1, alphabet="AB", smoothing=1.0)
    out = model.sample(2000, random.Random(0))
    assert "B" in out


@pytest.mark.parametrize(
    ("training", "order", "smoothing", "error"),
    [
        ("ABAB", 0, 0.0, InvalidInputError),
        ("ABAB", 1, -1.0, InvalidInputError),
        ("AB", 2, 0.0, InsufficientDataError),
    ],
)
def test_fit_markov_rejects_bad_input(
    training: str, order: int, smoothing: float, error: type[Exception]
) -> None:
    with pytest.raises(error):
        fit_markov(training, order, smoothing=smoothing)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"order": 0, "alphabet": "AB", "transitions": {(): {"A": 1.0}}},
        {"order": 1, "alphabet": "", "transitions": {("A",): {"A": 1.0}}},
        {"order": 1, "alphabet": "AB", "transitions": {}},
        {"order": 1, "alphabet": "AB", "transitions": {("A", "B"): {"A": 1.0}}},
        {"order": 1, "alphabet": "AB", "transitions": {("A",): {"A": -1.0}}},
        {"order": 1, "alphabet": "AB", "transitions": {("A",): {"A": 0.0}}},
    ],
)
def test_model_rejects_bad_weights(kwargs: dict) -> None:
    with pytest.raises(InvalidInputError):
        MarkovModel(**kwargs)
