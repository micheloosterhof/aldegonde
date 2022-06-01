"""Class to group information about a sequence.
"""

from typing import Optional, Union
from . import alphabet as abc


class Sequence:
    """A sequence object, composed of plaintext or ciphertext
    It consists of elements, modeled as integers, and an alphabet of all possible options

    Example:
        >>> decryption = Sequence(text="plaintext")
    """

    text: str = ""
    data: list[int] = []
    alphabet: abc.Alphabet

    def __init__(
        self,
        text: Optional[str] = None,
        data: Optional[list[int]] = None,
        alphabet: Union[list[str], str, abc.Alphabet, None] = None,
    ) -> None:
        """
        Args:
            text: The text
            data: Raw elements as indices to the alphabet
        """
        if text is not None and data is not None:
            raise TypeError("Either construct with data or text, not both")

        if isinstance(alphabet, abc.Alphabet):
            self.alphabet = alphabet
        if isinstance(alphabet, str) or isinstance(alphabet, list):
            self.alphabet = abc.Alphabet(alphabet)
        elif alphabet is None:
            self.alphabet = abc.Alphabet()
        else:
            raise TypeError

        if text is not None:
            self.data = []
            self.text = text
            skips = []
            for c in text:
                try:
                    self.data.append(self.alphabet.a2i(c))
                except KeyError:
                    skips.append(c)
                    pass
            print(f"skipped characters {set(skips)}")

        elif data is not None:
            self.data = list(data)
            self.text = ""
            for i in self.data:
                self.text += self.alphabet.i2a(i)
        else:
            self.data = []
            self.text = ""
            # empty array
            pass

    def restore_punctuation(self) -> str:
        """
        Restore original punctuation
        """
        out: str = ""
        count: int = 0
        for c in self.text:
            try:
                out += self.alphabet.i2a(self.data[count])
                count += 1
            except IndexError:
                print(f"unknown character {c}")
                out += c
        return out

    def __getitem__(self, key: Union[int, slice]):
        """
        Return character at this position like a normal sequence
        """
        return self.data.__getitem__(key)

    def __len__(self) -> int:
        """
        Number of elements
        """
        return len(self.data)

    def __repr__(self) -> str:
        return (
            "Sequence <data="
            + repr(self.data)
            + " alphabet="
            + repr(self.alphabet)
            + ">"
        )

    def __iter__(self):
        """
        TODO: use separate iterator object
        """
        self.idx = 0
        return self

    def __next__(self):
        """ """
        self.idx += 1
        try:
            return self.data[idx - 1]
        except:
            raise StopIteration

    def __str__(self) -> str:
        """ """
        return self.restore_punctuation()

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
        return Sequence(data=self.data + other.data, alphabet=self.alphabet)

    def __eq__(self, other):
        if other.alphabet != self.alphabet:
            return False
        if other.data != self.data:
            print(f"data mismatch {other.data} != {self.data}")
            return False
        return True

    def copy(self):
        newone = type(self)()
        newone.__dict__.update(self.__dict__)
        return newone
