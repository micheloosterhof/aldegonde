"""polygraphic substitution cipher.

Polygraphic substitution is a cipher in which a uniform substitution is performed on blocks of letters.
Examples are Playfair, Two-Square, Four-Square and Hill Cipher
"""

from collections.abc import Callable, Sequence

from aldegonde.exceptions import CipherError, InvalidInputError
from aldegonde.validation import validate_positive_integer, validate_text_sequence


def pgsc_encrypt(
    plaintext: str,
    length: int,
    encryptfn: Callable[[str], str],
) -> str:
    """Polygraphic substitution encryption.

    Args:
        plaintext: Text to encrypt
        length: Block length for polygraphic substitution
        encryptfn: Function to encrypt each block

    Returns:
        Encrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If encryption fails
    """
    validate_text_sequence(plaintext, min_length=1)
    validate_positive_integer(length, "length")

    if not callable(encryptfn):
        msg = "encryptfn must be callable"
        raise InvalidInputError(msg)

    if len(plaintext) % length != 0:
        msg = f"Plaintext length {len(plaintext)} must be divisible by block length {length}"
        raise InvalidInputError(msg)

    try:
        ciphertext = ""
        for i in range(0, len(plaintext), length):
            block = plaintext[i : i + length]
            ciphertext += encryptfn(block)
    except Exception as exc:
        msg = f"Polygraphic encryption failed: {exc}"
        raise CipherError(msg, cipher_type="polygraphic") from exc
    else:
        return ciphertext


def pgsc_decrypt(
    ciphertext: str,
    length: int,
    decryptfn: Callable[[str], str],
) -> str:
    """Polygraphic substitution decryption.

    Args:
        ciphertext: Text to decrypt
        length: Block length for polygraphic substitution
        decryptfn: Function to decrypt each block

    Returns:
        Decrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If decryption fails
    """
    validate_text_sequence(ciphertext, min_length=1)
    validate_positive_integer(length, "length")

    if not callable(decryptfn):
        msg = "decryptfn must be callable"
        raise InvalidInputError(msg)

    if len(ciphertext) % length != 0:
        msg = f"Ciphertext length {len(ciphertext)} must be divisible by block length {length}"
        raise InvalidInputError(msg)

    try:
        plaintext = ""
        for i in range(0, len(ciphertext), length):
            block = ciphertext[i : i + length]
            plaintext += decryptfn(block)
    except Exception as exc:
        msg = f"Polygraphic decryption failed: {exc}"
        raise CipherError(msg, cipher_type="polygraphic") from exc
    else:
        return plaintext


def playfair_get_position(letter: str, matrix: list[list[str]]) -> tuple[int, int]:
    """Find the row and column of the letter in the matrix.

    Args:
        letter: Letter to find
        matrix: 5x5 Playfair matrix

    Returns:
        Tuple of (row, column) position

    Raises:
        CipherError: If letter not found in matrix
    """
    for i in range(5):
        for j in range(5):
            if matrix[i][j] == letter:
                return (i, j)
    msg = f"Letter '{letter}' not found in Playfair matrix"
    raise CipherError(msg, cipher_type="playfair")


def playfair_square(word: Sequence[str], alphabet: Sequence[str]) -> list[list[str]]:
    """Generate the Playfair Square.

    Args:
        word: Keyword for the square
        alphabet: Alphabet to use (must be 25 characters)

    Returns:
        5x5 Playfair square matrix

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If square generation fails
    """
    if len(alphabet) != 25:
        msg = f"Alphabet must be exactly 25 characters, got {len(alphabet)}"
        raise InvalidInputError(msg)

    try:
        # deduplicate key
        key_letters: list[str] = []
        for letter in word:
            if letter not in key_letters:
                key_letters.append(letter)

        elements: list[str] = []
        for i in key_letters:
            if i not in elements:
                elements.append(i)
        for i in alphabet:
            if i not in elements:
                elements.append(i)

        if len(elements) != 25:
            msg = f"Generated square has {len(elements)} elements, expected 25"
            raise CipherError(msg, cipher_type="playfair")

        square: list[list[str]] = []
        while elements:
            square.append(elements[:5])
            elements = elements[5:]

    except Exception as exc:
        if isinstance(exc, InvalidInputError | CipherError):
            raise
        msg = f"Playfair square generation failed: {exc}"
        raise CipherError(msg, cipher_type="playfair") from exc
    else:
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

    def encryptfn(pair: str) -> str:
        return playfair_encrypt_pair(pair=pair, matrix=square)

    return "".join(pgsc_encrypt(plaintext, length=2, encryptfn=encryptfn))


def playfair_decrypt(ciphertext: str, keyword: str) -> str:
    """Playfair decrypt"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    square = playfair_square(keyword, alphabet=alphabet)

    def decryptfn(pair: str) -> str:
        return playfair_decrypt_pair(pair=pair, matrix=square)

    return "".join(pgsc_decrypt(ciphertext, length=2, decryptfn=decryptfn))
