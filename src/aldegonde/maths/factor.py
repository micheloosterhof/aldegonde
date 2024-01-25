"""prime factorization."""


def prime_factors(number: int) -> list[int]:
    """
    all prime factors of a number
    """
    i = 2
    factors = []
    while i * i <= number:
        if number % i:
            i += 1
        else:
            number //= i
            factors.append(i)
    if number > 1:
        factors.append(number)
    return factors


def factor_pairs(number: int) -> list[tuple[int, int]]:
    """
    Based on integer input, output all factors that make up this number
    """
    output = []
    for factor1 in range(1, number + 1):
        if number % factor1 == 0:
            factor2 = number // factor1
            output.append((factor1, factor2))
    return output
