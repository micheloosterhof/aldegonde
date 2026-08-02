# ABOUTME: Spectral and cross-correlation detectors: keystream-reuse alignment
# ABOUTME: by FFT, and multiplier-DFT periodicity for arbitrary modulus.
"""Spectral detectors for structure that lag statistics miss.

Two Fourier-based probes over a symbol stream:

`crosscorrelation_coincidence` finds the alignment at which two streams
coincide most, in O(n log n), by summing the circular cross-correlation of
their per-symbol indicator vectors. It detects a shared or reused keystream
between two messages at every relative shift at once, where a pairwise lag
scan would cost O(n^2).

`multiplier_dft` detects additive periodic structure at periods that need
not be integers. For each nonzero multiplier m it takes the DFT of
exp(2*pi*i*m*x/N) over the alphabet indices; a spike at frequency f exposes
a component whose phase advances by m*f per step. Under the null each
power is exponentially distributed, so the peak is read against a threshold
that counts the whole multiplier-by-frequency scan. Integer-lag kappa and
Kasiski cannot see a non-integer period; this can.
"""

from __future__ import annotations

from math import log
from typing import TYPE_CHECKING, NamedTuple, TypeVar

import numpy as np

from aldegonde.exceptions import InsufficientDataError, InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


class AlignmentPeak(NamedTuple):
    """The strongest coincidence alignment between two streams.

    Attributes:
        shift: Cyclic shift maximizing coincidences, in the convention that
            first[i] aligns with second[(i + shift) mod n]; normalized to
            the range (-n/2, n/2]
        coincidences: Matching positions at that shift
        expected: Coincidences expected by chance at that overlap
        z: Binomial standard score of the peak against chance
    """

    shift: int
    coincidences: int
    expected: float
    z: float


def crosscorrelation_coincidence(
    first: Sequence[T],
    second: Sequence[T],
    alphabet: Sequence[T],
) -> AlignmentPeak:
    """Find the shift where two streams coincide most, by FFT.

    Sums the circular cross-correlation of the per-symbol indicator vectors
    of the two streams, giving the coincidence count at every cyclic shift
    in O(n log n). The best shift and its binomial z against the chance rate
    1/alphabetsize are returned — the reused-keystream / running-key-depth
    detector, at every alignment at once.

    Args:
        first: First stream
        second: Second stream, cyclically shifted against the first
        alphabet: The alphabet fixing symbol indices

    Returns:
        The peak alignment, its coincidence count, chance expectation, and z

    Raises:
        InvalidInputError: If the streams differ in length or a symbol is
            missing from the alphabet
        InsufficientDataError: If the streams are empty
    """
    if len(first) != len(second):
        msg = f"streams differ in length: {len(first)} vs {len(second)}"
        raise InvalidInputError(msg)
    n = len(first)
    if n == 0:
        msg = "crosscorrelation_coincidence needs non-empty streams"
        raise InsufficientDataError(msg, 1, 0)
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    size = len(alphabet)
    try:
        a = np.array([index[s] for s in first])
        b = np.array([index[s] for s in second])
    except KeyError as exc:
        msg = f"symbol {exc.args[0]!r} not in alphabet"
        raise InvalidInputError(msg) from exc
    correlation = np.zeros(n)
    for symbol in range(size):
        indicator_a = (a == symbol).astype(float)
        indicator_b = (b == symbol).astype(float)
        spectrum = np.fft.rfft(indicator_a) * np.conj(np.fft.rfft(indicator_b))
        correlation += np.fft.irfft(spectrum, n)
    peak = int(np.argmax(correlation))
    coincidences = int(round(correlation[peak]))
    # irfft(rfft(a) * conj(rfft(b)))[k] sums a[i] b[(i - k) mod n]; the
    # aligning shift in the first[i] ~ second[i + shift] convention is -k,
    # normalized to (-n/2, n/2] for readability
    shift = (n - peak) % n
    if shift > n // 2:
        shift -= n
    expected = n / size
    sd = (n * (1.0 / size) * (1.0 - 1.0 / size)) ** 0.5
    z = (coincidences - expected) / sd if sd > 0 else 0.0
    return AlignmentPeak(
        shift=shift,
        coincidences=coincidences,
        expected=expected,
        z=z,
    )


class SpectralPeak(NamedTuple):
    """The strongest multiplier-DFT peak of a stream.

    Attributes:
        multiplier: The multiplier m attaining the peak
        frequency: The DFT bin index of the peak
        power: Normalized power at the peak (mean 1 under the null)
        threshold: The log(cells) + 3 significance level, where cells counts
            every (multiplier, nonzero frequency) bin scanned
    """

    multiplier: int
    frequency: int
    power: float
    threshold: float


def multiplier_dft(
    text: Sequence[T],
    alphabet: Sequence[T],
    multipliers: Sequence[int] | None = None,
) -> SpectralPeak:
    """Find the strongest additive-periodic component across all multipliers.

    For each multiplier m the stream indices are mapped to unit phasors
    exp(2*pi*i*m*x/N) and transformed; the power spectrum is normalized to
    unit mean, so under the null each bin is exponentially distributed. The
    largest normalized power over all multipliers and nonzero frequencies is
    returned with a max-of-bins threshold of log(bins) + 3 — clearing it
    signals a periodic component (possibly at a non-integer period) that
    integer-lag tests miss.

    Args:
        text: Sequence to analyze
        alphabet: The alphabet fixing symbol indices and the modulus N
        multipliers: Multipliers m to scan; 1..N-1 when omitted

    Returns:
        The peak multiplier, frequency, normalized power, and threshold

    Raises:
        InvalidInputError: If a symbol is missing from the alphabet
        InsufficientDataError: If the text has fewer than 2 symbols
    """
    n = len(text)
    if n < 2:
        msg = "multiplier_dft needs at least 2 symbols"
        raise InsufficientDataError(msg, 2, n)
    modulus = len(alphabet)
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    try:
        values = np.array([index[s] for s in text], dtype=float)
    except KeyError as exc:
        msg = f"symbol {exc.args[0]!r} not in alphabet"
        raise InvalidInputError(msg) from exc
    scan = list(multipliers) if multipliers is not None else list(range(1, modulus))
    # The peak is a maximum over every (multiplier, nonzero frequency) cell,
    # so the exponential-tail threshold must count the whole family, not one
    # spectrum's bins.
    cells = len(scan) * (n - 1)
    threshold = log(cells) + 3.0 if cells > 0 else 0.0
    best = SpectralPeak(multiplier=0, frequency=0, power=0.0, threshold=threshold)
    for multiplier in scan:
        phasors = np.exp(2j * np.pi * multiplier * values / modulus)
        spectrum = np.fft.fft(phasors)
        power = np.abs(spectrum) ** 2
        mean = power.mean()
        if mean <= 0:
            continue
        normalized = power / mean
        # Skip the zero-frequency (DC) bin: it only reflects the mean phasor
        frequency = int(np.argmax(normalized[1:])) + 1
        peak = float(normalized[frequency])
        if peak > best.power:
            best = SpectralPeak(
                multiplier=multiplier,
                frequency=frequency,
                power=peak,
                threshold=threshold,
            )
    return best
