# ABOUTME: Extremal bounds on substitution-induced statistics: the min/max
# ABOUTME: diagonal (doublet) rate any permutation can produce for a language.
"""Extremal diagonal-rate bounds for monoalphabetic substitution steps.

Given a matrix of adjacent-pair weights (a bigram count matrix of the
plaintext language), a substitution step g exposes a doublet exactly where a
pair (x, y) has y == g(x): the doublet rate it induces is the fraction of
pair mass lying on the graph of g. Optimizing that mass over all
permutations is an assignment problem, so the Hungarian algorithm yields the
provable minimum and maximum doublet rate any monoalphabetic step can
produce for the given language.

These are cipher-independent bounds for refuting mechanism classes: if an
observed doublet rate falls below the minimum, no substitution step over
that language explains it, whatever the key. The same bound applies to any
pair-weight matrix and lag, not only adjacent bigrams.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, TypeVar

import numpy as np
from scipy.optimize import linear_sum_assignment

from aldegonde.exceptions import InsufficientDataError, InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


def pair_counts(
    text: Sequence[T],
    alphabet: Sequence[T],
    lag: int = 1,
) -> list[list[int]]:
    """Count ordered symbol pairs at a lag into an alphabet-indexed matrix.

    Args:
        text: Sequence to analyze
        alphabet: The alphabet fixing the index of every symbol
        lag: Distance between the paired symbols

    Returns:
        A matrix with entry [i][j] counting positions where alphabet[i] is
        followed at distance lag by alphabet[j]

    Raises:
        InvalidInputError: If lag is not positive or a symbol is missing
            from the alphabet
    """
    if lag < 1:
        msg = f"lag must be positive, got {lag}"
        raise InvalidInputError(msg)
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    matrix = [[0] * len(alphabet) for _ in alphabet]
    for i in range(len(text) - lag):
        try:
            matrix[index[text[i]]][index[text[i + lag]]] += 1
        except KeyError as exc:
            msg = f"symbol {exc.args[0]!r} not in alphabet"
            raise InvalidInputError(msg) from exc
    return matrix


def diagonal_rate(
    matrix: Sequence[Sequence[float]],
    perm: Sequence[int],
) -> float:
    """Return the fraction of pair mass a permutation puts on its graph.

    This is the doublet rate a substitution step with permutation `perm`
    exposes when the pair weights describe the plaintext: the mass at
    (x, perm[x]) summed over x, over the total mass.

    Args:
        matrix: Pair-weight matrix, e.g. from `pair_counts`
        perm: Permutation in index form (see `aldegonde.perm`)

    Returns:
        The diagonal mass fraction, 0.0 when the matrix is empty

    Raises:
        InvalidInputError: If the permutation size differs from the matrix
    """
    if len(perm) != len(matrix):
        msg = f"permutation size {len(perm)} != matrix size {len(matrix)}"
        raise InvalidInputError(msg)
    total = sum(sum(row) for row in matrix)
    if total == 0:
        return 0.0
    return sum(matrix[x][perm[x]] for x in range(len(perm))) / total


class DiagonalBound(NamedTuple):
    """An extremal diagonal rate and a permutation attaining it.

    Attributes:
        rate: The extremal diagonal mass fraction
        perm: A permutation in index form attaining it
    """

    rate: float
    perm: list[int]


def extremal_diagonal_rate(
    matrix: Sequence[Sequence[float]],
    *,
    maximize: bool = False,
) -> DiagonalBound:
    """Return the minimum (or maximum) diagonal rate over all permutations.

    Solves the assignment problem on the pair-weight matrix, so the bound is
    exact and holds over the full symmetric group — not merely over the keys
    some search visited. An observed doublet rate below the minimum refutes
    every monoalphabetic substitution step over this language at once; a
    cycle-type-restricted key class can only do worse than this bound, never
    better.

    Args:
        matrix: Pair-weight matrix, e.g. from `pair_counts`
        maximize: Return the maximum achievable rate instead of the minimum

    Returns:
        The extremal rate and a permutation attaining it

    Raises:
        InsufficientDataError: If the matrix is empty or holds no mass
    """
    if len(matrix) == 0:
        msg = "extremal_diagonal_rate needs a non-empty matrix"
        raise InsufficientDataError(msg, 1, 0)
    weights = np.asarray(matrix, dtype=float)
    total = float(weights.sum())
    if total == 0:
        msg = "extremal_diagonal_rate needs positive total pair mass"
        raise InsufficientDataError(msg, 1, 0)
    rows, columns = linear_sum_assignment(weights, maximize=maximize)
    perm = [0] * len(matrix)
    for row, column in zip(rows.tolist(), columns.tolist()):
        perm[row] = column
    return DiagonalBound(
        rate=float(weights[rows, columns].sum()) / total,
        perm=perm,
    )
