"""Cryptanalysis algorithms."""

from aldegonde.analysis.coincidence import (
    BoundaryCoincidence,
    BoundaryPermutation,
    DeltaRepeat,
    JointCount,
    boundary_coincidence,
    boundary_permutation_test,
    delta_repeat_counts,
    joint_coincidence,
    match_indicator,
    recut_words,
    word_index_map,
)
from aldegonde.analysis.delta import DeltaOp, delta, delta2
from aldegonde.analysis.friedman import friedman_test, friedman_test_with_interrupter
from aldegonde.analysis.guballa import bigram_break_pasc
from aldegonde.analysis.indepth import AlignmentResult, alignment_coincidence
from aldegonde.analysis.kasiski import (
    distance_spectrum,
    kasiski_examination,
    print_kasiski_statistics,
    repeat_distances,
)
from aldegonde.analysis.rune_frequency import (
    FrequencyProfile,
    find_best_suppression,
    matrix_mapping,
    natural_mapping,
    scan_state_spaces,
    truncated_byte_mapping,
)
from aldegonde.analysis.split import (
    split_by_character,
    split_by_doublet,
    split_by_slice,
    split_by_slice_interrupted,
    split_by_whitespace,
    trim,
)
from aldegonde.analysis.twist import twist, twist_test, twist_test_with_interrupter

__all__ = [
    # coincidence
    "BoundaryCoincidence",
    "BoundaryPermutation",
    "DeltaRepeat",
    "JointCount",
    "boundary_coincidence",
    "boundary_permutation_test",
    "delta_repeat_counts",
    "joint_coincidence",
    "match_indicator",
    "recut_words",
    "word_index_map",
    # delta
    "DeltaOp",
    "delta",
    "delta2",
    # friedman
    "friedman_test",
    "friedman_test_with_interrupter",
    # guballa
    "bigram_break_pasc",
    # indepth
    "AlignmentResult",
    "alignment_coincidence",
    # kasiski
    "distance_spectrum",
    "kasiski_examination",
    "print_kasiski_statistics",
    "repeat_distances",
    # rune_frequency
    "FrequencyProfile",
    "find_best_suppression",
    "matrix_mapping",
    "natural_mapping",
    "scan_state_spaces",
    "truncated_byte_mapping",
    # split
    "split_by_character",
    "split_by_doublet",
    "split_by_slice",
    "split_by_slice_interrupted",
    "split_by_whitespace",
    "trim",
    # twist
    "twist",
    "twist_test",
    "twist_test_with_interrupter",
]
