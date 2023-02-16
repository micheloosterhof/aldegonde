"""
modular division in python
"""

import math


def modInverse(b: int, m: int) -> int:
    """
    Function to find modulo inverse of b. It returns -1 when inverse doesn't
    modInverse works for prime m
    """
    g = math.gcd(b, m)
    if g != 1:
        # print("Inverse doesn't exist")
        return -1
    # If b and m are relatively prime,
    # then modulo inverse is b^(m-2) mode m
    return pow(b, m - 2, m)


def modDivide(a: int, b: int, m: int) -> int:
    """
    Function to compute a/b under modulo m
    """
    a = a % m
    inv = modInverse(b, m)
    if inv == -1:
        raise Exception(f"Division not defined {a}/{b}%{m}")

    return (inv * a) % m


def div29(a, b):
    """
    convenience function for 3301
    """
    return modDivide(a, b, 29)
