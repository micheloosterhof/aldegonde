"""monoalphabetic substitution cipher.

This contains all ciphers of this type. This includes Caesar, ROT13, Affine ciphers, etc
All are monoalphabetic 
"""


from collections.abc import Sequence
import random
from typing import TypeVar

T = TypeVar("T")


def masc_encrypt(plaintext: Sequence[T], key: dict[T, T]) -> tuple[T, ...]:
    """Encrypt with monalphabetic substitution."""
    return tuple(key[e] for e in plaintext)


def reverse_key(key: dict[T, T]) -> dict[T, T]:
    """Take a dict containing all elements and reverses the index and the value.

    Returns output if the input contains valid values, else raises ValueError.
    """
    output: dict[T, T] = {}
    for k, v in key.items():
        output[v] = k
    return output


def masc_decrypt(ciphertext: Sequence[T], key: dict[T, T]) -> tuple[T, ...]:
    """Decrypt monoalphabetic substitution.

    NOTE: key input is the same as for encryption, this function will reverse the key.
    """
    reversed_key: dict[T, T] = reverse_key(key)
    return tuple(reversed_key[e] for e in ciphertext)


def randomkey(alphabet: Sequence[T]) -> dict[T, T]:
    """Generate a random key for use in the previous functions."""
    key: dict[T, T] = {}
    shuffled = random.sample(alphabet, len(alphabet))
    for k, v in zip(alphabet, shuffled, strict=True):
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

    Parameter A must be coprime to the alphabet length to generate a valid encoding.
    """
    key: dict[T, T] = {}
    for i, e in enumerate(alphabet):
        key[e] = alphabet[(a * i + b) % len(alphabet)]
    if set(key.keys()) != set(key.values()):
        print(f"{key.items()} {key.values()}")
        raise ValueError(
            "Invalid Affine cipher parameter: A={a} is not coprime with the size of the alphabet {len(alphabet)}"
        )
    return key


def keywordkey(alphabet: Sequence[T], keyword: Sequence[T]) -> list[T]:
    """Return a custom alphabet based on a keyword.

    example: keyword:  PAULBRANDT
             alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZ
             returns:  PAULBRNDTCEFGHIJKMOQSVWXYZ
    """
    output: list = []
    assert False not in [letter in alphabet for letter in keyword]

    for letter in keyword:
        if letter not in output:
            output.append(letter)
    for letter in alphabet:
        if letter not in output:
            output.append(letter)

    assert len(output) == len(alphabet)
    return output
