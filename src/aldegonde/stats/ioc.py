"""IOC calculation."""

from collections.abc import Sequence
from math import log, sqrt
from typing import NamedTuple

from aldegonde.exceptions import (
    InsufficientDataError,
    InvalidInputError,
    StatisticalAnalysisError,
)
from aldegonde.stats.ngrams import ngram_distribution
from aldegonde.stats.nulls import NullModel
from aldegonde.stats.resample import monte_carlo_map
from aldegonde.stats.zscore import z_score
from aldegonde.validation import validate_positive_integer, validate_text_sequence


class IocResult(NamedTuple):
    """Result of normalized IOC calculation."""

    ioc: float
    nioc: float
    z_score: float


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
        msg = f"Cut value {cut} must be between 0 and {length}"
        raise InvalidInputError(msg)

    try:
        freqs: dict[str, int] = ngram_distribution(text, length=length, cut=cut)
        L: int = sum(x for x in freqs.values())

        if L < 2:
            msg = f"Insufficient n-grams ({L}) for IOC calculation"
            raise InsufficientDataError(
                msg,
                required_length=2,
                actual_length=L,
                analysis_type="IOC",
            )

        freqsum: float = sum(v * (v - 1) for v in freqs.values())
        return freqsum / (L * (L - 1))

    except Exception as exc:
        if isinstance(exc, InvalidInputError | InsufficientDataError):
            raise
        msg = f"IOC calculation failed: {exc}"
        raise StatisticalAnalysisError(msg, analysis_type="IOC") from exc


def nioc(
    text: Sequence[object],
    alphabetsize: int,
    length: int = 1,
    cut: int = 0,
) -> IocResult:
    """Return normalized IOC with z-score.

    Output is the Index of Coincidence formatted as a float,
    normalized to alphabet size, and the signed number of standard
    deviations away from random data.
    """
    freqs: dict[str, int] = ngram_distribution(text, length=length, cut=cut)
    L: int = sum(x for x in freqs.values())
    if L < 2:
        return IocResult(ioc=0.0, nioc=0.0, z_score=0.0)
    freqsum: float = sum(v * (v - 1) for v in freqs.values())
    ic = freqsum / (L * (L - 1))
    C = pow(alphabetsize, length)  # size of alphabet
    nic = C * ic
    sd = sqrt(2 * (C - 1)) / sqrt(L * (L - 1))

    return IocResult(ioc=ic, nioc=nic, z_score=z_score(nic, 1.0, sd))


def _nioc_grid_against_null(
    text: Sequence[object],
    alphabetsize: int,
    cells: list[tuple[int, int]],
    null: NullModel[object],
    trials: int,
    seed: int,
) -> dict[tuple[int, int], tuple[float, float]]:
    """Score every (length, cut) cell against one shared set of surrogates.

    A single monte_carlo_map pass draws each surrogate once and evaluates the
    whole grid on it, rather than regenerating surrogates per cell.
    """

    def statistic(sample: Sequence[object]) -> dict[int, float]:
        return {
            index: nioc(sample, alphabetsize=alphabetsize, length=length, cut=cut).nioc
            for index, (length, cut) in enumerate(cells)
        }

    results = monte_carlo_map(
        statistic, null, text, keys=list(range(len(cells))), trials=trials, seed=seed
    )
    return {
        cell: (results[index].observed, results[index].z)
        for index, cell in enumerate(cells)
    }


def print_ioc_statistics(
    text: Sequence[object],
    alphabetsize: int,
    *,
    null: NullModel[object] | None = None,
    null_label: str | None = None,
    trials: int = 1000,
    seed: int = 0,
) -> None:
    """Print the multigraphic IOC grid with z-scores against a null hypothesis.

    By default the null is uniform random text and z is the closed-form standard
    score. Pass `null` (a resampler) to compare instead against a Monte Carlo
    null, for example one that preserves frequencies and suppresses doublets;
    z is then standard deviations from that null's distribution, and `null_label`
    names it in the header. A frequency-preserving null leaves monographic IOC
    invariant (z = 0), so only multigraphic IOC carries signal against it.
    """
    cells = [
        (length, cut)
        for length in range(1, 6)
        for cut in range(length + 1)
        if not (length == 1 and cut == 1)
    ]
    scored: dict[tuple[int, int], tuple[float, float]]
    if null is None:
        print(
            f"null hypothesis: uniform random text over {alphabetsize} symbols "
            f"(normalized IOC = 1.0); z = standard deviations from this null"
        )
        scored = {}
        for length, cut in cells:
            result = nioc(text, alphabetsize=alphabetsize, length=length, cut=cut)
            scored[(length, cut)] = (result.nioc, result.z_score)
    else:
        print(
            f"null hypothesis: {null_label or 'injected null model'}; "
            f"z = standard deviations from this null"
        )
        scored = _nioc_grid_against_null(text, alphabetsize, cells, null, trials, seed)
    for length in range(1, 6):
        for cut in range(length + 1):
            if length == 1 and cut == 1:
                continue
            value, z = scored[(length, cut)]
            print(f"ΔIC{length} (cut={cut}) = {value:.3f} z={z:+.3f} ", end="| ")
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
        msg = f"Text length {len(text)} is insufficient for window size {window} with n-gram length {length}"
        raise InsufficientDataError(
            msg,
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
