"""monoalphabetic substitution cipher.

This contains all ciphers of this type. This includes Caesar, ROT13, Affine ciphers, etc
All are monoalphabetic
"""

import random
from collections.abc import Generator, Iterable, Sequence
from typing import TypeVar

from aldegonde.exceptions import AldegondeKeyError, CipherError, InvalidInputError
from aldegonde.validation import validate_alphabet, validate_text_sequence

T = TypeVar("T")


def masc_encrypt(plaintext: Iterable[T], key: dict[T, T]) -> Generator[T, None, None]:
    """Encrypt with monoalphabetic substitution.

    Args:
        plaintext: Text to encrypt
        key: Substitution key dictionary

    Yields:
        Encrypted characters

    Raises:
        InvalidInputError: If key format is invalid
        CipherError: If encryption fails
    """
    if not isinstance(key, dict):
        msg = f"Key must be a dictionary, got {type(key).__name__}"
        raise InvalidInputError(msg)

    plaintext_seq = (
        list(plaintext) if not isinstance(plaintext, Sequence) else plaintext
    )
    validate_text_sequence(plaintext_seq)

    try:
        for e in plaintext_seq:
            if e not in key:
                msg = f"Plaintext symbol '{e}' not found in substitution key"
                raise CipherError(msg, cipher_type="monoalphabetic")
            yield key[e]
    except Exception as exc:
        if isinstance(exc, CipherError | InvalidInputError):
            raise
        msg = f"Monoalphabetic encryption failed: {exc}"
        raise CipherError(msg, cipher_type="monoalphabetic") from exc


def reverse_key(key: dict[T, T]) -> dict[T, T]:
    """Take a dict containing all elements and reverses the index and the value.

    Args:
        key: Dictionary to reverse

    Returns:
        Reversed dictionary

    Raises:
        InvalidInputError: If key format is invalid
        CipherError: If key contains duplicate values
    """
    if not isinstance(key, dict):
        msg = f"Key must be a dictionary, got {type(key).__name__}"
        raise InvalidInputError(msg)

    output: dict[T, T] = {}
    for k, v in key.items():
        if v in output:
            msg = f"Key contains duplicate value '{v}', cannot reverse"
            raise CipherError(msg, cipher_type="monoalphabetic")
        output[v] = k
    return output


def masc_decrypt(ciphertext: Iterable[T], key: dict[T, T]) -> Generator[T, None, None]:
    """Decrypt monoalphabetic substitution.

    NOTE: key input is the same as for encryption, this function will reverse the key.
    """
    reversed_key: dict[T, T] = reverse_key(key)
    for e in ciphertext:
        yield reversed_key[e]


def atbashkey(alphabet: Sequence[T]) -> dict[T, T]:
    """Generate a key that reverses everything in the alphabet"""
    key: dict[T, T] = {}
    for k, r in zip(alphabet, reversed(alphabet)):
        key[k] = r
    return key


def randomkey(alphabet: Sequence[T]) -> dict[T, T]:
    """Generate a random key for use in the previous functions."""
    key: dict[T, T] = {}
    shuffled = random.sample(alphabet, len(alphabet))
    for k, v in zip(alphabet, shuffled):
        key[k] = v
    return key


def shiftedkey(alphabet: Sequence[T], shift: int = 3) -> dict[T, T]:
    """Generate a shifted key for use in the previous functions.

    Use `3` for Caesar and `13` for ROT13.
    """
    key: dict[T, T] = {}
    for i, e in enumerate(alphabet):
        key[e] = alphabet[(i + shift) % len(alphabet)]
    return key


def affinekey(alphabet: Sequence[T], a: int = 3, b: int = 8) -> dict[T, T]:
    """Generate an affine key for use in the previous functions.

    Args:
        alphabet: The alphabet to use
        a: Multiplicative parameter (must be coprime to alphabet length)
        b: Additive parameter

    Returns:
        Affine cipher key dictionary

    Raises:
        InvalidInputError: If parameters are invalid
        KeyError: If 'a' is not coprime with alphabet length
    """
    validate_alphabet(alphabet)

    if not isinstance(a, int) or not isinstance(b, int):
        msg = "Parameters 'a' and 'b' must be integers"
        raise InvalidInputError(msg)

    key: dict[T, T] = {}
    for i, e in enumerate(alphabet):
        key[e] = alphabet[(a * i + b) % len(alphabet)]

    if set(key.keys()) != set(key.values()):
        msg = f"Invalid Affine cipher parameter: a={a} is not coprime with alphabet length {len(alphabet)}"
        raise AldegondeKeyError(
            msg,
            key=a,
            cipher_type="affine",
        )

    return key


def mixedalphabet(alphabet: Sequence[T], keyword: Sequence[T]) -> list[T]:
    """Return a custom alphabet based on a keyword.

    Args:
        alphabet: Base alphabet
        keyword: Keyword to use for alphabet mixing

    Returns:
        Mixed alphabet as a list

    Raises:
        InvalidInputError: If keyword contains invalid characters

    Example:
        keyword:  PAULBRANDT
        alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZ
        returns:  PAULBRNDTCEFGHIJKMOQSVWXYZ
    """
    validate_alphabet(alphabet)

    alphabet_set = set(alphabet)
    invalid_chars = [letter for letter in keyword if letter not in alphabet_set]
    if invalid_chars:
        msg = f"Keyword contains characters not in alphabet: {invalid_chars}"
        raise InvalidInputError(msg)

    output: list[T] = []
    for letter in keyword:
        if letter not in output:
            output.append(letter)
    for letter in alphabet:
        if letter not in output:
            output.append(letter)

    return output


def mixedalphabet2key(
    plainalphabet: Sequence[T],
    cipheralphabet: Sequence[T],
) -> dict[T, T]:
    """
    turn an alphabet into a dict structure
    """
    out: dict[T, T] = {}
    for p, c in zip(plainalphabet, cipheralphabet):
        out[p] = c
    return out


def cycles(key: dict[T, T]) -> list[list[T]]:
    """
    TODO: analyze a key to determine its cycles
    example, key FLYINGSAUCERBDHJKMOPQTVWXZ
    has cycles: (AFGSOH) (BLRM) (CYXWVTPJ) (DIUQKEN) (Z)
    """
    alphabet: list[T] = list(key.keys())
    solved: set[T] = set()
    loops: list[list[T]] = []
    for letter in alphabet:
        if letter in solved:
            continue
        loop: list[T] = [letter]
        nextletter = key[letter]
        while nextletter != loop[0]:
            loop.append(nextletter)
            solved.add(nextletter)
            nextletter = key[nextletter]
        loops.append(loop)
    return loops
