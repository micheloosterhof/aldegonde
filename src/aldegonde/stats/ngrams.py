"""functions for ngrams."""

from collections import Counter, defaultdict
from collections.abc import Generator, Sequence
from typing import TypeVar

T = TypeVar("T")


def iterngrams(
    runes: Sequence[T],
    length: int,
    cut: int = 0,
) -> Generator[Sequence[T], None, None]:
    """Return ngrams for the given sequence
    Args:
        runes: Sequence
        length: size of ngram
        cut: where to start ngrams.

    Yields
    ------
        ngrams: ngrams

    Specify `cut=0` to return sliding blocks of runes: ABC, BCD, CDE, ...
    Specify `cut=1` to return non-overlapping blocks of runes: ABC, DEF, ...
    Specify `cut=2` to return non-overlapping blocks of runes: BCD, EFG, ...
    """
    # assert length > 0
    # assert 0 <= cut <= length
    N = len(runes)  # size of sequence
    # https://stackoverflow.com/questions/24527006/split-a-generator-into-chunks-without-pre-walking-it
    # this is like itertools.pairwise()
    if cut == 0:  # pylint: disable=C2001
        for i in range(N - length + 1):
            yield runes[i : i + length]
    # this is like itertools.batched()
    elif cut <= length and cut > 0:
        for i in range(cut - 1, N - length + 1, length):
            yield runes[i : i + length]


def ngrams(runes: Sequence[T], length: int, cut: int = 0) -> list[Sequence[T]]:
    """Input is a Sequence
    Output is a list of ngrams.

    Specify `cut=0` and it operates on sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 runes: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 runes: BCD, EFG, ...
    """
    return list(iterngrams(runes, length=length, cut=cut))


def digraphs(runes: Sequence[T], cut: int = 0) -> list[Sequence[T]]:
    """Return digraphs."""
    return ngrams(runes, length=2, cut=cut)


def trigraphs(runes: Sequence[T], cut: int = 0) -> list[Sequence[T]]:
    """Return trigraphs."""
    return ngrams(runes, length=3, cut=cut)


def tetragraphs(runes: Sequence[T], cut: int = 0) -> list[Sequence[T]]:
    """Return tetragraphs."""
    return ngrams(runes, length=4, cut=cut)


def bigrams(runes: Sequence[T], cut: int = 0) -> list[Sequence[T]]:
    """Return digrams."""
    return ngrams(runes, length=2, cut=cut)


def trigrams(runes: Sequence[T], cut: int = 0) -> list[Sequence[T]]:
    """Return trigrams."""
    return ngrams(runes, length=3, cut=cut)


def quadgrams(runes: Sequence[T], cut: int = 0) -> list[Sequence[T]]:
    """Return tetragrams."""
    return ngrams(runes, length=4, cut=cut)


def ngram_distribution(
    text: Sequence[T],
    length: int = 1,
    cut: int = 0,
) -> dict[str, int]:
    """Return ngrams by count."""
    return Counter([str(g) for g in iterngrams(text, length=length, cut=cut)])


def ngram_positions(
    text: Sequence[T],
    length: int = 1,
    cut: int = 0,
) -> dict[str, list[int]]:
    """Return each ngram and its starting locations in the source text."""
    out: dict[str, list[int]] = defaultdict(list)
    for i, e in enumerate(iterngrams(text, length=length, cut=cut)):
        out[str(e)].append(i)
    return out
