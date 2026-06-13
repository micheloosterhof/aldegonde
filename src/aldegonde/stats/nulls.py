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

Randomness is injected as a random.Random so a seeded run is reproducible and
trials are independent; the resampler is a pure function of (data, rng).
"""

from __future__ import annotations

import heapq
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
    positions. This is the frequency-matched, doublet-suppressed null: it
    holds frequencies fixed while removing the adjacency structure, so a
    surviving signal is order structure beyond nearest-neighbour suppression.

    Args:
        data: Observed sequence
        rng: Injected random source

    Returns:
        A new list with the same symbols and no equal adjacent pair

    Raises:
        InvalidInputError: If no doublet-free arrangement exists, i.e. the most
            frequent symbol occurs more than ceil(len(data) / 2) times
    """
    counts = Counter(data)
    n = len(data)
    if counts and max(counts.values()) > (n + 1) // 2:
        msg = "no doublet-free arrangement exists: a symbol exceeds ceil(n/2)"
        raise InvalidInputError(msg)

    # Max-heap on remaining count, with a random tie-break so equally frequent
    # symbols arrange differently across seeds. The just-placed symbol is held
    # aside for one step so it cannot be chosen again immediately; feasibility
    # guarantees the heap is never empty while a symbol is still held.
    heap: list[tuple[int, float, T]] = [
        (-count, rng.random(), symbol) for symbol, count in counts.items()
    ]
    heapq.heapify(heap)

    out: list[T] = []
    held: tuple[int, float, T] | None = None
    while heap:
        neg_count, _, symbol = heapq.heappop(heap)
        out.append(symbol)
        if held is not None:
            heapq.heappush(heap, held)
            held = None
        remaining = -neg_count - 1
        if remaining > 0:
            held = (-remaining, rng.random(), symbol)
    return out
