from collections import Counter

from ..structures import sequence


def print_dist(runes: sequence.Sequence) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    col = 0
    freqs = Counter(runes)
    print("frequency distribution:")
    for rune in range(0, len(runes.alphabet)):
        if col > 0 and col % 5 == 0:
            print("")
        print(
            f"{rune:02d}: {runes.alphabet[rune]}: {freqs[rune]:03d}: {freqs[rune]/N*100:.3f}% | ",
            end="",
        )
        col = col + 1
    print("")


def monograph_dist(runes: sequence.Sequence) -> dict[int, int]:
    """
    print frequency distribution
    """
    out: dict[int, int] = {}
    N = len(runes)
    freqs = Counter(runes)
    for rune in range(0, len(runes.alphabet)):
        out[rune] = freqs[rune]
    return out
