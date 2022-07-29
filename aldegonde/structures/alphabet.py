"""Class to group information about alphabets.
"""

from typing import Union, overload

LOWERCASE_ALPHABET = [chr(code) for code in range(ord("a"), ord("z") + 1)]
UPPERCASE_ALPHABET = [chr(code) for code in range(ord("A"), ord("Z") + 1)]
DIGITS_ALPHABET = [chr(code) for code in range(ord("0"), ord("9") + 1)]
BASE62_ALPHABET = LOWERCASE_ALPHABET + UPPERCASE_ALPHABET + DIGITS_ALPHABET


class Alphabet:
    """
    Example:
        >>> abc = Alphabet(LOWERCASE_ALPHABET)
    """

    def __init__(self, data: Union[list[str], str, None] = UPPERCASE_ALPHABET) -> None:
        """ """
        if isinstance(data, list):
            self.alphabet = data
        elif isinstance(data, str):
            self.data = list(data)
        elif data is None:
            self.data = []
        else:
            raise TypeError

        self.alphabetsize = len(self.alphabet)
        self.reversealphabet: dict[str, int] = {}
        for i, e in enumerate(self.alphabet):
            self.reversealphabet[e] = i

    def __len__(self) -> int:
        return self.alphabetsize

    @overload
    def __getitem__(self, key: int) -> str:
        ...

    @overload
    def __getitem__(self, key: slice) -> Union[str, list[str]]:
        ...

    def __getitem__(self, key: Union[int, slice]) -> Union[str, list[str]]:
        """
        Return character at this position like a normal sequence
        """
        return self.alphabet.__getitem__(key)

    def __repr__(self) -> str:
        return "Alphabet(" + "".join(self.alphabet) + ")"

    def __str__(self) -> str:
        """ """
        return "".join(self.alphabet) + f" ({len(self.alphabet)} symbols)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Alphabet):
            return NotImplemented
        return self.alphabet == other.alphabet

    def __iter__(self):
        """
        TODO: use separate iterator object
        """
        return AlphabetIterator(self)

    def a2i(self, a: str) -> int:
        i = self.reversealphabet[a]
        if i is not None:
            return self.reversealphabet[a]
        else:
            raise KeyError("Character not in alphabet")

    def i2a(self, i: int) -> str:
        try:
            return self.alphabet[i]
        except IndexError:
            raise KeyError("Character not in alphabet")


class AlphabetIterator:
    """
    Iterator for alphabet
    """

    def __init__(self, obj: Alphabet) -> None:
        self.idx: int = 0
        self.obj = obj

    def __next__(self):
        self.idx += 1
        try:
            return self.obj[self.idx - 1]
        except IndexError:
            raise StopIteration


def a2i(text: str) -> list[int]:
    """
    LETTER 2 INTEGER [A-Z] -> [0-25]
    """
    output: list[int] = []
    for c in text:
        output.append(ord(c) - ord("A"))
    return output


def i2a(text: list[int]) -> str:
    """
    LETTER 2 ASCII [0-25] -> [A-Z]
    """
    output: str = ""
    for c in text:
        output += chr(ord("A") + c)
    return output


def alphabet(text: list[int]) -> list[int]:
    """
    Find all unique values in a sequence or list
    """
    return sorted(list(set(text)))


def keyword_to_mixed_alphabet(keyword: list[int]) -> Alphabet:
    """
    construct alphabet order based on keyword
    example:    keyword_to_alphabet(a2i("HYDRAULIC"))
    """
    alphabet = Alphabet(keyword)
    return alphabet
