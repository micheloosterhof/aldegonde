# ABOUTME: Detailed doublet analysis of Liber Primus ciphertext
# ABOUTME: Calculates exact doublet rates and investigates identity character candidates

"""
Detailed analysis of LP doublet statistics.

Goal: Determine the exact doublet rate and identify which rune
at that frequency could be the "identity character" in an autokey cipher.
"""

import sys
sys.path.insert(0, 'src')

from collections import Counter
from aldegonde import c3301


def load_lp_text(filepath: str) -> str:
    """Load LP text from file."""
    with open(filepath) as f:
        return f.read()


def clean_runes(text: str) -> str:
    """Extract only valid runes from text."""
    return "".join(c for c in text if c in c3301.CICADA_ALPHABET)


def count_doublets(text: str) -> tuple[int, int, float]:
    """Count consecutive identical characters (doublets)."""
    if len(text) < 2:
        return 0, 0, 0.0
    count = sum(1 for i in range(len(text) - 1) if text[i] == text[i + 1])
    possible = len(text) - 1
    return count, possible, count / possible


def count_triplets(text: str) -> tuple[int, int, float]:
    """Count three consecutive identical characters."""
    if len(text) < 3:
        return 0, 0, 0.0
    count = sum(1 for i in range(len(text) - 2)
                if text[i] == text[i + 1] == text[i + 2])
    possible = len(text) - 2
    return count, possible, count / possible


def frequency_analysis(text: str) -> list[tuple[str, int, float]]:
    """Return sorted frequency analysis."""
    counts = Counter(text)
    total = len(text)
    return sorted(
        [(char, count, count / total) for char, count in counts.items()],
        key=lambda x: x[2]  # Sort by frequency ascending
    )


if __name__ == "__main__":
    # Load LP text
    lp_text = load_lp_text("data/page0-58.txt")
    runes = clean_runes(lp_text)

    print("=" * 70)
    print("Liber Primus Doublet Analysis")
    print("=" * 70)

    print(f"\nTotal rune count: {len(runes)}")
    print(f"Unique runes: {len(set(runes))}")
    print(f"Expected (29 runes): {c3301.CICADA_ALPHABET}")

    # Doublet analysis
    doublets, possible, doublet_rate = count_doublets(runes)
    triplets, _, triplet_rate = count_triplets(runes)

    expected_doublet_rate = 1 / 29
    suppression_factor = expected_doublet_rate / doublet_rate if doublet_rate > 0 else float('inf')

    print(f"\n--- Doublet Statistics ---")
    print(f"Doublets found: {doublets}")
    print(f"Possible positions: {possible}")
    print(f"Doublet rate: {doublet_rate:.6f} ({doublet_rate * 100:.4f}%)")
    print(f"Expected random: {expected_doublet_rate:.6f} ({expected_doublet_rate * 100:.4f}%)")
    print(f"Suppression factor: {suppression_factor:.2f}x")
    print(f"\nTriplets found: {triplets}")
    print(f"Triplet rate: {triplet_rate:.6f}")

    # Frequency analysis
    print(f"\n--- Frequency Analysis (sorted by ascending frequency) ---")
    freqs = frequency_analysis(runes)

    print("\nRunes sorted by frequency (rarest first):")
    for i, (rune, count, freq) in enumerate(freqs):
        # Mark runes with frequency close to doublet rate
        marker = " <-- MATCHES DOUBLET RATE" if abs(freq - doublet_rate) < 0.003 else ""
        idx = c3301.CICADA_ALPHABET.index(rune) if rune in c3301.CICADA_ALPHABET else -1
        english = c3301.CICADA_ENGLISH_ALPHABET[idx] if 0 <= idx < len(c3301.CICADA_ENGLISH_ALPHABET) else "?"
        print(f"  {rune} ({english:2s}) idx={idx:2d}: {count:4d} = {freq*100:5.2f}%{marker}")

    # Calculate which frequency matches doublet rate
    print(f"\n--- Identity Character Candidates ---")
    print(f"Looking for rune with frequency ≈ {doublet_rate*100:.2f}%")

    for rune, count, freq in freqs:
        if abs(freq - doublet_rate) < 0.005:  # Within 0.5%
            idx = c3301.CICADA_ALPHABET.index(rune)
            english = c3301.CICADA_ENGLISH_ALPHABET[idx]
            print(f"  CANDIDATE: {rune} ({english}) at {freq*100:.2f}% (diff: {abs(freq-doublet_rate)*100:.3f}%)")

    # Show doublet details
    print(f"\n--- Doublet Locations ---")
    doublet_chars = Counter()
    for i in range(len(runes) - 1):
        if runes[i] == runes[i + 1]:
            doublet_chars[runes[i]] += 1

    print("Runes that appear as doublets:")
    for rune, count in doublet_chars.most_common():
        idx = c3301.CICADA_ALPHABET.index(rune)
        english = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {rune} ({english}): {count} doublets")

    # Segment analysis
    print(f"\n--- Per-Segment Doublet Rates ---")
    segments = lp_text.split("$")

    for i, seg in enumerate(segments[:10]):
        seg_runes = clean_runes(seg)
        if len(seg_runes) < 10:
            continue
        d, p, rate = count_doublets(seg_runes)
        supp = (1/29) / rate if rate > 0 else float('inf')
        print(f"  Segment {i}: len={len(seg_runes):4d}, doublets={d:3d}, rate={rate*100:.3f}%, suppression={supp:.1f}x")
