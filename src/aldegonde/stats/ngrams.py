"""functions for ngrams."""

from collections import Counter, defaultdict
from collections.abc import Generator, Sequence
from typing import TypeVar

T = TypeVar("T")


def iterngram_positions(
    runes: Sequence[T],
    length: int,
    cut: int = 0,
) -> Generator[tuple[int, Sequence[T]], None, None]:
    """Return (position, ngram) pairs for the given sequence
    Args:
        runes: Sequence
        length: size of ngram
        cut: where to start ngrams.

    Yields
    ------
        pairs of (starting position in the source text, ngram)

    Specify `cut=0` to return sliding blocks of runes: ABC, BCD, CDE, ...
    Specify `cut=1` to return non-overlapping blocks of runes: ABC, DEF, ...
    Specify `cut=2` to return non-overlapping blocks of runes: BCD, EFG, ...
    """
    N = len(runes)  # size of sequence
    # https://stackoverflow.com/questions/24527006/split-a-generator-into-chunks-without-pre-walking-it
    # this is like itertools.pairwise()
    if cut == 0:  # pylint: disable=C2001
        for i in range(N - length + 1):
            yield i, runes[i : i + length]
    # this is like itertools.batched()
    elif cut <= length and cut > 0:
        for i in range(cut - 1, N - length + 1, length):
            yield i, runes[i : i + length]


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
    for _, gram in iterngram_positions(runes, length=length, cut=cut):
        yield gram


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
    text: Sequence[object],
    length: int = 1,
    cut: int = 0,
) -> dict[str, int]:
    """Return ngrams by count."""
    return Counter([str(g) for g in iterngrams(text, length=length, cut=cut)])


def ngram_positions(
    text: Sequence[object],
    length: int = 1,
    cut: int = 0,
) -> dict[str, list[int]]:
    """Return each ngram and its starting locations in the source text."""
    out: dict[str, list[int]] = defaultdict(list)
    for i, e in iterngram_positions(text, length=length, cut=cut):
        out[str(e)].append(i)
    return out
