# ABOUTME: An order-k Markov model over any alphabet, fitted from a training sequence
# ABOUTME: or built from stated transition weights, that samples fresh sequences.
"""Markov text models.

A simulation argument, "this cipher over language-like text would give these
statistics", needs a source of language-like text. A MarkovModel holds, for
every context of k symbols, a distribution over the next symbol, and samples
sequences of any length from an injected random source. `fit_markov` learns
one from a training sequence; the constructor takes stated weights, so a
chain with a pinned property (a doublet rate, say) is one dictionary.

A model generates. The generative null models in `stats.nulls` wrap one to
produce surrogates of an observed sequence.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Generic, TypeVar

from aldegonde.exceptions import InsufficientDataError, InvalidInputError

if TYPE_CHECKING:
    import random
    from collections.abc import Hashable, Mapping, Sequence

T = TypeVar("T", bound="Hashable")
U = TypeVar("U")


def _cumulative(weights: Mapping[U, float]) -> list[tuple[float, U]]:
    """Turn a weight mapping into a cumulative distribution over its keys."""
    if any(weight < 0 for weight in weights.values()):
        msg = "a Markov distribution holds a negative weight"
        raise InvalidInputError(msg)
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

    Attributes:
        order: Number of symbols of context
        alphabet: The symbols the model generates
    """

    def __init__(
        self,
        order: int,
        alphabet: Sequence[T],
        transitions: Mapping[tuple[T, ...], Mapping[T, float]],
        starts: Mapping[tuple[T, ...], float] | None = None,
    ) -> None:
        """Build a model from stated weights.

        Args:
            order: Number of symbols of context, at least 1
            alphabet: The symbols the model generates
            transitions: For each context of `order` symbols, the relative
                weight of each next symbol; any positive scale works
            starts: Relative weight of each starting context; every context
                equally when omitted

        Raises:
            InvalidInputError: If order is not positive, the alphabet is
                empty, a context has the wrong length, a weight is negative,
                or a distribution has no positive weight
        """
        if order < 1:
            msg = f"order must be positive, got {order}"
            raise InvalidInputError(msg)
        if not alphabet:
            msg = "alphabet must not be empty"
            raise InvalidInputError(msg)
        if not transitions:
            msg = "transitions must hold at least one context"
            raise InvalidInputError(msg)
        for context in transitions:
            if len(context) != order:
                msg = f"context {context!r} does not have {order} symbols"
                raise InvalidInputError(msg)
        self.order = order
        self.alphabet = list(alphabet)
        self._rows = {
            context: _cumulative(weights) for context, weights in transitions.items()
        }
        if starts is None:
            starts = dict.fromkeys(transitions, 1.0)
        self._starts = _cumulative(starts)

    def sample(self, length: int, rng: random.Random) -> list[T]:
        """Sample a sequence of the given length.

        A context the model has no row for restarts the chain from a
        starting context.

        Args:
            length: Number of symbols to generate
            rng: Random source

        Returns:
            The generated symbols

        Raises:
            InvalidInputError: If length is negative
        """
        if length < 0:
            msg = f"length must be non-negative, got {length}"
            raise InvalidInputError(msg)
        out: list[T] = []
        if length == 0:
            return out
        context: tuple[T, ...] = _draw(self._starts, rng)
        out.extend(context[:length])
        while len(out) < length:
            row = self._rows.get(context)
            if row is None:
                context = _draw(self._starts, rng)
                out.extend(context[: length - len(out)])
                continue
            symbol = _draw(row, rng)
            out.append(symbol)
            context = (*context[1:], symbol)
        return out


def fit_markov(
    training: Sequence[T],
    order: int,
    alphabet: Sequence[T] | None = None,
    smoothing: float = 0.0,
) -> MarkovModel[T]:
    """Fit an order-k model to a training sequence.

    Args:
        training: Sequence to learn the transition counts from
        order: Number of symbols of context; 1 is a bigram model
        alphabet: Symbols to smooth over; the symbols seen when omitted
        smoothing: Pseudo-count added for every next symbol, so unseen
            transitions stay possible

    Returns:
        The fitted model, with starting contexts weighted by how often they
        occur

    Raises:
        InvalidInputError: If order is not positive or smoothing is negative
        InsufficientDataError: If the training sequence has no more than
            `order` symbols
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
    symbols = list(alphabet) if alphabet is not None else list(dict.fromkeys(training))
    counts: dict[tuple[T, ...], Counter[T]] = {}
    starts: Counter[tuple[T, ...]] = Counter()
    for i in range(len(training) - order):
        context = tuple(training[i : i + order])
        counts.setdefault(context, Counter())[training[i + order]] += 1
        starts[context] += 1
    transitions = {
        context: {symbol: seen.get(symbol, 0) + smoothing for symbol in symbols}
        for context, seen in counts.items()
    }
    return MarkovModel(order, symbols, transitions, dict(starts))
