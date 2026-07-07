#!/usr/bin/env python3
"""Delta stream analysis of Liber Primus.

Computes the delta stream (consecutive rune differences mod 29) for each
LP segment and runs full statistical analysis on it to characterize the
suppression of symbol 0.
"""

import os

from aldegonde import c3301
from aldegonde.analysis import friedman
from aldegonde.analysis.rune_frequency import (
    analyze_byte_mappings,
    analyze_matrix_sizes,
    find_best_suppression,
    natural_mapping,
    print_frequency_profile,
)
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor
from aldegonde.stats.dist import print_dist
from aldegonde.stats.entropy import shannon_entropy
from aldegonde.stats.ioc import print_ioc_statistics
from aldegonde.stats.kappa import print_kappa
from aldegonde.stats.repeats import print_repeat_statistics


def deltastream(runes: list[int], skip: int = 1) -> list[int]:
    """Calculate delta stream mod 29."""
    diff = []
    for i in range(len(runes) - skip):
        diff.append((runes[i + skip] - runes[i]) % 29)
    return diff


def main() -> None:
    """Main analysis function."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "..", "data", "page0-58.txt")

    with open(data_file) as f:
        lp = f.read()

    segments = lp.split("$")
    z = segments[0:10]

    print(f"{len(segments)} segments")

    # Collect all deltas across all segments for aggregate analysis
    all_deltas_runes: list[str] = []

    for i, s in enumerate(z):
        if len(s) == 0:
            continue
        print(f"\n\n{'='*60}")
        print(f"SEGMENT {i} - DELTA STREAM ANALYSIS")
        print(f"{'='*60}")

        raw = "".join([x for x in s if x in c3301.CICADA_ALPHABET])
        if len(raw) < 3:
            print(f"  Segment too short ({len(raw)} runes), skipping")
            continue

        # Convert to indices and compute delta stream
        indices = [c3301.r2i(r) for r in raw]
        deltas = deltastream(indices, skip=1)

        # Convert delta values back to runes for statistical analysis
        delta_runes = "".join(c3301.i2r(d) for d in deltas)
        all_deltas_runes.extend(delta_runes)

        print(f"Raw length: {len(raw)}, Delta length: {len(deltas)}")

        # Show first few deltas
        print(f"First 30 deltas: {deltas[:30]}")

        # Count zeros
        zero_count = deltas.count(0)
        print(f"Delta=0 count: {zero_count}/{len(deltas)} "
              f"({zero_count / len(deltas) * 100:.2f}%)")
        print(f"Expected uniform: {len(deltas) / 29:.1f} "
              f"({100 / 29:.2f}%)")

        if len(delta_runes) < 10:
            print("  Too few deltas for full analysis")
            continue

        # Run statistics on delta stream (as rune characters)
        print(f"\nused alphabet: {len(set(delta_runes))} symbols")
        print(f"length: {len(delta_runes)} symbols")
        print(f"   prime factors =: {factor.prime_factors(len(delta_runes))}")

        print_dist(delta_runes)
        shannon_entropy(delta_runes)
        print_ioc_statistics(delta_runes, alphabetsize=29)
        bigram_diagram.print_auto_bigram_diagram(
            delta_runes, alphabet=c3301.CICADA_ALPHABET,
        )
        print_kappa(delta_runes)
        friedman.friedman_test(delta_runes, maxperiod=34)
        print_repeat_statistics(delta_runes, minimum=2)

    # Aggregate analysis across all segments
    all_delta_str = "".join(all_deltas_runes)
    if len(all_delta_str) > 10:
        print(f"\n\n{'='*60}")
        print("AGGREGATE DELTA STREAM - ALL SEGMENTS")
        print(f"{'='*60}")
        print(f"Total deltas: {len(all_delta_str)}")

        all_indices = [c3301.r2i(r) for r in all_delta_str]
        zero_count = all_indices.count(0)
        print(f"Delta=0 count: {zero_count}/{len(all_indices)} "
              f"({zero_count / len(all_indices) * 100:.2f}%)")
        print(f"Expected uniform: {len(all_indices) / 29:.1f} "
              f"({100 / 29:.2f}%)")

        print_dist(all_delta_str)
        shannon_entropy(all_delta_str)
        print_ioc_statistics(all_delta_str, alphabetsize=29)

        # Frequency suppression model analysis
        print(f"\n{'='*60}")
        print("FREQUENCY SUPPRESSION MODEL ANALYSIS")
        print(f"{'='*60}")

        # Compute observed delta=0 frequency
        observed_freq = zero_count / len(all_indices)
        uniform = 1.0 / 29
        ratio = observed_freq / uniform
        print(f"\nObserved delta=0 frequency: {observed_freq:.5f}")
        print(f"Uniform expectation:        {uniform:.5f}")
        print(f"Suppression ratio:          {ratio:.4f}")

        # Model: 13x13 matrix
        print("\n--- 13x13 Matrix Model ---")
        observed_dict = {}
        from collections import Counter
        counts = Counter(all_indices)
        for idx in range(29):
            observed_dict[idx] = counts.get(idx, 0) / len(all_indices)

        best_count, best_profile = find_best_suppression(
            observed_dict, 13, 29, 0,
        )
        print(f"Best fit: symbol 0 gets {best_count} of 169 pre-images")
        print_frequency_profile(best_profile, "13x13 best fit for delta=0")

        # Natural mapping comparisons
        print("\n--- Natural Mapping Comparison ---")
        for n in [169, 256, 512, 841]:
            profile = natural_mapping(n, 29)
            suppressed = profile.suppressed_symbols
            print(f"  {n} states: suppressed={suppressed[:5]}{'...' if len(suppressed) > 5 else ''}, "
                  f"sym0 ratio={profile.suppression_ratio[0]:.4f}")

        analyze_matrix_sizes()
        analyze_byte_mappings()


if __name__ == "__main__":
    main()
