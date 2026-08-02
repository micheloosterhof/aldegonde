# ABOUTME: Integer-sequence generators for keystream hypotheses: primes,
# ABOUTME: totient, figurate, and linear-recurrence families, length-bounded.
"""Integer sequences used as running keys.

A running-key attack tries a deterministic integer sequence as the
keystream: primes, Euler totients, Fibonacci, the triangular numbers, and
so on. This module generates the first `n` terms of each as plain integers;
reduce them modulo the alphabet size at the point of use. The generators
are length-bounded (not infinite) so a scan over families and offsets stays
finite, and `catalogue` bundles the common families behind one name so an
attack can sweep them all.

These are the sequences themselves, not the attack: pair them with a
keystream subtraction scan and a proper multiple-comparison correction.
"""

from __future__ import annotations

from aldegonde.exceptions import InvalidInputError
from aldegonde.maths.moebius import moebius
from aldegonde.maths.primes import primes as _primes_up_to
from aldegonde.maths.totient import phi_func


def _validate_n(n: int) -> None:
    if n < 0:
        msg = f"n must be non-negative, got {n}"
        raise InvalidInputError(msg)


def naturals(n: int, start: int = 0) -> list[int]:
    """Return n consecutive integers from `start` (the index sequence)."""
    _validate_n(n)
    return list(range(start, start + n))


def primes(n: int) -> list[int]:
    """Return the first n prime numbers."""
    _validate_n(n)
    if n == 0:
        return []
    # Overestimate the bound: the nth prime is below n(ln n + ln ln n) for
    # n >= 6, with a small floor for the first few.
    from math import log

    bound = 15 if n < 6 else int(n * (log(n) + log(log(n))) + 3)
    found = _primes_up_to(bound)
    while len(found) < n:
        bound *= 2
        found = _primes_up_to(bound)
    return found[:n]


def prime_gaps(n: int) -> list[int]:
    """Return the first n gaps between consecutive primes."""
    _validate_n(n)
    if n == 0:
        return []
    ps = primes(n + 1)
    return [ps[i + 1] - ps[i] for i in range(n)]


def totients(n: int, start: int = 1) -> list[int]:
    """Return Euler's totient phi(k) for n integers k from `start`."""
    _validate_n(n)
    if start < 1:
        msg = f"totient start must be positive, got {start}"
        raise InvalidInputError(msg)
    return [phi_func(k) for k in range(start, start + n)]


def moebius_sequence(n: int, start: int = 1) -> list[int]:
    """Return the Moebius function mu(k) for n integers k from `start`."""
    _validate_n(n)
    if start < 1:
        msg = f"moebius start must be positive, got {start}"
        raise InvalidInputError(msg)
    return [moebius(k) for k in range(start, start + n)]


def triangular(n: int) -> list[int]:
    """Return the first n triangular numbers k(k+1)/2, from k = 1."""
    _validate_n(n)
    return [k * (k + 1) // 2 for k in range(1, n + 1)]


def polygonal(n: int, sides: int) -> list[int]:
    """Return the first n polygonal numbers with the given side count.

    Sides 3 gives triangular numbers, 4 the squares, 5 the pentagonal
    numbers, and so on.

    Args:
        n: Number of terms
        sides: Polygon side count (>= 3)

    Returns:
        The first n s-gonal numbers, from k = 1

    Raises:
        InvalidInputError: If n is negative or sides < 3
    """
    _validate_n(n)
    if sides < 3:
        msg = f"sides must be at least 3, got {sides}"
        raise InvalidInputError(msg)
    return [((sides - 2) * k * k - (sides - 4) * k) // 2 for k in range(1, n + 1)]


def linear_recurrence(
    n: int,
    seed: list[int],
    coefficients: list[int],
) -> list[int]:
    """Return n terms of a linear recurrence over the integers.

    Term k is the dot product of the given coefficients with the previous
    len(seed) terms: x[k] = sum(coefficients[j] * x[k-1-j]). Fibonacci is
    seed [0, 1] with coefficients [1, 1]; Lucas is seed [2, 1]; a tribonacci
    is seed [0, 0, 1] with coefficients [1, 1, 1].

    Args:
        n: Number of terms
        seed: Initial terms; also fixes the recurrence order
        coefficients: One coefficient per previous term, most recent first

    Returns:
        The first n terms, starting from the seed

    Raises:
        InvalidInputError: If n is negative, the seed is empty, or the
            coefficient count differs from the seed length
    """
    _validate_n(n)
    if not seed:
        msg = "linear_recurrence needs a non-empty seed"
        raise InvalidInputError(msg)
    if len(coefficients) != len(seed):
        msg = f"{len(coefficients)} coefficients for order-{len(seed)} recurrence"
        raise InvalidInputError(msg)
    if n <= len(seed):
        return list(seed[:n])
    out = list(seed)
    order = len(seed)
    for _ in range(n - order):
        out.append(sum(coefficients[j] * out[-1 - j] for j in range(order)))
    return out


def fibonacci(n: int) -> list[int]:
    """Return the first n Fibonacci numbers, from 0, 1."""
    return linear_recurrence(n, [0, 1], [1, 1])


def lucas(n: int) -> list[int]:
    """Return the first n Lucas numbers, from 2, 1."""
    return linear_recurrence(n, [2, 1], [1, 1])


def catalogue(n: int) -> dict[str, list[int]]:
    """Return a bundle of common keystream sequences, each of length n.

    A convenience for scanning every family at once: the keys name the
    sequence, the values are the first n integer terms (reduce modulo the
    alphabet at use). Extend or subset it as an attack requires.

    Args:
        n: Number of terms per sequence

    Returns:
        A mapping from sequence name to its first n terms

    Raises:
        InvalidInputError: If n is negative
    """
    _validate_n(n)
    return {
        "naturals": naturals(n),
        "primes": primes(n),
        "prime_gaps": prime_gaps(n),
        "totients": totients(n),
        "moebius": moebius_sequence(n),
        "triangular": triangular(n),
        "squares": polygonal(n, 4),
        "pentagonal": polygonal(n, 5),
        "fibonacci": fibonacci(n),
        "lucas": lucas(n),
    }
