#!/usr/bin/env python3
# ABOUTME: Tests whether the DJU-BEI abelianization relation and the parity
# ABOUTME: condition are real filters on candidate (g, sigma) keys. Both are
# ABOUTME: vacuous on the Quagmire candidate space.
"""Are the cheap filters on the walk key actually cheap, or actually filters?

`length-clocked-walk.md` derived `[g] = -1449*[sigma]` from the DJU-BEI
state return and listed it, alongside a parity condition, as a constraint
every candidate key must satisfy. Both claims are checked here.

1. ABELIANIZATION. The relation lives in the abelianization of the FREE
   group on two generators. It constrains concrete permutations only if
   <g, sigma> has a matching abelian quotient. We compute |G/G'| directly
   for order-5 g against a random sigma and against a 29-cycle disk sigma
   (the Quagmire shape).

2. PARITY. Every non-identity conjugated shift K(add d)K^-1 on 29 points
   is a single 29-cycle, i.e. an even permutation. If so the parity
   condition cannot reject any Quagmire sigma.

Scope: the abelianization result is a sample of order-5 g across k = 1..5
five-cycles, not a proof. A specially-constructed pair generating a small
solvable group could have a larger abelian quotient -- but such a pair is
excluded anyway by the base-count requirement in `sigma-power-step.md`.
"""

from __future__ import annotations

import random

from sympy.combinatorics import Permutation, PermutationGroup

M = 29
TRIALS_PARITY = 2000


def order5(rng: random.Random, k: int) -> Permutation:
    """A permutation of order 5: k five-cycles, the rest fixed."""
    pts = list(range(M))
    rng.shuffle(pts)
    return Permutation([pts[5 * i : 5 * i + 5] for i in range(k)], size=M)


def conj_shift(rng: random.Random, delta: int) -> list[int]:
    """K(add delta)K^-1 for a random mixed alphabet K, as a 0..28 list."""
    K = list(range(M))
    rng.shuffle(K)
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    return [K[(pos[x] + delta) % M] for x in range(M)]


def parity_even(p: list[int]) -> bool:
    seen = [False] * M
    swaps = 0
    for i in range(M):
        if seen[i]:
            continue
        length = 0
        j = i
        while not seen[j]:
            seen[j] = True
            j = p[j]
            length += 1
        swaps += length - 1
    return swaps % 2 == 0


def main() -> None:
    rng = random.Random(3301)

    print("=== 1. abelianization of <g, sigma> ===")
    print("the DJU-BEI relation has content only if |G/G'| > 2\n")
    print(f"{'sigma type':<16}{'g: k 5-cycles':>14}{'|G/G-prime|':>13}  verdict")
    worst = 1
    for label, make in (
        ("random perm", lambda: Permutation(rng.sample(range(M), M))),
        ("29-cycle disk", lambda: Permutation(conj_shift(rng, rng.randrange(1, M)))),
    ):
        for k in range(1, 6):
            G = PermutationGroup([order5(rng, k), make()])
            ab = G.order() // G.derived_subgroup().order()
            worst = max(worst, ab)
            verdict = {1: "trivial - VACUOUS", 2: "Z_2 - IS the parity condition"}.get(
                ab, "extra content!"
            )
            print(f"{label:<16}{k:>14}{ab:>13}  {verdict}")
    print(f"\nlargest abelianization seen: {worst}")
    print("=> the relation never exceeds parity; it is not an extra filter.")

    print("\n=== 2. parity on Quagmire sigma ===")
    odd = tot = 0
    for _ in range(TRIALS_PARITY):
        K = list(range(M))
        rng.shuffle(K)
        pos = [0] * M
        for i, r in enumerate(K):
            pos[r] = i
        for dl in range(1, M):
            tot += 1
            if not parity_even([K[(pos[x] + dl) % M] for x in range(M)]):
                odd += 1
    print(f"conjugated shifts tested: {tot:,}   rejected by parity: {odd:,}")
    print("=> a 29-cycle is 28 transpositions, hence even. Parity cannot")
    print("   reject any Quagmire sigma either.")

    print("\nNet: of the four filters once listed (joint doublet count,")
    print("parity, sigma not in <g>, base count, DJU-BEI abelianization),")
    print("only 'sigma not in <g>' and the base count do any work. The real")
    print("gate is the full 1,449-step state return.")


if __name__ == "__main__":
    main()
