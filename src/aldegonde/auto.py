"""ciphertext autokey variations."""

from collections import deque
from collections.abc import Generator, Iterable, Sequence
from itertools import chain

from aldegonde.exceptions import CipherError, InvalidInputError
from aldegonde.pasc import TR, T, reverse_tr
from aldegonde.validation import validate_key_length, validate_text_sequence


def ciphertext_autokey_encrypt(
    plaintext: Iterable[T],
    primer: Sequence[T],
    tr: TR[T],
) -> Generator[T, None, None]:
    """Ciphertext Autokey Encryption.

    Args:
        plaintext: Text to encrypt
        primer: Initial key sequence
        tr: Tabula recta for the cipher

    Yields:
        Encrypted characters

    Raises:
        CipherError: If encryption fails
    """
    plaintext_seq = (
        list(plaintext) if not isinstance(plaintext, Sequence) else plaintext
    )
    validate_text_sequence(plaintext_seq)
    validate_key_length(primer)

    try:
        key: deque[T] = deque(primer)
        for e in plaintext_seq:
            if not key:
                msg = "Key deque is empty during encryption"
                raise CipherError(msg, cipher_type="autokey")
            k = key.popleft()
            if k not in tr:
                msg = f"Key symbol '{k}' not found in tabula recta"
                raise CipherError(msg, cipher_type="autokey")
            if e not in tr[k]:
                msg = f"Plaintext symbol '{e}' not found in tabula recta for key '{k}'"
                raise CipherError(msg, cipher_type="autokey")
            c = tr[k][e]
            key.append(c)
            yield c
    except Exception as exc:
        if isinstance(exc, CipherError | InvalidInputError):
            raise
        msg = f"Ciphertext autokey encryption failed: {exc}"
        raise CipherError(msg, cipher_type="autokey") from exc


def ciphertext_autokey_decrypt(
    ciphertext: Sequence[T],
    primer: Sequence[T],
    tr: TR[T],
) -> Generator[T, None, None]:
    """Ciphertext Autokey Decryption.

    Args:
        ciphertext: Text to decrypt
        primer: Initial key sequence
        tr: Tabula recta for the cipher

    Yields:
        Decrypted characters

    Raises:
        InvalidInputError: If inputs are invalid
        CipherError: If decryption fails
    """
    validate_text_sequence(ciphertext)
    validate_key_length(primer)

    try:
        rtr: TR[T] = reverse_tr(tr)
        for e, k in zip(ciphertext, chain(primer, ciphertext)):
            if k not in rtr:
                msg = f"Key symbol '{k}' not found in reversed tabula recta"
                raise CipherError(msg, cipher_type="autokey")
            if e not in rtr[k]:
                msg = f"Ciphertext symbol '{e}' not found in reversed tabula recta for key '{k}'"
                raise CipherError(msg, cipher_type="autokey")
            yield rtr[k][e]
    except Exception as exc:
        if isinstance(exc, CipherError | InvalidInputError):
            raise
        msg = f"Ciphertext autokey decryption failed: {exc}"
        raise CipherError(msg, cipher_type="autokey") from exc


def plaintext_autokey_encrypt(
    plaintext: Sequence[T],
    primer: Sequence[T],
    tr: dict[T, dict[T, T]],
) -> Generator[T, None, None]:
    """Plaintext Autokey Encryption."""
    for e, k in zip(plaintext, chain(primer, plaintext)):
        yield tr[k][e]


def plaintext_autokey_decrypt(
    ciphertext: Iterable[T],
    primer: Sequence[T],
    tr: dict[T, dict[T, T]],
) -> Generator[T, None, None]:
    """Plaintext Autokey Decryption primitive P[i] = DF(C[i], P[i-1])."""
    rtr = reverse_tr(tr)
    key: deque[T] = deque(primer)
    for e in ciphertext:
        p = rtr[key.popleft()][e]
        key.append(p)
        yield p
