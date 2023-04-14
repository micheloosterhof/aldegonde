"""polyalphabetic substitution cipher.

This contains all ciphers of this type. This includes Vigenere, Beaufort, Variant Beaufort, 
Quagmire 1, 2, 3 and 4. And the generic polyalphabetic subsitution cipher.

All are polyalphabetic substitution ciphers with a fixed key length
"""

from collections.abc import Sequence
from collections import defaultdict
import random
from typing import Any, Protocol, TypeVar


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


def pasc_encrypt(
    plaintext: Sequence[T], keyword: Sequence[T], tr: TR[T]
) -> tuple[T, ...]:
    """Polyalphabetic substitution."""
    return tuple(tr[keyword[i % len(keyword)]][e] for i, e in enumerate(plaintext))


# This is a good candidate for functool caching
def reverse_tr(tr: TR[T]) -> TR[T]:
    """Take a dict containing all elements and reverses the index and the value
    Returns output if the input contains valid values, else raises ValueError.
    """
    output: TR = defaultdict(dict)
    for keyword in tr:
        for k, v in tr[keyword].items():
            output[keyword][v] = k
    return output


def pasc_decrypt(
    ciphertext: Sequence[T], keyword: Sequence[T], tr: TR[T]
) -> tuple[T, ...]:
    """Polyalphabetic substitution
    NOTE: tr input is the same as for encryption, this function will reverse the key.
    """
    reversed_tr: TR[T] = reverse_tr(tr)
    return tuple(
        reversed_tr[keyword[i % len(keyword)]][e] for i, e in enumerate(ciphertext)
    )


def random_tr(alphabet: Sequence[T]) -> TR[T]:
    """Generate a random TR for use in the previous functions."""
    tr: TR[T] = defaultdict(dict)
    for key in alphabet:
        shuffled = random.sample(alphabet, len(alphabet))
        for k, v in zip(alphabet, shuffled):
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


def quagmire1_tr(alphabet: Sequence[T]) -> TR[T]:
    """ """
    tr: TR[T] = defaultdict(dict)
    for i, key in enumerate(sorted(alphabet)):
        for j, e in enumerate(sorted(alphabet)):
            tr[key][e] = alphabet[(i + j) % len(alphabet)]
    return tr


def quagmire2_tr(alphabet: Sequence[T]) -> TR[T]:
    """ """
    raise NotImplementedError


def quagmire3_tr(alphabet: Sequence[T]) -> TR[T]:
    """ """
    tr: TR[T] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(i + j) % len(alphabet)]
    return tr


def quagmire4_tr(alphabet: Sequence[T]) -> TR[T]:
    """ """
    raise NotImplementedError


def print_tr(tr: TR[T]) -> None:
    """Print TR."""
    print("  | ", end="")
    for i in tr.keys():
        for j in tr[i].keys():
            print(f"{j} ", end="")
        break
    print("|\n--+-" + (len(tr.keys()) * "--") + "+-")
    for i in tr.keys():
        print(f"{i} | ", end="")
        for j in tr[i].keys():
            print(f"{tr[i][j]} ", end="")
        print("|")
