"""Class to group information about a sequence.
"""

import collections.abc
from typing import Optional, Union, overload, Iterator, Iterable

import aldegonde.structures.alphabet as alpha

# TODO: can we inherit from abc.Sequence?


class Sequence(collections.abc.Sequence):
    """A sequence object, composed of plaintext or ciphertext
    It consists of elements, modeled as integers, and an alphabet of all possible symbols

    Example:
        >>> decryption = Sequence(text="plaintext")
    """

    text: str
    data: list[int]
    alphabet: alpha.Alphabet

    def __init__(
        self,
        text: str = None,
        data: list[int] = None,
        alphabet: alpha.Alphabet = alpha.LOWERCASE_ALPHABET,
    ) -> None:
        """
        Args:
            text: The text
            data: Raw elements as indices to the alphabet
        """
        self.alphabet = alphabet
        self.data = data
        self.text = text

    @classmethod
    def fromlist(cls, data: list[int], alphabet: list[str]) -> None:
        """from list constructor"""
        text: str = ""
        abc = alpha.Alphabet(alphabet)
        for i in data:
            text += abc.i2a(i)
        return cls(text=text, data=data.copy(), alphabet=abc)

    @classmethod
    def fromstr(cls, text: str, alphabet: list[str]) -> None:
        """from str constructor"""
        abc = alpha.Alphabet(alphabet)
        data = []
        skips = []
        for c in text:
            try:
                data.append(abc.a2i(c))
            except KeyError:
                skips.append(c)
                pass
        print(f"skipped characters {repr(set(skips))}")
        return cls(text=text, data=data, alphabet=abc)

    def restore_punctuation(self) -> str:
        """
        Restore original punctuation
        """
        out: str = ""
        count: int = 0
        skips: list = []
        for c in self.text:
            try:
                out += self.alphabet.i2a(self.data[count])
                count += 1
            except IndexError:
                skips.append(c)
                out += c
        print(f"skips: {repr(set(skips))}")
        return out

    @overload
    def __getitem__(self, key: int) -> int:
        ...

    @overload
    def __getitem__(self, key: slice) -> Union[int, list[int]]:
        ...

    def __getitem__(self, key: Union[int, slice]) -> Union[int, list[int]]:
        """Return character at this position like a normal sequence"""
        return self.data.__getitem__(key)

    def __len__(self) -> int:
        """Number of elements"""
        return len(self.data)

    def __repr__(self) -> str:
        return (
            "Sequence(data="
            + repr(self.data)
            + ", alphabet="
            + repr(self.alphabet)
            + ")"
        )

    def __iter__(self) -> Iterator[int]:
        """ """
        return SequenceIterator(self)

    def __str__(self) -> str:
        """ """
        if self.text:
            return self.restore_punctuation()
        else:
            return "".join(map(self.alphabet.i2a, self.data))

    def index(self, elem: int) -> int:
        """
        return index of element
        """
        return self.data.index(elem)

    def append(self, item):
        """ """
        if not isinstance(item, int):
            raise TypeError
        if item > len(self.alphabet):
            raise TypeError("Item outside alphabet")
        self.data.append(item)

    def __add__(self, other):
        if other.alphabet != self.alphabet:
            raise TypeError("Alphabets don't match")
        return Sequence(data=(self.data + other.data), alphabet=self.alphabet)

    def __eq__(self, other):
        try:
            if other.alphabet != self.alphabet:
                return False
        except AttributeError:
            return False
        if other.data != self.data:
            print(f"data mismatch {other.data} != {self.data}")
            return False
        return True

    def copy(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone


class SequenceIterator:
    """
    Iterator for Sequence
    """

    def __init__(self, obj: Sequence) -> None:
        self.idx: int = 0
        self.obj = obj

    def __next__(self):
        self.idx += 1
        try:
            return self.obj[self.idx - 1]
        except IndexError:
            raise StopIteration


def find(sequence: list[int], runes: list[int]) -> list[int]:
    """
    find `sequence` inside the list of `runes`, return array with indexes
    """
    N = len(runes)
    results = []
    for index in range(0, N - len(sequence) + 1):
        if sequence == runes[index : index + len(sequence)]:
            results.append(index)
    return results
