# ABOUTME: Converts between the symbols of an alphabet and the integer indices
# ABOUTME: 0..N-1 that the algebraic and table-based functions operate on.
"""Alphabet codec.

Functions that index tables or do arithmetic work on integers 0..N-1. An
Alphabet fixes the order of N symbols and converts text to those integers and
back. A symbol is any hashable value, so a multi-character token such as
"TH" is one symbol.

The order of the symbols is part of the encoding: the same text encoded under
two orders gives two different integer sequences.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from typing import Generic, TypeVar

from aldegonde.exceptions import AlphabetError
from aldegonde.validation import validate_alphabet

T = TypeVar("T", bound=Hashable)


class Alphabet(Generic[T]):
    """An ordered set of symbols with its integer encoding."""

    __slots__ = ("_indices", "_symbols")

    def __init__(self, symbols: Sequence[T]) -> None:
        """Fix the order of the symbols.

        Args:
            symbols: The symbols in index order, without duplicates

        Raises:
            AlphabetError: If there are fewer than 2 symbols or a duplicate
        """
        validate_alphabet(symbols)
        self._symbols: tuple[T, ...] = tuple(symbols)
        self._indices: dict[T, int] = {s: i for i, s in enumerate(self._symbols)}

    def __len__(self) -> int:
        """Return the number of symbols."""
        return len(self._symbols)

    @property
    def symbols(self) -> tuple[T, ...]:
        """The symbols in index order."""
        return self._symbols

    def index(self, symbol: T) -> int:
        """Return the index of a symbol.

        Args:
            symbol: A symbol of the alphabet

        Returns:
            Its index, from 0 to N-1

        Raises:
            AlphabetError: If the symbol is not in the alphabet
        """
        try:
            return self._indices[symbol]
        except KeyError:
            msg = f"Symbol {symbol!r} is not in the alphabet"
            raise AlphabetError(msg, alphabet=self._symbols) from None

    def symbol(self, index: int) -> T:
        """Return the symbol at an index.

        Args:
            index: An index from 0 to N-1

        Returns:
            The symbol at that index

        Raises:
            AlphabetError: If the index is outside the alphabet
        """
        if not 0 <= index < len(self._symbols):
            msg = f"Index {index} is outside the alphabet of size {len(self)}"
            raise AlphabetError(msg, alphabet=self._symbols)
        return self._symbols[index]

    def encode(self, text: Iterable[T]) -> list[int]:
        """Convert symbols to indices.

        Args:
            text: Symbols of the alphabet

        Returns:
            The index of each symbol, in order

        Raises:
            AlphabetError: If a symbol is not in the alphabet
        """
        return [self.index(symbol) for symbol in text]

    def decode(self, indices: Iterable[int]) -> list[T]:
        """Convert indices to symbols.

        Args:
            indices: Indices from 0 to N-1

        Returns:
            The symbol at each index, in order

        Raises:
            AlphabetError: If an index is outside the alphabet
        """
        return [self.symbol(index) for index in indices]
