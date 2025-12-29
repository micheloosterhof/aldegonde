"""polyalphabetic substitution cipher.

This contains all ciphers of this type. This includes Vigenere, Beaufort, Variant Beaufort,
Quagmire 1, 2, 3 and 4. And the generic polyalphabetic subsitution cipher.

All are polyalphabetic substitution ciphers with a fixed key length
"""

import random
from collections import defaultdict
from collections.abc import Generator, Iterable, Sequence
from itertools import cycle
from typing import Any, Protocol, TypeVar

from aldegonde import masc
from aldegonde.exceptions import AldegondeKeyError, CipherError, InvalidInputError
from aldegonde.validation import (
    validate_key_length,
    validate_text_sequence,
)


class Comparable(Protocol):
    def __lt__(self, __other: Any, /) -> bool: ...

    def __gt__(self, __other: Any, /) -> bool: ...


T = TypeVar("T", bound=Comparable)

# the key here is tradionally called a Tabula Recta
# implemented as dict[T, dict[T, T]]
# the first key here is the letter of the keyword used for the polygraphic substitution.
# the second key is the plaintext being encrypted
TR = dict[T, dict[T, T]]

# There is a similar type, the `key table`. This contains all permutations to decrypt a text.
# It may have duplicates (for duplicate key letters) and probably will not have all key letters.
# The size is the period of the substitution
KT = dict[int, dict[T, T]]


def pasc_encrypt(
    plaintext: Iterable[T],
    keyword: Sequence[T],
    tr: TR[T],
) -> Generator[T, None, None]:
    """Polyalphabetic substitution.

    Args:
        plaintext: Text to encrypt
        keyword: Encryption key sequence
        tr: Tabula recta for the cipher

    Yields:
        Encrypted characters

    Raises:
        KeyError: If key is invalid
        CipherError: If encryption fails
    """
    # Convert to sequences for validation
    plaintext_seq = (
        list(plaintext) if not isinstance(plaintext, Sequence) else plaintext
    )
    validate_text_sequence(plaintext_seq)
    validate_key_length(keyword)

    try:
        for e, k in zip(plaintext_seq, cycle(keyword)):
            if k not in tr:
                msg = f"Key symbol '{k}' not found in tabula recta"
                raise AldegondeKeyError(
                    msg,
                    key=k,
                    cipher_type="polyalphabetic",
                )
            if e not in tr[k]:
                msg = f"Plaintext symbol '{e}' not found in tabula recta for key '{k}'"
                raise CipherError(msg, cipher_type="polyalphabetic")
            yield tr[k][e]
    except Exception as exc:
        if isinstance(exc, AldegondeKeyError | CipherError):
            raise
        msg = f"Encryption failed: {exc}"
        raise CipherError(msg, cipher_type="polyalphabetic") from exc


def pasc_encrypt_interrupted(
    plaintext: Iterable[T],
    keyword: Sequence[T],
    tr: TR[T],
    ciphertext_interruptor: T | None = None,
    plaintext_interruptor: T | None = None,
) -> Generator[T, None, None]:
    """Polyalphabetic substitution with interruptor.

    Args:
        plaintext: Text to encrypt
        keyword: Encryption key sequence
        tr: Tabula recta for the cipher
        ciphertext_interruptor: Symbol that resets key position in ciphertext
        plaintext_interruptor: Symbol that resets key position in plaintext

    Yields:
        Encrypted characters

    Raises:
        InvalidInputError: If no interruptor is specified
        KeyError: If key is invalid
        CipherError: If encryption fails
    """
    if ciphertext_interruptor is None and plaintext_interruptor is None:
        msg = "At least one interruptor (ciphertext or plaintext) must be specified"
        raise InvalidInputError(msg)

    plaintext_seq = (
        list(plaintext) if not isinstance(plaintext, Sequence) else plaintext
    )
    validate_text_sequence(plaintext_seq)
    validate_key_length(keyword)

    try:
        keyword_index = 0
        for e in plaintext_seq:
            key: T = keyword[keyword_index % len(keyword)]
            if key not in tr:
                msg = f"Key symbol '{key}' not found in tabula recta"
                raise AldegondeKeyError(
                    msg,
                    key=key,
                    cipher_type="polyalphabetic",
                )
            if e not in tr[key]:
                msg = (
                    f"Plaintext symbol '{e}' not found in tabula recta for key '{key}'"
                )
                raise CipherError(msg, cipher_type="polyalphabetic")

            output = tr[key][e]
            keyword_index = keyword_index + 1
            if output == ciphertext_interruptor or e == plaintext_interruptor:
                keyword_index = 0
            yield output
    except Exception as exc:
        if isinstance(exc, AldegondeKeyError | CipherError | InvalidInputError):
            raise
        msg = f"Interrupted encryption failed: {exc}"
        raise CipherError(msg, cipher_type="polyalphabetic") from exc


# This is a good candidate for functool caching
def reverse_tr(tr: TR[T]) -> TR[T]:
    """Take a dict containing all elements and reverses the index and the value.

    Args:
        tr: Tabula recta to reverse

    Returns:
        Reversed tabula recta

    Raises:
        InvalidInputError: If tabula recta format is invalid
        CipherError: If tabula recta is ambiguous
    """
    if not isinstance(tr, dict):
        msg = f"Tabula recta must be a dictionary, got {type(tr).__name__}"
        raise InvalidInputError(msg)

    output: TR[T] = defaultdict(dict)
    for keyword in tr:
        if not isinstance(tr[keyword], dict):
            msg = f"Inner tabula recta for key '{keyword}' must be a dictionary"
            raise InvalidInputError(msg)

        for k, v in tr[keyword].items():
            output[keyword][v] = k

        if len(output[keyword]) != len(tr[keyword]):
            msg = f"Tabula recta is ambiguous for key '{keyword}' - contains duplicate values"
            raise CipherError(msg, cipher_type="polyalphabetic")

    return output


