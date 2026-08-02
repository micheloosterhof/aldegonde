# ABOUTME: Permutation algebra over index form: composition, powers, order,
# ABOUTME: parity, cycle structure, conjugation, and alphabet-key conversion.
"""Permutation algebra for rotor, gear, and progressive cipher work.

A permutation is represented in index form: a list of length n holding each of
0..n-1 exactly once, where perm[i] is the image of i. Monoalphabetic keys over
an arbitrary alphabet convert to and from this form with `from_key` and
`to_key`, so the algebra stays integer-only while the ciphers stay
alphabet-generic.

Conventions:
    compose(f, g) applies g first: compose(f, g)[i] == f[g[i]]
    power(p, 0) is the identity; negative exponents use the inverse
    parity is +1 for even permutations, -1 for odd
    cycles are rotated to start at their smallest element and sorted by it,
    and include fixed points, so cycle output is canonical
"""

from __future__ import annotations

from math import lcm
from typing import TYPE_CHECKING, TypeVar

from aldegonde.exceptions import InvalidInputError

if TYPE_CHECKING:
    import random
    from collections.abc import Mapping, Sequence

T = TypeVar("T")

Permutation = list[int]
"""A permutation in index form: perm[i] is the image of i."""


def validate_permutation(perm: Sequence[int]) -> None:
    """Reject a sequence that is not a permutation of 0..n-1.

    Args:
        perm: Candidate permutation in index form

    Raises:
        InvalidInputError: If the sequence is not a bijection on 0..n-1
    """
    if sorted(perm) != list(range(len(perm))):
        msg = f"not a permutation of 0..{len(perm) - 1}: {list(perm)!r}"
        raise InvalidInputError(msg)


def identity(n: int) -> Permutation:
    """Return the identity permutation on n points."""
    return list(range(n))


def compose(f: Sequence[int], g: Sequence[int]) -> Permutation:
    """Compose two permutations, applying g first.

    Args:
        f: Outer permutation
        g: Inner permutation, applied first

    Returns:
        The permutation mapping i to f[g[i]]

    Raises:
        InvalidInputError: If the permutations act on different point counts
    """
    if len(f) != len(g):
        msg = f"cannot compose permutations of sizes {len(f)} and {len(g)}"
        raise InvalidInputError(msg)
    return [f[g[i]] for i in range(len(g))]


def invert(perm: Sequence[int]) -> Permutation:
    """Return the inverse permutation."""
    inverse = [0] * len(perm)
    for i, image in enumerate(perm):
        inverse[image] = i
    return inverse


def power(perm: Sequence[int], exponent: int) -> Permutation:
    """Return the permutation raised to an integer power.

    Exponent 0 gives the identity; negative exponents are powers of the
    inverse. Uses binary exponentiation, so large exponents are cheap.

    Args:
        perm: Permutation in index form
        exponent: Any integer

    Returns:
        The permutation composed with itself exponent times
    """
    base = list(perm) if exponent >= 0 else invert(perm)
    remaining = abs(exponent)
    result = identity(len(perm))
    while remaining:
        if remaining & 1:
            result = compose(base, result)
        base = compose(base, base)
        remaining >>= 1
    return result


def cycles(perm: Sequence[int]) -> list[list[int]]:
    """Return the cycle decomposition, including fixed points.

    Each cycle is rotated to start at its smallest element and the cycles are
    sorted by that element, so equal permutations yield identical output.

    Args:
        perm: Permutation in index form

    Returns:
        The cycles as lists of points
    """
    seen = [False] * len(perm)
    result: list[list[int]] = []
    for start in range(len(perm)):
        if seen[start]:
            continue
        cycle = [start]
        seen[start] = True
        point = perm[start]
        while point != start:
            cycle.append(point)
            seen[point] = True
            point = perm[point]
        result.append(cycle)
    return result


def cycle_type(perm: Sequence[int]) -> tuple[int, ...]:
    """Return the cycle lengths, sorted descending.

    The cycle type is the conjugacy invariant: two permutations are conjugate
    exactly when their cycle types match.
    """
    return tuple(sorted((len(cycle) for cycle in cycles(perm)), reverse=True))


def order(perm: Sequence[int]) -> int:
    """Return the order: the smallest k >= 1 with perm^k the identity.

    The order is the least common multiple of the cycle lengths.
    """
    return lcm(*(len(cycle) for cycle in cycles(perm))) if len(perm) else 1


def parity(perm: Sequence[int]) -> int:
    """Return +1 for an even permutation, -1 for an odd one.

    A cycle of length L contributes L - 1 transpositions, so the sign is
    (-1) ** (n - number_of_cycles). The sign is multiplicative under
    composition, which makes it a cheap necessary condition: a product of
    permutations can only be the identity if its total parity is even.
    """
    return 1 if (len(perm) - len(cycles(perm))) % 2 == 0 else -1


