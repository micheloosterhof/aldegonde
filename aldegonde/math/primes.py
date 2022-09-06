"""primes
"""

import itertools
from typing import Iterable, Iterator


def primes(n: int) -> list[int]:
    """primes as a list"""
    out = list()
    sieve = [True] * (n + 1)
    for p in range(2, n + 1):
        if sieve[p]:
            out.append(p)
            for i in range(p, n + 1, p):
                sieve[i] = False
    return out


class PrimeGenerator(Iterable):
    """primes as a generator"""

    def __init__(self) -> None:
        self.primes: list[int] = []
        self.current = 1

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        candidate = self.current + 1
        while True:
            for prime in itertools.takewhile(
                lambda p: candidate >= p**2, self.primes
            ):
                if candidate % prime == 0:
                    break
            else:
                self.primes.append(candidate)
                self.current = candidate
                break

            candidate += 1

        return self.current
