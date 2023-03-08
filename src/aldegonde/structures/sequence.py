"""Class to group information about a sequence.
"""

import collections.abc
from typing import overload
from collections.abc import Iterator, Iterable

import aldegonde.structures.alphabet as alpha


class Sequence(collections.abc.Sequence[int], Iterable):
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
        text: str | None = None,
        data: list[int] | None = None,
        alphabet: alpha.Alphabet = alpha.Alphabet(alpha.LOWERCASE_ALPHABET),
    ) -> None:
        """
        Args:
            text: The text
            data: Raw elements as indices to the alphabet
        """
        if data:
            self.data = data.copy()
        else:
            self.data = []
        if text:
            self.text = text
        else:
            self.text = ""
        self.alphabet = alphabet

    @classmethod
    def fromlist(cls, data: list[int], alphabet: list[str]) -> "Sequence":
        """from list constructor"""
        text: str = ""
        abc = alpha.Alphabet(alphabet)
        for i in data:
            text += abc.i2a(i)
        return cls(text=text, data=data.copy(), alphabet=abc)

    @classmethod
    def fromstr(cls, text: str, alphabet: list[str]) -> "Sequence":
        """from str constructor"""
        abc = alpha.Alphabet(alphabet)
        data: list[int] = []
        skips: list[str] = []
        for symbol in text:
            try:
                data.append(abc.a2i(symbol))
            except KeyError:
                skips.append(symbol)
        if skips:
            print(f"skipped characters {repr(set(skips))}")
        return cls(text=text, data=data, alphabet=abc)

    def restore_punctuation(self) -> str:
        """
        Restore original punctuation
        """
        out: str = ""
        index: int = 0
        skips: list[str] = []
        for symbol in self.text:
            if symbol in self.alphabet:
                out += self.alphabet.i2a(self.data[index])
                index += 1
            else:
                skips.append(symbol)
                out += symbol
        if skips:
            print(f"skips: {repr(set(skips))}")
        return out

    @overload
    def __getitem__(self, key: int) -> int:
        ...

    @overload
    def __getitem__(self, key: slice) -> int | list[int]:
        ...

    def __getitem__(self, key: int | slice) -> int | list[int]:
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
        return "".join(map(self.alphabet.i2a, self.data))

    def index(self, value: int) -> int:
        # def index(self, value: int, start: int = ..., stop: int = ...) -> int:
        """
        return index of element
        """
        return self.data.index(value)

    def append(self, item: int) -> None:
        """append element"""
        if not isinstance(item, int):
            raise TypeError
        if item > len(self.alphabet):
            raise TypeError("Item outside alphabet")
        self.data.append(item)

    def __add__(self, other: "Sequence") -> "Sequence":
        if other.alphabet != self.alphabet:
            raise TypeError("Alphabets don't match")
        return Sequence(data=(self.data + other.data), alphabet=self.alphabet)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sequence):
            return NotImplemented
        try:
            if other.alphabet != self.alphabet:
                return False
        except AttributeError:
            return False
        if other.data != self.data:
            print(f"data mismatch {other.data} != {self.data}")
            return False
        return True

    def copy(self) -> "Sequence":
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone


class SequenceIterator(Iterator):
    """
    Iterator for Sequence
    """

    def __init__(self, obj: Sequence) -> None:
        self.idx: int = 0
        self.obj = obj

    def __next__(self) -> int:
        self.idx += 1
        try:
            return self.obj[self.idx - 1]
        except IndexError:
            raise StopIteration


def find(sequence: list[int], runes: list[int]) -> list[int]:
    """
    find `sequence` inside the list of `runes`, return array with indexes
    """
    results = []
    for index in range(0, len(runes) - len(sequence) + 1):
        if sequence == runes[index : index + len(sequence)]:
            results.append(index)
    return results
