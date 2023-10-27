from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def hamming_distance(s1: Sequence[T], s2: Sequence[T]) -> int:
    """Return the Hamming distance between two equal-length strings of symbols.
    It is the number of positions at which the corresponding symbols
    are different.
    """
    if len(s1) != len(s2):
        msg = "Undefined for sequences of unequal length."
        raise ValueError(msg)
    return sum(el1 != el2 for el1, el2 in zip(s1, s2))
