# ABOUTME: Is a compact-state (hand-runnable) machine possible at all? Burnside
# ABOUTME: on 29 points forces the state group to be tiny or astronomical.
"""Michel's objection: an evolving permutation table is not how anyone would
run an encryption algorithm; you would expect a compact algebraic form.

"Compact" has a precise meaning here. To operate the cipher you must track
the current alphabet base_w. Every base lies in the coset base_0.<g,sigma>,
so the operator's state space is the group G = <g, sigma>. If |G| is small
you can index it -- a wheel with |G| positions, a lookup table, a counter.
If |G| is astronomical you must carry and update the whole 29-entry
permutation by hand, which is exactly the objection.

29 is PRIME, and that is decisive. Burnside: a transitive permutation group
of prime degree p is either 2-transitive, or has a normal Sylow p-subgroup
and so embeds in AGL(1,p). For p = 29 the 2-transitive groups are only A_29
and S_29 (29 is not (q^d-1)/(q-1) for any prime power q, and no sporadic
2-transitive group has degree 29). So a transitive G is either

    |G| <= |AGL(1,29)| = 812     or     |G| >= |A_29| = 4.4e30

and there is nothing in between. But the walk needs an order-5 element g,
and 5 does not divide 812 -- so the small branch cannot contain g at all.

Conclusion, if it holds: given order-5 g and a transitive state group, the
operator's state space is forced to be astronomical. The model is
descriptive not because a compact form was missed, but because none exists
under its own premises. The escape is intransitivity, which this script
also prices.

Everything below is verified numerically rather than asserted.
"""

from __future__ import annotations

import math
import random

from sympy.combinatorics import Permutation, PermutationGroup

N = 29


def agl1_order(p: int) -> int:
    return p * (p - 1)


def is_prime_power(q: int) -> bool:
    """True iff q = r^k for a single prime r and k >= 1."""
    if q < 2:
        return False
    primes = set()
    m, d = q, 2
    while d * d <= m:
        while m % d == 0:
            primes.add(d)
            m //= d
        d += 1
    if m > 1:
        primes.add(m)
    return len(primes) == 1


def is_2transitive_degree_possible(p: int) -> list[str]:
    """Projective 2-transitive degrees (q^d-1)/(q-1) equal to p, q a prime power."""
    hits = []
    for q in range(2, 200):
        if not is_prime_power(q):
            continue
        for d in range(2, 8):
            val = (q**d - 1) // (q - 1)
            if val == p:
                hits.append(f"q={q}, d={d}")
            if val > p:
                break
    return hits


def random_order5(rng: random.Random) -> list[int]:
    """A permutation of cycle type 5^5 1^4 -- the richest order-5 type on 29."""
    pts = list(range(N))
    rng.shuffle(pts)
    perm = list(range(N))
    for c in range(5):
        cyc = pts[5 * c : 5 * c + 5]
        for i in range(5):
            perm[cyc[i]] = cyc[(i + 1) % 5]
    return perm


def random_perm(rng: random.Random) -> list[int]:
    p = list(range(N))
    rng.shuffle(p)
    return p


def order_of(perm: list[int]) -> int:
    ident = list(range(N))
    cur, k = perm, 1
    while cur != ident:
        cur = [perm[x] for x in cur]
        k += 1
    return k


def main() -> None:
    print("--- the arithmetic behind the dichotomy ---")
    print(f"  |AGL(1,29)| = 29 * 28 = {agl1_order(N)}")
    print(f"  5 divides 812? {'yes' if agl1_order(N) % 5 == 0 else 'NO'}")
    proj = is_2transitive_degree_possible(N)
    print(f"  29 = (q^d-1)/(q-1) solutions: {proj or 'NONE'}")
    print(f"  |A_29| = 29!/2 = {math.factorial(N) // 2:.6e}")
    assert agl1_order(N) % 5 != 0
    assert not proj

    # An order-5 element cannot live in the small branch. Verify by brute force
    # over the whole affine group rather than by citing Lagrange.
    orders = set()
    for a in range(1, N):
        for b in range(N):
            perm = [(a * x + b) % N for x in range(N)]
            orders.add(order_of(perm))
    print(f"\n  element orders present in AGL(1,29): {sorted(orders)}")
    assert 5 not in orders, "order-5 affine map exists?!"
    print("  -> no affine map on 29 points has order 5 (brute-forced all 812)")

    # Now the empirical half: what does <g, sigma> actually come out as?
    print("\n--- |<g, sigma>| for random order-5 g and random mixed sigma ---")
    rng = random.Random(3301)
    for trial in range(6):
        g = random_order5(rng)
        s = random_perm(rng)
        G = PermutationGroup([Permutation(g), Permutation(s)])
        o = G.order()
        trans = G.is_transitive()
        label = "A_29 or S_29" if o >= math.factorial(N) // 2 else "smaller"
        print(f"  trial {trial}: transitive={trans!s:<5} |G| = {o:.4e}  ({label})")
        assert trans, "expected transitive"
        assert o >= math.factorial(N) // 2, o

    # And a 29-cycle sigma -- the "rotating mixed disk" the repo proposes.
    print("\n--- sigma = a 29-cycle (the rotating-disk device) ---")
    for trial in range(3):
        g = random_order5(rng)
        cyc = list(range(N))
        rng.shuffle(cyc)
        s = list(range(N))
        for i in range(N):
            s[cyc[i]] = cyc[(i + 1) % N]
        G = PermutationGroup([Permutation(g), Permutation(s)])
        o = G.order()
        print(
            f"  trial {trial}: |<g, disk>| = {o:.4e}   (state space the operator must track)"
        )
        assert o >= math.factorial(N) // 2, o

    print(
        "\n  Even the most device-like sigma available -- a single rotating\n"
        "  mixed disk -- generates the full alternating/symmetric group once\n"
        "  combined with an order-5 letter step. There is no wheel to index."
    )

    # The one escape: intransitivity.
    print("\n--- the escape: an INTRANSITIVE state group ---")
    print("  If <g,sigma> is intransitive the runes split into blocks that no")
    print("  base ever mixes, so |G| can be moderate. Price of that:")
    g = random_order5(rng)
    # sigma preserving g's orbit structure: permute within the 25 moved points
    # and within the 4 fixed points separately.
    moved = [x for x in range(N) if g[x] != x]
    fixed = [x for x in range(N) if g[x] == x]
    s = list(range(N))
    mm = moved[:]
    rng.shuffle(mm)
    for a, b in zip(moved, mm):
        s[a] = b
    ff = fixed[:]
    rng.shuffle(ff)
    for a, b in zip(fixed, ff):
        s[a] = b
    G = PermutationGroup([Permutation(g), Permutation(s)])
    print(
        f"  block-preserving sigma: transitive={G.is_transitive()}, |G| = {G.order():.4e}"
    )
    print(f"  orbits: {[sorted(o) for o in G.orbits()]}")
    print(
        "\n  A block structure means a plaintext rune can only ever encipher to a\n"
        "  rune in its own block, for the whole book. Each block's ciphertext mass\n"
        "  then equals its plaintext mass -- but ciphertext is flat (each block\n"
        "  gets k/29), so the plaintext block masses must already be flat. That is\n"
        "  a strong constraint on the plaintext, not on the cipher."
    )


if __name__ == "__main__":
    main()
