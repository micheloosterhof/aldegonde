"""polyalphabetic substitution cipher

This contains all ciphers of this type. This includes Vigenere, Beaufort, Variant Beaufort, 
Quagmire 1, 2, 3 and 4. And the generic polyalphabetic subsitution cipher.

All are polyalphabetic substitution ciphers with a fixed key length
"""

from collections.abc import Sequence
from collections import defaultdict
import random
from typing import TypeVar

T = TypeVar("T")

# the key here is tradionally called a Tabula Recta
# implemented as dict[T, dict[T, T]]
# could also implement as dict[int, dict[T, T]]
# because it's periodic and we could numerically index
# for autokey, we will need dict[T, dict[T, T]], might as well standardize


def pasc_encrypt(
    plaintext: Sequence[T], keyword: Sequence[T], tr: dict[T, dict[T, T]]
) -> list[T]:
    """
    Polyalphabetic substitution
    """
    ciphertext: list = []
    for i, e in enumerate(plaintext):
        ciphertext.append(tr[keyword[i % len(keyword)]][e])
    return ciphertext


# This is a good candidate for functool caching
def reverse_tr(tr: dict[T, dict[T, T]]) -> dict[T, dict[T, T]]:
    """
    Takes a dict containing all elements and reverses the index and the value
    Returns output if the input contains valid values, else raises ValueError
    """
    output: dict[T, dict[T, T]] = defaultdict(dict)
    for keyword in tr:
        for k, v in tr[keyword].items():
            output[keyword][v] = k
    return output


def pasc_decrypt(
    ciphertext: Sequence[T], keyword: Sequence[T], tr: dict[T, dict[T, T]]
) -> list[T]:
    """Polyalphabetic substitution
    NOTE: tr input is the same as for encryption, this function will reverse the key
    """
    reversed_tr: dict[T, dict[T, T]] = reverse_tr(tr)
    plaintext: list = []
    for i, e in enumerate(ciphertext):
        plaintext.append(reversed_tr[keyword[i % len(keyword)]][e])
    return plaintext


def random_tr(alphabet: Sequence[T]) -> dict[T, dict[T, T]]:
    """Generate a random TR for use in the previous functions"""
    tr: dict[T, dict[T, T]] = defaultdict(dict)
    for key in alphabet:
        shuffled = random.sample(alphabet, len(alphabet))
        for k, v in zip(alphabet, shuffled):
            tr[key][k] = v
    return tr


def vigenere_tr(alphabet: Sequence[T]) -> dict[T, dict[T, T]]:
    """
    Generate a Vigenere tabula recta with the standard alphabet
    """
    tr: dict[T, dict[T, T]] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(i + j) % len(alphabet)]
    return tr


def beaufort_tr(alphabet: Sequence[T]) -> dict[T, dict[T, T]]:
    """
    Generate a Beaufort tabula recta (reversed alphabet)
    """
    tr: dict[T, dict[T, T]] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(i - j) % len(alphabet)]
    return tr


def variantbeaufort_tr(alphabet: Sequence[T], shift: int = 3) -> dict[T, dict[T, T]]:
    """
    Generate a Variant Beaufort tabula recta
    """
    tr: dict[T, dict[T, T]] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(j - i) % len(alphabet)]
    return tr


def quagmire1_tr(alphabet: Sequence[T]) -> dict[T, dict[T, T]]:
    """
    THIS IS INCORRECT
    """
    tr: dict[T, dict[T, T]] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = sorted(alphabet)[(i + j) % len(alphabet)]
    return tr


def quagmire3_tr(alphabet: Sequence[T]) -> dict[T, dict[T, T]]:
    """ """
    tr: dict[T, dict[T, T]] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(i + j) % len(alphabet)]
    return tr
