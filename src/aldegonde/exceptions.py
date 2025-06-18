"""Custom exception hierarchy for Aldegonde cryptography library."""

from typing import Any, Sequence


class AldegendeError(Exception):
    """Base exception class for all Aldegonde-related errors."""

    pass


class CipherError(AldegendeError):
    """Base exception for cipher-related errors."""

    def __init__(self, message: str, cipher_type: str | None = None) -> None:
        self.cipher_type = cipher_type
        super().__init__(message)


class KeyError(CipherError):
    """Exception raised for key-related errors in ciphers."""

    def __init__(
        self,
        message: str,
        key: Any = None,
        cipher_type: str | None = None,
    ) -> None:
        self.key = key
        super().__init__(message, cipher_type)


class AlphabetError(AldegendeError):
    """Exception raised for alphabet-related errors."""

    def __init__(
        self,
        message: str,
        alphabet: Sequence[Any] | None = None,
        expected_size: int | None = None,
    ) -> None:
        self.alphabet = alphabet
        self.expected_size = expected_size
        super().__init__(message)


class InvalidInputError(AldegendeError):
    """Exception raised for invalid input to cryptographic functions."""

    def __init__(
        self,
        message: str,
        input_value: Any = None,
        expected_type: type | None = None,
    ) -> None:
        self.input_value = input_value
        self.expected_type = expected_type
        super().__init__(message)


class StatisticalAnalysisError(AldegendeError):
    """Exception raised during statistical analysis operations."""

    def __init__(
        self,
        message: str,
        analysis_type: str | None = None,
        data_length: int | None = None,
    ) -> None:
        self.analysis_type = analysis_type
        self.data_length = data_length
        super().__init__(message)


class InsufficientDataError(StatisticalAnalysisError):
    """Exception raised when insufficient data is provided for analysis."""

    def __init__(
        self,
        message: str,
        required_length: int,
        actual_length: int,
        analysis_type: str | None = None,
    ) -> None:
        self.required_length = required_length
        self.actual_length = actual_length
        super().__init__(message, analysis_type, actual_length)


class MathematicalError(AldegendeError):
    """Exception raised for mathematical computation errors."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        operands: tuple[Any, ...] | None = None,
    ) -> None:
        self.operation = operation
        self.operands = operands
        super().__init__(message)