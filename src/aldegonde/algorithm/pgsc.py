"""polygraphic substitution cipher.

Polygraphic substitution is a cipher in which a uniform substitution is performed on blocks of letters.
Examples are Playfair, Two-Square, Four-Square and Hill Cipher
"""

from collections.abc import Callable, Sequence
from typing import Any, Protocol, TypeVar


class Comparable(Protocol):
    def __lt__(self, __other: Any) -> bool:
        ...

    def __gt__(self, __other: Any) -> bool:
        ...


T = TypeVar("T", bound=Comparable)
function = Callable[[Sequence[T]],Sequence[T]]


def pgsc_encrypt(
    plaintext: Sequence[T], length: int, encryptfn: function
) -> tuple[T, ...]:
    """Polygraphic substitution."""
    return tuple(plaintext)


def pgsc_decrypt(
    ciphertext: Sequence[T], length: int, decryptfn: function
) -> tuple[T, ...]:
    """Polygraphic substitution."""
    return tuple(ciphertext)
