# ABOUTME: Guards the Liber Primus transcription data files, which record
# ABOUTME: apostrophes that must never enter the rune stream or split a word.

import sys
from pathlib import Path

import pytest

from aldegonde.c3301 import CICADA_ALPHABET
from aldegonde.c3301 import LINE_WRAP as CICADA_WRAPS
from aldegonde.c3301 import MARKS as CICADA_MARKS

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402

DATA = ROOT / "data"

CORPUS_FILES = [
    "liber-primus__transcription--master.txt",
    "page0-58.txt",
    "page0-56.txt",
]

# The four contraction words, keyed by the page image they appear on. Each is a
# complete word: an apostrophe with exactly one rune after it.
CONTRACTIONS = {
    "4.jpg": "ᛗᛉᛁ'ᚹ",
    "21.jpg": "ᚫᚩ'ᚣ",
    "35.jpg": "ᛈᛖ'ᛏ",
    "41.jpg": "ᛉᛚᛄ'ᚳ",
}

# Quotation marks, recovered from the page scans alongside the apostrophes.
# Seven spans, so fourteen marks, all on pages 6 through 53.
QUOTE_COUNT = 14

# Clean corpus = sections 0-9 of page0-58.txt, excluding the solved AN END page
# and the plaintext Parable.
CLEAN_RUNES = 12956
CLEAN_WORDS = 2928
CLEAN_DOUBLETS = 86


@pytest.mark.parametrize("filename", CORPUS_FILES)
@pytest.mark.parametrize("page,word", CONTRACTIONS.items())
def test_contraction_recorded(filename: str, page: str, word: str) -> None:
    """Each contraction is transcribed with its apostrophe."""
    text = (DATA / filename).read_text()
    assert word in text, f"{filename} is missing the apostrophe on {page}"


@pytest.mark.parametrize("filename", CORPUS_FILES)
def test_no_stray_apostrophes(filename: str) -> None:
    """Only the four known contractions carry an apostrophe."""
    text = (DATA / filename).read_text()
    assert text.count("'") == len(CONTRACTIONS)


@pytest.mark.parametrize("filename", CORPUS_FILES)
def test_quotes_recorded(filename: str) -> None:
    """All seven quoted spans are transcribed."""
    text = (DATA / filename).read_text()
    assert text.count('"') == QUOTE_COUNT


def test_quotes_alternate() -> None:
    """Quotes open and close in strict alternation, so the spans nest.

    A mark preceded by a separator opens a span; one followed by a separator
    closes it. Decorative marks would not alternate.
    """
    text = (DATA / "page0-58.txt").read_text()
    kinds = []
    for i, char in enumerate(text):
        if char != '"':
            continue
        # a mark in either encoding, or a line wrap; taken from the library so
        # a change to the mark alphabet cannot silently break this test
        delims = CICADA_MARKS | CICADA_WRAPS
        opening = text[i - 1] in delims
        closing = text[i + 1] in delims
        assert opening != closing, f"mark at {i} is neither an open nor a close"
        kinds.append("open" if opening else "close")
    assert kinds == ["open", "close"] * (QUOTE_COUNT // 2)


def test_apostrophe_is_not_a_rune() -> None:
    """The apostrophe is punctuation, so it cannot reach the rune stream."""
    assert "'" not in CICADA_ALPHABET
    stream, _ = lp_corpus.load_clean()
    assert all(0 <= r < len(CICADA_ALPHABET) for r in stream)


def test_apostrophe_does_not_split_words() -> None:
    """Tokenization is unchanged: a contraction stays a single word."""
    stream, word_id = lp_corpus.load_clean()
    doublets = sum(1 for i in range(len(stream) - 1) if stream[i] == stream[i + 1])
    assert len(stream) == CLEAN_RUNES
    assert word_id[-1] + 1 == CLEAN_WORDS
    assert doublets == CLEAN_DOUBLETS
