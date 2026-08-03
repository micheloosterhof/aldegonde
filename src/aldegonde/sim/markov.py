# ABOUTME: Markov text generation from fitted or supplied n-gram counts, plus
# ABOUTME: cutting a stream into words by an empirical length distribution.
"""Language-like text generation for statistical controls.

A simulation-based argument — "this cipher over natural language would
produce these statistics" — needs a source of language-like plaintext. This
module fits an order-k Markov model to an n-gram count table (or a training
sequence) and samples fresh sequences from it, so a control corpus can be
generated at any length over any alphabet. `cut_by_lengths` then segments a
generated stream into words drawn from an empirical word-length
distribution, reproducing the token structure the boundary-aware statistics
need.

This is generation, not a null model: use it to build a control corpus,
then run the same analysis on it as on the real ciphertext. For a
resampling null of an observed sequence, see `stats.nulls`.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Generic, TypeVar

from aldegonde.exceptions import InsufficientDataError, InvalidInputError

if TYPE_CHECKING:
    import random
    from collections.abc import Mapping, Sequence

T = TypeVar("T")
U = TypeVar("U")


def _cumulative(weights: Mapping[U, float]) -> list[tuple[float, U]]:
    """Turn a weight mapping into a cumulative distribution over its keys."""
    total = sum(weights.values())
    if total <= 0:
        msg = "a Markov distribution has no positive weight"
        raise InvalidInputError(msg)
    cumulative: list[tuple[float, U]] = []
    running = 0.0
    for symbol, weight in weights.items():
        running += weight / total
        cumulative.append((running, symbol))
    return cumulative


def _draw(cumulative: list[tuple[float, U]], rng: random.Random) -> U:
    """Draw one key from a cumulative distribution."""
    target = rng.random()
    for bound, symbol in cumulative:
        if target < bound:
            return symbol
    return cumulative[-1][1]


class MarkovModel(Generic[T]):
    """An order-k Markov model over a fixed alphabet.

    Holds, for each length-k context, a cumulative distribution over next
    symbols, plus a distribution over starting contexts. Sampling is a pure
    function of an injected random source.
    """

    def __init__(
        self,
        order: int,
        alphabet: Sequence[T],
        transitions: Mapping[tuple[T, ...], Mapping[T, float]],
        starts: Mapping[tuple[T, ...], float],
    ) -> None:
        self.order = order
        self.alphabet = list(alphabet)
        self._rows = {
            context: _cumulative(weights) for context, weights in transitions.items()
        }
        self._start_cumulative = _cumulative(starts)

    def sample(self, length: int, rng: random.Random) -> list[T]:
        """Sample a sequence of the given length from the model.

        Args:
            length: Number of symbols to generate
            rng: Injected random source

        Returns:
            A generated sequence of alphabet symbols

        Raises:
            InvalidInputError: If length is negative
        """
        if length < 0:
            msg = f"length must be non-negative, got {length}"
            raise InvalidInputError(msg)
        if length == 0:
            return []
        context: tuple[T, ...] = _draw(self._start_cumulative, rng)
        out = list(context[:length])
        while len(out) < length:
            row = self._rows.get(context)
            if row is None:
                # unseen context: restart from a random starting context
                context = _draw(self._start_cumulative, rng)
                out.extend(context[: length - len(out)])
                continue
            nxt = _draw(row, rng)
            out.append(nxt)
            context = (*context[1:], nxt)
        return out[:length]


def fit_markov(
    training: Sequence[T],
    order: int,
    alphabet: Sequence[T] | None = None,
    smoothing: float = 0.0,
) -> MarkovModel[T]:
    """Fit an order-k Markov model to a training sequence.

    Args:
        training: Sequence to learn transition counts from
        order: Context length k (order 1 is a bigram model)
        alphabet: Alphabet to smooth over; the symbols seen when omitted
        smoothing: Add-`smoothing` pseudo-count for every next symbol,
            keeping unseen transitions possible

    Returns:
        A fitted MarkovModel

    Raises:
        InvalidInputError: If order is not positive or smoothing is negative
        InsufficientDataError: If the training sequence is shorter than the
            order plus one
    """
    if order < 1:
        msg = f"order must be positive, got {order}"
        raise InvalidInputError(msg)
    if smoothing < 0:
        msg = f"smoothing must be non-negative, got {smoothing}"
        raise InvalidInputError(msg)
    if len(training) < order + 1:
        msg = f"need more than {order} symbols to fit an order-{order} model"
        raise InsufficientDataError(msg, order + 1, len(training))
    symbols = (
        list(alphabet)
        if alphabet is not None
        else list(dict.fromkeys(training))  # stable unique, no ordering needed
    )
    transitions: dict[tuple[T, ...], Counter[T]] = {}
    starts: Counter[tuple[T, ...]] = Counter()
    for i in range(len(training) - order):
        context = tuple(training[i : i + order])
        nxt = training[i + order]
        transitions.setdefault(context, Counter())[nxt] += 1
        starts[context] += 1
    weighted: dict[tuple[T, ...], dict[T, float]] = {}
    for context, counts in transitions.items():
        weighted[context] = {
            symbol: counts.get(symbol, 0) + smoothing for symbol in symbols
        }
    return MarkovModel(order, symbols, weighted, dict(starts))


def generate(model: MarkovModel[T], length: int, rng: random.Random) -> list[T]:
    """Sample a sequence of the given length from a fitted model."""
    return model.sample(length, rng)


def cut_by_lengths(
    stream: Sequence[T],
    length_distribution: Mapping[int, float],
    rng: random.Random,
) -> list[list[T]]:
    """Cut a stream into words drawn from an empirical length distribution.

    Word lengths are sampled from the given distribution until the stream is
    consumed; the final word is whatever remains, so no symbols are lost.

    Args:
        stream: Symbol stream to segment
        length_distribution: Mapping from word length to relative weight
        rng: Injected random source

    Returns:
        The stream cut into words

    Raises:
        InvalidInputError: If the distribution is empty, has a non-positive
            length, or has no positive weight
    """
    if not length_distribution:
        msg = "length_distribution must not be empty"
        raise InvalidInputError(msg)
    lengths = list(length_distribution)
    weights = [length_distribution[length] for length in lengths]
    if any(length < 1 for length in lengths):
        msg = "word lengths must be positive"
        raise InvalidInputError(msg)
    if sum(weights) <= 0:
        msg = "length_distribution has no positive weight"
        raise InvalidInputError(msg)
    words: list[list[T]] = []
    position = 0
    n = len(stream)
    while position < n:
        length = rng.choices(lengths, weights=weights, k=1)[0]
        words.append(list(stream[position : position + length]))
        position += length
    return words
