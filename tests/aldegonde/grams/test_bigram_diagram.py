# ABOUTME: Tests for the bigram diagram helpers, covering the within-word
# ABOUTME: pairing that restricts bigrams to a single word at a chosen skip.
from aldegonde.grams.bigram_diagram import within_word_pairs


def test_within_word_pairs_skip_one() -> None:
    """Adjacent pairs are taken inside each word, never across the boundary."""
    words = [[1, 2, 3], [4, 5]]
    rows, columns = within_word_pairs(words, skip=1)
    assert rows == [1, 2, 4]
    assert columns == [2, 3, 5]


def test_within_word_pairs_larger_skip_drops_short_words() -> None:
    """A word shorter than skip+1 contributes no pair."""
    words = [[1, 2, 3], [4, 5]]
    rows, columns = within_word_pairs(words, skip=2)
    assert rows == [1]
    assert columns == [3]


def test_within_word_pairs_never_cross_boundary() -> None:
    """The last symbol of a word is never paired with the first of the next."""
    words = [[7, 8], [9, 10]]
    rows, columns = within_word_pairs(words, skip=1)
    assert (8, 9) not in list(zip(rows, columns))
