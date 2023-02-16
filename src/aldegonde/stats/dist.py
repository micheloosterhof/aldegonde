from collections import Counter

from ..structures import sequence
from .ngrams import iterngrams


def print_dist(runes: sequence.Sequence) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    col = 0
    freqs = Counter(runes)
    print("frequency distribution:")
    for i, e in enumerate(runes.alphabet):
        if col > 0 and col % 5 == 0:
            print("")
        print(
            f"{i:02d}: {e}: {freqs[i]:03d}: {freqs[i]/N*100:.3f}% | ",
            end="",
        )
        col = col + 1
    print("")


def dist(runes: sequence.Sequence, length: int = 1, cut: int = 0) -> dict[str, int]:
    """
    flexible dist function
    """
    out: dict[str, int] = {}
    for g in iterngrams(runes, length=length, cut=cut):
        k = "-".join([str(x) for x in g])
        out[k] = out.get(k, 0) + 1
    return out
