"""Cryptanalysis algorithms."""

from aldegonde.analysis.autokey_repeat import (
    count_violations,
    forced_equal_positions,
)
from aldegonde.analysis.bounds import (
    DiagonalBound,
    diagonal_rate,
    extremal_diagonal_rate,
    pair_counts,
)
from aldegonde.analysis.coincidence import (
    BoundaryCoincidence,
    BoundaryPermutation,
    BucketCoincidence,
    JointCount,
    boundary_coincidence,
    boundary_permutation_test,
    bucket_coincidence,
    joint_coincidence,
    match_indicator,
    match_separations,
    recut_words,
    within_delta_histogram,
    word_index_map,
)
from aldegonde.analysis.delta import DeltaOp, delta, delta2
from aldegonde.analysis.fingerprint import compare, fingerprint
from aldegonde.analysis.fourpoint import FourPointCount, fourpoint_coincidence
from aldegonde.analysis.friedman import friedman_test, friedman_test_with_interrupter
from aldegonde.analysis.guballa import bigram_break_pasc
from aldegonde.analysis.indepth import AlignmentResult, alignment_coincidence
from aldegonde.analysis.kasiski import (
    distance_spectrum,
    kasiski_examination,
    print_kasiski_statistics,
    repeat_distances,
)
from aldegonde.analysis.keystream import (
    AutokeySplit,
    OffsetHit,
    autokey_split,
    offset_scan,
)
from aldegonde.analysis.relations import (
    linear_relation_scan,
    positional_relation_scan,
)
from aldegonde.analysis.rune_frequency import (
    FrequencyProfile,
    find_best_suppression,
    matrix_mapping,
    natural_mapping,
    scan_state_spaces,
    truncated_byte_mapping,
)
from aldegonde.analysis.spectral import (
    AlignmentPeak,
    SpectralPeak,
    crosscorrelation_coincidence,
    multiplier_dft,
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
    # autokey_repeat
    "count_violations",
    "forced_equal_positions",
    # bounds
    "DiagonalBound",
    "diagonal_rate",
    "extremal_diagonal_rate",
    "pair_counts",
    # coincidence
    "BoundaryCoincidence",
    "BoundaryPermutation",
    "BucketCoincidence",
    "JointCount",
    "boundary_coincidence",
    "boundary_permutation_test",
    "bucket_coincidence",
    "joint_coincidence",
    "match_indicator",
    "match_separations",
    "recut_words",
    "within_delta_histogram",
    "word_index_map",
    # delta
    "DeltaOp",
    "delta",
    "delta2",
    # fingerprint
    "compare",
    "fingerprint",
    # fourpoint
    "FourPointCount",
    "fourpoint_coincidence",
    # keystream
    "AutokeySplit",
    "OffsetHit",
    "autokey_split",
    "offset_scan",
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
    # relations
    "linear_relation_scan",
    "positional_relation_scan",
    # spectral
    "AlignmentPeak",
    "SpectralPeak",
    "crosscorrelation_coincidence",
    "multiplier_dft",
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
