# ABOUTME: Pair tables of symbols a fixed distance apart inside words, the share of
# ABOUTME: pairs that satisfy a permutation relation, and that share's exact extremes.
"""Pair tables and relation rates.

A pair table counts, for every ordered pair of symbols (u, v), how often u
stands a fixed distance before v inside one word. On integer symbols it is an
N x N array indexed by the symbols themselves.

A permutation relation holds for a pair when u == perm[v]. The identity gives
the doublet rate; the lag-k relation of a progressive cipher gives the rate
at which c_i == c_(i+k) when p_i == g^k(p_(i+k)). `relation_rate` reads that
rate off a table, and `extremal_relation_rate` gives the smallest or largest
rate any permutation can reach, by solving the assignment problem. A rate
observed below the minimum refutes every permutation at once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

import numpy as np
from scipy.optimize import linear_sum_assignment

from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.validation import validate_permutation, validate_positive_integer

if TYPE_CHECKING:
    from collections.abc import Sequence


def pair_counts(
    words: Sequence[Sequence[int]],
    size: int,
    lag: int = 1,
) -> np.ndarray:
    """Count ordered symbol pairs at a lag, inside words.

    Args:
        words: Text as words of symbols 0..size-1; pass [stream] to count
            across a whole stream
        size: Alphabet size
        lag: Distance between the paired symbols

    Returns:
        An array with entry [u, v] counting positions where u stands lag
        places before v in the same word

    Raises:
        InvalidInputError: If size or lag is not a positive integer, or a
            symbol is outside 0..size-1
    """
    validate_positive_integer(size, "size")
    validate_positive_integer(lag, "lag")
    table = np.zeros((size, size), dtype=np.int64)
    for word in words:
        symbols = np.asarray(word, dtype=np.int64)
        if symbols.size and (symbols.min() < 0 or symbols.max() >= size):
            msg = f"symbol outside 0..{size - 1} in word {list(word)!r}"
            raise InvalidInputError(msg, input_value=word)
        if symbols.size > lag:
            np.add.at(table, (symbols[:-lag], symbols[lag:]), 1)
    return table


def _validate_table(table: Sequence[Sequence[float]]) -> np.ndarray:
    """Return the table as a square float array."""
    weights = np.asarray(table, dtype=float)
    if weights.ndim != 2 or weights.shape[0] != weights.shape[1]:
        msg = f"pair table must be square, got shape {weights.shape}"
        raise InvalidInputError(msg)
    return weights


def relation_rate(table: Sequence[Sequence[float]], perm: Sequence[int]) -> float:
    """Return the share of pairs (u, v) with u == perm[v].

    The identity permutation gives the doublet rate.

    Args:
        table: Pair table, as from `pair_counts`
        perm: Permutation of 0..N-1

    Returns:
        The share of all pair mass on the relation, or 0.0 for an empty table

    Raises:
        InvalidInputError: If perm is not a permutation or its size differs
            from the table
    """
    weights = _validate_table(table)
    images = validate_permutation(perm)
    if len(images) != weights.shape[0]:
        msg = (
            f"permutation size {len(images)} differs from table size {weights.shape[0]}"
        )
        raise InvalidInputError(msg)
    total = float(weights.sum())
    if total == 0:
        return 0.0
    columns = np.arange(len(images))
    return float(weights[np.asarray(images), columns].sum()) / total


class RelationBound(NamedTuple):
    """An extreme relation rate and a permutation that reaches it.

    Attributes:
        rate: The extreme share of pair mass
        perm: A permutation reaching it
    """

    rate: float
    perm: list[int]


def extremal_relation_rate(
    table: Sequence[Sequence[float]],
    *,
    maximize: bool = False,
) -> RelationBound:
    """Return the smallest, or largest, relation rate over all permutations.

    This is the assignment problem on the table, so the bound is exact over
    the whole symmetric group. A permutation restricted to a cycle type can
    only do worse than this bound, never better.

    Args:
        table: Pair table, as from `pair_counts`
        maximize: Return the largest rate instead of the smallest

    Returns:
        The extreme rate and a permutation reaching it

    Raises:
        InvalidInputError: If the table is not square
        InsufficientDataError: If the table is empty or holds no mass
    """
    if np.asarray(table, dtype=float).size == 0:
        msg = "extremal_relation_rate needs a non-empty table"
        raise InsufficientDataError(msg, required_length=1, actual_length=0)
    weights = _validate_table(table)
    total = float(weights.sum())
    if total == 0:
        msg = "extremal_relation_rate needs positive total pair mass"
        raise InsufficientDataError(msg, required_length=1, actual_length=0)
    # the relation puts mass at (perm[v], v), so assign a row to each column
    rows, columns = linear_sum_assignment(weights.T, maximize=maximize)
    perm = [0] * weights.shape[0]
    for column, row in zip(rows.tolist(), columns.tolist()):
        perm[column] = row
    return RelationBound(rate=float(weights.T[rows, columns].sum()) / total, perm=perm)
