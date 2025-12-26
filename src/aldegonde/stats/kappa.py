"""Kappa test for period detection using doublet analysis.

The kappa test measures the frequency of repeated n-grams at a given skip distance,
which can reveal periodic patterns in ciphertext. Multigraphic kappa extends this
to detect repeated digraphs, trigraphs, etc.
"""

from collections.abc import Sequence
from math import sqrt
from typing import TypeVar

from scipy.stats import poisson

T = TypeVar("T")


def doublets(
    text: Sequence[object],
    skip: int = 1,
    length: int = 1,
    *,
    trace: bool = False,
) -> tuple[list[int], int]:
    """Find number of repeated n-grams at a given skip distance.

    A doublet is an n-gram followed by the same n-gram at position + skip.
    For length=1: X...X (monographic)
    For length=2: XY...XY (digraphic)
    For length=3: XYZ...XYZ (trigraphic)

    Args:
        text: Sequence to analyze
        skip: Distance between compared n-grams
        length: Size of n-gram (1=monographic, 2=digraphic, etc.)
        trace: Print debug information

    Returns:
        Tuple of (list of positions where doublets occur, total comparisons made)
    """
    positions: list[int] = []
    n = len(text)

    # Need at least length + skip elements to make one comparison
    if n < length + skip:
        return ([], 0)

    # Number of valid starting positions for comparison
    # We compare ngram at [i:i+length] with ngram at [i+skip:i+skip+length]
    # Last valid i is when i+skip+length-1 < n, so i < n - skip - length + 1
    num_comparisons = n - skip - length + 1

    if num_comparisons <= 0:
        return ([], 0)

    for index in range(num_comparisons):
        # Compare n-gram starting at index with n-gram starting at index + skip
        ngram1 = tuple(text[index : index + length])
        ngram2 = tuple(text[index + skip : index + skip + length])

        if ngram1 == ngram2:
            positions.append(index)
            if trace:
                ngram_str = "".join(str(x) for x in ngram1)
                print(f"doublet at {index}: {ngram_str} (skip={skip}, length={length})")

    return (positions, num_comparisons)


def kappa(
    text: Sequence[object],
    skip: int = 1,
    length: int = 1,
    *,
    trace: bool = False,
) -> float:
    """Calculate kappa (doublet frequency) for n-grams at a given skip distance.

    Kappa is the ratio of observed doublets to possible doublet positions.
    Higher kappa at a particular skip value suggests that skip may be
    related to the cipher's period.

    Args:
        text: Sequence to analyze
        skip: Distance between compared n-grams
        length: Size of n-gram (1=monographic, 2=digraphic, etc.)
        trace: Print debug information

    Returns:
        Kappa value as a float (0.0 to 1.0)
    """
    dbl, total = doublets(text, skip=skip, length=length, trace=trace)
    if total == 0:
        return 0.0
    return len(dbl) / total


def kappa2(text: Sequence[object], skip: int = 1, *, trace: bool = False) -> float:
    """Digraphic kappa - detect repeated digraphs at skip distance."""
    return kappa(text, skip=skip, length=2, trace=trace)


def kappa3(text: Sequence[object], skip: int = 1, *, trace: bool = False) -> float:
    """Trigraphic kappa - detect repeated trigraphs at skip distance."""
    return kappa(text, skip=skip, length=3, trace=trace)


def kappa4(text: Sequence[object], skip: int = 1, *, trace: bool = False) -> float:
    """Tetragraphic kappa - detect repeated tetragraphs at skip distance."""
    return kappa(text, skip=skip, length=4, trace=trace)


# def doublets(
#    inp: Iterator[T], skip: int = 1, *, trace: bool = False
# ) -> tuple[list[int], int]:
#    """Find number of doublets. doublet is X followed by X for any X.
#    returns the positions of the doublets as a list plus the length of the input"""
#    positions: list[int] = []
#    buffer: list[T] = []
#    index = 0
#
#    for item in inp:
#        buffer.append(item)
#        if len(buffer) > skip:
#            buffer.pop(0)
#        if len(buffer) == skip and buffer[0] == buffer[-1]:
#            positions.append(index - skip)
#            if trace:
#                print(f"doublet at {index - skip}: {buffer[0]}-{buffer[1]}")
#        index += 1
#
#    return (positions, index - skip)


def triplets(text: Sequence[object]) -> int:
    """Find number of triplet. triplet is X followed by XX for any X."""
    N = len(text)
    trpl: int = 0
    for index in range(N - 2):
        if text[index] == text[index + 1] and text[index] == text[index + 2]:
            trpl += 1
    # expected = N / MAX / MAX
    return trpl


def print_kappa(
    ciphertext: Sequence[object],
    alphabetsize: int = 0,
    minimum: int = 1,
    maximum: int = 51,
    length: int = 1,
    threshold: float = 1.3,
    *,
    trace: bool = False,
) -> None:
    """Kappa test for a range of skip values.

    Prints kappa statistics for each skip value, including observed count,
    expected count (Poisson), statistical significance (sigmage), and
    normalized IOC.

    Args:
        ciphertext: Sequence to analyze
        alphabetsize: Size of alphabet (0 = auto-detect from unique symbols)
        minimum: Minimum skip value to test
        maximum: Maximum skip value to test
        length: Size of n-gram (1=monographic, 2=digraphic, etc.)
        threshold: Significance threshold (unused, kept for compatibility)
        trace: Print debug information
    """
    assert maximum >= 0
    assert minimum >= 1
    assert length >= 1

    if alphabetsize == 0:
        alphabetsize = len(set(ciphertext))
    if maximum == 0:
        maximum = int(len(ciphertext) / 2)
    elif maximum > len(ciphertext):
        maximum = len(ciphertext)

    # For multigraphic, the effective alphabet size is alphabetsize^length
    effective_alphabet = int(pow(alphabetsize, length))

    length_names = {1: "mono", 2: "di", 3: "tri", 4: "tetra"}
    length_name = length_names.get(length, f"{length}-")

    for skip in range(minimum, maximum):
        dbl, num_comparisons = doublets(ciphertext, skip=skip, length=length)
        if num_comparisons == 0:
            continue
        count = len(dbl)
        normalized_ioc = effective_alphabet * count / num_comparisons
        mu = num_comparisons / effective_alphabet
        mean, var = poisson.stats(mu, loc=0, moments="mv")
        sigmage: float = abs(count - mean) / sqrt(var) if var > 0 else 0.0
        print(
            f"kappa({length_name}): skip={skip:<2d} count={count:<3d} "
            f"expected={mean:<6.2f} S={sigmage:5.2f}σ ioc={normalized_ioc:1.3f}",
        )
        if trace and count > 0:
            for pos in dbl:
                ngram = "".join(str(x) for x in ciphertext[pos : pos + length])
                print(f"  pos {pos}: {ngram}")
    print()


def print_kappa_statistics(
    ciphertext: Sequence[object],
    alphabetsize: int = 0,
    minimum: int = 1,
    maximum: int = 51,
    max_length: int = 4,
    *,
    trace: bool = False,
) -> None:
    """Print kappa statistics for monographic through multigraphic analysis.

    Args:
        ciphertext: Sequence to analyze
        alphabetsize: Size of alphabet (0 = auto-detect)
        minimum: Minimum skip value to test
        maximum: Maximum skip value to test
        max_length: Maximum n-gram length to analyze (1-4)
        trace: Print debug information
    """
    for length in range(1, max_length + 1):
        print_kappa(
            ciphertext,
            alphabetsize=alphabetsize,
            minimum=minimum,
            maximum=maximum,
            length=length,
            trace=trace,
        )
