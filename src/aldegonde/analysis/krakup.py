# ABOUTME: KRAKUP - Tests for cyclic phenomena in nonhomogeneous material
# ABOUTME: NSA GUPPY program #37 for detecting periodicities in mixed/irregular data

"""
KRAKUP: Cyclic Phenomena Detection in Nonhomogeneous Material

This module implements the KRAKUP algorithm from the NSA GUPPY suite.
Unlike standard periodicity tests (Kasiski, Friedman) which assume uniform
material, KRAKUP is designed to find cycles in data where:
- The period might change mid-stream
- Phase slips occur (cycle restarts unexpectedly)
- Material is mixed (plaintext + ciphertext interleaved)
- The cycle strength varies (amplitude modulation)

The algorithm uses:
1. Local periodicity profiling via sliding windows
2. Time-frequency spectrogram analysis
3. Phase tracking and slip detection
4. Multi-resolution confirmation
"""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from math import log2
from statistics import mean
from typing import TypeVar

import numpy as np

T = TypeVar("T")


@dataclass
class KrakupResult:
    """Results from KRAKUP cyclic phenomena analysis."""

    # Primary findings
    dominant_periods: list[tuple[int, float]]  # (period, confidence)

    # Spatial analysis
    periodicity_profile: list[tuple[int, int, float]]  # (position, period, strength)
    stable_regions: list[tuple[int, int, int, float]]  # (start, end, period, strength)

    # Anomaly detection
    phase_slips: list[tuple[int, int, float]]  # (position, period, magnitude)
    period_changes: list[tuple[int, int, int]]  # (position, old_period, new_period)

    # Diagnostics
    homogeneity_score: float  # 0=very nonhomogeneous, 1=uniform
    spectrogram: np.ndarray = field(repr=False)  # 2D: position × period


def text_to_numeric(text: Sequence[T]) -> np.ndarray:
    """Convert text to numeric sequence."""
    unique = set(text)
    symbols = list(unique)
    symbol_to_num = {sym: i for i, sym in enumerate(symbols)}
    return np.array([symbol_to_num[sym] for sym in text])


def column_ioc(text: Sequence[T], period: int) -> float:
    """Compute average IoC of columns when text is arranged with given period."""
    if len(text) < period * 2:
        return 0.0

    columns: list[list[T]] = [[] for _ in range(period)]
    for i, char in enumerate(text):
        columns[i % period].append(char)

    iocs = []
    for col in columns:
        if len(col) < 2:
            continue
        counts = Counter(col)
        n = len(col)
        numerator = sum(c * (c - 1) for c in counts.values())
        denominator = n * (n - 1)
        if denominator > 0:
            iocs.append(numerator / denominator)

    return mean(iocs) if iocs else 0.0


def autocorrelation_score(numeric: np.ndarray, period: int) -> float:
    """Compute normalized autocorrelation at given period."""
    if len(numeric) <= period:
        return 0.0

    shifted = numeric[period:]
    original = numeric[: len(shifted)]

    # Count matches
    matches = int(np.sum(shifted == original))
    return float(matches / len(shifted))


def differential_entropy_score(
    numeric: np.ndarray, period: int, alphabet_size: int
) -> float:
    """
    Compute entropy of differences at given period.
    Low entropy = predictable differences = likely true period.
    """
    if len(numeric) <= period:
        return 1.0  # High entropy = bad score

    diffs = (numeric[period:] - numeric[:-period]) % alphabet_size
    counts = Counter(diffs.tolist())
    n = len(diffs)

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / n
            entropy -= p * log2(p)

    # Normalize: 0 = no entropy (perfect), 1 = max entropy (random)
    max_entropy = log2(min(alphabet_size, n))
    if max_entropy > 0:
        return entropy / max_entropy
    return 1.0


def compute_spectrogram(
    text: Sequence[T],
    numeric: np.ndarray,
    min_period: int,
    max_period: int,
    window_size: int,
    step: int,
    alphabet_size: int,
) -> tuple[np.ndarray, list[tuple[int, int, float]]]:
    """
    Compute time-frequency spectrogram of periodicity.

    Returns:
        spectrogram: 2D array [positions, periods] with strength values
        profile: List of (position, best_period, strength) tuples
    """
    n_positions = (len(text) - window_size) // step + 1
    n_periods = max_period - min_period + 1

    if n_positions <= 0:
        return np.zeros((1, n_periods)), [(0, min_period, 0.0)]

    spectrogram = np.zeros((n_positions, n_periods))
    profile: list[tuple[int, int, float]] = []

    for i in range(n_positions):
        start = i * step
        end = start + window_size
        window_text = text[start:end]
        window_numeric = numeric[start:end]

        best_period = min_period
        best_strength = 0.0

        for p_idx, p in enumerate(range(min_period, max_period + 1)):
            if p >= len(window_text) // 2:
                continue

            # Compute combined score for this period
            ioc_score = column_ioc(window_text, p)
            auto_score = autocorrelation_score(window_numeric, p)
            diff_score = 1.0 - differential_entropy_score(
                window_numeric, p, alphabet_size
            )

            strength = 0.4 * ioc_score + 0.3 * auto_score + 0.3 * diff_score
            spectrogram[i, p_idx] = strength

            if strength > best_strength:
                best_strength = strength
                best_period = p

        profile.append((start, best_period, best_strength))

    return spectrogram, profile


