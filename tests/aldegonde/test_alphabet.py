# ABOUTME: Tests the alphabet codec that converts symbols to integer indices
# ABOUTME: and back, including its rejection of unknown symbols and indices.
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from aldegonde import c3301
from aldegonde.alphabet import Alphabet
from aldegonde.exceptions import AlphabetError

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_encode_gives_position_in_alphabet() -> None:
    assert Alphabet("ABC").encode("CAB") == [2, 0, 1]


def test_decode_gives_symbol_at_position() -> None:
    assert Alphabet("ABC").decode([2, 0, 1]) == ["C", "A", "B"]


def test_size_is_number_of_symbols() -> None:
    assert len(Alphabet(ABC)) == 26


def test_symbols_keep_their_order() -> None:
    assert Alphabet("CAB").symbols == ("C", "A", "B")


def test_symbols_may_be_longer_than_one_character() -> None:
    alphabet = Alphabet(["TH", "E", "NG"])
    assert alphabet.encode(["NG", "TH"]) == [2, 0]
    assert alphabet.decode([1, 2]) == ["E", "NG"]


def test_index_and_symbol_convert_one_item() -> None:
    alphabet = Alphabet("ABC")
    assert alphabet.index("B") == 1
    assert alphabet.symbol(1) == "B"


@given(st.text(alphabet=ABC, max_size=100))
def test_decode_inverts_encode(text: str) -> None:
    alphabet = Alphabet(ABC)
    assert alphabet.decode(alphabet.encode(text)) == list(text)


def test_encode_agrees_with_rune_index() -> None:
    alphabet = Alphabet(c3301.CICADA_ALPHABET)
    assert len(alphabet) == 29
    assert alphabet.encode(c3301.CICADA_ALPHABET) == [
        c3301.r2i(rune) for rune in c3301.CICADA_ALPHABET
    ]


def test_unknown_symbol_is_rejected() -> None:
    with pytest.raises(AlphabetError, match="not in the alphabet"):
        Alphabet("ABC").encode("ABD")


@pytest.mark.parametrize("index", [-1, 3])
def test_index_outside_alphabet_is_rejected(index: int) -> None:
    with pytest.raises(AlphabetError, match="outside the alphabet"):
        Alphabet("ABC").decode([0, index])


def test_duplicate_symbols_are_rejected() -> None:
    with pytest.raises(AlphabetError, match="duplicate"):
        Alphabet("ABCA")
