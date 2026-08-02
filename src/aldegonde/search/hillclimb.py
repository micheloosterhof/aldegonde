# ABOUTME: Generic hill-climbing solver: injected neighborhood and score,
# ABOUTME: stagnation cutoff, and a seeded multi-start driver.
"""Hill climbing over an arbitrary key space.

The climber is generic over the state type: the caller injects a scoring
function (n-gram fitness, IOC, a composite with structural penalties) and a
neighborhood move (swap two symbols of a key, conjugate a permutation), so
one solver serves monoalphabetic keys, mixed alphabets, permutation gears,
and anything else with a local move.

Hill climbing finds local optima; the standard remedy is many independent
starts, provided by `multi_start` with one deterministic seed per start.
Before trusting a search that fails to find a key, run it on a planted
instance: encrypt known plaintext with a known key and confirm the search
recovers it — a search that cannot recover a planted key says nothing about
a real ciphertext.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar

from aldegonde.exceptions import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Sequence

S = TypeVar("S")

Score = Callable[[S], float]
"""A fitness function to maximize: state -> score."""

Neighbor = Callable[[S, random.Random], S]
"""A local move: (state, random source) -> nearby state."""


@dataclass(frozen=True)
class ClimbResult(Generic[S]):
    """Outcome of a hill climb.

    Attributes:
        state: The best state found
        score: Its score
        proposals: Neighbor proposals evaluated
        improvements: Proposals that improved the score
    """

    state: S
    score: float
    proposals: int
    improvements: int


def hill_climb(
    initial: S,
    neighbor: Neighbor[S],
    score: Score[S],
    *,
    iterations: int = 10_000,
    stagnation: int | None = None,
    rng: random.Random,
) -> ClimbResult[S]:
    """Climb from an initial state, accepting strictly improving neighbors.

    Proposes up to `iterations` neighbors, moving whenever the proposal
    scores strictly higher. With `stagnation` set, the climb stops early
    after that many consecutive non-improving proposals — the signal that a
    local optimum is reached and further proposals are wasted; spend the
    budget on another start instead.

    Args:
        initial: Starting state
        neighbor: Local move proposing a nearby state
        score: Fitness function to maximize
        iterations: Maximum neighbor proposals
        stagnation: Consecutive non-improving proposals before stopping;
            None climbs the full budget
        rng: Injected random source driving the neighborhood

    Returns:
        The best state found with its score and proposal counts

    Raises:
        InvalidInputError: If iterations or stagnation is not positive
    """
    if iterations < 1:
        msg = f"iterations must be positive, got {iterations}"
        raise InvalidInputError(msg)
    if stagnation is not None and stagnation < 1:
        msg = f"stagnation must be positive, got {stagnation}"
        raise InvalidInputError(msg)
    best = initial
    best_score = score(initial)
    proposals = 0
    improvements = 0
    since_improvement = 0
    for _ in range(iterations):
        proposals += 1
        candidate = neighbor(best, rng)
        candidate_score = score(candidate)
        if candidate_score > best_score:
            best = candidate
            best_score = candidate_score
            improvements += 1
            since_improvement = 0
        else:
            since_improvement += 1
            if stagnation is not None and since_improvement >= stagnation:
                break
    return ClimbResult(
        state=best,
        score=best_score,
        proposals=proposals,
        improvements=improvements,
    )


def multi_start(
    initial_factory: Callable[[random.Random], S],
    neighbor: Neighbor[S],
    score: Score[S],
    *,
    starts: int = 10,
    iterations: int = 10_000,
    stagnation: int | None = None,
    seed: int = 0,
) -> tuple[ClimbResult[S], list[ClimbResult[S]]]:
    """Run independent seeded climbs from fresh starts and keep the best.

    Start i draws its initial state and its whole climb from
    random.Random(seed + i), so a run is reproducible, any single start can
    be replayed in isolation, and the starts are independent — the standard
    answer to hill climbing's local optima.

    Args:
        initial_factory: Draws a fresh starting state from a random source
        neighbor: Local move proposing a nearby state
        score: Fitness function to maximize
        starts: Number of independent climbs
        iterations: Maximum proposals per climb
        stagnation: Early-stop cutoff per climb; None climbs the full budget
        seed: Base seed; start i uses random.Random(seed + i)

    Returns:
        The best climb result, and every start's result in start order

    Raises:
        InvalidInputError: If starts is not positive
    """
    if starts < 1:
        msg = f"starts must be positive, got {starts}"
        raise InvalidInputError(msg)
    results: list[ClimbResult[S]] = []
    for start in range(starts):
        rng = random.Random(seed + start)
        results.append(
            hill_climb(
                initial_factory(rng),
                neighbor,
                score,
                iterations=iterations,
                stagnation=stagnation,
                rng=rng,
            )
        )
    best = max(results, key=lambda result: result.score)
    return best, results


def swap_neighbor(state: Sequence[S], rng: random.Random) -> list[S]:
    """Swap two distinct positions of a sequence state.

    The canonical neighborhood for substitution keys and mixed alphabets:
    every arrangement is reachable, and each move changes exactly two
    images.

    Args:
        state: Sequence state, e.g. an alphabet arrangement
        rng: Injected random source

    Returns:
        A new list with two positions exchanged

    Raises:
        InvalidInputError: If the state has fewer than 2 elements
    """
    if len(state) < 2:
        msg = "swap_neighbor needs at least 2 elements"
        raise InvalidInputError(msg)
    out = list(state)
    i, j = rng.sample(range(len(out)), 2)
    out[i], out[j] = out[j], out[i]
    return out


def conjugation_neighbor(state: Sequence[int], rng: random.Random) -> list[int]:
    """Conjugate a permutation state by a random transposition.

    The cycle-type-preserving neighborhood: use it when the key is a
    permutation whose cycle structure is part of the hypothesis (a gear of
    known order) and only the labeling is unknown. See
    `aldegonde.perm.transposition_conjugate`.

    Args:
        state: Permutation in index form
        rng: Injected random source

    Returns:
        A conjugate permutation with the same cycle type
    """
    from aldegonde.perm import transposition_conjugate

    a, b = rng.sample(range(len(state)), 2)
    return transposition_conjugate(state, a, b)