def find_stable_regions(
    profile: list[tuple[int, int, float]], min_region_size: int = 3
) -> list[tuple[int, int, int, float]]:
    """
    Find contiguous regions where the same period dominates.

    Returns list of (start_pos, end_pos, period, avg_strength)
    """
    if not profile:
        return []

    regions: list[tuple[int, int, int, float]] = []
    current_start = profile[0][0]
    current_period = profile[0][1]
    current_strengths = [profile[0][2]]

    for pos, period, strength in profile[1:]:
        if period == current_period:
            current_strengths.append(strength)
        else:
            # End current region
            if len(current_strengths) >= min_region_size:
                regions.append(
                    (current_start, pos, current_period, mean(current_strengths))
                )
            # Start new region
            current_start = pos
            current_period = period
            current_strengths = [strength]

    # Don't forget last region
    if len(current_strengths) >= min_region_size:
        last_pos = profile[-1][0]
        regions.append(
            (current_start, last_pos, current_period, mean(current_strengths))
        )

    return regions


def detect_phase_slips(
    text: Sequence[T], period: int, threshold: float = 0.5
) -> list[tuple[int, float]]:
    """
    Detect phase slips within text for a given period.

    Returns list of (position, slip_magnitude) where slip was detected.
    """
    if len(text) < period * 3:
        return []

    slips: list[tuple[int, float]] = []

    # Compute fingerprints for each cycle
    fingerprints: list[tuple[int, dict[T, float]]] = []
    for i in range(0, len(text) - period, period):
        cycle = list(text[i : i + period])
        # Fingerprint = normalized frequency distribution
        counts = Counter(cycle)
        total = sum(counts.values())
        fingerprint: dict[T, float] = {k: v / total for k, v in counts.items()}
        fingerprints.append((i, fingerprint))

    # Compare consecutive fingerprints
    for i in range(1, len(fingerprints)):
        pos1, fp1 = fingerprints[i - 1]
        pos2, fp2 = fingerprints[i]

        # Compute distance between fingerprints (total variation distance)
        all_keys = set(fp1.keys()) | set(fp2.keys())
        distance = sum(abs(fp1.get(k, 0) - fp2.get(k, 0)) for k in all_keys) / 2

        if distance > threshold:
            slips.append((pos2, distance))

    return slips


def detect_period_changes(
    profile: list[tuple[int, int, float]], min_gap: int = 2
) -> list[tuple[int, int, int]]:
    """
    Detect points where the dominant period changes.

    Returns list of (position, old_period, new_period)
    """
    changes: list[tuple[int, int, int]] = []

    i = 0
    while i < len(profile) - min_gap:
        current_period = profile[i][1]

        # Look ahead to see if period changes
        j = i + 1
        while j < len(profile) and profile[j][1] == current_period:
            j += 1

        if j < len(profile):
            # Found a change
            new_period = profile[j][1]
            if new_period != current_period:
                # Confirm it's stable (not just noise)
                stable_count = 0
                for k in range(j, min(j + min_gap, len(profile))):
                    if profile[k][1] == new_period:
                        stable_count += 1

                if stable_count >= min_gap:
                    changes.append((profile[j][0], current_period, new_period))

        i = j

    return changes


def compute_homogeneity_score(profile: list[tuple[int, int, float]]) -> float:
    """
    Compute how homogeneous the material is.
    1.0 = perfectly uniform (same period throughout)
    0.0 = very nonhomogeneous (constantly changing)
    """
    if len(profile) < 2:
        return 1.0

    periods = [p for _, p, _ in profile]

    # Count how often the period stays the same
    same_count = sum(1 for i in range(1, len(periods)) if periods[i] == periods[i - 1])

    return same_count / (len(periods) - 1)


