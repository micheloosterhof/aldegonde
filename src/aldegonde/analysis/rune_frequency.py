"""Rune frequency suppression analysis.

Models how a mapping from a larger state space to base 29 can naturally
produce a suppressed symbol 0 in the output (ciphertext delta stream),
even when the input (plaintext) has natural language distribution.

The LP delta stream shows:
- Symbol 0 appears LESS often than expected for uniform (suppressed)
- The remaining 28 symbols are approximately uniform
- The plaintext has natural language statistics (high IoC)

This signature arises naturally when N input states are mapped to 29 output
symbols and N mod 29 != 0. The remainder determines which symbols get fewer
pre-images. Two concrete models:

1. **13x13 matrix (169 states)**: 169 = 5*29 + 24. In a naive sequential
   assignment, 24 symbols get 6 pre-images and 5 symbols get only 5.
   If symbol 0 is among the 5, its expected frequency is 5/169 = 2.96%
   vs 6/169 = 3.55% for the others. The matrix structure could represent
   a digraphic cipher (pairs from a 13-symbol intermediate alphabet).

2. **Truncated 256 -> 29**: 256 = 8*29 + 24. Without rejection, 24 symbols
   get 9 pre-images and 5 get 8. Symbol 0 at 8/256 = 3.125% vs 9/256 =
   3.516%. With rejection sampling (discard 24 values), perfectly uniform.
   The non-rejected variant naturally suppresses 5 symbols including
   potentially symbol 0.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

from aldegonde.stats.ngrams import ngram_distribution

if TYPE_CHECKING:
    from collections.abc import Sequence

T = TypeVar("T")


@dataclass
class FrequencyProfile:
    """Frequency profile from mapping N input states to M output symbols.

    Attributes:
        mapping: Dict mapping each output symbol index to its count of
            pre-images (number of input states that produce it).
        total_states: Total number of input states used (after rejection).
        alphabet_size: Size of the output alphabet.
        expected_frequencies: Expected output frequency for each symbol,
            assuming uniform input distribution over used states.
        chi_square: Chi-square statistic vs uniform output distribution.
        entropy: Shannon entropy of the output distribution (bits).
    """

    mapping: dict[int, int]
    total_states: int
    alphabet_size: int
    expected_frequencies: dict[int, float] = field(default_factory=dict)
    chi_square: float = 0.0
    entropy: float = 0.0

    def __post_init__(self) -> None:
        """Compute derived statistics."""
        self.expected_frequencies = {
            k: v / self.total_states for k, v in self.mapping.items()
        }
        uniform = 1.0 / self.alphabet_size
        self.chi_square = sum(
            (freq - uniform) ** 2 / uniform
            for freq in self.expected_frequencies.values()
        )
        self.entropy = -sum(
            freq * math.log2(freq)
            for freq in self.expected_frequencies.values()
            if freq > 0
        )

    @property
    def suppressed_symbols(self) -> list[int]:
        """Symbols with fewer pre-images than the maximum."""
        if not self.mapping:
            return []
        max_count = max(self.mapping.values())
        return sorted(s for s, c in self.mapping.items() if c < max_count)

    @property
    def suppression_ratio(self) -> dict[int, float]:
        """Ratio of each symbol's frequency to uniform expectation."""
        uniform = 1.0 / self.alphabet_size
        return {
            k: freq / uniform
            for k, freq in self.expected_frequencies.items()
        }


def _validate_alphabet_size(alphabet_size: int) -> None:
    if alphabet_size < 2:
        msg = f"alphabet_size must be >= 2, got {alphabet_size}"
        raise ValueError(msg)


def _validate_symbol_range(symbol: int, alphabet_size: int) -> None:
    if symbol < 0 or symbol >= alphabet_size:
        msg = f"suppressed_symbol {symbol} out of range [0, {alphabet_size})"
        raise ValueError(msg)


