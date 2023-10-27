from collections.abc import Sequence
from typing import TypeVar

from scipy.stats import chisquare

from aldegonde.stats.ngrams import ngram_distribution

T = TypeVar("T")

"""
Functions for ngram distribution
"""


def print_dist(runes: Sequence[T]) -> None:
    """Print frequency distribution."""
    N = len(runes)
    col = 0
    freqs = ngram_distribution(runes)
    print("Frequency Distribution:")
    for i, e in enumerate([x[0] for x in sorted(freqs.items(), key=lambda x: x[1])]):
        if col > 0 and col % 5 == 0:
            print("")
        print(
            f"#{i:02d}: {e:4s}: {freqs[e]:03d}: {freqs[e]/N*100:.3f}% | ",
            end="",
        )
        col = col + 1
    print("")

    observed = [freqs[i] for i in freqs]
    chi2, p = chisquare(f_obs=observed)
    print(f"chi2 goodness of fit for uniform distribution = {chi2:.5f} p-value={p:.5f}")
