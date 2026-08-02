# ABOUTME: Scans for linear and positional relations between symbols at a lag,
# ABOUTME: the omnibus detector for affine, LFSR, and drifting-key structure.
"""Linear-relation scans over a modular alphabet.

If a cipher relates a symbol to an earlier one linearly — Vigenere and
Beaufort make x[i+d] +/- x[i] constant per key position, an affine step
makes a*x[i] + x[i+d] structured, a lagged-Fibonacci keystream makes some
tap combination degenerate — then the derived stream
(x[i+d] + a*x[i]) mod N is non-uniform for the right (d, a). Scanning
lags against coefficients and chi-squaring each derived stream for
uniformity detects that whole family at once; the positional variant
(x[i] + a*i) mod N catches keys that drift linearly with the position.

Every cell of the scan is one test: read results through
`stats.multitest` (Bonferroni over the grid size) or confirm a hit with a
resampled null before believing it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.chisq import ChiSquare, uniformity

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


def _indices(text: Sequence[T], alphabet: Sequence[T]) -> list[int]:
    """Map a sequence to alphabet indices."""
    index = {symbol: i for i, symbol in enumerate(alphabet)}
    try:
        return [index[symbol] for symbol in text]
    except KeyError as exc:
        msg = f"symbol {exc.args[0]!r} not in alphabet"
        raise InvalidInputError(msg) from exc


def linear_relation_scan(
    text: Sequence[T],
    alphabet: Sequence[T],
    lags: Sequence[int],
    coefficients: Sequence[int] | None = None,
) -> dict[tuple[int, int], ChiSquare]:
    """Chi-square the derived streams (x[i+d] + a*x[i]) mod N for uniformity.

    A significant cell at (d, a) means the symbol at distance d carries a
    linear relation with coefficient a — the signature of additive keys,
    affine steps, and linear-recurrence keystreams. The scan has
    len(lags) * len(coefficients) cells; correct for that with
    `stats.multitest.bonferroni` before reading any single cell.

    Args:
        text: Sequence to analyze
        alphabet: The alphabet fixing symbol indices and the modulus N
        lags: Lags d to scan
        coefficients: Coefficients a to scan; 1..N-1 when omitted

    Returns:
        A ChiSquare per (lag, coefficient) cell that admits at least two
        pairs

    Raises:
        InvalidInputError: If a lag is not positive or a symbol is missing
            from the alphabet
    """
    numbers = _indices(text, alphabet)
    modulus = len(alphabet)
    scan_coefficients = (
        list(coefficients) if coefficients is not None else list(range(1, modulus))
    )
    results: dict[tuple[int, int], ChiSquare] = {}
    for lag in lags:
        if lag < 1:
            msg = f"lag must be positive, got {lag}"
            raise InvalidInputError(msg)
        pairs = len(numbers) - lag
        if pairs < 2:
            continue
        for coefficient in scan_coefficients:
            counts = [0] * modulus
            for i in range(pairs):
                counts[(numbers[i + lag] + coefficient * numbers[i]) % modulus] += 1
            results[(lag, coefficient)] = uniformity(counts)
    return results


def positional_relation_scan(
    text: Sequence[T],
    alphabet: Sequence[T],
    coefficients: Sequence[int] | None = None,
) -> dict[int, ChiSquare]:
    """Chi-square the derived streams (x[i] + a*i) mod N for uniformity.

    A significant coefficient a means the symbols carry a component linear
    in their position — a progressively shifting key, a counter mixed into
    the cipher, or a positional drift. One test per coefficient: correct
    with `stats.multitest` over the scan size.

    Args:
        text: Sequence to analyze
        alphabet: The alphabet fixing symbol indices and the modulus N
        coefficients: Coefficients a to scan; 1..N-1 when omitted

    Returns:
        A ChiSquare per coefficient

    Raises:
        InvalidInputError: If a symbol is missing from the alphabet
        InsufficientDataError: If the text is empty
    """
    numbers = _indices(text, alphabet)
    modulus = len(alphabet)
    scan_coefficients = (
        list(coefficients) if coefficients is not None else list(range(1, modulus))
    )
    results: dict[int, ChiSquare] = {}
    for coefficient in scan_coefficients:
        counts = [0] * modulus
        for i, number in enumerate(numbers):
            counts[(number + coefficient * i) % modulus] += 1
        results[coefficient] = uniformity(counts)
    return results
