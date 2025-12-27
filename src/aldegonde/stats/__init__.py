"""Statistical analysis tools for cryptanalysis."""

from aldegonde.stats.compare import (
    NgramScorer,
    bigramscore,
    chisquarescipy,
    frequency_to_probability,
    gtest,
    loadgrams,
    logdist,
    mychisquare,
    quadgramscore,
    trigramscore,
)
from aldegonde.stats.dist import print_dist
from aldegonde.stats.entropy import shannon2_entropy, shannon_entropy
from aldegonde.stats.hamming import hamming_distance
from aldegonde.stats.ioc import (
    ioc,
    ioc2,
    ioc3,
    ioc4,
    nioc,
    print_ioc_statistics,
    renyi,
    sliding_window_ioc,
)
from aldegonde.stats.isomorph import (
    isomorph,
    isomorph_distribution,
    isomorph_positions,
    isomorph_statistics,
    print_isomorph_statistics,
    random_isomorph_statistics,
)
from aldegonde.stats.kappa import doublets, kappa, print_kappa, triplets
from aldegonde.stats.mioc import MiocTuple, mioc, nmioc, print_mioc_statistics
from aldegonde.stats.ngrams import (
    bigrams,
    digraphs,
    iterngrams,
    ngram_distribution,
    ngram_positions,
    ngrams,
    quadgrams,
    tetragraphs,
    trigrams,
    trigraphs,
)
from aldegonde.stats.repeats import (
    odd_spaced_repeats,
    print_repeat_positions,
    print_repeat_statistics,
    repeat_distribution,
    repeat_positions,
)

__all__ = [
    # compare
    "NgramScorer",
    "bigramscore",
    "chisquarescipy",
    "frequency_to_probability",
    "gtest",
    "loadgrams",
    "logdist",
    "mychisquare",
    "quadgramscore",
    "trigramscore",
    # dist
    "print_dist",
    # entropy
    "shannon_entropy",
    "shannon2_entropy",
    # hamming
    "hamming_distance",
    # ioc
    "ioc",
    "ioc2",
    "ioc3",
    "ioc4",
    "nioc",
    "print_ioc_statistics",
    "renyi",
    "sliding_window_ioc",
    # isomorph
    "isomorph",
    "isomorph_distribution",
    "isomorph_positions",
    "isomorph_statistics",
    "print_isomorph_statistics",
    "random_isomorph_statistics",
    # kappa
    "doublets",
    "kappa",
    "print_kappa",
    "triplets",
    # mioc
    "MiocTuple",
    "mioc",
    "nmioc",
    "print_mioc_statistics",
    # ngrams
    "bigrams",
    "digraphs",
    "iterngrams",
    "ngram_distribution",
    "ngram_positions",
    "ngrams",
    "quadgrams",
    "tetragraphs",
    "trigrams",
    "trigraphs",
    # repeats
    "odd_spaced_repeats",
    "print_repeat_positions",
    "print_repeat_statistics",
    "repeat_distribution",
    "repeat_positions",
]
