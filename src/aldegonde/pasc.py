"""polyalphabetic substitution cipher.

This contains all ciphers of this type. This includes Vigenere, Beaufort, Variant Beaufort, 
Quagmire 1, 2, 3 and 4. And the generic polyalphabetic subsitution cipher.

All are polyalphabetic substitution ciphers with a fixed key length
"""

from collections.abc import Generator, Iterable, Sequence
from collections import defaultdict
from itertools import cycle
import random
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


def pasc_encrypt(
    plaintext: Iterable[T], keyword: Sequence[T], tr: TR[T]
) -> Generator[T, None, None]:
    """Polyalphabetic substitution."""
    for e, k in zip(plaintext, cycle(keyword)):
        yield tr[k][e]


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
            raise ValueError(f"TR ambiguous for key `{keyword}`")
    return output


def pasc_decrypt(
    ciphertext: Iterable[T], keyword: Sequence[T], tr: TR[T]
) -> Generator[T, None, None]:
    """Polyalphabetic substitution
    NOTE: tr input is the same as for encryption, this function will reverse the key.
    """
    reversed_tr: TR[T] = reverse_tr(tr)
    for e, k in zip(ciphertext, cycle(keyword)):
        yield reversed_tr[k][e]


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


def quagmire1_tr(alphabet: Sequence[T]) -> TR[T]:
    """ """
    tr: TR[T] = defaultdict(dict)
    for i, key in enumerate(sorted(alphabet)):
        for j, e in enumerate(sorted(alphabet)):
            tr[key][e] = alphabet[(i + j) % len(alphabet)]
    return tr


def doublekeywordtr(
    alphabet: Sequence[T], keyword1: Sequence[T], keyword2: Sequence[T]
) -> TR[T]:
    """
    i think this is actually quagmire 1
    """
    al1 = masc.mixedalphabet(alphabet, keyword1)
    al2 = masc.mixedalphabet(alphabet, keyword2)
    tr: TR[T] = defaultdict(dict)
    for i, e in enumerate(al1):
        for j, f in enumerate(al2):
            tr[e][f] = alphabet[(i + j) % len(alphabet)]
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