def from_cycles(point_cycles: Sequence[Sequence[int]], n: int) -> Permutation:
    """Build a permutation on n points from its cycles.

    Points not mentioned in any cycle are fixed.

    Args:
        point_cycles: Cycles as sequences of points in 0..n-1
        n: Number of points

    Returns:
        The permutation in index form

    Raises:
        InvalidInputError: If a point is out of range or appears twice
    """
    perm = identity(n)
    used: set[int] = set()
    for cycle in point_cycles:
        for point in cycle:
            if not 0 <= point < n:
                msg = f"cycle point {point} out of range 0..{n - 1}"
                raise InvalidInputError(msg)
            if point in used:
                msg = f"cycle point {point} appears more than once"
                raise InvalidInputError(msg)
            used.add(point)
        for i, point in enumerate(cycle):
            perm[point] = cycle[(i + 1) % len(cycle)]
    return perm


def from_cycle_type(lengths: Sequence[int], n: int) -> Permutation:
    """Build the canonical permutation on n points with the given cycle type.

    Points 0..n-1 are filled into cycles of the given lengths in order;
    lengths that do not sum to n leave the remaining points fixed. Combine
    with `conjugate` by a random permutation to sample the conjugacy class.

    Args:
        lengths: Desired cycle lengths
        n: Number of points

    Returns:
        A permutation with exactly the given cycle type

    Raises:
        InvalidInputError: If a length is not positive or the lengths overrun n
    """
    total = 0
    point_cycles: list[list[int]] = []
    for length in lengths:
        if length < 1:
            msg = f"cycle length must be positive, got {length}"
            raise InvalidInputError(msg)
        point_cycles.append(list(range(total, total + length)))
        total += length
    if total > n:
        msg = f"cycle lengths sum to {total}, more than {n} points"
        raise InvalidInputError(msg)
    return from_cycles(point_cycles, n)


def conjugate(perm: Sequence[int], by: Sequence[int]) -> Permutation:
    """Return the conjugate by ∘ perm ∘ by⁻¹.

    Conjugation relabels the points of perm by the permutation `by`,
    preserving the cycle type. It is the move that explores a conjugacy class
    without leaving it.
    """
    return compose(compose(list(by), list(perm)), invert(by))


def transposition_conjugate(perm: Sequence[int], a: int, b: int) -> Permutation:
    """Conjugate by the transposition (a b): swap two points' roles.

    The canonical cycle-type-preserving mutation for hill-climbing over a
    conjugacy class: one call swaps the labels a and b everywhere in the
    cycle structure and changes nothing else.

    Args:
        perm: Permutation in index form
        a: First point
        b: Second point

    Returns:
        The mutated permutation, with the same cycle type
    """
    swap = identity(len(perm))
    swap[a], swap[b] = swap[b], swap[a]
    return conjugate(perm, swap)


def random_permutation(n: int, rng: random.Random) -> Permutation:
    """Return a uniform random permutation on n points from an injected source."""
    perm = identity(n)
    rng.shuffle(perm)
    return perm


def from_key(alphabet: Sequence[T], key: Mapping[T, T]) -> Permutation:
    """Convert a monoalphabetic substitution key to index form.

    Args:
        alphabet: The alphabet fixing the index of every symbol
        key: Mapping from plaintext symbol to ciphertext symbol

    Returns:
        The permutation with perm[i] the index of key[alphabet[i]]

    Raises:
        InvalidInputError: If the key is not a bijection on the alphabet
    """
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    try:
        perm = [index[key[symbol]] for symbol in alphabet]
    except KeyError as exc:
        msg = f"key is not a bijection on the alphabet: missing {exc.args[0]!r}"
        raise InvalidInputError(msg) from exc
    validate_permutation(perm)
    return perm


def to_key(alphabet: Sequence[T], perm: Sequence[int]) -> dict[T, T]:
    """Convert a permutation in index form to a monoalphabetic key.

    Args:
        alphabet: The alphabet fixing the index of every symbol
        perm: Permutation in index form

    Returns:
        The key mapping alphabet[i] to alphabet[perm[i]]

    Raises:
        InvalidInputError: If perm is not a permutation of the alphabet indices
    """
    validate_permutation(perm)
    if len(perm) != len(alphabet):
        msg = f"permutation size {len(perm)} != alphabet size {len(alphabet)}"
        raise InvalidInputError(msg)
    return {alphabet[i]: alphabet[perm[i]] for i in range(len(perm))}
