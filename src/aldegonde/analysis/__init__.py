"""Cryptanalysis algorithms."""

from aldegonde.analysis.friedman import friedman_test, friedman_test_with_interrupter
from aldegonde.analysis.guballa import bigram_break_pasc
from aldegonde.analysis.split import (
    split_by_character,
    split_by_doublet,
    split_by_slice,
    split_by_slice_interrupted,
    split_by_whitespace,
    trim,
)
from aldegonde.analysis.rune_frequency import (
    FrequencyProfile,
    analyze_byte_mappings,
    analyze_matrix_sizes,
    find_best_suppression,
    matrix_mapping,
    natural_mapping,
    print_frequency_profile,
    scan_state_spaces,
    truncated_byte_mapping,
)
from aldegonde.analysis.twist import twist, twist_test, twist_test_with_interrupter

__all__ = [
    # friedman
    "friedman_test",
    "friedman_test_with_interrupter",
    # guballa
    "bigram_break_pasc",
    # split
    "split_by_character",
    "split_by_doublet",
    "split_by_slice",
    "split_by_slice_interrupted",
    "split_by_whitespace",
    "trim",
    # rune_frequency
    "FrequencyProfile",
    "analyze_byte_mappings",
    "analyze_matrix_sizes",
    "find_best_suppression",
    "matrix_mapping",
    "natural_mapping",
    "print_frequency_profile",
    "scan_state_spaces",
    "truncated_byte_mapping",
    # twist
    "twist",
    "twist_test",
    "twist_test_with_interrupter",
]
