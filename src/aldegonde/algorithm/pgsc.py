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


def playfair_get_position(letter: str, matrix: list[list[str]]) -> tuple[int, int]:
    # Find the row and column of the letter in the matrix
    for i in range(5):
        for j in range(5):
            if matrix[i][j] == letter:
                return (i, j)


def playfair_decrypt_pair(pair: str, matrix: list[list[str]]) -> str:
    # Get the row and column of each letter in the pair
    row1, col1 = playfair_get_position(pair[0], matrix)
    row2, col2 = playfair_get_position(pair[1], matrix)

    # If the letters are in the same row, shift them to the left
    if row1 == row2:
        col1 = (col1 - 1) % 5
        col2 = (col2 - 1) % 5
    # If the letters are in the same column, shift them up
    elif col1 == col2:
        row1 = (row1 - 1) % 5
        row2 = (row2 - 1) % 5
    # If the letters are not in the same row or column, form a rectangle and swap the letters
    else:
        temp = col1
        col1 = col2
        col2 = temp

    # Get the plaintext pair
    plaintext = matrix[row1][col1] + matrix[row2][col2]

    return plaintext


def playfair_square(word: Sequence[T], alphabet: Sequence[T]) -> list[list[T]]:
    """
    Generate the Playfair Square
    """
    # deduplicate key
    key_letters: list[T] = []
    for letter in word:
        if letter not in key_letters:
            key_letters.append(letter)

    elements: list[T] = []
    for i in key_letters:
        if i not in elements:
            elements.append(i)
    for i in alphabet:
        if i not in elements:
            elements.append(i)

    assert len(elements) == 25

    square: list[list[T]] = []
    while elements:
        square.append(elements[:5])
        elements = elements[5:]

    return square


def playfair_encrypt_pair(pair: str, matrix: list[list[str]]) -> str:
    # Get the row and column of each letter in the pair
    row1, col1 = playfair_get_position(pair[0], matrix)
    row2, col2 = playfair_get_position(pair[1], matrix)

    # If the letters are in the same row, shift them to the right
    if row1 == row2:
        col1 = (col1 + 1) % 5
        col2 = (col2 + 1) % 5
    # If the letters are in the same column, shift them down
    elif col1 == col2:
        row1 = (row1 + 1) % 5
        row2 = (row2 + 1) % 5
    # If the letters are not in the same row or column, form a rectangle and swap the letters
    else:
        temp = col1
        col1 = col2
        col2 = temp

    # Get the ciphertext pair
    ciphertext = matrix[row1][col1] + matrix[row2][col2]

    return ciphertext


def playfair_encrypt(plaintext: Sequence[T], keyword: Sequence[T]) -> tuple[T, ...]:
    """playfair encrypt"""
    square = playfair_square(keyword)
    encryptfn = playfair_encrypt_pair(square)
    return pgsc_encrypt(plaintext, length=2, encryptfn=encryptfn)


def playfair_decrypt(ciphertext: Sequence[T], keyword: Sequence[T]) -> tuple[T, ...]:
    """playfair decrypt"""
    square = playfair_square(keyword)
    decryptfn = playfair_decrypt_pair(square)
    return pgsc_decrypt(ciphertext, length=2, decryptfn=decryptfn)
