from aldegonde.stats.ngrams import (
    iterngram_positions,
    iterngrams,
    ngram_distribution,
    ngram_positions,
    ngrams,
)

uniq = [0, 1, 2, 3, 4]
string = "ABCDEF"


def test_ngram_unique() -> None:
    assert ngrams(uniq, length=2, cut=0) == [[0, 1], [1, 2], [2, 3], [3, 4]]
    assert ngrams(uniq, length=2, cut=1) == [[0, 1], [2, 3]]
    assert ngrams(uniq, length=2, cut=2) == [[1, 2], [3, 4]]
    assert ngrams(uniq, length=3, cut=0) == [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
    assert ngrams(uniq, length=3, cut=1) == [[0, 1, 2]]
    assert ngrams(uniq, length=3, cut=2) == [[1, 2, 3]]
    assert ngrams(uniq, length=3, cut=3) == [[2, 3, 4]]
    assert ngrams(uniq, length=4, cut=0) == [[0, 1, 2, 3], [1, 2, 3, 4]]
    assert ngrams(uniq, length=4, cut=1) == [[0, 1, 2, 3]]
    assert ngrams(uniq, length=4, cut=2) == [[1, 2, 3, 4]]
    assert ngrams(uniq, length=4, cut=3) == []
    assert ngrams(uniq, length=4, cut=4) == []
    assert ngrams(string, length=4, cut=0) == ["ABCD", "BCDE", "CDEF"]
    assert ngrams(string, length=4, cut=1) == ["ABCD"]
    assert list(iterngrams(uniq, length=4, cut=4)) == []


abc = "ABC"
nz = "NOPQRSTUVWXYZ"
a = "A"


def test_dist() -> None:
    assert ngram_distribution(abc) == {"A": 1, "B": 1, "C": 1}


def test_dist_positions() -> None:
    assert ngram_positions(abc) == {"A": [0], "B": [1], "C": [2]}


def test_dist_positions_cut() -> None:
    """With cut != 0, positions are text offsets, not block indices."""
    assert ngram_positions("ABCABC", length=3, cut=1) == {"ABC": [0, 3]}
    assert ngram_positions("ABCDEFG", length=3, cut=2) == {"BCD": [1], "EFG": [4]}


def test_iterngram_positions() -> None:
    assert list(iterngram_positions("ABCD", length=2)) == [
        (0, "AB"),
        (1, "BC"),
        (2, "CD"),
    ]
    assert list(iterngram_positions("ABCD", length=2, cut=1)) == [(0, "AB"), (2, "CD")]
    assert list(iterngram_positions(uniq, length=4, cut=4)) == []