def pasc_decrypt(
    ciphertext: Iterable[T],
    keyword: Sequence[T],
    tr: TR[T],
) -> Generator[T, None, None]:
    """Polyalphabetic substitution
    NOTE: tr input is the same as for encryption, this function will reverse the key.
    """
    reversed_tr: TR[T] = reverse_tr(tr)
    for e, k in zip(ciphertext, cycle(keyword)):
        yield reversed_tr[k][e]


def pasc_decrypt_interrupted(
    ciphertext: Iterable[T],
    keyword: Sequence[T],
    tr: TR[T],
    ciphertext_interruptor: T | None = None,
    plaintext_interruptor: T | None = None,
) -> Generator[T, None, None]:
    """Polyalphabetic substitution.
    NOTE: tr input is the same as for encryption, this function will reverse the key.
    """
    assert ciphertext_interruptor is not None or plaintext_interruptor is not None
    reversed_tr: TR[T] = reverse_tr(tr)
    keyword_index = 0
    for e in ciphertext:
        key: T = keyword[keyword_index % len(keyword)]
        output = reversed_tr[key][e]
        keyword_index = keyword_index + 1
        if e == ciphertext_interruptor or output == plaintext_interruptor:
            keyword_index = 0
        yield output


def random_tr(alphabet: Sequence[T]) -> TR[T]:
    """Generate a random TR for use in the previous functions."""
    tr: TR[T] = defaultdict(dict)
    for key in alphabet:
        shuffled = random.sample(alphabet, len(alphabet))
        for k, v in zip(alphabet, shuffled, strict=True):
            tr[key][k] = v
    return tr


def vigenere_tr(alphabet: Sequence[T]) -> TR[T]:
    """Generate a Vigenere tabula recta with the standard alphabet."""
    tr: TR[T] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(i + j) % len(alphabet)]
    return tr


def beaufort_tr(alphabet: Sequence[T]) -> TR[T]:
    """Generate a Beaufort tabula recta (reversed alphabet)."""
    tr: TR[T] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(i - j) % len(alphabet)]
    return tr


def variantbeaufort_tr(alphabet: Sequence[T]) -> TR[T]:
    """Generate a Variant Beaufort tabula recta."""
    tr: TR[T] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(j - i) % len(alphabet)]
    return tr


def quagmire1_tr(
    alphabet: Sequence[T],
    keyword: Sequence[T],
    key: Sequence[T],
) -> TR[T]:
    """https://www.cryptogram.org/downloads/aca.info/ciphers/QuagmireI.pdf
    keyword is the mixed alphabet for the plaintext
    key is the equivalent of the vigenere keyword
    the indicator letter is always the first in the alphabet, this could be a future parameter
    key could be optional, we can generate the entire TR without it but we would generate unused lines
    """
    al1 = masc.mixedalphabet(alphabet, keyword)
    tr: TR[T] = defaultdict(dict)
    index: int = al1.index(alphabet[0])
    for i, e in enumerate(alphabet):
        if e in key:
            for j, f in enumerate(al1):
                tr[e][f] = alphabet[(i + j - index) % len(alphabet)]
    return tr


def quagmire2_tr(
    alphabet: Sequence[T],
    keyword: Sequence[T],
    key: Sequence[T],
    indicator: T,
) -> TR[T]:
    """https://www.cryptogram.org/downloads/aca.info/ciphers/QuagmireII.pdf"""
    al1 = masc.mixedalphabet(alphabet, keyword)
    tr: TR[T] = defaultdict(dict)
    index: int = alphabet.index(indicator)
    for e in alphabet:
        if e in key:
            idx2: int = al1.index(e)
            for j, f in enumerate(alphabet):
                tr[e][f] = al1[(j - index + idx2) % len(alphabet)]
    return tr


def quagmire3_tr(alphabet: Sequence[T]) -> TR[T]:
    """https://www.cryptogram.org/downloads/aca.info/ciphers/QuagmireIII.pdf"""
    tr: TR[T] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(i + j) % len(alphabet)]
    return tr


def quagmire4_tr(
    alphabet: Sequence[T],
    ptkeyword: Sequence[T],
    ctkeyword: Sequence[T],
    key: Sequence[T],
    indicator: T,
) -> TR[T]:
    """https://www.cryptogram.org/downloads/aca.info/ciphers/QuagmireIV.pdf"""
    ptmixal = masc.mixedalphabet(alphabet, ptkeyword)
    ctmixal = masc.mixedalphabet(alphabet, ctkeyword)
    tr: TR[T] = defaultdict(dict)
    index: int = ptmixal.index(indicator)
    for _i, e in enumerate(alphabet):
        if e in key:
            idx2: int = ctmixal.index(e)
            for j, f in enumerate(ptmixal):
                tr[e][f] = ctmixal[(j - index + idx2) % len(alphabet)]
    return tr


def print_tr(tr: TR[T]) -> None:
    """Print TR."""
    print("  | ", end="")
    for i in tr:
        for j in tr[i]:
            print(f"{j} ", end="")
        break
    print("|\n--+-" + (len(tr.keys()) * "--") + "+-")
    for i in tr:
        print(f"{i} | ", end="")
        for j in tr[i]:
            print(f"{tr[i][j]} ", end="")
        print("|")
