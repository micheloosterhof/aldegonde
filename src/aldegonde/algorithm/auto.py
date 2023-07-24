"""ciphertext autokey variations."""

from collections.abc import Generator, Iterable, Sequence
from itertools import chain

from aldegonde.algorithm.pasc import reverse_tr, T, TR


def ciphertext_autokey_encrypt(
    plaintext: Iterable[T], primer: Sequence[T], tr: TR
) -> list[T]:
    """Ciphertext Autokey Encryption."""
    key: list = list(primer)
    output: list[T] = []
    for i, e in enumerate(plaintext):
        c = tr[key[i]][e]
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_decrypt(
    ciphertext: Sequence[T], primer: Sequence[T], tr: TR
) -> Generator[T, None, None]:
    """Ciphertext Autokey Decryption."""
    rtr: TR[T] = reverse_tr(tr)
    for e, k in zip(ciphertext, chain(primer, ciphertext)):
        yield rtr[k][e]


def plaintext_autokey_encrypt(
    plaintext: Sequence[T], primer: Sequence[T], tr: dict[T, dict[T, T]]
) -> Generator[T, None, None]:
    """Plaintext Autokey Encryption."""
    for e, k in zip(plaintext, chain(primer, plaintext)):
        yield tr[k][e]


def plaintext_autokey_decrypt(
    ciphertext: Iterable[T], primer: Sequence[T], tr: dict[T, dict[T, T]]
) -> Sequence:
    """Plaintext Autokey Decryption primitive P[i] = DF(C[i], P[i-1])."""
    rtr = reverse_tr(tr)
    key: list = list(primer)
    output: list = []
    for i, e in enumerate(ciphertext):
        c = rtr[key[i]][e]
        output.append(c)
        key.append(c)
    return output
