from collections import Counter

from ..structures import sequence


def print_dist(runes: sequence.Sequence) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    freqs = Counter(runes)
    print("frequency distribution")
    for rune in range(0, len(runes.alphabet)):
        print(f"{rune}: {freqs[rune]/N*100}")


def monograph_dist(runes: sequence.Sequence) -> dict[int, int]:
    """
    print frequency distribution
    """
    out: dict[int, int] = {}
    N = len(runes)
    freqs = Counter(runes)
    for rune in range(0, len(runes.alphabet)):
        out[runes.alphabet[rune]] = freqs[rune]
    return out