def natural_mapping(
    total_states: int,
    alphabet_size: int,
) -> FrequencyProfile:
    """Create the natural (sequential) mapping from N states to M symbols.

    Maps states 0..N-1 to symbols via state % alphabet_size. This is the
    simplest non-rejection mapping. The first (N mod M) symbols each get
    floor(N/M)+1 pre-images; the rest get floor(N/M).

    Args:
        total_states: Number of input states (e.g., 169, 256).
        alphabet_size: Number of output symbols (e.g., 29).

    Returns:
        FrequencyProfile showing which symbols are naturally suppressed.

    Raises:
        ValueError: If parameters are invalid.
    """
    _validate_alphabet_size(alphabet_size)
    if total_states < 1:
        msg = f"total_states must be >= 1, got {total_states}"
        raise ValueError(msg)

    base = total_states // alphabet_size
    remainder = total_states % alphabet_size

    # First `remainder` symbols get base+1, rest get base
    mapping: dict[int, int] = {}
    for symbol in range(alphabet_size):
        mapping[symbol] = base + 1 if symbol < remainder else base

    return FrequencyProfile(
        mapping=mapping,
        total_states=total_states,
        alphabet_size=alphabet_size,
    )


def matrix_mapping(
    matrix_size: int,
    alphabet_size: int,
    suppressed_symbol: int = 0,
    suppressed_count: int | None = None,
) -> FrequencyProfile:
    """Create a frequency profile from an NxN matrix mapped to an alphabet.

    The matrix has matrix_size^2 states. In the default mode (suppressed_count
    is None), uses natural sequential mapping where symbol 0 may or may not
    be among the suppressed symbols depending on the remainder.

    With explicit suppressed_count, forces a specific number of pre-images
    for the target symbol and distributes the rest.

    Args:
        matrix_size: Side length of the square matrix (e.g., 13 for 13x13=169).
        alphabet_size: Size of the output alphabet (e.g., 29 for runes).
        suppressed_symbol: Index of the symbol to control (default 0).
        suppressed_count: Explicit number of pre-images for this symbol.
            If None, uses natural mapping.

    Returns:
        FrequencyProfile with the mapping and statistics.

    Raises:
        ValueError: If parameters are invalid.
    """
    total = matrix_size * matrix_size
    _validate_alphabet_size(alphabet_size)
    _validate_symbol_range(suppressed_symbol, alphabet_size)

    if suppressed_count is None:
        return natural_mapping(total, alphabet_size)

    if suppressed_count < 0 or suppressed_count > total:
        msg = f"suppressed_count {suppressed_count} out of range"
        raise ValueError(msg)

    # Distribute remaining states among non-suppressed symbols
    remaining = total - suppressed_count
    other_count = alphabet_size - 1
    other_base = remaining // other_count
    other_remainder = remaining % other_count

    mapping: dict[int, int] = {}
    idx = 0
    for symbol in range(alphabet_size):
        if symbol == suppressed_symbol:
            mapping[symbol] = suppressed_count
        else:
            extra = 1 if idx < other_remainder else 0
            mapping[symbol] = other_base + extra
            idx += 1

    return FrequencyProfile(
        mapping=mapping,
        total_states=total,
        alphabet_size=alphabet_size,
    )


def truncated_byte_mapping(
    alphabet_size: int,
    byte_size: int = 256,
    suppressed_symbol: int = 0,
    suppressed_count: int | None = None,
) -> FrequencyProfile:
    """Create a frequency profile from a byte-to-alphabet mapping.

    Maps byte_size input states (default 256) to alphabet_size output symbols.

    Without suppressed_count (None): uses rejection sampling to achieve
    perfect uniformity. floor(byte_size/alphabet_size)*alphabet_size states
    are used, remainder are rejected.

    With suppressed_count: uses all byte_size states with the specified
    count assigned to the suppressed symbol.

    Args:
        alphabet_size: Size of the output alphabet (e.g., 29).
        byte_size: Number of input states (default 256 for bytes).
        suppressed_symbol: Index of the symbol to control (default 0).
        suppressed_count: Number of pre-images for the suppressed symbol.
            If None, uses uniform truncated mapping.

    Returns:
        FrequencyProfile with the mapping and statistics.

    Raises:
        ValueError: If parameters are invalid.
    """
    _validate_alphabet_size(alphabet_size)
    _validate_symbol_range(suppressed_symbol, alphabet_size)

    if suppressed_count is None:
        # Uniform truncated: reject byte_size % alphabet_size values
        per_symbol = byte_size // alphabet_size
        effective_total = per_symbol * alphabet_size
        uniform_mapping = dict.fromkeys(range(alphabet_size), per_symbol)
        return FrequencyProfile(
            mapping=uniform_mapping,
            total_states=effective_total,
            alphabet_size=alphabet_size,
        )

    # Non-uniform: use all states, control one symbol
    remaining = byte_size - suppressed_count
    other_count = alphabet_size - 1
    other_base = remaining // other_count
    other_remainder = remaining % other_count

    mapping: dict[int, int] = {}
    idx = 0
    for symbol in range(alphabet_size):
        if symbol == suppressed_symbol:
            mapping[symbol] = suppressed_count
        else:
            extra = 1 if idx < other_remainder else 0
            mapping[symbol] = other_base + extra
            idx += 1

    return FrequencyProfile(
        mapping=mapping,
        total_states=byte_size,
        alphabet_size=alphabet_size,
    )


