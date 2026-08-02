# ABOUTME: Null-hypothesis resamplers that turn an observed sequence into
# ABOUTME: surrogate sequences preserving chosen nuisance structure.
"""Null models for resampling-based significance testing.

A null model is a resampler: given the observed sequence and an injected
random source, it returns a surrogate sequence drawn under a null hypothesis
that preserves some nuisance structure (frequencies, doublet rate, ...) and
randomizes everything else. Comparing an observed statistic against the
distribution of the same statistic over many surrogates isolates the
structure the null does not contain.

Two families are implemented. The shuffle family preserves the exact
multiset of symbols of the observed sequence:

    shuffle             exact unigram frequencies, order destroyed
    no_doublet_shuffle  exact frequencies and no adjacent equal symbols
    doublet_shuffle     exact frequencies at a chosen adjacent-doublet rate

The generative family draws fresh symbols from a first-order Markov chain,
matching the observed sequence only in length. This is the standard
surrogate-data construction for "my corpus has a known bigram-level nuisance
property; the null must carry it or every downstream scan lies":

    markov_model        surrogates from an explicit transition matrix
    fitted_markov       transitions fitted to the observed sequence
    doublet_markov      uniform marginals with a pinned self-transition rate

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

    symbols = list(counts)
    remaining = dict(counts)
    draw = rng.random
    out: list[T] = []
    previous: T | None = None
    for slots in range(n, 0, -1):
        half = slots // 2
        # One pass over the alphabet: total candidate weight, and the at-most-one
        # symbol whose remaining count forces it to be placed now
        total = 0.0
        forced: T | None = None
        for symbol in symbols:
            count = remaining[symbol]
            if count > half:
                forced = symbol
                break
            if count:
                total += count * (factor if symbol == previous else 1.0)
        if forced is not None:
            chosen: T = forced
        else:
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


def _cumulative_rows(
    alphabet: Sequence[T],
    transitions: dict[T, list[float]],
) -> dict[T, list[float]]:
    """Normalize each transition row into a cumulative distribution."""
    rows: dict[T, list[float]] = {}
    for symbol, weights in transitions.items():
        total = sum(weights)
        if total <= 0:
            msg = f"transition row for {symbol!r} has no positive weight"
            raise InvalidInputError(msg)
        cumulative: list[float] = []
        running = 0.0
        for weight in weights:
            if weight < 0:
                msg = f"negative transition weight in row for {symbol!r}"
                raise InvalidInputError(msg)
            running += weight / total
            cumulative.append(running)
        cumulative[-1] = 1.0
        rows[symbol] = cumulative
    return rows


def _draw(alphabet: Sequence[T], cumulative: list[float], rng: random.Random) -> T:
    """Draw one symbol from a cumulative distribution over the alphabet."""
    target = rng.random()
    for i, bound in enumerate(cumulative):
        if target < bound:
            return alphabet[i]
    return alphabet[-1]


def _generate_chain(
    alphabet: Sequence[T],
    rows: dict[T, list[float]],
    initial: list[float],
    length: int,
    rng: random.Random,
) -> list[T]:
    """Generate a sequence from a first-order chain in cumulative form."""
    out: list[T] = []
    if length == 0:
        return out
    previous = _draw(alphabet, initial, rng)
    out.append(previous)
    for _ in range(length - 1):
        previous = _draw(alphabet, rows[previous], rng)
        out.append(previous)
    return out


def markov_model(
    alphabet: Sequence[T],
    transitions: dict[T, Sequence[float]],
    initial: Sequence[float] | None = None,
) -> NullModel[T]:
    """Build a generative null from an explicit first-order Markov chain.

    Surrogates are drawn fresh from the chain and match the observed sequence
    only in length — unlike the shuffle family, the symbol multiset is not
    preserved. Use this when the null hypothesis is a *process* ("text whose
    only structure is these transition rates") rather than a rearrangement of
    the observed symbols.

    Args:
        alphabet: The alphabet; row weights are indexed in this order
        transitions: Weight row per symbol; each row is normalized, so any
            positive scale works
        initial: Weights for the first symbol; uniform when omitted

    Returns:
        A null model generating length-matched surrogates from the chain

    Raises:
        InvalidInputError: If the alphabet is empty, a row is missing or the
            wrong size, or any weight is negative or a row sums to zero
    """
    if not alphabet:
        msg = "alphabet must not be empty"
        raise InvalidInputError(msg)
    for symbol in alphabet:
        if symbol not in transitions:
            msg = f"transition row missing for symbol {symbol!r}"
            raise InvalidInputError(msg)
        if len(transitions[symbol]) != len(alphabet):
            msg = f"transition row for {symbol!r} has wrong size"
            raise InvalidInputError(msg)
    rows = _cumulative_rows(
        alphabet, {symbol: list(row) for symbol, row in transitions.items()}
    )
    start_weights = list(initial) if initial is not None else [1.0] * len(alphabet)
    if len(start_weights) != len(alphabet):
        msg = "initial distribution has wrong size"
        raise InvalidInputError(msg)
    start = _cumulative_rows(alphabet, {alphabet[0]: start_weights})[alphabet[0]]

    def model(data: Sequence[T], rng: random.Random) -> list[T]:
        return _generate_chain(alphabet, rows, start, len(data), rng)

    return model


def fitted_markov(alphabet: Sequence[T], smoothing: float = 1.0) -> NullModel[T]:
    """Build a generative null fitting the chain to the observed sequence.

    Each call fits add-`smoothing` smoothed first-order transition counts and
    the unigram distribution to the observed sequence, then generates a fresh
    surrogate from that chain. This is the order-1 surrogate standard in
    surrogate-data testing: it preserves the observed bigram statistics in
    expectation and randomizes all longer-range structure.

    Args:
        alphabet: The alphabet the chain runs over
        smoothing: Pseudo-count added to every transition cell, keeping
            unseen transitions possible

    Returns:
        A null model generating length-matched surrogates from the fitted
        chain

    Raises:
        InvalidInputError: If the alphabet is empty or smoothing is negative
    """
    if not alphabet:
        msg = "alphabet must not be empty"
        raise InvalidInputError(msg)
    if smoothing < 0:
        msg = f"smoothing must be non-negative, got {smoothing}"
        raise InvalidInputError(msg)
    index = {symbol: i for i, symbol in enumerate(alphabet)}

    def model(data: Sequence[T], rng: random.Random) -> list[T]:
        counts = {symbol: [smoothing] * len(alphabet) for symbol in alphabet}
        marginal = [smoothing] * len(alphabet)
        for symbol in data:
            marginal[index[symbol]] += 1.0
        for a, b in zip(data, data[1:]):
            counts[a][index[b]] += 1.0
        rows = _cumulative_rows(alphabet, counts)
        start = _cumulative_rows(alphabet, {alphabet[0]: marginal})[alphabet[0]]
        return _generate_chain(alphabet, rows, start, len(data), rng)

    return model


def doublet_markov(alphabet: Sequence[T], rate: float) -> NullModel[T]:
    """Build a generative null with a pinned self-transition (doublet) rate.

    Each symbol repeats the previous one with probability `rate` and is
    otherwise uniform over the remaining alphabet; marginals stay uniform.
    This is the null for text whose only known structure is a suppressed (or
    enhanced) adjacent-repeat rate: rate = 1/alphabetsize recovers uniform
    random text, smaller rates model doublet suppression. Statistics judged
    against a uniform null on such text produce artifacts; this null holds
    the doublet rate fixed so only structure beyond it can score.

    Args:
        alphabet: The alphabet to generate over
        rate: Probability that a symbol equals its predecessor

    Returns:
        A null model generating length-matched surrogates at the pinned rate

    Raises:
        InvalidInputError: If the alphabet has fewer than 2 symbols or rate
            is outside [0, 1]
    """
    if len(alphabet) < 2:
        msg = "doublet_markov needs at least 2 symbols"
        raise InvalidInputError(msg)
    if not 0.0 <= rate <= 1.0:
        msg = f"rate must be in [0, 1], got {rate}"
        raise InvalidInputError(msg)
    other = (1.0 - rate) / (len(alphabet) - 1)
    transitions = {
        symbol: [rate if candidate == symbol else other for candidate in alphabet]
        for symbol in alphabet
    }
    return markov_model(alphabet, {s: list(row) for s, row in transitions.items()})
