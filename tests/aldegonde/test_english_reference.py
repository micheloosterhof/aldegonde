# ABOUTME: Guards the English-to-runeglish transliteration that builds the English
# ABOUTME: reference text for the experiments, so every rune can appear in it.

import sys
from pathlib import Path

import pytest

from aldegonde.c3301 import CICADA_ENGLISH_ALPHABET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))

import d5_partial_leak  # noqa: E402  # ty: ignore[unresolved-import]  # resolved by the sys.path bootstrap two lines above
import doublet_design_intensity  # noqa: E402  # ty: ignore[unresolved-import]
import ea_crib  # noqa: E402  # ty: ignore[unresolved-import]
import keyed_square_doublet  # noqa: E402  # ty: ignore[unresolved-import]
import order5_permutation_search  # noqa: E402  # ty: ignore[unresolved-import]
import product_form_ciphers  # noqa: E402  # ty: ignore[unresolved-import]
import quagmire_bigram_test  # noqa: E402  # ty: ignore[unresolved-import]
import runeglish_frequency  # noqa: E402  # ty: ignore[unresolved-import]
import verify_quagmire_hypothesis  # noqa: E402  # ty: ignore[unresolved-import]

from aldegonde import c3301  # noqa: E402

LABEL_INDEX = {label: i for i, label in enumerate(CICADA_ENGLISH_ALPHABET)}

# Every English transliteration the experiments define, as a function from a
# word to rune indices.
AS_INDICES = {
    "d5_partial_leak": lambda word: [
        LABEL_INDEX[label] for label in d5_partial_leak.to_runeglish(word)
    ],
    "runeglish_frequency": lambda word: c3301.RUNES.encode(
        runeglish_frequency.english_to_runeglish(word)
    ),
    "quagmire_bigram_test": lambda word: c3301.RUNES.encode(
        quagmire_bigram_test.english_to_runeglish(word)
    ),
    "verify_quagmire_hypothesis": lambda word: c3301.RUNES.encode(
        verify_quagmire_hypothesis.english_to_runeglish(word)
    ),
    "ea_crib": lambda word: c3301.RUNES.encode(ea_crib.to_runeglish(word)),
    "order5_permutation_search": order5_permutation_search.transliterate,
    "doublet_design_intensity": doublet_design_intensity.transliterate,
    "keyed_square_doublet": keyed_square_doublet.transliterate,
    "product_form_ciphers": product_form_ciphers.transliterate,
}

# Transliterations that give None for a word holding anything but letters.
REFUSES_NON_LETTERS = {
    "ea_crib": ea_crib.to_runeglish,
    "order5_permutation_search": order5_permutation_search.transliterate,
    "doublet_design_intensity": doublet_design_intensity.transliterate,
    "keyed_square_doublet": keyed_square_doublet.transliterate,
    "product_form_ciphers": product_form_ciphers.transliterate,
}


@pytest.mark.parametrize("module", AS_INDICES)
@pytest.mark.parametrize(
    "word", ["THINGS", "BEING", "QUESTION", "AETHEREAL", "BEHAVIORS", "KNOWLEDGE"]
)
def test_experiments_spell_as_the_library_does(module: str, word: str) -> None:
    assert AS_INDICES[module](word) == c3301.encode_english(word)


@pytest.mark.parametrize("module", REFUSES_NON_LETTERS)
@pytest.mark.parametrize("word", ["DON'T", "CAFÉ", "A1"])
def test_a_word_with_a_non_letter_is_refused(module: str, word: str) -> None:
    assert REFUSES_NON_LETTERS[module](word) is None


@pytest.mark.parametrize("label", CICADA_ENGLISH_ALPHABET)
def test_every_rune_label_is_one_token(label: str) -> None:
    """Each rune's English label transliterates to exactly that rune."""
    assert d5_partial_leak.to_runeglish(label) == [label]


def test_ae_is_one_rune() -> None:
    assert d5_partial_leak.to_runeglish("AETHER") == ["AE", "TH", "E", "R"]
