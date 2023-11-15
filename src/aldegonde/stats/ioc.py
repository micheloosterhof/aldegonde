"""IOC calculation."""

from collections.abc import Sequence
from math import sqrt
from typing import NamedTuple, TypeVar

from mypy_extensions import mypyc_attr

from aldegonde.stats.ngrams import ngram_distribution

T = TypeVar("T")


def ioc(text: Sequence[T], length: int = 1, cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC
    Args:
        text: Sequence
        length: size of ngram
        cut: where to start ngrams.

    Yields
    ------
        Output is the Index of Coincidence formatted as a float,

    Specify `cut=0` and it operates on sliding blocks of 2 text: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 text: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 text: BCD, EFG, ...
    """
    freqs: dict[str, int] = ngram_distribution(text, length=length, cut=cut)
    L: int = sum(x for x in freqs.values())
    if L < 2:
        return 0.0
    freqsum: float = sum(v * (v - 1) for v in freqs.values())
    return freqsum / (L * (L - 1))


def nioc(
    text: Sequence[T],
    alphabetsize: int,
    length: int = 1,
    cut: int = 0,
) -> tuple[float, float, float]:
    """Yield
    Output is the Index of Coincidence formatted as a float,
    normalized to to alphabet size, and the number of standard
    deviations away from random data.
    """
    freqs: dict[str, int] = ngram_distribution(text, length=length, cut=cut)
    L: int = sum(x for x in freqs.values())
    if L < 2:
        return (0.0, 0.0, 0.0)
    freqsum: float = sum(v * (v - 1) for v in freqs.values())
    ic = freqsum / (L * (L - 1))
    C = pow(alphabetsize, length)  # size of alphabet
    nic = C * ic
    sd = sqrt(2 * (C - 1)) / sqrt(L * (L - 1))
    sigmage = abs(nic - 1.0) / sd

    @mypyc_attr(allow_interpreted_subclasses=True)
    class Ioc(NamedTuple):
        ioc: float
        nioc: float
        sigmage: float

    return Ioc(ioc=ic, nioc=nic, sigmage=sigmage)


def print_ioc_statistics(text: Sequence[T], alphabetsize: int) -> None:
    """Print IOC statistics."""
    for length in range(1, 6):
        for cut in range(length + 1):
            if length == 1 and cut == 1:
                continue
            _, nic, sigmage = nioc(
                text,
                alphabetsize=alphabetsize,
                length=length,
                cut=cut,
            )
            print(f"ΔIC{length} (cut={cut}) = {nic:.3f} S={sigmage:.3f}σ ", end="| ")
        print()


def sliding_window_ioc(
    text: Sequence[T],
    length: int = 1,
    cut: int = 0,
    window: int = 100,
) -> list[float]:
    """Calculate sliding window IOC of a large data set."""
    output: list[float] = []
    for i in range(len(text) - window):
        output.append(ioc(text[i : i + window], length=length, cut=cut))
    return output


def ioc2(text: Sequence[T], cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC."""
    return ioc(text, cut=cut, length=2)


def ioc3(text: Sequence[T], cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC."""
    return ioc(text, cut=cut, length=3)


def ioc4(text: Sequence[T], cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC."""
    return ioc(text, cut=cut, length=4)
