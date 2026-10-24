# ABOUTME: Tests for c3301.tokenize, the one tokenizer for the transcription,
# ABOUTME: pinning the counts every recorded Liber Primus number depends on.
from collections import Counter
from pathlib import Path

import pytest

from aldegonde import c3301

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "page0-56.txt"
R = c3301.CICADA_ALPHABET


def test_marks_end_words_and_wraps_do_not() -> None:
    text = R[0] + R[1] + "①" + R[2] + "/\n" + R[3] + "④" + R[4]
    tok = c3301.tokenize(text)
    assert tok.words() == [[0, 1], [2, 3], [4]]
    assert tok.closing == ["①", "④", ""]
    assert tok.line == [0, 0, 0, 1, 1]


def test_structure_characters_end_words_and_count_pages_and_sections() -> None:
    text = R[0] + "%" + R[1] + "&" + R[2] + "$" + R[3] + "$" + "%" + R[4]
    tok = c3301.tokenize(text)
    assert tok.words() == [[0], [1], [2], [3], [4]]
    assert tok.closing == ["%", "&", "", "", ""]
    assert tok.page == [0, 1, 1, 1, 2]
    assert tok.section == [0, 0, 0, 1, 2]


def test_join_pages_runs_a_word_through_a_bare_page_break() -> None:
    text = R[0] + "%" + R[1] + "①" + R[2] + "%" + R[3]
    cut = c3301.tokenize(text)
    joined = c3301.tokenize(text, join_pages=True)
    assert cut.words() == [[0], [1], [2], [3]]
    assert joined.words() == [[0, 1], [2, 3]]
    assert joined.page == [0, 1, 1, 2]


def test_sections_filter_counts_only_rune_bearing_sections() -> None:
    text = "$$" + R[0] + "$" + "12" + "$" + R[1] + "$" + R[2]
    tok = c3301.tokenize(text, sections=[1])
    assert tok.stream == [1]
    assert tok.section == [1]


def test_latin_annotations_and_apostrophes_are_not_boundaries() -> None:
    text = R[0] + "'" + R[1] + "DsW" + R[2]
    assert c3301.tokenize(text).words() == [[0, 1, 2]]


def test_numerals_and_quotes_end_words() -> None:
    text = R[0] + '"' + R[1] + "3" + R[2]
    tok = c3301.tokenize(text)
    assert tok.words() == [[0], [1], [2]]
    assert tok.closing == ['"', "3", ""]


def test_circled_marks_split_words() -> None:
    # Regression: a literal class of legacy marks stopped matching when the
    # transcription moved to circled numerals and returned 60 words.
    text = "①".join(R[i] for i in range(29))
    assert len(c3301.tokenize(text).words()) == 29


@pytest.mark.skipif(not CLEAN.exists(), reason="corpus file not checked out")
def test_clean_corpus_counts() -> None:
    tok = c3301.tokenize(CLEAN.read_text(encoding="utf-8"), sections=range(10))
    assert len(tok.stream) == 12956
    assert tok.word[-1] + 1 == 2928
    doublets = sum(a == b for a, b in zip(tok.stream, tok.stream[1:], strict=False))
    assert doublets == 86
    assert tok.page[-1] == 55
    assert tok.section[-1] == 9
    assert Counter(tok.closing)["①"] == 2718
    joined = c3301.tokenize(CLEAN.read_text(encoding="utf-8"), join_pages=True)
    assert joined.word[-1] + 1 == 2896
    assert joined.stream == tok.stream