def observed_delta_frequencies(
    runes: Sequence[object],
    alphabet_size: int = 29,
) -> dict[int, float]:
    """Compute observed frequency distribution of a delta stream.

    Args:
        runes: Sequence of delta values (as strings or objects).
        alphabet_size: Size of the alphabet.

    Returns:
        Dict mapping symbol index to observed frequency (proportion).
    """
    dist = ngram_distribution(runes, length=1, cut=0)
    total = sum(dist.values())
    if total == 0:
        return {}
    return {i: dist.get(str(i), 0) / total for i in range(alphabet_size)}


def find_best_suppression(
    observed_freq: dict[int, float],
    matrix_size: int,
    alphabet_size: int = 29,
    suppressed_symbol: int = 0,
) -> tuple[int, FrequencyProfile]:
    """Find the suppressed_count that best matches observed frequencies.

    Searches over possible pre-image counts for the suppressed symbol
    to find which best explains its observed frequency in the delta stream.

    Args:
        observed_freq: Observed frequency dict (symbol index -> proportion).
        matrix_size: Side length of the matrix.
        alphabet_size: Output alphabet size.
        suppressed_symbol: Symbol whose frequency is suppressed.

    Returns:
        Tuple of (best_count, best_profile).
    """
    total = matrix_size * matrix_size
    best_count = 0
    best_error = float("inf")
    best_profile = matrix_mapping(matrix_size, alphabet_size, suppressed_symbol, 1)

    target = observed_freq.get(suppressed_symbol, 0.0)

    for count in range(total):
        profile = matrix_mapping(matrix_size, alphabet_size, suppressed_symbol, count)
        predicted = profile.expected_frequencies[suppressed_symbol]
        error = abs(predicted - target)
        if error < best_error:
            best_error = error
            best_count = count
            best_profile = profile

    return best_count, best_profile


def scan_state_spaces(
    alphabet_size: int = 29,
    max_states: int = 1024,
    target_symbol: int = 0,
) -> list[tuple[int, int, float, list[int]]]:
    """Scan state space sizes to find which naturally suppress a given symbol.

    For each total_states from alphabet_size to max_states, computes the
    natural mapping and checks whether target_symbol is among the suppressed
    symbols (those with fewer pre-images).

    Args:
        alphabet_size: Output alphabet size (default 29).
        max_states: Maximum state space size to scan.
        target_symbol: Symbol index to check for suppression.

    Returns:
        List of (total_states, remainder, suppression_ratio, suppressed_list)
        tuples where target_symbol is suppressed.
    """
    results: list[tuple[int, int, float, list[int]]] = []
    for n in range(alphabet_size, max_states + 1):
        profile = natural_mapping(n, alphabet_size)
        if target_symbol in profile.suppressed_symbols:
            remainder = n % alphabet_size
            ratio = profile.suppression_ratio[target_symbol]
            results.append((n, remainder, ratio, profile.suppressed_symbols))
    return results


