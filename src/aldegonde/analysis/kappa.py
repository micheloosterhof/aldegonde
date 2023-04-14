"""module description."""

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def kappa(text: Sequence[T], shift: int) -> float:
    """The `Kappa` test. Overlay the ciphertext with itself shifted by a number
    of positions, then count the positions with the same character. Normalize by
    text size.
    """
    dups: int = 0
    for i in range(0, len(text) - shift):
        if text[i] == text[i + shift]:
            dups = dups + 1
    return dups / (len(text) - shift)


def print_kappa(
    ciphertext: Sequence[T],
    alphabetsize: int,
    minimum: int = 1,
    maximum: int = 51,
    threshold: float = 1.3,
    trace: bool = False,
) -> None:
    """Kappa test for a range."""
    assert maximum >= 0
    assert minimum >= 1
    MAX = alphabetsize
    if maximum == 0:
        maximum = int(len(ciphertext) / 2)
    elif maximum > len(ciphertext):
        maximum = len(ciphertext)
    for keylen in range(minimum, maximum):
        k = MAX * kappa(ciphertext, shift=keylen)
        if k > threshold or trace is True:
            print(f"kappa: keylen={keylen:02d}," + f"ioc={k:.3f} ")
    print()
