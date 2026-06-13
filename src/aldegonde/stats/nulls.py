# ABOUTME: Null-hypothesis resamplers that turn an observed sequence into
# ABOUTME: surrogate sequences preserving chosen nuisance structure.
"""Null models for resampling-based significance testing.

A null model is a resampler: given the observed sequence and an injected
random source, it returns a surrogate sequence drawn under a null hypothesis
that preserves some nuisance structure (frequencies, digraphs, ...) and
randomizes everything else. Comparing an observed statistic against the
distribution of the same statistic over many surrogates isolates the
structure the null does not contain.

The ladder of nulls these implement:

    shuffle             exact unigram frequencies, order destroyed
    no_doublet_shuffle  exact frequencies and no adjacent equal symbols
    markov1             first-order transition structure (doublet rate included)

All resamplers are alphabet-agnostic in their values; markov-based models take
the alphabet explicitly so estimation never re-infers it per surrogate (a
surrogate that happens to omit a rare symbol must still share the observed
alphabet, or downstream normalization drifts).

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

TransitionMatrix = Sequence[Sequence[float]]
"""Row-stochastic matrix indexed by alphabet position: P(next=j | current=i)."""


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


def unigram_distribution(
    data: Sequence[T],
    alphabet: Sequence[T],
    *,
    smoothing: float = 0.0,
) -> list[float]:
    """Return the symbol frequencies of data as a distribution over alphabet.

    Args:
        data: Observed sequence
        alphabet: The full symbol set, fixing the output order
        smoothing: Pseudo-count added to every symbol before normalizing

    Returns:
        A probability distribution over the alphabet positions
    """
    counts = Counter(data)
    weights = [counts.get(symbol, 0) + smoothing for symbol in alphabet]
    total = sum(weights)
    if total == 0:
        size = len(alphabet)
        return [1.0 / size for _ in alphabet]
    return [w / total for w in weights]


def estimate_transitions(
    data: Sequence[T],
    alphabet: Sequence[T],
    *,
    smoothing: float = 0.0,
) -> list[list[float]]:
    """Estimate a first-order transition matrix over a fixed alphabet.

    Counts adjacent pairs in data and normalizes each row to a probability
    distribution. Smoothing adds a pseudo-count to every transition before
    normalizing, shrinking the estimate toward uniform; this matters on short
    sequences where an unsmoothed matrix overfits and a surrogate sampled from
    it reproduces the very structure being tested.

    Args:
        data: Observed sequence
        alphabet: The full symbol set, fixing the matrix index order
        smoothing: Pseudo-count added to every transition (0.0 = none)

    Returns:
        A row-stochastic transition matrix indexed by alphabet position
    """
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    size = len(alphabet)
    counts = [[smoothing] * size for _ in range(size)]
    for current, following in zip(data, data[1:]):
        counts[index[current]][index[following]] += 1

    matrix: list[list[float]] = []
    for row in counts:
        total = sum(row)
        if total == 0:
            matrix.append([1.0 / size for _ in range(size)])
        else:
            matrix.append([value / total for value in row])
    return matrix


def from_transition_matrix(
    alphabet: Sequence[T],
    matrix: TransitionMatrix,
    start: Sequence[float],
) -> NullModel[T]:
    """Build a null model that samples from a first-order Markov chain.

    The returned resampler ignores the surrogate's content and uses only the
    observed length, generating that many symbols by walking the chain from a
    symbol drawn from the start distribution. A chosen transition matrix
    expresses any first-order structure, including a suppressed doublet rate as
    a small diagonal.

    Args:
        alphabet: The symbol set, indexing the matrix and start distribution
        matrix: Row-stochastic transition matrix
        start: Initial-symbol distribution over the alphabet

    Returns:
        A null model that emits a Markov-sampled sequence of the observed length
    """
    symbols = list(alphabet)

    def model(data: Sequence[T], rng: random.Random) -> list[T]:
        n = len(data)
        if n == 0:
            return []
        index = _sample_index(start, rng)
        out = [symbols[index]]
        for _ in range(n - 1):
            index = _sample_index(matrix[index], rng)
            out.append(symbols[index])
        return out

    return model


def markov1(alphabet: Sequence[T], *, smoothing: float = 0.0) -> NullModel[T]:
    """Build a first-order Markov null estimated from the observed sequence.

    The returned resampler estimates the transition matrix from each call's
    observed sequence (over the fixed alphabet, with smoothing) and samples a
    fresh sequence of the same length. Preserves the digraph distribution in
    expectation; deviations from this null are structure beyond first order,
    which is where polyalphabetic periodicity lives.

    Args:
        alphabet: The full symbol set, fixed across surrogates
        smoothing: Pseudo-count passed to transition estimation

    Returns:
        A null model that emits a Markov-sampled sequence of the observed length
    """

    def model(data: Sequence[T], rng: random.Random) -> Sequence[T]:
        matrix = estimate_transitions(data, alphabet, smoothing=smoothing)
        start = unigram_distribution(data, alphabet, smoothing=smoothing)
        return from_transition_matrix(alphabet, matrix, start)(data, rng)

    return model


def _sample_index(weights: Sequence[float], rng: random.Random) -> int:
    """Sample an index in proportion to a weight distribution."""
    threshold = rng.random() * sum(weights)
    cumulative = 0.0
    for index, weight in enumerate(weights):
        cumulative += weight
        if threshold < cumulative:
            return index
    return len(weights) - 1
