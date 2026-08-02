import random

import pytest

from aldegonde import perm
from aldegonde.exceptions import InvalidInputError
from aldegonde.search.hillclimb import (
    conjugation_neighbor,
    hill_climb,
    multi_start,
    swap_neighbor,
)

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _match_score(target: str):
    def score(candidate: list[str]) -> float:
        return sum(a == b for a, b in zip(candidate, target))

    return score


def test_hill_climb_reaches_optimum() -> None:
    target = list("DCBA" * 3)
    score = _match_score(target)
    start = sorted(target)
    result = hill_climb(
        start, swap_neighbor, score, iterations=5000, rng=random.Random(0)
    )
    assert result.state == target
    assert result.score == len(target)
    assert result.improvements <= result.proposals


def test_hill_climb_never_worsens() -> None:
    target = list("ZYXWVU")
    result = hill_climb(
        sorted(target),
        swap_neighbor,
        _match_score(target),
        iterations=2000,
        rng=random.Random(1),
    )
    assert result.score >= sum(a == b for a, b in zip(sorted(target), target))


def test_stagnation_stops_early() -> None:
    # constant score: every proposal stagnates, so it stops after `stagnation`
    result = hill_climb(
        list("AB"),
        swap_neighbor,
        lambda _s: 1.0,
        iterations=10_000,
        stagnation=50,
        rng=random.Random(2),
    )
    assert result.proposals == 50


def test_hill_climb_invalid_args() -> None:
    with pytest.raises(InvalidInputError):
        hill_climb([1, 2], swap_neighbor, sum, iterations=0, rng=random.Random(0))
    with pytest.raises(InvalidInputError):
        hill_climb([1, 2], swap_neighbor, sum, stagnation=0, rng=random.Random(0))


def test_multi_start_is_reproducible() -> None:
    target = list("HGFEDCBA")

    def factory(r: random.Random) -> list[str]:
        return r.sample(target, len(target))

    a, _ = multi_start(factory, swap_neighbor, _match_score(target), starts=4, seed=5)
    b, _ = multi_start(factory, swap_neighbor, _match_score(target), starts=4, seed=5)
    assert a.state == b.state
    assert a.score == b.score


def test_multi_start_returns_best_and_all() -> None:
    target = list("BADCFE")
    best, results = multi_start(
        lambda r: r.sample(target, len(target)),
        swap_neighbor,
        _match_score(target),
        starts=5,
        seed=0,
    )
    assert len(results) == 5
    assert best.score == max(r.score for r in results)


def test_multi_start_invalid_starts() -> None:
    with pytest.raises(InvalidInputError):
        multi_start(lambda r: [0], swap_neighbor, sum, starts=0)


def test_planted_substitution_key_recovered() -> None:
    # encrypt known plaintext with a known key; the climber must recover it
    rng = random.Random(7)
    plaintext = [rng.choice("ETAOINSHRD") for _ in range(500)]
    key = list(ABC)
    random.Random(11).shuffle(key)
    enc = dict(zip(ABC, key))
    cipher = [enc[p] for p in plaintext]

    def score(candidate: list[str]) -> float:
        dec = {c: p for p, c in zip(ABC, candidate)}
        return sum(dec[c] == p for c, p in zip(cipher, plaintext))

    best, _ = multi_start(
        lambda r: r.sample(ABC, 26),
        swap_neighbor,
        score,
        starts=8,
        iterations=5000,
        stagnation=1000,
        seed=1,
    )
    assert best.score == len(cipher)


def test_swap_neighbor_changes_two_positions() -> None:
    state = list(range(10))
    out = swap_neighbor(state, random.Random(0))
    differing = [i for i in range(10) if out[i] != state[i]]
    assert len(differing) == 2
    assert sorted(out) == state


def test_swap_neighbor_too_short_raises() -> None:
    with pytest.raises(InvalidInputError):
        swap_neighbor([1], random.Random(0))


def test_conjugation_neighbor_preserves_cycle_type() -> None:
    g = perm.from_cycle_type([4, 3, 2], 9)
    for seed in range(10):
        mutated = conjugation_neighbor(g, random.Random(seed))
        assert perm.cycle_type(mutated) == perm.cycle_type(g)
