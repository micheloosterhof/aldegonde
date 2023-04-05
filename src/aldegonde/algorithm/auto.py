"""
ciphertext autokey variations
"""

from collections.abc import Sequence

from aldegonde.algorithm.pasc import reverse_tr, T, TR


def ciphertext_autokey_encrypt(
    plaintext: Sequence[T], primer: Sequence[T], tr: TR
) -> list[T]:
    """
    Ciphertext Autokey Encryption
    """
    key: list = list(primer)
    output: list[T] = []
    for i, e in enumerate(plaintext):
        c = tr[key[i]][e]
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_decrypt(
    ciphertext: Sequence[T], primer: Sequence[T], tr: TR
) -> list[T]:
    """
    Ciphertext Autokey Decryption
    """
    rtr: TR[T] = reverse_tr(tr)
    key: list[T] = list(primer) + list(ciphertext)
    output: list[T] = []
    for i, e in enumerate(ciphertext):
        output.append(rtr[key[i]][e])
    return output


def plaintext_autokey_encrypt(
    plaintext: Sequence[T], primer: Sequence[T], tr: dict[T, dict[T, T]]
) -> Sequence:
    """
    Plaintext Autokey Encryption
    """
    key: list[T] = list(primer) + list(plaintext)
    output: list[T] = []
    for i, e in enumerate(plaintext):
        output.append(tr[key[i]][e])
    return output


def plaintext_autokey_decrypt(
    ciphertext: Sequence, primer: Sequence, tr: dict[T, dict[T, T]]
) -> Sequence:
    """
    Plaintext Autokey Decryption primitive P[i] = DF(C[i], P[i-1])
    """
    rtr = reverse_tr(tr)
    key: list = list(primer)
    output: list = []
    for i, e in enumerate(ciphertext):
        c = rtr[key[i]][e]
        output.append(c)
        key.append(c)
    return output
