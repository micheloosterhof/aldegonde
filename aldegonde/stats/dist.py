from collections import Counter

def dist(runes: list[int]) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    freqs = Counter(runes)
    print("frequency distribution")
    for rune in range(0, MAX):
        print(f"{rune}: {freqs[rune]/N*100}")
