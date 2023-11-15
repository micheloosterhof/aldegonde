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
    plaintext: Sequence[T],
    length: int,
    encryptfn: function,
) -> tuple[T, ...]:
    """Polygraphic substitution."""
    ciphertext: list[T] = []
    for i in range(0, len(plaintext), length):
        ciphertext.extend(encryptfn(plaintext[i : i + length]))
    return tuple(ciphertext)


def pgsc_decrypt(
    ciphertext: Sequence[T],
    length: int,
    decryptfn: function,
) -> tuple[T, ...]:
    """Polygraphic substitution."""
    plaintext: list[T] = []
    for i in range(0, len(ciphertext), length):
        plaintext.extend(decryptfn(ciphertext[i : i + length]))
    return tuple(plaintext)


def playfair_get_position(letter: T, matrix: list[list[T]]) -> tuple[int, int]:
    """Find the row and column of the letter in the matrix"""
    for i in range(5):
        for j in range(5):
            if matrix[i][j] == letter:
                return (i, j)
    raise ValueError


def playfair_square(word: Sequence[T], alphabet: Sequence[T]) -> list[list[T]]:
    """Generate the Playfair Square"""
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

    print(elements)
    assert len(elements) == 25

    square: list[list[T]] = []
    while elements:
        square.append(elements[:5])
        elements = elements[5:]

    return square


def playfair_encrypt_pair(pair: str, matrix: list[list[str]]) -> str:
    assert len(pair) == 2

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
        col1, col2 = col2, col1

    # Return the ciphertext pair
    return matrix[row1][col1] + matrix[row2][col2]


def playfair_decrypt_pair(pair: str, matrix: list[list[str]]) -> str:
    assert len(pair) == 2

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
        col1, col2 = col2, col1

    # Return the plaintext pair
    return matrix[row1][col1] + matrix[row2][col2]


def playfair_encrypt(plaintext: str, keyword: str) -> str:
    """Playfair encrypt"""
    if len(plaintext) % 2 == 1:
        plaintext += "Z"
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    square = playfair_square(keyword, alphabet=alphabet)

    def encryptfn(pair):
        return playfair_encrypt_pair(pair=pair, matrix=square)

    return "".join(pgsc_encrypt(plaintext, length=2, encryptfn=encryptfn))


def playfair_decrypt(ciphertext: str, keyword: str) -> str:
    """Playfair decrypt"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    square = playfair_square(keyword, alphabet=alphabet)

    def decryptfn(pair):
        return playfair_decrypt_pair(pair=pair, matrix=square)

    return "".join(pgsc_decrypt(ciphertext, length=2, decryptfn=decryptfn))
