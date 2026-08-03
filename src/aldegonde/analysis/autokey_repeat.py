# ABOUTME: Key-independent structural constraints from repeated ciphertext
# ABOUTME: under a ciphertext-autokey cipher: forced-equal plaintext positions.
"""Repeat-consistency constraints for ciphertext autokey.

A ciphertext-autokey cipher keys each position on an earlier ciphertext
symbol: the plaintext at position i is a fixed unknown function of the
ciphertext at i and at i - depth. That forces a structural fact that holds
whatever the key is. Inside a repeated ciphertext substring, once the
running position is at least `depth` past the start, both the ciphertext
symbol and its key symbol are copies of symbols from earlier in the same
matched run, so the two occurrences must decrypt to the same plaintext
there.

This module turns that observation into equivalence classes over stream
positions — positions forced to share a plaintext symbol. The classes are
key-independent, so they both prune a search (reject any candidate key
whose plaintext is not constant within a class) and, where two occurrences
have differing key symbols, pin relations the true tableau must satisfy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from aldegonde.exceptions import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


class _Union:
    """Minimal union-find over integer position labels."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def forced_equal_positions(
    cipher: Sequence[T],
    depth: int,
    window: int,
) -> list[list[int]]:
    """Group stream positions a ciphertext autokey forces to share plaintext.

    Slides a window of length `window` over the ciphertext, groups equal
    windows, and for every pair of equal windows links the positions at
    offsets depth..window-1 — the tail beyond the point where both the
    ciphertext and its autokey source are copies from inside the matched
    window. The result is the set of equivalence classes of size two or
    more.

    Args:
        cipher: Ciphertext stream
        depth: Autokey feedback depth (key at i is the ciphertext at
            i - depth)
        window: Length of the repeated substrings to search; must exceed
            depth to force anything

    Returns:
        Equivalence classes of stream positions, each a sorted list of at
        least two positions forced to hold the same plaintext symbol

    Raises:
        InvalidInputError: If depth is negative, window is not positive, or
            window does not exceed depth
    """
    if depth < 0:
        msg = f"depth must be non-negative, got {depth}"
        raise InvalidInputError(msg)
    if window < 1:
        msg = f"window must be positive, got {window}"
        raise InvalidInputError(msg)
    if window <= depth:
        msg = f"window {window} must exceed depth {depth} to force positions"
        raise InvalidInputError(msg)
    n = len(cipher)
    union = _Union(n)
    groups: dict[tuple[T, ...], list[int]] = {}
    for start in range(n - window + 1):
        key = tuple(cipher[start : start + window])
        groups.setdefault(key, []).append(start)
    for starts in groups.values():
        if len(starts) < 2:
            continue
        first = starts[0]
        for other in starts[1:]:
            for offset in range(depth, window):
                union.union(first + offset, other + offset)
    classes: dict[int, list[int]] = {}
    for position in range(n):
        root = union.find(position)
        classes.setdefault(root, []).append(position)
    return sorted(
        (sorted(members) for members in classes.values() if len(members) > 1),
        key=lambda members: members[0],
    )


def count_violations(
    plaintext: Sequence[T],
    classes: Sequence[Sequence[int]],
) -> int:
    """Count equivalence classes a candidate plaintext fails to keep constant.

    A valid ciphertext-autokey decryption holds one plaintext symbol per
    forced class; this counts the classes that contain more than one
    distinct symbol. Zero means the plaintext respects every repeat
    constraint — a necessary condition for the key, cheap to check inside a
    search or a filter cascade.

    Args:
        plaintext: Candidate plaintext aligned to the ciphertext positions
        classes: Equivalence classes from `forced_equal_positions`

    Returns:
        The number of classes holding more than one distinct plaintext
        symbol

    Raises:
        InvalidInputError: If a class references a position outside the
            plaintext
    """
    violations = 0
    for members in classes:
        symbols = set()
        for position in members:
            if not 0 <= position < len(plaintext):
                msg = (
                    f"position {position} outside plaintext of length {len(plaintext)}"
                )
                raise InvalidInputError(msg)
            symbols.add(plaintext[position])
        if len(symbols) > 1:
            violations += 1
    return violations
