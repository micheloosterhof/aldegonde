"""Functions to split a text in various ways"""

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def split_by_slice(inp: Sequence[T], size: int) -> dict[int, Sequence[T]]:
    """
    Create slices of the input, with a certain slice size
    This will return every N'th element
    For size 3, it will return a dictionary of lists with elements:
       [0, 3, 6, 9] [1, 4, 7, 10] [2, 5, 8]
    """
    outp: dict[int, Sequence[T]] = {}
    for i in range(0, size):
        outp[i] = inp[slice(i, len(inp), size)]
    return outp


def split_by_character(inp: Sequence[T]) -> dict[T, list[T]]:
    """
    by previous character
    """
    outp: dict[T, list[T]] = {}
    for e in set(inp):
        outp[e] = []
    for i in range(0, len(inp) - 1):
        outp[inp[i]].append(inp[i + 1])
    return outp


def split_by_doublet(ciphertext: Sequence[T]) -> list[list[T]]:
    """
    split in simple chunks separated by a doublet
    """
    output: list[list[T]] = []
    current: list[T] = []
    for i in range(0, len(ciphertext)):
        if ciphertext[i] == ciphertext[i - 1]:
            output.append(current)
            current = [ciphertext[i]]
        else:
            current.append(ciphertext[i])
    output.append(current)
    return output
