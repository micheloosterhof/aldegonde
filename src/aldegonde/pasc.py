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


class Comparable(Protocol):
    def __lt__(self, __other: Any) -> bool:
        ...

    def __gt__(self, __other: Any) -> bool:
        ...


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
    """Polyalphabetic substitution."""
    for e, k in zip(plaintext, cycle(keyword)):
        yield tr[k][e]


def pasc_encrypt_interrupted(
    plaintext: Iterable[T],
    keyword: Sequence[T],
    tr: TR[T],
    ciphertext_interruptor: T | None = None,
    plaintext_interruptor: T | None = None,
) -> Generator[T, None, None]:
    """Polyalphabetic substitution."""
    assert ciphertext_interruptor is not None or plaintext_interruptor is not None
    keyword_index = 0
    for e in plaintext:
        key: T = keyword[keyword_index % len(keyword)]
        output = tr[key][e]
        keyword_index = keyword_index + 1
        if output == ciphertext_interruptor or e == plaintext_interruptor:
            keyword_index = 0
        yield output


# This is a good candidate for functool caching
def reverse_tr(tr: TR[T]) -> TR[T]:
    """Take a dict containing all elements and reverses the index and the value
    Returns output if the input contains valid values, else raises ValueError.
    """
    output: TR = defaultdict(dict)
    for keyword in tr:
        for k, v in tr[keyword].items():
            output[keyword][v] = k
        if len(output[keyword]) != len(tr[keyword]):
            msg = "TR ambiguous for key `{keyword}`"
            raise ValueError(msg)
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
