# ABOUTME: Guards the English-to-runeglish transliteration that builds the English
# ABOUTME: reference text for the experiments, so every rune can appear in it.

import sys
from pathlib import Path

import pytest

from aldegonde.c3301 import CICADA_ENGLISH_ALPHABET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))

import d5_partial_leak  # noqa: E402  # ty: ignore[unresolved-import]  # resolved by the sys.path bootstrap two lines above


@pytest.mark.parametrize("label", CICADA_ENGLISH_ALPHABET)
def test_every_rune_label_is_one_token(label: str) -> None:
    """Each rune's English label transliterates to exactly that rune."""
    assert d5_partial_leak.to_runeglish(label) == [label]


def test_ae_is_one_rune() -> None:
    assert d5_partial_leak.to_runeglish("AETHER") == ["AE", "TH", "E", "R"]
