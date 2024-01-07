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


def two_factors(number: int) -> list[tuple[int, int]]:
    """
    Based on integer input, output all factors that make up this number
    """
    output = []
    highest = number
    for factor1 in range(2, number // 2):
        if factor1 >= highest:
            break
        if number % factor1 == 0:
            factor2 = number // factor1
            highest = factor2
            output.append((factor1, factor2))
    return output
