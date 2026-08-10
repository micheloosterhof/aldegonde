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
    # Slice here rather than dropping the position from iterngram_positions: this
    # runs once per ngram over the whole corpus, and delegating costs a second
    # generator frame every time.
    total = len(runes)
    if cut == 0:
        for i in range(total - length + 1):
            yield runes[i : i + length]
    elif 0 < cut <= length:
        for i in range(cut - 1, total - length + 1, length):
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


def ngram_counts(
    text: Sequence[object],
    length: int = 1,
    cut: int = 0,
) -> Counter[object]:
    """Count ngrams, keyed by whatever is cheapest to hash.

    For a caller that only needs the counts -- an index of coincidence, a repeat
    census -- the key never has to be readable, so formatting each ngram as a
    string is pure cost. Use `ngram_distribution` when the keys are displayed or
    matched against a table of string ngrams.

    Args:
        text: Sequence to count over
        length: Size of the ngram
        cut: 0 for sliding ngrams, otherwise the offset of non-overlapping ones

    Returns:
        Counts keyed by str slice, tuple, or whatever the sequence yields
    """
    if isinstance(text, str):
        return Counter(iterngrams(text, length=length, cut=cut))
    if cut == 0:
        # zip over offset views builds the sliding tuples entirely in C
        return Counter(zip(*(text[i:] for i in range(length))))
    return Counter(tuple(gram) for gram in iterngrams(text, length=length, cut=cut))


def ngram_distribution(
    text: Sequence[object],
    length: int = 1,
    cut: int = 0,
) -> dict[str, int]:
    """Return ngrams by count, keyed by the ngram as a string."""
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
