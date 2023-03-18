from collections.abc import Sequence
from typing import TypeVar

from aldegonde.stats.ngrams import ngram_distribution

T = TypeVar("T")


def print_dist(runes: Sequence[T]) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    col = 0
    freqs = ngram_distribution(runes)
    print("Frequency Distribution:")
    for i, e in enumerate(freqs.keys()):
        if col > 0 and col % 5 == 0:
            print("")
        print(
            f"#{i:02d}: {e:4s}: {freqs[e]:03d}: {freqs[e]/N*100:.3f}% | ",
            end="",
        )
        col = col + 1
    print("")