def print_frequency_profile(profile: FrequencyProfile, label: str = "") -> None:
    """Print a frequency profile summary.

    Args:
        profile: The FrequencyProfile to display.
        label: Optional label for the output.
    """
    if label:
        print(f"\n=== {label} ===")
    print(f"Total states: {profile.total_states}")
    print(f"Alphabet size: {profile.alphabet_size}")
    print(f"Entropy: {profile.entropy:.4f} bits")
    print(f"Max entropy: {math.log2(profile.alphabet_size):.4f} bits")
    print(f"Chi-square vs uniform: {profile.chi_square:.6f}")
    print(f"Suppressed symbols: {profile.suppressed_symbols}")
    print()

    uniform = 1.0 / profile.alphabet_size
    print(f"{'Symbol':>6} {'States':>6} {'Freq':>8} {'Uniform':>8} {'Ratio':>8}")
    print("-" * 42)
    for symbol in sorted(profile.mapping.keys()):
        states = profile.mapping[symbol]
        freq = profile.expected_frequencies[symbol]
        ratio = profile.suppression_ratio[symbol]
        marker = " <<" if ratio < 0.95 else ""
        print(
            f"{symbol:>6} {states:>6} {freq:>8.4f} {uniform:>8.4f} {ratio:>8.3f}{marker}"
        )


def analyze_matrix_sizes(
    alphabet_size: int = 29,
    target_symbol: int = 0,
    max_matrix: int = 20,
) -> None:
    """Print analysis of square matrix sizes and natural suppression.

    For each matrix size N, shows whether symbol 0 is naturally suppressed
    by the N^2 mod 29 remainder structure.

    Args:
        alphabet_size: Output alphabet size (default 29).
        target_symbol: Symbol to track (default 0).
        max_matrix: Maximum matrix side length to test.
    """
    print(f"\nMatrix size analysis (alphabet={alphabet_size}, "
          f"tracking symbol {target_symbol})")
    print(f"{'N':>3} {'N^2':>5} {'Base':>5} {'Rem':>4} "
          f"{'Sym0 freq':>10} {'Uniform':>8} {'Ratio':>7} {'Suppressed?':>12}")
    print("-" * 62)

    for n in range(2, max_matrix + 1):
        total = n * n
        profile = natural_mapping(total, alphabet_size)
        freq = profile.expected_frequencies[target_symbol]
        ratio = profile.suppression_ratio[target_symbol]
        remainder = total % alphabet_size
        suppressed = target_symbol in profile.suppressed_symbols
        marker = "YES" if suppressed else ""
        print(f"{n:>3} {total:>5} {total // alphabet_size:>5} {remainder:>4} "
              f"{freq:>10.5f} {profile.expected_frequencies[0]:>8.5f} "
              f"{ratio:>7.4f} {marker:>12}")


def analyze_byte_mappings(
    alphabet_size: int = 29,
    target_symbol: int = 0,
) -> None:
    """Print analysis of byte-to-rune mapping options.

    Shows the natural mapping (no rejection) and how different byte sizes
    affect suppression of symbol 0.

    Args:
        alphabet_size: Output alphabet size (default 29).
        target_symbol: Symbol to track (default 0).
    """
    print(f"\n=== Byte mapping analysis (N -> {alphabet_size}) ===")
    print(f"Tracking symbol: {target_symbol}")

    for byte_size in [128, 256, 512, 1024]:
        profile = natural_mapping(byte_size, alphabet_size)
        remainder = byte_size % alphabet_size
        freq0 = profile.expected_frequencies[target_symbol]
        ratio = profile.suppression_ratio[target_symbol]
        suppressed = target_symbol in profile.suppressed_symbols

        print(f"\n  {byte_size} states: "
              f"{byte_size}={byte_size // alphabet_size}*{alphabet_size}+{remainder}")
        print(f"    Symbol {target_symbol} freq: {freq0:.5f}  ratio: {ratio:.4f}  "
              f"suppressed: {suppressed}")
        print(f"    Suppressed symbols ({len(profile.suppressed_symbols)}): "
              f"{profile.suppressed_symbols}")

    # Detailed view for 256
    print("\n  --- 256-state detail ---")
    profile = natural_mapping(256, alphabet_size)
    print(f"  {'Symbol':>6} {'States':>6} {'Freq':>8} {'Ratio':>7}")
    for s in range(alphabet_size):
        states = profile.mapping[s]
        freq = profile.expected_frequencies[s]
        ratio = profile.suppression_ratio[s]
        marker = " <<" if s in profile.suppressed_symbols else ""
        print(f"  {s:>6} {states:>6} {freq:>8.5f} {ratio:>7.4f}{marker}")
