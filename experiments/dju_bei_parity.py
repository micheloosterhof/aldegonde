# ABOUTME: Derives sigma's parity from the DJU-BEI return, which settles A29 against S29
# ABOUTME: for the base family without needing to know anything else about the key.
"""One bit of key falls out of the return, and it is the bit that names the group.

`dju-bei-needs-a-product-step.md` shows no bare sigma can produce the return: the base
step must be a product `g^a o sigma` whose exponents depend on the block lengths. That
looks like it makes the return depend on 1,449 unknowns. It does not, because parity is a
homomorphism and the exponents drop out.

    sign(g^a o sigma) = sign(g)^a * sign(sigma) = sign(sigma)

since g has order 5, so every one of its cycles is a 5-cycle -- an even permutation -- and
sign(g) = +1 whatever its cycle count. The product over the gap is therefore

    sign(product) = sign(sigma)^gap

and a state return needs the product to be the identity, whose sign is +1. With an ODD
gap that forces sign(sigma) = +1.

The repo-default word gap is 1,449, which is odd. So sigma is even, g is even, and the
group they generate lies in A29 -- which decides the question
`base-family-is-the-symmetric-group.md` leaves open.

    python dju_bei_parity.py
"""

from __future__ import annotations

import random

M = 29
GAPS = (1378, 1448, 1449, 1451, 1709, 1711)  # the tokenization audit's range


def sign(p: list[int]) -> int:
    seen = [False] * len(p)
    s = 1
    for i in range(len(p)):
        if seen[i]:
            continue
        j, n = i, 0
        while not seen[j]:
            seen[j] = True
            j = p[j]
            n += 1
        if n % 2 == 0:
            s = -s
    return s


def compose(p: list[int], q: list[int]) -> list[int]:
    return [p[q[x]] for x in range(M)]


def order5(rng: random.Random, cycles: int) -> list[int]:
    pts = list(range(M))
    rng.shuffle(pts)
    g = list(range(M))
    for c in range(cycles):
        blk = pts[c * 5 : (c + 1) * 5]
        for a, b in zip(blk, blk[1:] + blk[:1]):
            g[a] = b
    return g


def main() -> None:
    rng = random.Random(3)
    print("g has order 5, so all its cycles are 5-cycles, which are even:")
    for k in (1, 3, 5):
        print(
            f"  g with {k} 5-cycle{'s' if k > 1 else ' '}: sign {sign(order5(rng, k)):+d}"
        )

    print("\nthe product of 1,449 steps g^a o sigma, exponents drawn at random:")
    g = order5(rng, 5)
    for label, want in (("sigma even", +1), ("sigma odd", -1)):
        while True:
            s = list(range(M))
            rng.shuffle(s)
            if sign(s) == want:
                break
        prod = list(range(M))
        for _ in range(1449):
            step = s
            for _ in range(rng.randrange(5)):
                step = compose(g, step)
            prod = compose(prod, step)
        ok = "can be the identity" if sign(prod) == 1 else "CANNOT be the identity"
        print(f"  {label:<11} product sign {sign(prod):+d}  -> {ok}")

    print("\nby tokenization:")
    for gap in GAPS:
        forced = "sigma must be EVEN" if gap % 2 else "no constraint"
        print(f"  word gap {gap:>5} ({'odd ' if gap % 2 else 'even'}): {forced}")
    print(
        "\nThe repo-default gap is 1,449 and Michel's convention ruling selects it. Four"
        "\nof the six audited conventions give an odd gap and force sigma even; the two"
        "\neven ones leave parity free. So the conclusion holds under the ruling and"
        "\nunder most alternatives, and is vacuous rather than contradicted under the"
        "\nrest."
    )


if __name__ == "__main__":
    main()
