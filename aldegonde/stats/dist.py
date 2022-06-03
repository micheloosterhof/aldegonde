from collections import Counter

from ..structures import sequence


def dist(runes: sequence.Sequence) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    freqs = Counter(runes)
    print("frequency distribution")
    for rune in range(0, len(runes.alphabet)):
        print(f"{rune}: {freqs[rune]/N*100}")
