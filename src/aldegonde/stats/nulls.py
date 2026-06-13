# ABOUTME: Null-hypothesis resamplers that turn an observed sequence into
# ABOUTME: surrogate sequences preserving chosen nuisance structure.
"""Null models for resampling-based significance testing.

A null model is a resampler: given the observed sequence and an injected
random source, it returns a surrogate sequence drawn under a null hypothesis
that preserves some nuisance structure (frequencies, doublet rate, ...) and
randomizes everything else. Comparing an observed statistic against the
distribution of the same statistic over many surrogates isolates the
structure the null does not contain.

The nulls implemented here both preserve the exact multiset of symbols:

    shuffle             exact unigram frequencies, order destroyed
    no_doublet_shuffle  exact frequencies and no adjacent equal symbols
    doublet_shuffle     exact frequencies at a chosen adjacent-doublet rate

Randomness is injected as a random.Random so a seeded run is reproducible and
trials are independent; the resampler is a pure function of (data, rng).
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Callable, Sequence
from typing import TypeVar

from aldegonde.exceptions import InvalidInputError

T = TypeVar("T")

NullModel = Callable[[Sequence[T], random.Random], Sequence[T]]
"""A resampler: (observed sequence, random source) -> surrogate sequence."""


def shuffle(data: Sequence[T], rng: random.Random) -> list[T]:
    """Return a uniform random permutation of the observed sequence.

    Preserves the exact multiset of symbols (every unigram frequency) and
    destroys all ordering. This is the frequency-matched null; a statistic
    that is invariant under it (monographic IOC) carries no information beyond
    the frequencies.

    Args:
        data: Observed sequence
        rng: Injected random source

    Returns:
        A new list holding the same symbols in random order
    """
    out = list(data)
    rng.shuffle(out)
    return out


def no_doublet_shuffle(data: Sequence[T], rng: random.Random) -> list[T]:
    """Return a random arrangement of the observed symbols with no doublets.

    Preserves the exact multiset and forbids two equal symbols in adjacent
    positions. This is the rate = 0 case of doublet_shuffle.

    Args:
        data: Observed sequence
        rng: Injected random source

    Returns:
        A new list with the same symbols and no equal adjacent pair

    Raises:
        InvalidInputError: If no doublet-free arrangement exists, i.e. the most
            frequent symbol occurs more than ceil(len(data) / 2) times
    """
    return _doublet_fill(data, rng, 0.0)


def doublet_shuffle(rate: float) -> NullModel[T]:
    """Build a frequency-exact null targeting a given adjacent-doublet rate.

    The returned resampler preserves the exact multiset and reproduces, in
    expectation, a target fraction of equal adjacent symbols. rate = 0 forbids
    doublets entirely; the frequency-matched chance rate (the sum of squared
    symbol frequencies) leaves them unsuppressed. The rate is hit approximately,
    by down-weighting the just-placed symbol relative to that chance rate, so a
    surrogate matches the observed frequencies and doublet rate while
    randomizing everything else.

    Args:
        rate: Target fraction of adjacent positions holding equal symbols

    Returns:
        A null model whose surrogates approximate the target doublet rate
    """

    def model(data: Sequence[T], rng: random.Random) -> list[T]:
        counts = Counter(data)
        n = len(data)
        chance = sum((count / n) ** 2 for count in counts.values()) if n else 0.0
        factor = rate / chance if chance > 0 else 0.0
        return _doublet_fill(data, rng, factor)

    return model


def _doublet_fill(data: Sequence[T], rng: random.Random, factor: float) -> list[T]:
    """Fill positions left to right, down-weighting the previous symbol by factor.

    Weighting each choice by the symbol's remaining count keeps surrogates
    representative rather than a single greedy arrangement. A symbol whose count
    exceeds half the remaining slots would strand, so it must be placed now.
    With factor = 0 the previous symbol is never chosen freely and, since the
    forced symbol is never the previous one for a feasible multiset, no doublet
    forms; larger factors admit doublets in proportion to factor.
    """
    counts = Counter(data)
    n = len(data)
    if factor == 0.0 and counts and max(counts.values()) > (n + 1) // 2:
        msg = "no doublet-free arrangement exists: a symbol exceeds ceil(n/2)"
        raise InvalidInputError(msg)

    remaining = dict(counts)
    out: list[T] = []
    previous: T | None = None
    for slots in range(n, 0, -1):
        forced = [s for s, count in remaining.items() if count > slots // 2]
        if forced:
            chosen = forced[0]
        else:
            candidates: list[T] = []
            weights: list[float] = []
            for symbol, count in remaining.items():
                if count == 0:
                    continue
                weight = count * (factor if symbol == previous else 1.0)
                if weight > 0:
                    candidates.append(symbol)
                    weights.append(weight)
            chosen = _weighted_choice(candidates, weights, rng)
        out.append(chosen)
        remaining[chosen] -= 1
        previous = chosen
    return out


def _weighted_choice(items: list[T], weights: Sequence[float], rng: random.Random) -> T:
    """Pick an item with probability proportional to its weight."""
    target = rng.random() * sum(weights)
    cumulative = 0.0
    for item, weight in zip(items, weights):
        cumulative += weight
        if target < cumulative:
            return item
    return items[-1]
