# ABOUTME: Intersects sigma's parity with its order bounds, which narrows the cycle type
# ABOUTME: sharply under one clock reading and mildly under the other.
"""Two results about sigma compose, and the composition is worth more than either.

`sigma-is-even.md` derives sign(sigma) = +1 from the DJU-BEI return: the base step is a
product `g^a o sigma`, g is even because all its cycles are 5-cycles, so the product's sign
is sign(sigma)^gap, and an identity return with an odd gap forces sigma even.

`key-local-channel-is-empty.md` bounds ord(sigma) from the depth data at **307** under a
continuous letter clock or **1,536** under a per-block reset --
`clock-convention-is-out-of-reach.md` shows the corpus cannot choose between them, and
`dju-bei-favours-the-continuous-clock.md` gives 5 : 1 for the continuous one.

Intersecting parity with each bound is a finite computation over the 4,565 partitions of
29, weighted by conjugacy-class size so the answer is in permutations rather than in
cycle types.

    python sigma_cycle_types.py
"""

from __future__ import annotations

import collections
import math

N = 29


def partitions(n: int, largest: int | None = None):
    if largest is None:
        largest = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, largest), 0, -1):
        for rest in partitions(n - k, k):
            yield (k, *rest)


def order(p) -> int:
    o = 1
    for c in p:
        o = o * c // math.gcd(o, c)
    return o


def is_even(p) -> bool:
    return sum(c - 1 for c in p) % 2 == 0


def class_size(p) -> int:
    m = collections.Counter(p)
    d = 1
    for i, k in m.items():
        d *= (i**k) * math.factorial(k)
    return math.factorial(N) // d


def main() -> None:
    parts = list(partitions(N))
    total = math.factorial(N)
    print(f"{len(parts):,} cycle types of {N} points\n")

    def frac(sel):
        return sum(class_size(p) for p in sel) / total

    for floor, label in ((307, "continuous clock"), (1536, "per-block reset")):
        high = [p for p in parts if order(p) >= floor]
        even = [p for p in high if is_even(p)]
        print(f"ord(sigma) >= {floor}  ({label})")
        print(f"  cycle types: {len(high)} of {len(parts):,}, of which even {len(even)}")
        print(f"  all parities: {frac(high):.5f} of S29  ({math.log2(1 / frac(high)):.1f} bits)")
        print(f"  even only   : {frac(even):.5f} of S29  ({math.log2(1 / frac(even)):.1f} bits)")
        if len(even) <= 3:
            for p in even:
                print(f"    the surviving type: {p}, order {order(p)}")
        print()

    print(
        "Under the reset reading the intersection is a single cycle type -- (11, 7, 5, 4,"
        "\n2), order 1,540 -- so sigma's cycle structure would be fully determined, worth"
        "\n11.6 bits. Under the continuous reading 151 types survive, worth 4.3."
        "\n\nThe uncomfortable part is that the evidence points the other way: the return's"
        "\nrune gap favours the CONTINUOUS clock at 5 : 1, which is the branch giving the"
        "\nweaker answer. Both are quoted and neither is chosen."
    )


if __name__ == "__main__":
    main()
