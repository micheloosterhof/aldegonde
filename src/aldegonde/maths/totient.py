def gcd(p: int, q: int) -> int:
    # Create the gcd of two positive integers.
    while q != 0:
        p, q = q, p % q
    return p


def is_coprime(x: int, y: int) -> bool:
    return gcd(x, y) == 1


def phi_func(x: int) -> int:
    """Euler phi // totient."""
    if x == 1:
        return 1
    n = [y for y in range(1, x) if is_coprime(x, y)]
    return len(n)
