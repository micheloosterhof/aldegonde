"""
Various transposition ciphers
"""

from aldegonde.exceptions import CipherError, InvalidInputError
from aldegonde.validation import validate_text_sequence, validate_positive_integer


def rail_encrypt(plaintext: str, key: int) -> str:
    """
    Encrypt a message with rail fence cipher.

    Args:
        plaintext: Text to encrypt
        key: Number of rails (rows)

    Returns:
        Encrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If encryption fails
    """
    validate_text_sequence(plaintext, min_length=1)
    validate_positive_integer(key, "key")

    if key == 1:
        return plaintext

    if key >= len(plaintext):
        raise InvalidInputError(
            f"Key {key} must be less than text length {len(plaintext)}"
        )

    try:
        rail: list[list[str]] = [["\n" for _i in plaintext] for _j in range(key)]

        dir_down: bool = False
        row: int = 0
        col: int

        for col, letter in enumerate(plaintext):
            if row in (0, key - 1):
                dir_down = not dir_down
            rail[row][col] = letter
            if dir_down:
                row += 1
            else:
                row -= 1

        result: list[str] = []
        for line in rail:
            for letter in line:
                if letter != "\n":
                    result.append(letter)
        return "".join(result)

    except Exception as exc:
        raise CipherError(
            f"Rail fence encryption failed: {exc}", cipher_type="rail_fence"
        ) from exc


def rail_decrypt(ciphertext: str, key: int) -> str:
    """
    Decrypt a rail fence cipher.

    Args:
        ciphertext: Text to decrypt
        key: Number of rails (rows)

    Returns:
        Decrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If decryption fails
    """
    validate_text_sequence(ciphertext, min_length=1)
    validate_positive_integer(key, "key")

    if key == 1:
        return ciphertext

    if key >= len(ciphertext):
        raise InvalidInputError(
            f"Key {key} must be less than text length {len(ciphertext)}"
        )

    try:
        rail: list[list[str]] = [["\n" for _i in ciphertext] for _j in range(key)]

        # create the rail matrix and fill with *'s
        dir_down: bool = False
        row: int = 0
        col: int
        for col in range(len(ciphertext)):
            if row in (0, key - 1):
                dir_down = not dir_down
            rail[row][col] = "*"
            if dir_down:
                row += 1
            else:
                row -= 1

        # now we can fill the rail matrix with ciphertext values
        index = 0
        for i in range(key):
            for j in range(len(ciphertext)):
                if (rail[i][j] == "*") and (index < len(ciphertext)):
                    rail[i][j] = ciphertext[index]
                    index += 1

        # now read the matrix in zig-zag manner to construct the resultant text
        result = []
        dir_down = False
        row = 0
        for col in range(len(ciphertext)):
            if row in (0, key - 1):
                dir_down = not dir_down
            result.append(rail[row][col])
            if dir_down:
                row += 1
            else:
                row -= 1

        return "".join(result)

    except Exception as exc:
        raise CipherError(
            f"Rail fence decryption failed: {exc}", cipher_type="rail_fence"
        ) from exc


def scytale_encrypt(plaintext: str, key: int) -> str:
    """
    Encrypt a message with scytale cipher.

    Args:
        plaintext: Text to encrypt
        key: Number of wraps around the scytale

    Returns:
        Encrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If encryption fails
    """
    validate_text_sequence(plaintext, min_length=1)
    validate_positive_integer(key, "key")

    if key == 1:
        return plaintext

    try:
        scytale: list[list[str]] = [["" for _i in plaintext] for _j in range(key)]

        for col, letter in enumerate(plaintext):
            scytale[col % key][col] = letter

        result: list[str] = []
        for line in scytale:
            for letter in line:
                if letter:
                    result.append(letter)
        return "".join(result)

    except Exception as exc:
        raise CipherError(
            f"Scytale encryption failed: {exc}", cipher_type="scytale"
        ) from exc


