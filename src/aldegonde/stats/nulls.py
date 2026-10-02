# ABOUTME: Null-hypothesis resamplers that turn an observed sequence into
# ABOUTME: surrogate sequences preserving chosen nuisance structure.
"""Null models for resampling-based significance testing.

A null model is a resampler: given the observed sequence and an injected
random source, it returns a surrogate sequence drawn under a null hypothesis
that preserves some nuisance structure (frequencies, doublet rate, ...) and
randomizes everything else. Comparing an observed statistic against the
distribution of the same statistic over many surrogates isolates the
structure the null does not contain.

The shuffle nulls preserve the exact multiset of symbols:

    shuffle             exact unigram frequencies, order destroyed
    no_doublet_shuffle  exact frequencies and no adjacent equal symbols
    doublet_shuffle     exact frequencies at a chosen adjacent-doublet rate

The generative nulls draw each surrogate fresh from a Markov model, so only
the length is preserved:

    markov_null         any model from `stats.markov`
    fitted_markov       an order-k model fitted to the observed sequence
    doublet_markov      uniform marginals with a pinned adjacent-doublet rate

Randomness is injected as a random.Random so a seeded run is reproducible and
trials are independent; the resampler is a pure function of (data, rng).
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Callable, Hashable, Sequence
from typing import TypeVar

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.markov import MarkovModel, fit_markov

T = TypeVar("T", bound=Hashable)

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

    symbols = list(counts)
    remaining = dict(counts)
    draw = rng.random
    out: list[T] = []
    previous: T | None = None
    # `bound` is an UPPER bound on the largest remaining count, refreshed to the
    # exact value whenever it is consulted. Counts only fall, so a stale bound
    # can only be too high, which costs an extra scan but can never miss a
    # symbol that must be placed now.
    bound = max(remaining.values())
    for slots in range(n, 0, -1):
        half = slots // 2
        forced: T | None = None
        if bound > half:
            # only here is a pass over the alphabet needed, and only near the end
            bound = 0
            for symbol in symbols:
                count = remaining[symbol]
                bound = max(bound, count)
                if count > half:
                    forced = symbol
        if forced is not None:
            chosen: T = forced
        else:
            # The candidate weight has a closed form: remaining counts sum to the
            # slots left, so down-weighting one symbol subtracts a known amount.
            # That removes a second pass over the alphabet at every position.
            total = float(slots)
            if previous is not None:
                total -= remaining[previous] * (1.0 - factor)
            # Weighted pick proportional to remaining count, down-weighting the
            # previous symbol by factor; equivalent to a cumulative-weight scan
            target = draw() * total
            cumulative = 0.0
            chosen = symbols[-1]
            for symbol in symbols:
                count = remaining[symbol]
                if not count:
                    continue
                weight = count * (factor if symbol == previous else 1.0)
                if weight <= 0:
                    continue
                chosen = symbol
                cumulative += weight
                if target < cumulative:
                    break
        out.append(chosen)
        remaining[chosen] -= 1
        previous = chosen
    return out


def markov_null(model: MarkovModel[T]) -> NullModel[T]:
    """Build a generative null from a Markov model.

    Each surrogate is drawn fresh from the model and matches the observed
    sequence in length only; the symbol multiset is not preserved. This is
    the null for a hypothesis stated as a process, "text whose only structure
    is these transition rates", where the shuffle family states it as a
    rearrangement of the observed symbols.

    Args:
        model: The model to draw surrogates from

    Returns:
        A null model generating length-matched surrogates
    """

    def null(data: Sequence[T], rng: random.Random) -> list[T]:
        return model.sample(len(data), rng)

    return null


def fitted_markov(
    order: int = 1,
    smoothing: float = 1.0,
    alphabet: Sequence[T] | None = None,
) -> NullModel[T]:
    """Build a generative null that fits a Markov model to the observed sequence.

    Every call fits an order-k model to the data it is given and samples a
    surrogate from it, so the surrogates share the observed n-gram statistics
    in expectation and nothing of longer range.

    Args:
        order: Number of symbols of context
        smoothing: Pseudo-count added for every next symbol
        alphabet: Symbols to smooth over; the symbols seen when omitted

    Returns:
        A null model generating length-matched surrogates from the fitted
        chain

    Raises:
        InvalidInputError: If order is not positive or smoothing is negative
    """
    if order < 1:
        msg = f"order must be positive, got {order}"
        raise InvalidInputError(msg)
    if smoothing < 0:
        msg = f"smoothing must be non-negative, got {smoothing}"
        raise InvalidInputError(msg)

    def null(data: Sequence[T], rng: random.Random) -> list[T]:
        return fit_markov(data, order, alphabet, smoothing).sample(len(data), rng)

    return null


def doublet_markov(alphabet: Sequence[T], rate: float) -> NullModel[T]:
    """Build a generative null with a pinned adjacent-doublet rate.

    Each symbol repeats its predecessor with probability `rate` and is
    otherwise uniform over the rest of the alphabet, so the marginals stay
    uniform. rate = 1/N gives uniform random text; a smaller rate models
    doublet suppression. Statistics judged against a uniform null on such
    text show artifacts; this null holds the doublet rate fixed so only
    structure beyond it can score.

    Args:
        alphabet: The symbols to generate
        rate: Probability that a symbol equals its predecessor

    Returns:
        A null model generating length-matched surrogates at that rate

    Raises:
        InvalidInputError: If the alphabet has fewer than 2 symbols or the
            rate is outside [0, 1]
    """
    if len(alphabet) < 2:
        msg = "doublet_markov needs at least 2 symbols"
        raise InvalidInputError(msg)
    if not 0.0 <= rate <= 1.0:
        msg = f"rate must be between 0 and 1, got {rate}"
        raise InvalidInputError(msg)
    other = (1.0 - rate) / (len(alphabet) - 1)
    transitions: dict[tuple[T, ...], dict[T, float]] = {
        (symbol,): {
            candidate: rate if candidate == symbol else other for candidate in alphabet
        }
        for symbol in alphabet
    }
    return markov_null(MarkovModel(1, alphabet, transitions))
