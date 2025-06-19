"""
Columnar transposition cipher implementation.
"""

from aldegonde.exceptions import CipherError, InvalidInputError
from aldegonde.validation import validate_text_sequence


def encrypt_message(message: str, key: str, padding: str = " ") -> str:
    """
    Encrypt message using columnar transposition.

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
        msg = "Key must contain only digits"
        raise InvalidInputError(msg)

    key_digits = [int(d) for d in key]
    if len(set(key_digits)) != len(key_digits):
        msg = "Key must not contain duplicate digits"
        raise InvalidInputError(msg)

    if not all(1 <= d <= len(key) for d in key_digits):
        msg = f"Key digits must be between 1 and {len(key)}"
        raise InvalidInputError(msg)

    try:
        message = message.replace(" ", "").upper()
        num_cols = len(key)
        num_rows = -(-len(message) // num_cols)  # Ceiling division
        message += padding * (num_rows * num_cols - len(message))

        # Create an empty matrix to store the message
        matrix: list[list[str]] = [
            ["" for _ in range(num_cols)] for _ in range(num_rows)
        ]

        # Fill the matrix row by row (corrected from original)
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

    except Exception as exc:
        if isinstance(exc, InvalidInputError):
            raise
        msg = f"Columnar transposition encryption failed: {exc}"
        raise CipherError(msg, cipher_type="columnar") from exc
    else:
        return ciphertext


def decrypt_message(ciphertext: str, key: str) -> str:
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
        msg = "Key must contain only digits"
        raise InvalidInputError(msg)

    key_digits = [int(d) for d in key]
    if len(set(key_digits)) != len(key_digits):
        msg = "Key must not contain duplicate digits"
        raise InvalidInputError(msg)

    if not all(1 <= d <= len(key) for d in key_digits):
        msg = f"Key digits must be between 1 and {len(key)}"
        raise InvalidInputError(msg)

    try:
        num_cols = len(key)
        if len(ciphertext) % num_cols != 0:
            # Handle uneven divisions more gracefully
            num_rows = len(ciphertext) // num_cols + (
                1 if len(ciphertext) % num_cols else 0
            )
        else:
            num_rows = len(ciphertext) // num_cols

        # Create an empty matrix to store the encrypted message
        matrix = [["" for _ in range(num_cols)] for _ in range(num_rows)]

        # Calculate the number of characters in the last row
        last_row_chars = len(ciphertext) % num_cols

        # Track the number of characters taken from the encrypted message
        taken_chars = 0

        # Fill the matrix column by column
        for col in range(num_cols):
            col_index = key.index(str(col + 1))
            extra_char = 1 if col_index < last_row_chars else 0

            for row in range(num_rows - extra_char):
                if taken_chars < len(ciphertext):
                    matrix[row][col_index] = ciphertext[taken_chars]
                    taken_chars += 1

        # Read the matrix row by row to get the decrypted message
        plaintext = ""
        for row in range(num_rows):
            for col in range(num_cols):
                plaintext += matrix[row][col]

    except Exception as exc:
        if isinstance(exc, InvalidInputError):
            raise
        msg = f"Columnar transposition decryption failed: {exc}"
        raise CipherError(msg, cipher_type="columnar_transposition") from exc
    else:
        return plaintext


if __name__ == "__main__":
    plaintext = """The nose is pointing down and the houses are getting bigger"""
    key = "1423756"
    encrypted = encrypt_message(plaintext, key)
    print("ciphertext:", encrypted)

    decrypted = decrypt_message(encrypted, key)
    print("Decrypted:", decrypted)