def aggregate_period_confidences(
    profile: list[tuple[int, int, float]], min_period: int
) -> list[tuple[int, float]]:
    """
    Aggregate evidence for each period across all positions.

    Returns sorted list of (period, confidence) with highest confidence first.
    """
    period_evidence: dict[int, list[float]] = {}

    # From profile
    for _, period, strength in profile:
        if period not in period_evidence:
            period_evidence[period] = []
        period_evidence[period].append(strength)

    # Compute confidence for each period
    confidences: list[tuple[int, float]] = []
    for period, strengths in period_evidence.items():
        # Confidence = frequency * average strength
        frequency = len(strengths) / len(profile)
        avg_strength = mean(strengths)
        confidence = frequency * avg_strength
        confidences.append((period, confidence))

    # Sort by confidence descending
    confidences.sort(key=lambda x: x[1], reverse=True)

    return confidences


def krakup(
    text: Sequence[T],
    min_period: int = 2,
    max_period: int = 50,
    window_size: int = 100,
    step: int = 10,
    alphabet_size: int | None = None,
) -> KrakupResult:
    """
    KRAKUP: Detect cyclic phenomena in nonhomogeneous material.

    Args:
        text: Input text sequence
        min_period: Minimum period to test
        max_period: Maximum period to test
        window_size: Size of sliding window for local analysis
        step: Step size for sliding window
        alphabet_size: Size of alphabet (auto-detected if None)

    Returns:
        KrakupResult with detected periods, phase slips, and analysis data
    """
    if len(text) < window_size:
        window_size = len(text) // 2
    if window_size < min_period * 2:
        window_size = min_period * 2

    if alphabet_size is None:
        alphabet_size = len(set(text))

    # Convert to numeric
    numeric = text_to_numeric(text)

    # Compute spectrogram and profile
    spectrogram, profile = compute_spectrogram(
        text, numeric, min_period, max_period, window_size, step, alphabet_size
    )

    # Find stable regions
    stable_regions = find_stable_regions(profile)

    # Detect phase slips in each stable region
    all_phase_slips: list[tuple[int, int, float]] = []
    for start, end, period, _ in stable_regions:
        # Extract region text
        region_text = text[start:end] if end > start else text[start:]
        slips = detect_phase_slips(region_text, period)
        # Adjust positions to global coordinates
        for pos, magnitude in slips:
            all_phase_slips.append((start + pos, period, magnitude))

    # Detect period changes
    period_changes = detect_period_changes(profile)

    # Compute homogeneity
    homogeneity = compute_homogeneity_score(profile)

    # Aggregate period confidences
    dominant_periods = aggregate_period_confidences(profile, min_period)

    return KrakupResult(
        dominant_periods=dominant_periods[:10],  # Top 10
        periodicity_profile=profile,
        stable_regions=stable_regions,
        phase_slips=all_phase_slips,
        period_changes=period_changes,
        homogeneity_score=homogeneity,
        spectrogram=spectrogram,
    )


def print_krakup_analysis(text: Sequence[T], **kwargs: int) -> KrakupResult:
    """Run KRAKUP analysis and print results."""
    result = krakup(text, **kwargs)

    print("\n" + "=" * 70)
    print("KRAKUP: Cyclic Phenomena Analysis (Nonhomogeneous Material)")
    print("=" * 70)

    print(f"\nText length: {len(text)}")
    print(f"Homogeneity score: {result.homogeneity_score:.3f}", end="")
    if result.homogeneity_score > 0.8:
        print(" (uniform material)")
    elif result.homogeneity_score > 0.5:
        print(" (moderately nonhomogeneous)")
    else:
        print(" (highly nonhomogeneous)")

    print("\n--- Dominant Periods ---")
    for period, confidence in result.dominant_periods[:5]:
        bar = "█" * int(confidence * 50)
        print(f"  Period {period:3d}: {confidence:.4f} {bar}")

    if result.stable_regions:
        print("\n--- Stable Regions ---")
        for start, end, period, strength in result.stable_regions[:10]:
            length = end - start
            print(
                f"  Positions {start:5d}-{end:5d} (len={length:4d}): "
                f"period={period:2d}, strength={strength:.3f}"
            )

    if result.period_changes:
        print("\n--- Period Change Points ---")
        for pos, old_p, new_p in result.period_changes[:10]:
            print(f"  Position {pos:5d}: period {old_p} → {new_p}")

    if result.phase_slips:
        print("\n--- Phase Slips Detected ---")
        for pos, period, magnitude in result.phase_slips[:10]:
            print(f"  Position {pos:5d}: period={period}, magnitude={magnitude:.3f}")

    # Print spectrogram summary
    if result.spectrogram.size > 0:
        print("\n--- Spectrogram Summary ---")
        # Find periods with highest average power
        avg_power = np.mean(result.spectrogram, axis=0)
        min_p = kwargs.get("min_period", 2)
        top_indices = np.argsort(avg_power)[-5:][::-1]
        print("  Periods with highest average power:")
        for idx in top_indices:
            period = min_p + idx
            power = avg_power[idx]
            print(f"    Period {period:3d}: {power:.4f}")

    print("=" * 70)

    return result
