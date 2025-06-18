"""Tests for exception hierarchy and validation."""

import pytest
from aldegonde.exceptions import (
    AldegondeError,
    CipherError,
    KeyError,
    AlphabetError,
    InvalidInputError,
    StatisticalAnalysisError,
    InsufficientDataError,
    MathematicalError,
)
from aldegonde.validation import (
    validate_alphabet,
    validate_text_sequence,
    validate_key_length,
    validate_tabula_recta,
    validate_positive_integer,
)


class TestExceptionHierarchy:
    """Test the exception class hierarchy."""

    def test_base_exception(self):
        """Test base AldegondeError."""
        exc = AldegondeError("test message")
        assert str(exc) == "test message"
        assert isinstance(exc, Exception)

    def test_cipher_error(self):
        """Test CipherError with cipher type."""
        exc = CipherError("cipher failed", cipher_type="vigenere")
        assert str(exc) == "cipher failed"
        assert exc.cipher_type == "vigenere"
        assert isinstance(exc, AldegondeError)

    def test_key_error(self):
        """Test KeyError with key and cipher type."""
        exc = KeyError("invalid key", key="ABC", cipher_type="caesar")
        assert str(exc) == "invalid key"
        assert exc.key == "ABC"
        assert exc.cipher_type == "caesar"
        assert isinstance(exc, CipherError)

    def test_alphabet_error(self):
        """Test AlphabetError with alphabet and expected size."""
        alphabet = ["A", "B", "C"]
        exc = AlphabetError("invalid alphabet", alphabet=alphabet, expected_size=26)
        assert str(exc) == "invalid alphabet"
        assert exc.alphabet == alphabet
        assert exc.expected_size == 26
        assert isinstance(exc, AldegondeError)

    def test_statistical_analysis_error(self):
        """Test StatisticalAnalysisError with analysis type and data length."""
        exc = StatisticalAnalysisError(
            "analysis failed", analysis_type="IOC", data_length=10
        )
        assert str(exc) == "analysis failed"
        assert exc.analysis_type == "IOC"
        assert exc.data_length == 10
        assert isinstance(exc, AldegondeError)

    def test_insufficient_data_error(self):
        """Test InsufficientDataError with required and actual lengths."""
        exc = InsufficientDataError(
            "not enough data",
            required_length=100,
            actual_length=50,
            analysis_type="IOC",
        )
        assert str(exc) == "not enough data"
        assert exc.required_length == 100
        assert exc.actual_length == 50
        assert exc.analysis_type == "IOC"
        assert isinstance(exc, StatisticalAnalysisError)

    def test_mathematical_error(self):
        """Test MathematicalError with operation and operands."""
        exc = MathematicalError("math failed", operation="division", operands=(10, 0))
        assert str(exc) == "math failed"
        assert exc.operation == "division"
        assert exc.operands == (10, 0)
        assert isinstance(exc, AldegondeError)


class TestValidation:
    """Test validation functions."""

    def test_validate_alphabet_valid(self):
        """Test valid alphabet validation."""
        alphabet = ["A", "B", "C", "D"]
        validate_alphabet(alphabet)  # Should not raise

    def test_validate_alphabet_empty(self):
        """Test empty alphabet validation."""
        with pytest.raises(AlphabetError, match="Alphabet cannot be empty"):
            validate_alphabet([])

    def test_validate_alphabet_too_small(self):
        """Test alphabet with single symbol."""
        with pytest.raises(
            AlphabetError, match="Alphabet must contain at least 2 symbols"
        ):
            validate_alphabet(["A"])

    def test_validate_alphabet_duplicates(self):
        """Test alphabet with duplicate symbols."""
        with pytest.raises(AlphabetError, match="Alphabet contains duplicate symbols"):
            validate_alphabet(["A", "B", "A", "C"])

    def test_validate_text_sequence_valid(self):
        """Test valid text sequence validation."""
        validate_text_sequence("HELLO", min_length=3)  # Should not raise

    def test_validate_text_sequence_too_short(self):
        """Test text sequence that's too short."""
        with pytest.raises(
            InsufficientDataError, match="Text length 2 is below minimum required 5"
        ):
            validate_text_sequence("HI", min_length=5)

    def test_validate_text_sequence_invalid_type(self):
        """Test text sequence with invalid type."""
        with pytest.raises(InvalidInputError, match="Text must be a sequence"):
            validate_text_sequence(123)

    def test_validate_key_length_valid(self):
        """Test valid key length validation."""
        validate_key_length("KEY", min_length=2)  # Should not raise

    def test_validate_key_length_too_short(self):
        """Test key that's too short."""
        with pytest.raises(
            InsufficientDataError, match="Key length 1 is below minimum required 3"
        ):
            validate_key_length("A", min_length=3)

    def test_validate_positive_integer_valid(self):
        """Test valid positive integer."""
        result = validate_positive_integer(5, "test_param")
        assert result == 5

    def test_validate_positive_integer_not_int(self):
        """Test non-integer value."""
        with pytest.raises(InvalidInputError, match="test_param must be an integer"):
            validate_positive_integer("5", "test_param")

    def test_validate_positive_integer_not_positive(self):
        """Test non-positive integer."""
        with pytest.raises(InvalidInputError, match="test_param must be positive"):
            validate_positive_integer(0, "test_param")

    def test_validate_tabula_recta_valid(self):
        """Test valid tabula recta validation."""
        alphabet = ["A", "B"]
        tr = {"A": {"A": "A", "B": "B"}, "B": {"A": "B", "B": "A"}}
        validate_tabula_recta(tr, alphabet)  # Should not raise

    def test_validate_tabula_recta_not_dict(self):
        """Test tabula recta that's not a dictionary."""
        with pytest.raises(
            InvalidInputError, match="Tabula recta must be a dictionary"
        ):
            validate_tabula_recta("not_a_dict", ["A", "B"])

    def test_validate_tabula_recta_missing_outer_keys(self):
        """Test tabula recta missing outer keys."""
        alphabet = ["A", "B", "C"]
        tr = {
            "A": {"A": "A", "B": "B", "C": "C"},
            "B": {"A": "B", "B": "A", "C": "C"},
            # Missing "C"
        }
        with pytest.raises(AlphabetError, match="Tabula recta missing outer keys"):
            validate_tabula_recta(tr, alphabet)

    def test_validate_tabula_recta_missing_inner_keys(self):
        """Test tabula recta missing inner keys."""
        alphabet = ["A", "B", "C"]
        tr = {
            "A": {"A": "A", "B": "B"},  # Missing "C"
            "B": {"A": "B", "B": "A", "C": "C"},
            "C": {"A": "C", "B": "C", "C": "A"},
        }
        with pytest.raises(
            AlphabetError, match="Tabula recta for key 'A' missing inner keys"
        ):
            validate_tabula_recta(tr, alphabet)

    def test_validate_tabula_recta_invalid_values(self):
        """Test tabula recta with invalid values."""
        alphabet = ["A", "B"]
        tr = {
            "A": {"A": "A", "B": "X"},  # "X" not in alphabet
            "B": {"A": "B", "B": "A"},
        }
        with pytest.raises(
            AlphabetError, match="Tabula recta for key 'A' contains invalid values"
        ):
            validate_tabula_recta(tr, alphabet)
