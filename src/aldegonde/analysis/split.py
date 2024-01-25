"""Functions to split a text in various ways."""

from collections import defaultdict, deque
from collections.abc import Generator, Iterator, Sequence
from typing import TypeVar

T = TypeVar("T")


def split_by_slice(inp: Sequence[T], size: int) -> dict[int, Sequence[T]]:
    """Create slices of the input, with a certain slice size
    This will return every N'th element
    For size 3, it will return a dictionary of lists with elements:
       [0, 3, 6, 9] [1, 4, 7, 10] [2, 5, 8].
    """
    outp: dict[int, Sequence[T]] = {}
    for i in range(size):
        outp[i] = inp[slice(i, len(inp), size)]
    return outp


def split_by_slice_interrupted(
    seq: Sequence[T],
    step: int,
    interrupter: T,
) -> dict[int, list[T]]:
    """Similar to split_by_splice() but with ciphertext interrupters and it returns all slices for a step"""
    counter = 0
    slices: dict[int, list[T]] = defaultdict(list)
    for e in seq:
        if counter == step or e == interrupter:
            counter = 0
        slices[counter].append(e)
        counter = counter + 1
    return slices


def split_by_character(inp: Sequence[T], skip: int = 1) -> dict[T, list[T]]:
    """By previous character."""
    outp: dict[T, list[T]] = {}
    for e in set(inp):
        outp[e] = []
    for i in range(len(inp) - skip):
        outp[inp[i]].append(inp[i + skip])
    return outp


def trim(
    inp: Iterator[T],
    whitespace: Sequence[str] = [" ", "\r", "\n", "\t"],
) -> Generator[T, None, None]:
    """
    Trim whitespace from beginning and end
    """
    buffer: deque = deque()
    begin: bool = True
    for e in inp:
        if begin:
            if e in whitespace:
                continue
            else:
                begin = False
                buffer.append(e)
        elif e in whitespace:
            buffer.append(e)
        else:
            while buffer:
                yield buffer.popleft()
            yield e


def split_by_whitespace(
    inp: Sequence[str],
    whitespace: Sequence[str] = [" ", "\r", "\n", "\t"],
) -> list[list[str]]:
    """
    split by whitespace
    """
    return [[""]]


def split_by_doublet(ciphertext: Sequence[T]) -> list[list[T]]:
    """Split in simple chunks separated by a doublet."""
    output: list[list[T]] = []
    current: list[T] = []
    for i in range(len(ciphertext)):
        if ciphertext[i] == ciphertext[i - 1]:
            output.append(current)
            current = [ciphertext[i]]
        else:
            current.append(ciphertext[i])
    output.append(current)
    return output
