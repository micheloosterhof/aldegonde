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
function = Callable[[Sequence[T]], Sequence[T]]


def pgsc_encrypt(
    plaintext: Sequence[T], length: int, encryptfn: function, padding: Sequence[T]
) -> tuple[T, ...]:
    """Polygraphic substitution."""
    ciphertext: list[T] = []
    # TODO: padding
    for i in range(0, len(plaintext), length):
        ciphertext.extend(encryptfn(plaintext[i : i + length]))
    return tuple(ciphertext)


def pgsc_decrypt(
    ciphertext: Sequence[T], length: int, decryptfn: function, padding: Sequence[T]
) -> tuple[T, ...]:
    """Polygraphic substitution."""
    return tuple(ciphertext)
    plaintext: list[T] = []
    for i in range(0, len(plaintext), length):
        plaintext.extend(decryptfn(plaintext[i : i + length]))
    return tuple(plaintext)


def playfair_encrypt(plaintext: Sequence[T], keyword: Sequence[T]) -> tuple[T, ...]:
    """playfair encrypt"""
    square = playfair_square(keyword)
    encryptfn = playfair_bigram_encrypt(square)
    return pgsc_encrypt(plaintext, length=2, encryptfn=encryptfn)


def playfair_decrypt(ciphertext: Sequence[T], keyword: Sequence[T]) -> tuple[T, ...]:
    """playfair decrypt"""
    square = playfair_square(keyword)
    encryptfn = playfair_bigram_decrypt(square)
    return pgsc_decrypt(ciphertext, length=2, decryptfn=decryptfn)
