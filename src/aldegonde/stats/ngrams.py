"""functions for ngrams
"""

from typing import Iterator

from aldegonde.structures import sequence


def iterngrams(
    runes: sequence.Sequence, length: int, cut: int = 0
) -> Iterator[list[int]]:
    """Returns ngrams for the given sequence
    Args:
        runes: Sequence
        length: size of ngram
        cut: where to start ngrams

    Yields:
        ngrams: ngrams

    Specify `cut=0` to return sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` to return non-overlapping blocks of 3 runes: ABC, DEF, ...
    Specify `cut=2` to return non-overlapping blocks of 3 runes: BCD, EFG, ...
    """
    assert length > 0
    assert 0 <= cut <= length
    N = len(runes)  # size of sequence
    if cut == 0:  # pylint: disable=C2001
        for i in range(0, N - length + 1):
            yield list(runes[i : i + length])
    elif cut in range(1, length + 1):
        for i in range(cut - 1, N - length + 1, length):
            yield list(runes[i : i + length])


def ngrams(runes: sequence.Sequence, length: int, cut: int = 0) -> list[list[int]]:
    """
    Input is a Sequence
    Output is a list of ngrams

    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 runes: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 runes: BCD, EFG, ...
    """
    return list(iterngrams(runes, length=length, cut=cut))


def digraphs(runes: sequence.Sequence, cut: int = 0) -> list[list[int]]:
    """
    convenience function for digraphs
    """
    return ngrams(runes, length=2, cut=cut)


def trigraphs(runes: sequence.Sequence, cut: int = 0) -> list[list[int]]:
    """
    convenience function for trigraphs
    """
    return ngrams(runes, length=3, cut=cut)


def tetragraphs(runes: sequence.Sequence, cut: int = 0) -> list[list[int]]:
    """
    convenience function for tetragraphs
    """
    return ngrams(runes, length=4, cut=cut)


def bigrams(runes: sequence.Sequence, cut: int = 0) -> list[list[int]]:
    """
    convenience function for digrams
    """
    return ngrams(runes, length=2, cut=cut)


def trigrams(runes: sequence.Sequence, cut: int = 0) -> list[list[int]]:
    """
    convenience function for trigrams
    """
    return ngrams(runes, length=3, cut=cut)


def quadgrams(runes: sequence.Sequence, cut: int = 0) -> list[list[int]]:
    """
    convenience function for tetragrams
    """
    return ngrams(runes, length=4, cut=cut)
