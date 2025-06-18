"""IOC calculation."""

from collections.abc import Sequence
from math import log, sqrt
from typing import NamedTuple

from aldegonde.stats.ngrams import ngram_distribution
from aldegonde.exceptions import (
    StatisticalAnalysisError,
    InsufficientDataError,
    InvalidInputError,
)
from aldegonde.validation import validate_text_sequence, validate_positive_integer


def ioc(text: Sequence[object], length: int = 1, cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC

    Args:
        text: Sequence to analyze
        length: size of ngram
        cut: where to start ngrams

    Returns:
        Index of Coincidence as a float

    Raises:
        InvalidInputError: If parameters are invalid
        InsufficientDataError: If text is too short for analysis
        StatisticalAnalysisError: If analysis fails

    Specify `cut=0` and it operates on sliding blocks of 2 text: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 text: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 text: BCD, EFG, ...
    """
    validate_text_sequence(text, min_length=2)
    validate_positive_integer(length, "length")

    if cut < 0 or cut > length:
        raise InvalidInputError(f"Cut value {cut} must be between 0 and {length}")

    try:
        freqs: dict[str, int] = ngram_distribution(text, length=length, cut=cut)
        L: int = sum(x for x in freqs.values())

        if L < 2:
            raise InsufficientDataError(
                f"Insufficient n-grams ({L}) for IOC calculation",
                required_length=2,
                actual_length=L,
                analysis_type="IOC",
            )

        freqsum: float = sum(v * (v - 1) for v in freqs.values())
        return freqsum / (L * (L - 1))

    except Exception as exc:
        if isinstance(exc, (InvalidInputError, InsufficientDataError)):
            raise
        raise StatisticalAnalysisError(
            f"IOC calculation failed: {exc}", analysis_type="IOC"
        ) from exc


def nioc(
    text: Sequence[object],
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

    Ioc = NamedTuple(  # noqa: UP014
        "Ioc",
        [("ioc", float), ("nioc", float), ("sigmage", float)],
    )
    return Ioc(ioc=ic, nioc=nic, sigmage=sigmage)


def print_ioc_statistics(text: Sequence[object], alphabetsize: int) -> None:
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
    text: Sequence[object],
    length: int = 1,
    cut: int = 0,
    window: int = 100,
) -> list[float]:
    """Calculate sliding window IOC of a large data set.

    Args:
        text: Sequence to analyze
        length: size of ngram
        cut: where to start ngrams
        window: size of sliding window

    Returns:
        List of IOC values for each window position

    Raises:
        InvalidInputError: If parameters are invalid
        InsufficientDataError: If text is too short for analysis
    """
    validate_text_sequence(text, min_length=window + length)
    validate_positive_integer(length, "length")
    validate_positive_integer(window, "window")

    if len(text) < window + length:
        raise InsufficientDataError(
            f"Text length {len(text)} is insufficient for window size {window} with n-gram length {length}",
            required_length=window + length,
            actual_length=len(text),
            analysis_type="sliding window IOC",
        )

    output: list[float] = []
    for i in range(len(text) - window + 1):
        output.append(ioc(text[i : i + window], length=length, cut=cut))
    return output


def ioc2(text: Sequence[object], cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC."""
    return ioc(text, cut=cut, length=2)


def ioc3(text: Sequence[object], cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC."""
    return ioc(text, cut=cut, length=3)


def ioc4(text: Sequence[object], cut: int = 0) -> float:
    """Multigraphic Index of Coincidence: ΔIC."""
    return ioc(text, cut=cut, length=4)


def renyi(
    text: Sequence[object],
    order: float = 2.0,
    length: int = 1,
    cut: int = 0,
) -> float:
    """Renyi Entropy
    Args:
        text: Sequence of items
        order: renyi order, default 2.0
        length: size of ngram
        cut: where to start ngrams.

    Yields
    ------
        Output is the Renyi Entropy formatted as a float,

    Specify `cut=0` and it operates on sliding blocks of 2 text: ABC, BCD, CDE, ...
    Specify `cut=1` and it operates on non-overlapping blocks of 3 text: ABC, DEF, ...
    Specify `cut=2` and it operates on non-overlapping blocks of 3 text: BCD, EFG, ...

    order=1 converges to Shannon entropy
    https://www.johndcook.com/blog/2021/08/14/index-of-coincidence
    """
    freqs: dict[str, int] = ngram_distribution(text, length=length, cut=cut)
    L: int = sum(x for x in freqs.values())
    H: float
    if order == 1:
        H = -sum(v / L * log(v / L, 2) for v in freqs.values())
    else:
        freqsum: float = sum(abs(pow(v / L, order)) for v in freqs.values())
        H = 1 / (1 - order) * log(freqsum, 2)
    return H
