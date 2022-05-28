"""Class to group information about a sequence.
"""

from typing import Optional
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
        alphabet: Optional[list[str]] = None,
    ) -> None:
        """
        Args:
            text: The text
            data: Raw elements as indices to the alphabet
        """
        if text is not None and data is not None:
            raise TypeError("Either construct with data or text, not both")

        if alphabet != None:
            self.alphabet = abc.Alphabet(alphabet)
        else:
            self.alphabet = abc.Alphabet()

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
            for c in self.data:
                self.text += self.alphabet.i2a(c)
        else:
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

    def __getitem__(self, key: int) -> int:
        """
        Return numerical index of character at this position like a normal sequence
        """
        return self.data[key]

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

    def __str__(self) -> str:
        """ """
        return self.restore_punctuation()

    def append(self, item):
        if item.alphabet != self.alphabet:
            raise TypeError("Alphabets don't match")
        self.text = ""
        self.data.append(item.data)

    #    def __add__(self, other):
    #        if other.alphabet != self.alphabet:
    #            raise TypeError("Alphabets don't match")
    #        return Sequence(self.data + other.data, alphabet=self.alphabet)

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
