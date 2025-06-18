"""Tests for error handling in updated modules."""

import pytest
from aldegonde import pasc
from aldegonde.exceptions import CipherError, KeyError, InvalidInputError, StatisticalAnalysisError, InsufficientDataError, MathematicalError
from aldegonde.stats import ioc
from aldegonde.maths import factor


class TestPascErrorHandling:
    """Test error handling in pasc module."""

    def test_pasc_encrypt_empty_plaintext(self):
        """Test encryption with empty plaintext."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        tr = pasc.vigenere_tr(alphabet)
        with pytest.raises(InsufficientDataError, match="Text length 0 is below minimum required"):
            list(pasc.pasc_encrypt("", "KEY", tr))

    def test_pasc_encrypt_empty_keyword(self):
        """Test encryption with empty keyword."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        tr = pasc.vigenere_tr(alphabet)
        with pytest.raises(InsufficientDataError, match="Key length 0 is below minimum required"):
            list(pasc.pasc_encrypt("HELLO", "", tr))

    def test_pasc_encrypt_invalid_key_symbol(self):
        """Test encryption with invalid key symbol."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        tr = pasc.vigenere_tr(alphabet)
        with pytest.raises(KeyError, match="Key symbol 'X' not found in tabula recta"):
            # Create a TR that doesn't have 'X' as a key
            limited_tr = {k: v for k, v in tr.items() if k != 'X'}
            list(pasc.pasc_encrypt("HELLO", "XYZ", limited_tr))

    def test_pasc_encrypt_invalid_plaintext_symbol(self):
        """Test encryption with invalid plaintext symbol."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        tr = pasc.vigenere_tr(alphabet)
        with pytest.raises(CipherError, match="Plaintext symbol '1' not found in tabula recta"):
            list(pasc.pasc_encrypt("HELLO1", "KEY", tr))

    def test_pasc_encrypt_interrupted_no_interruptor(self):
        """Test interrupted encryption without specifying interruptor."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        tr = pasc.vigenere_tr(alphabet)
        with pytest.raises(InvalidInputError, match="At least one interruptor"):
            list(pasc.pasc_encrypt_interrupted("HELLO", "KEY", tr))

    def test_reverse_tr_invalid_input(self):
        """Test reverse_tr with invalid input."""
        with pytest.raises(InvalidInputError, match="Tabula recta must be a dictionary"):
            pasc.reverse_tr("not_a_dict")

    def test_reverse_tr_ambiguous(self):
        """Test reverse_tr with ambiguous tabula recta."""
        # Create a TR where one key maps to duplicate values
        tr = {
            "A": {"X": "A", "Y": "A"},  # Duplicate values
            "B": {"X": "B", "Y": "C"}
        }
        with pytest.raises(CipherError, match="Tabula recta is ambiguous for key 'A'"):
            pasc.reverse_tr(tr)


class TestIocErrorHandling:
    """Test error handling in IOC module."""

    def test_ioc_empty_text(self):
        """Test IOC with empty text."""
        with pytest.raises(InsufficientDataError, match="Text length 0 is below minimum required"):
            ioc.ioc([])

    def test_ioc_single_character(self):
        """Test IOC with single character."""
        with pytest.raises(InsufficientDataError, match="Text length 1 is below minimum required"):
            ioc.ioc(["A"])

    def test_ioc_invalid_length(self):
        """Test IOC with invalid n-gram length."""
        with pytest.raises(InvalidInputError, match="length must be an integer"):
            ioc.ioc("HELLO", length="invalid")

    def test_ioc_negative_length(self):
        """Test IOC with negative n-gram length."""
        with pytest.raises(InvalidInputError, match="length must be positive"):
            ioc.ioc("HELLO", length=-1)

    def test_ioc_invalid_cut(self):
        """Test IOC with invalid cut parameter."""
        with pytest.raises(InvalidInputError, match="Cut value 5 must be between 0 and 2"):
            ioc.ioc("HELLO", length=2, cut=5)

    def test_sliding_window_ioc_insufficient_data(self):
        """Test sliding window IOC with insufficient data."""
        with pytest.raises(InsufficientDataError, match="Text length .* is below minimum required"):
            ioc.sliding_window_ioc("ABC", window=100)

    def test_sliding_window_ioc_invalid_window(self):
        """Test sliding window IOC with invalid window size."""
        with pytest.raises(InvalidInputError, match="window must be positive"):
            ioc.sliding_window_ioc("HELLO" * 100, window=0)


class TestFactorErrorHandling:
    """Test error handling in factor module."""

    def test_prime_factors_invalid_input(self):
        """Test prime factorization with invalid input."""
        with pytest.raises(InvalidInputError, match="number must be an integer"):
            factor.prime_factors("not_a_number")

    def test_prime_factors_negative_number(self):
        """Test prime factorization with negative number."""
        with pytest.raises(InvalidInputError, match="number must be positive"):
            factor.prime_factors(-5)

    def test_prime_factors_zero(self):
        """Test prime factorization with zero."""
        with pytest.raises(InvalidInputError, match="number must be positive"):
            factor.prime_factors(0)

    def test_prime_factors_one(self):
        """Test prime factorization of 1."""
        result = factor.prime_factors(1)
        assert result == []

    def test_factor_pairs_invalid_input(self):
        """Test factor pairs with invalid input."""
        with pytest.raises(InvalidInputError, match="number must be an integer"):
            factor.factor_pairs(3.14)

    def test_factor_pairs_negative_number(self):
        """Test factor pairs with negative number."""
        with pytest.raises(InvalidInputError, match="number must be positive"):
            factor.factor_pairs(-10)

    def test_factor_pairs_valid_input(self):
        """Test factor pairs with valid input."""
        result = factor.factor_pairs(12)
        expected = [(1, 12), (2, 6), (3, 4), (4, 3), (6, 2), (12, 1)]
        assert result == expected


class TestErrorHandlingIntegration:
    """Test error handling integration across modules."""

    def test_chained_errors(self):
        """Test that errors chain properly through function calls."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        tr = pasc.vigenere_tr(alphabet)
        
        # This should raise a validation error that gets wrapped
        with pytest.raises(InsufficientDataError):
            list(pasc.pasc_encrypt("", "KEY", tr))

    def test_error_information_preservation(self):
        """Test that error information is preserved through the chain."""
        try:
            factor.prime_factors(-5)
        except InvalidInputError as e:
            assert e.input_value == -5
            assert "number must be positive" in str(e)

    def test_error_context_information(self):
        """Test that error context is properly set."""
        try:
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            tr = pasc.vigenere_tr(alphabet)
            list(pasc.pasc_encrypt("HELLO1", "KEY", tr))
        except CipherError as e:
            assert e.cipher_type == "polyalphabetic"
            assert "Plaintext symbol '1' not found" in str(e)