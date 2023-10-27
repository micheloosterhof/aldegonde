"""primes."""

import itertools
from collections.abc import Generator, Iterable, Iterator


def primes(n: int) -> list[int]:
    """Primes as a list."""
    out: list[int] = []
    sieve = [True] * (n + 1)
    for p in range(2, n + 1):
        if sieve[p]:
            out.append(p)
            for i in range(p, n + 1, p):
                sieve[i] = False
    return out


class PrimeGenerator(Iterable):
    """primes as a generator."""

    def __init__(self) -> None:
        self.primes: list[int] = []
        self.current = 1

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        candidate = self.current + 1
        while True:
            for prime in itertools.takewhile(
                lambda p: candidate >= p**2,  # noqa: B023
                self.primes,
            ):
                if candidate % prime == 0:
                    break
            else:
                self.primes.append(candidate)
                self.current = candidate
                break

            candidate += 1

        return self.current


def gen_primes_opt() -> Generator[int, None, None]:
    yield 2
    D: dict[int, int] = {}
    for q in itertools.count(3, step=2):
        p = D.pop(q, None)
        if not p:
            D[q * q] = q
            yield q
        else:
            x = q + p + p  # get odd multiples
            while x in D:
                x += p + p
            D[x] = p
