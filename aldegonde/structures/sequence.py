"""Class to group information about a sequence.
"""

from typing import Optional
from . import alphabet as abc

class Sequence:
    """A sequence object, composed of plaintext or ciphertext
       It consists of elements, modeled as integers, and an alphabet of all possible options

    Example:
        >>> decryption = Sequence("plaintext")
    """

    def __init__(self, text: str = "", alphabet: Optional[list[str]] = None) -> None:
        """
        Args:
            text: The text
        """
        self.text: str = text
        self.elements: list[int] = []
        self.alphabet: abc.Alphabet

        if alphabet is not None:
            self.alphabet = abc.Alphabet(alphabet)
        else:
            self.alphabet = abc.Alphabet()

        for c in text:
            try:
                self.elements.append(self.alphabet.a2i(c))
            except KeyError:
                pass

    def restore_punctuation(self) -> str:
        """
        Restore original punctuation
        """
        out: str = ""
        count: int = 0
        for c in self.text:
            try:
                out += self.alphabet.i2a(self.elements[count])
                count += 1
            except IndexError:
                print("eek")
                out += c
        return out

    def __str__(self) -> str:
        """ """
        return self.restore_punctuation()
