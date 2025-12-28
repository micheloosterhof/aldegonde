"""Input validation utilities for Aldegonde cryptography library."""

from collections.abc import Sequence
from typing import Any, TypeVar

from aldegonde.exceptions import AlphabetError, InsufficientDataError, InvalidInputError

T = TypeVar("T")


def validate_alphabet(alphabet: Sequence[T]) -> None:
    """Validate that an alphabet is suitable for cryptographic operations.

    Args:
        alphabet: The alphabet to validate

    Raises:
        AlphabetError: If alphabet is invalid
    """
    if not alphabet:
        msg = "Alphabet cannot be empty"
        raise AlphabetError(msg)

    if len(alphabet) < 2:
        msg = f"Alphabet must contain at least 2 symbols, got {len(alphabet)}"
        raise AlphabetError(msg)

    if len(set(alphabet)) != len(alphabet):
        duplicates = [x for i, x in enumerate(alphabet) if x in alphabet[:i]]
        msg = f"Alphabet contains duplicate symbols: {duplicates}"
        raise AlphabetError(msg, alphabet=alphabet)


def validate_text_sequence(text: Sequence[Any], min_length: int = 1) -> None:
    """Validate that a text sequence is suitable for analysis.

    Args:
        text: The text sequence to validate
        min_length: Minimum required length

    Raises:
        InsufficientDataError: If text is too short
    """
    if len(text) < min_length:
        msg = f"Text length {len(text)} is below minimum required {min_length}"
        raise InsufficientDataError(
            msg,
            required_length=min_length,
            actual_length=len(text),
        )


def validate_key_length(key: Sequence[Any], min_length: int = 1) -> None:
    """Validate that a key has appropriate length.

    Args:
        key: The key to validate
        min_length: Minimum required length

    Raises:
        InsufficientDataError: If key is too short
    """
    if len(key) < min_length:
        msg = f"Key length {len(key)} is below minimum required {min_length}"
        raise InsufficientDataError(
            msg,
            required_length=min_length,
            actual_length=len(key),
        )


def validate_tabula_recta(tr: dict[T, dict[T, T]], alphabet: Sequence[T]) -> None:
    """Validate that a tabula recta is complete and consistent.

    Args:
        tr: The tabula recta to validate
        alphabet: The expected alphabet

    Raises:
        AlphabetError: If tabula recta doesn't match alphabet
    """
    alphabet_set = set(alphabet)

    # Check that all alphabet symbols are present as outer keys
    missing_outer = alphabet_set - set(tr.keys())
    if missing_outer:
        msg = f"Tabula recta missing outer keys: {missing_outer}"
        raise AlphabetError(msg, alphabet=alphabet)

    # Check each inner dictionary
    for outer_key, inner_dict in tr.items():

        # Check that all alphabet symbols are present as inner keys
        missing_inner = alphabet_set - set(inner_dict.keys())
        if missing_inner:
            msg = f"Tabula recta for key '{outer_key}' missing inner keys: {missing_inner}"
            raise AlphabetError(msg, alphabet=alphabet)

        # Check that all values are valid alphabet symbols
        invalid_values = set(inner_dict.values()) - alphabet_set
        if invalid_values:
            msg = f"Tabula recta for key '{outer_key}' contains invalid values: {invalid_values}"
            raise AlphabetError(msg, alphabet=alphabet)


def validate_positive_integer(value: Any, name: str) -> int:
    """Validate that a value is a positive integer.

    Args:
        value: The value to validate
        name: Name of the parameter for error messages

    Returns:
        The validated integer value

    Raises:
        InvalidInputError: If value is not a positive integer
    """
    if not isinstance(value, int):
        msg = f"{name} must be an integer, got {type(value).__name__}"
        raise InvalidInputError(
            msg,
            input_value=value,
            expected_type=int,
        )

    if value < 1:
        msg = f"{name} must be positive, got {value}"
        raise InvalidInputError(msg, input_value=value)

    return value
