from collections import Counter
from collections.abc import Sequence
from typing import TypeVar

from aldegonde.stats.ngrams import iterngrams

T = TypeVar("T")


def print_dist(runes: Sequence[T]) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    col = 0
    freqs = dist(runes)
    print(freqs)
    print("frequency distribution:")
    for i, e in enumerate(freqs.keys()):
        if col > 0 and col % 5 == 0:
            print("")
        print(
            f"#{i:02d}: {e:4s}: {freqs[e]:03d}: {freqs[e]/N*100:.3f}% | ",
            end="",
        )
        col = col + 1
    print("")


def dist(text: Sequence[T], length: int = 1, cut: int = 0) -> dict[str, int]:
    """
    flexible dist function, returns ngrams by count
    """
    return Counter([str(g) for g in iterngrams(text, length=length, cut=cut)])
