# ABOUTME: Permutation algebra on the points 0..N-1: composition, inverse, powers,
# ABOUTME: cycle structure, conjugation, and seeded random generation.
"""Permutations of the points 0..N-1.

A permutation is a sequence p of length N where p[x] is the image of point x.
With symbols encoded as integers, a substitution alphabet is a permutation.

Composition applies the right operand first:

    compose(a, b)[x] == a[b[x]]

Every function checks that its arguments are permutations and returns a list
of integers. Any integer sequence is accepted, including a numpy array.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, TypeVar

from aldegonde.exceptions import InvalidInputError
from aldegonde.validation import (
    validate_alphabet,
    validate_permutation,
    validate_positive_integer,
)

if TYPE_CHECKING:
    import random
    from collections.abc import Collection, Hashable, Mapping, Sequence

T = TypeVar("T", bound="Hashable")


def _validate_point(point: int, size: int) -> int:
    """Return the point as an integer, rejecting one outside 0..size-1."""
    if not 0 <= point < size:
        msg = f"Point {point} is outside 0..{size - 1}"
        raise InvalidInputError(msg, input_value=point)
    return int(point)


def _validate_same_size(a: Sequence[int], b: Sequence[int]) -> None:
    """Reject two permutations that act on a different number of points."""
    if len(a) != len(b):
        msg = f"Permutations differ in size: {len(a)} and {len(b)}"
        raise InvalidInputError(msg)


def _cycles(images: Sequence[int]) -> list[list[int]]:
    """Return the cycles of a validated permutation."""
    seen = [False] * len(images)
    found: list[list[int]] = []
    for start in range(len(images)):
        if seen[start]:
            continue
        cycle = []
        point = start
        while not seen[point]:
            seen[point] = True
            cycle.append(point)
            point = images[point]
        found.append(cycle)
    return found


def identity(size: int) -> list[int]:
    """Return the permutation that maps every point to itself.

    Args:
        size: Number of points

    Returns:
        The identity on 0..size-1

    Raises:
        InvalidInputError: If size is not a positive integer
    """
    validate_positive_integer(size, "size")
    return list(range(size))


def shift(size: int, delta: int) -> list[int]:
    """Return the permutation that adds delta modulo size.

    Args:
        size: Number of points
        delta: Amount added to every point; any integer

    Returns:
        The permutation x -> (x + delta) mod size

    Raises:
        InvalidInputError: If size is not a positive integer
    """
    validate_positive_integer(size, "size")
    return [(x + delta) % size for x in range(size)]


def transposition(size: int, a: int, b: int) -> list[int]:
    """Return the permutation that swaps two points and fixes the rest.

    Args:
        size: Number of points
        a: First point
        b: Second point

    Returns:
        The permutation swapping a and b

    Raises:
        InvalidInputError: If size is not a positive integer or a point is
            outside 0..size-1
    """
    swapped = identity(size)
    a, b = _validate_point(a, size), _validate_point(b, size)
    swapped[a], swapped[b] = b, a
    return swapped


def compose(a: Sequence[int], b: Sequence[int]) -> list[int]:
    """Return the permutation that applies b, then a.

    Args:
        a: Permutation applied second
        b: Permutation applied first

    Returns:
        The permutation x -> a[b[x]]

    Raises:
        InvalidInputError: If an argument is not a permutation or the sizes
            differ
    """
    _validate_same_size(a, b)
    outer, inner = validate_permutation(a), validate_permutation(b)
    return [outer[x] for x in inner]


def inverse(perm: Sequence[int]) -> list[int]:
    """Return the permutation that undoes perm.

    Args:
        perm: Permutation to invert

    Returns:
        The permutation q with q[perm[x]] == x

    Raises:
        InvalidInputError: If perm is not a permutation
    """
    images = validate_permutation(perm)
    inverted = [0] * len(images)
    for point, image in enumerate(images):
        inverted[image] = point
    return inverted


def power(perm: Sequence[int], exponent: int) -> list[int]:
    """Return perm composed with itself exponent times.

    Args:
        perm: Permutation to raise
        exponent: Any integer; a negative exponent raises the inverse

    Returns:
        The permutation perm^exponent

    Raises:
        InvalidInputError: If perm is not a permutation
    """
    images = validate_permutation(perm)
    raised = [0] * len(images)
    for cycle in _cycles(images):
        length = len(cycle)
        for i, point in enumerate(cycle):
            raised[point] = cycle[(i + exponent) % length]
    return raised


def conjugate(perm: Sequence[int], by: Sequence[int]) -> list[int]:
    """Return perm with its points renamed by another permutation.

    The result has the cycle type of perm. Conjugating a shift by a mixed
    alphabet gives the step along that alphabet.

    Args:
        perm: Permutation to conjugate
        by: Permutation that renames the points

    Returns:
        The permutation by . perm . by^-1

    Raises:
        InvalidInputError: If an argument is not a permutation or the sizes
            differ
    """
    _validate_same_size(perm, by)
    images, renamed = validate_permutation(perm), validate_permutation(by)
    conjugated = [0] * len(images)
    for point, image in enumerate(images):
        conjugated[renamed[point]] = renamed[image]
    return conjugated


def cycles(perm: Sequence[int]) -> list[list[int]]:
    """Return the cycles of a permutation, fixed points included.

    Args:
        perm: Permutation to decompose

    Returns:
        The cycles, each starting at its smallest point, ordered by that
        point; a fixed point is a cycle of length 1

    Raises:
        InvalidInputError: If perm is not a permutation
    """
    return _cycles(validate_permutation(perm))


def cycle_type(perm: Sequence[int]) -> list[int]:
    """Return the cycle lengths of a permutation, longest first.

    Args:
        perm: Permutation to decompose

    Returns:
        The length of every cycle in descending order, fixed points included

    Raises:
        InvalidInputError: If perm is not a permutation
    """
    return sorted((len(cycle) for cycle in cycles(perm)), reverse=True)


def order(perm: Sequence[int]) -> int:
    """Return the smallest positive k with perm^k equal to the identity.

    Args:
        perm: Permutation to measure

    Returns:
        The least common multiple of the cycle lengths

    Raises:
        InvalidInputError: If perm is not a permutation
    """
    return math.lcm(*cycle_type(perm))


def parity(perm: Sequence[int]) -> int:
    """Return +1 for an even permutation and -1 for an odd one.

    A cycle of length L is L - 1 transpositions, so the sign is
    (-1) ** (N - number of cycles). The sign multiplies under composition.

    Args:
        perm: Permutation to inspect

    Returns:
        +1 or -1

    Raises:
        InvalidInputError: If perm is not a permutation
    """
    images = validate_permutation(perm)
    return 1 if (len(images) - len(_cycles(images))) % 2 == 0 else -1


def fixed_points(perm: Sequence[int]) -> list[int]:
    """Return the points a permutation maps to themselves.

    Args:
        perm: Permutation to inspect

    Returns:
        The fixed points in ascending order

    Raises:
        InvalidInputError: If perm is not a permutation
    """
    images = validate_permutation(perm)
    return [point for point, image in enumerate(images) if point == image]


def from_cycles(size: int, cycles: Sequence[Sequence[int]]) -> list[int]:
    """Return the permutation with the given cycles.

    Args:
        size: Number of points
        cycles: Disjoint cycles; each point maps to the next in its cycle and
            the last maps to the first

    Returns:
        The permutation, with every point not in a cycle fixed

    Raises:
        InvalidInputError: If size is not a positive integer, a point is
            outside 0..size-1, or a point appears twice
    """
    images = identity(size)
    seen = [False] * size
    for cycle in cycles:
        points = [_validate_point(point, size) for point in cycle]
        for i, point in enumerate(points):
            if seen[point]:
                msg = f"Point {point} appears more than once in the cycles"
                raise InvalidInputError(msg, input_value=cycles)
            seen[point] = True
            images[point] = points[(i + 1) % len(points)]
    return images


def random_permutation(size: int, rng: random.Random) -> list[int]:
    """Return a permutation drawn uniformly from all permutations.

    Args:
        size: Number of points
        rng: Random source

    Returns:
        A permutation of 0..size-1

    Raises:
        InvalidInputError: If size is not a positive integer
    """
    images = identity(size)
    rng.shuffle(images)
    return images


def random_with_cycle_type(
    size: int,
    cycle_lengths: Sequence[int],
    rng: random.Random,
    *,
    fixed: Collection[int] = (),
) -> list[int]:
    """Return a permutation drawn uniformly from those with the given cycles.

    Args:
        size: Number of points
        cycle_lengths: Length of each cycle to place
        rng: Random source
        fixed: Points that must map to themselves

    Returns:
        A permutation with one cycle per given length, on points outside
        `fixed`; every point left over is fixed

    Raises:
        InvalidInputError: If size or a cycle length is not a positive
            integer, a fixed point is outside 0..size-1, or the cycles need
            more points than are free
    """
    validate_positive_integer(size, "size")
    for length in cycle_lengths:
        validate_positive_integer(length, "cycle length")
    held = {_validate_point(point, size) for point in fixed}
    free = [point for point in range(size) if point not in held]
    needed = sum(cycle_lengths)
    if needed > len(free):
        msg = f"Cycles need {needed} points, only {len(free)} are free"
        raise InvalidInputError(msg, input_value=cycle_lengths)

    rng.shuffle(free)
    placed: list[list[int]] = []
    start = 0
    for length in cycle_lengths:
        placed.append(free[start : start + length])
        start += length
    return from_cycles(size, placed)


def from_key(alphabet: Sequence[T], key: Mapping[T, T]) -> list[int]:
    """Return a substitution key as a permutation of alphabet indices.

    Args:
        alphabet: The symbols in index order
        key: Maps each symbol of the alphabet to its substitute

    Returns:
        The permutation with image[i] the index of key[alphabet[i]]

    Raises:
        AlphabetError: If the alphabet is not valid
        InvalidInputError: If the key does not map the alphabet onto itself
    """
    validate_alphabet(alphabet)
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    images = []
    for symbol in alphabet:
        if symbol not in key or key[symbol] not in index:
            msg = f"key does not map {symbol!r} onto the alphabet"
            raise InvalidInputError(msg, input_value=key)
        images.append(index[key[symbol]])
    return validate_permutation(images)


def to_key(alphabet: Sequence[T], perm: Sequence[int]) -> dict[T, T]:
    """Return a permutation of alphabet indices as a substitution key.

    Args:
        alphabet: The symbols in index order
        perm: Permutation of 0..N-1, with N the alphabet size

    Returns:
        The key mapping alphabet[i] to alphabet[perm[i]]

    Raises:
        AlphabetError: If the alphabet is not valid
        InvalidInputError: If perm is not a permutation of the alphabet's
            indices
    """
    validate_alphabet(alphabet)
    images = validate_permutation(perm)
    if len(images) != len(alphabet):
        msg = (
            f"permutation size {len(images)} differs from alphabet size {len(alphabet)}"
        )
        raise InvalidInputError(msg, input_value=perm)
    return {symbol: alphabet[image] for symbol, image in zip(alphabet, images)}
