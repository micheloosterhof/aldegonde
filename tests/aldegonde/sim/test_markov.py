import random

import pytest

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.sim.markov import cut_by_lengths, fit_markov, generate


def test_generate_length_and_alphabet() -> None:
    training = list("ABCABCABC" * 10)
    model = fit_markov(training, order=1)
    out = generate(model, 50, random.Random(0))
    assert len(out) == 50
    assert set(out) <= set("ABC")


def test_generate_is_seeded() -> None:
    model = fit_markov(list("ABCDABCD" * 20), order=2, smoothing=0.1)
    a = generate(model, 100, random.Random(3))
    b = generate(model, 100, random.Random(3))
    assert a == b


def test_generate_reproduces_deterministic_structure() -> None:
    # a strictly cyclic training text yields a model that continues the cycle
    model = fit_markov(list("ABC" * 20), order=1)
    out = generate(model, 30, random.Random(1))
    # every A is followed by B, every B by C, every C by A
    for x, y in zip(out, out[1:]):
        assert (x, y) in {("A", "B"), ("B", "C"), ("C", "A")}


def test_generate_zero_length() -> None:
    model = fit_markov(list("ABAB" * 5), order=1)
    assert generate(model, 0, random.Random(0)) == []


def test_fit_markov_validation() -> None:
    with pytest.raises(InvalidInputError):
        fit_markov(list("ABC"), order=0)
    with pytest.raises(InvalidInputError):
        fit_markov(list("ABC"), order=1, smoothing=-1.0)
    with pytest.raises(InsufficientDataError):
        fit_markov(list("A"), order=2)


def test_cut_by_lengths_preserves_all_symbols() -> None:
    stream = list(range(100))
    words = cut_by_lengths(stream, {3: 5, 4: 3, 5: 2}, random.Random(2))
    assert sum(len(w) for w in words) == 100
    assert [s for w in words for s in w] == stream


def test_cut_by_lengths_single_length() -> None:
    words = cut_by_lengths(list("ABCDEF"), {2: 1.0}, random.Random(0))
    assert words == [list("AB"), list("CD"), list("EF")]


def test_cut_by_lengths_validation() -> None:
    with pytest.raises(InvalidInputError):
        cut_by_lengths([1, 2, 3], {}, random.Random(0))
    with pytest.raises(InvalidInputError):
        cut_by_lengths([1, 2, 3], {0: 1.0}, random.Random(0))
    with pytest.raises(InvalidInputError):
        cut_by_lengths([1, 2, 3], {2: 0.0}, random.Random(0))