def scytale_decrypt(ciphertext: str, key: int) -> str:
    """
    Decrypt a scytale cipher.

    Args:
        ciphertext: Text to decrypt
        key: Number of wraps around the scytale

    Returns:
        Decrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If decryption fails
    """
    validate_text_sequence(ciphertext, min_length=1)
    validate_positive_integer(key, "key")

    if key == 1:
        return ciphertext

    try:
        scytale: list[list[str]] = [["\n" for _i in ciphertext] for _j in range(key)]

        # create the scytale matrix and fill with *'s
        for col in range(len(ciphertext)):
            scytale[col % key][col] = "*"

        # now we can fill the scytale matrix with ciphertext values
        index = 0
        for i in range(key):
            for j in range(len(ciphertext)):
                if (scytale[i][j] == "*") and (index < len(ciphertext)):
                    scytale[i][j] = ciphertext[index]
                    index += 1

        result = []
        for col in range(len(ciphertext)):
            result.append(scytale[col % key][col])

        return "".join(result)

    except Exception as exc:
        raise CipherError(
            f"Scytale decryption failed: {exc}", cipher_type="scytale"
        ) from exc


def columnar_transposition_encrypt(message: str, key: str, padding: str = " ") -> str:
    """
    Encrypt with columnar transposition cipher.

    Args:
        message: Text to encrypt
        key: Numeric key string (e.g., "4312")
        padding: Character to use for padding

    Returns:
        Encrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If encryption fails
    """
    validate_text_sequence(message, min_length=1)
    validate_text_sequence(key, min_length=1)

    # Validate that key contains only digits and no duplicates
    if not key.isdigit():
        raise InvalidInputError("Key must contain only digits")

    key_digits = [int(d) for d in key]
    if len(set(key_digits)) != len(key_digits):
        raise InvalidInputError("Key must not contain duplicate digits")

    if not all(1 <= d <= len(key) for d in key_digits):
        raise InvalidInputError(f"Key digits must be between 1 and {len(key)}")

    try:
        message = message.replace(" ", "").upper()
        num_cols = len(key)
        num_rows = -(-len(message) // num_cols)  # Ceiling division
        message += padding * (num_rows * num_cols - len(message))

        # Create an empty matrix to store the message
        matrix: list[list[str]] = [
            ["" for _ in range(num_cols)] for _ in range(num_rows)
        ]

        # Fill the matrix row by row
        index = 0
        for row in range(num_rows):
            for col in range(num_cols):
                if index < len(message):
                    matrix[row][col] = message[index]
                    index += 1

        # Read the matrix column by column according to key order
        ciphertext = ""
        for col in range(1, num_cols + 1):
            col_index = key.index(str(col))
            for row in range(num_rows):
                ciphertext += matrix[row][col_index]

        return ciphertext

    except Exception as exc:
        raise CipherError(
            f"Columnar transposition encryption failed: {exc}",
            cipher_type="columnar_transposition",
        ) from exc


def columnar_transposition_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt columnar transposition cipher.

    Args:
        ciphertext: Text to decrypt
        key: Numeric key string (e.g., "4312")

    Returns:
        Decrypted text

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If decryption fails
    """
    validate_text_sequence(ciphertext, min_length=1)
    validate_text_sequence(key, min_length=1)

    # Validate key format
    if not key.isdigit():
        raise InvalidInputError("Key must contain only digits")

    key_digits = [int(d) for d in key]
    if len(set(key_digits)) != len(key_digits):
        raise InvalidInputError("Key must not contain duplicate digits")

    if not all(1 <= d <= len(key) for d in key_digits):
        raise InvalidInputError(f"Key digits must be between 1 and {len(key)}")

    try:
        num_cols = len(key)
        if len(ciphertext) % num_cols != 0:
            raise InvalidInputError(
                f"Ciphertext length {len(ciphertext)} must be divisible by key length {num_cols}"
            )

        num_rows = len(ciphertext) // num_cols

        # Create an empty matrix to store the encrypted message
        matrix = [["" for _ in range(num_cols)] for _ in range(num_rows)]

        # Fill the matrix column by column according to key order
        taken_chars = 0
        for col in range(1, num_cols + 1):
            col_index = key.index(str(col))
            for row in range(num_rows):
                if taken_chars < len(ciphertext):
                    matrix[row][col_index] = ciphertext[taken_chars]
                    taken_chars += 1

        # Read the matrix row by row to get the decrypted message
        plaintext = ""
        for row in range(num_rows):
            for col in range(num_cols):
                plaintext += matrix[row][col]

        return plaintext

    except Exception as exc:
        raise CipherError(
            f"Columnar transposition decryption failed: {exc}",
            cipher_type="columnar_transposition",
        ) from exc
