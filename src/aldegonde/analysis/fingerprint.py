# ABOUTME: A compact statistical fingerprint of a symbol stream, and a
# ABOUTME: comparison against a reference (a mechanism-consistency check).
"""Statistical fingerprint of a symbol stream.

A cipher hypothesis is tested by simulating the mechanism over language-like
plaintext and asking whether the simulated ciphertext reproduces the
observed statistics. That comparison needs a fixed vector of discriminating
statistics computed the same way on both sides. `fingerprint` returns that
vector — normalized IOC, doublet rate, and a short kappa profile — and
`compare` scores one fingerprint against a reference, so "is my ciphertext
consistent with mechanism X?" becomes: fingerprint the real text, simulate
X, fingerprint that, compare.

The fingerprint is deliberately small and composed of existing library
statistics; extend the returned mapping as a particular investigation needs
more discriminating power.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from aldegonde.exceptions import InsufficientDataError
from aldegonde.stats.ioc import nioc
from aldegonde.stats.kappa import kappa_spectrum

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

T = TypeVar("T")


def fingerprint(
    text: Sequence[T],
    *,
    alphabetsize: int | None = None,
    lags: Sequence[int] = (1, 2, 3, 4, 5),
) -> dict[str, float]:
    """Compute a compact statistical fingerprint of a stream.

    The vector holds the normalized index of coincidence (`nioc`), the
    monographic doublet rate (`doublet_rate`), and the frequency-matched
    kappa z at each requested lag (`kappa_z_<lag>`). All are alphabet-size
    normalized, so fingerprints of different texts are comparable.

    Args:
        text: Sequence to fingerprint
        alphabetsize: Alphabet size for IOC normalization; distinct-symbol
            count when omitted
        lags: Lags whose kappa z-scores enter the fingerprint

    Returns:
        A mapping from statistic name to value

    Raises:
        InsufficientDataError: If the text is too short for the statistics
    """
    if len(text) < 2:
        msg = "fingerprint needs at least 2 symbols"
        raise InsufficientDataError(msg, 2, len(text))
    size = alphabetsize if alphabetsize is not None else len(set(text))
    result: dict[str, float] = {
        "nioc": nioc(text, alphabetsize=size).nioc,
        "doublet_rate": sum(1 for a, b in zip(text, text[1:]) if a == b)
        / (len(text) - 1),
    }
    spectrum = kappa_spectrum(text, list(lags))
    for lag in lags:
        hit = spectrum.get(lag)
        result[f"kappa_z_{lag}"] = hit.z if hit is not None else 0.0
    return result


def compare(
    observed: Mapping[str, float],
    reference: Mapping[str, float],
    *,
    scales: Mapping[str, float] | None = None,
) -> float:
    """Score a fingerprint against a reference as a scaled squared distance.

    Sums, over the statistics both fingerprints share, the squared
    difference divided by a per-statistic scale (default 1.0). Smaller is a
    closer match; a simulated mechanism whose fingerprint sits closest to
    the observed one is the best-supported hypothesis. Supply `scales`
    (e.g. each statistic's spread under simulation) to weight the terms
    commensurately.

    Args:
        observed: Fingerprint of the real text
        reference: Fingerprint to compare against
        scales: Per-statistic divisor; 1.0 where unspecified

    Returns:
        The scaled squared distance over shared statistics

    Raises:
        InsufficientDataError: If the fingerprints share no statistics
    """
    shared = set(observed) & set(reference)
    if not shared:
        msg = "fingerprints share no statistics to compare"
        raise InsufficientDataError(msg, 1, 0)
    total = 0.0
    for name in shared:
        scale = 1.0 if scales is None else scales.get(name, 1.0)
        total += ((observed[name] - reference[name]) / scale) ** 2
    return total
