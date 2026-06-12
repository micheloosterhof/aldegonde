"""Cryptanalysis algorithms."""

from aldegonde.analysis.delta import DeltaOp, delta, delta2
from aldegonde.analysis.friedman import friedman_test, friedman_test_with_interrupter
from aldegonde.analysis.guballa import bigram_break_pasc
from aldegonde.analysis.kasiski import (
    distance_spectrum,
    kasiski_examination,
    print_kasiski_statistics,
    repeat_distances,
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
    # delta
    "DeltaOp",
    "delta",
    "delta2",
    # friedman
    "friedman_test",
    "friedman_test_with_interrupter",
    # guballa
    "bigram_break_pasc",
    # kasiski
    "distance_spectrum",
    "kasiski_examination",
    "print_kasiski_statistics",
    "repeat_distances",
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
