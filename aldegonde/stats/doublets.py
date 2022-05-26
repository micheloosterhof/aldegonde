from scipy.stats import poisson


def triplets(runes: list[int]) -> int:
    """
    find number of triplet. triplet is X followed by XX for any X
    """
    N = len(runes)
    triplets: int = 0
    for index in range(0, N - 2):
        if runes[index] == runes[index + 1] and runes[index] == runes[index + 2]:
            triplets += 1
    print(f"triplets = {triplets}")
    expected = N / MAX / MAX
    print(f"expected = {expected:.2f}")
    return triplets


def doublets(runes: list[int], skip: int = 1, trace: bool = False) -> list[int]:
    """
    find number of doublets. doublet is X followed by X for any X
    """
    N = len(runes)
    doublets: list[int] = []
    for index in range(0, N - skip - 1):
        if runes[index] == runes[index + skip]:
            doublets.append(index)
            if trace:
                print(
                    f"doublet at {index}: {runes[index-1]}-{runes[index]}-{runes[index+1]}-{runes[index+2]}"
                )
                print(
                    f" factors N-1: {prime_factors(index-1)}; N: {prime_factors(index)};  N+1: {prime_factors(index+1)} N+2 {prime_factors(index+2)}"
                )
    l: int = len(doublets)

    mu = N / MAX
    mean, var = poisson.stats(mu, loc=0, moments="mv")
    sigmage: float = abs(l - mean) / math.sqrt(var)
    print(f"doublets={l} expected={mean:.2f} S={sigmage:.2f}σ")
    return doublets
