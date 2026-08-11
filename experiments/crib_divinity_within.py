# ABOUTME: Turns the DIVINITY WITHIN crib into constraints on g and sigma and
# ABOUTME: measures how much of the key space they actually remove.
"""What the opening crib constrains, under the length-clocked walk.

The first two words of the corpus are 8 and 5 runes, exactly the runeglish
lengths of DIVINITY and WITHIN, and the red rubrication on page 0 line 0 covers
exactly those 13 runes and stops. Taking the crib as given, the walk

    c[j]        = base_w( g^(j mod 5)( p[j] ) )
    base_{w+1}  = base_w o g^((L_w - 1) mod 5) o sigma

turns 13 known plaintext runes into constraints. Word 0 has length 8, so
(8-1) mod 5 = 2 and base_1 = base_0 o g^2 o sigma.

Two kinds of constraint follow, and they differ in worth:

1. **On `g` alone.** Within a word, base_w is a bijection, so the arguments
   g^(k mod 5)(p_k) must be distinct exactly where the ciphertext runes are.
   Every crib ciphertext is distinct within its word, so every pair of arguments
   must differ. A candidate g that collapses two of them is refuted outright,
   with no reference to base_0 or sigma.

2. **On `sigma` given `g`.** Where the two words share a ciphertext rune at the
   same position, base_0 must receive the same argument from both, which pins
   sigma at a point. The two words agree at k=0 and k=2 -- and at exactly those
   positions the PLAINTEXTS differ, which is what makes them informative.

This matters because base_0 is already known to be cheap (a hillclimb recovers
it in seconds given g and sigma) while (g, sigma) is the whole difficulty. A
crib that only pinned base_0 would buy nothing. These constrain the hard half.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from aldegonde import c3301

if TYPE_CHECKING:
    from collections.abc import Sequence

M = 29
ALPHABET = c3301.CICADA_ALPHABET
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
INDEX = {r: i for i, r in enumerate(ALPHABET)}
BY_NAME = {n: i for i, n in enumerate(ENGLISH)}

# The crib. Runeglish, so TH is one rune and DIVINITY's V is the U rune.
CRIB = [
    (["D", "I", "U", "I", "N", "I", "T", "Y"], "ᛋᚻᛖᚩᚷᛗᛡᚠ"),
    (["W", "I", "TH", "I", "N"], "ᛋᚣᛖᛝᚳ"),
]
TRIALS = 200_000
random.seed(3301)


def order5(rng: random.Random) -> list[int]:
    """A permutation of cycle type 5,5,5,5,5,1,1,1,1: order 5, as the model wants."""
    pool = list(range(M))
    rng.shuffle(pool)
    perm = list(range(M))
    for c in range(5):
        cycle = pool[c * 5 : c * 5 + 5]
        for i, x in enumerate(cycle):
            perm[x] = cycle[(i + 1) % 5]
    return perm


def power(perm: Sequence[int], k: int) -> list[int]:
    out = list(range(M))
    for _ in range(k % 5):
        out = [perm[x] for x in out]
    return out


def arguments(perm: Sequence[int], plain: Sequence[str]) -> list[int]:
    """The value base_w actually receives at each position of a word."""
    powers = [power(perm, k % 5) for k in range(5)]
    return [powers[k % 5][BY_NAME[p]] for k, p in enumerate(plain)]


def survives(perm: Sequence[int]) -> bool:
    """Is this g consistent with the crib, before base_0 or sigma are chosen?"""
    for plain, cipher in CRIB:
        args = arguments(perm, plain)
        runes = [INDEX[r] for r in cipher]
        seen: dict[int, int] = {}
        for a, c in zip(args, runes):
            if a in seen and seen[a] != c:
                return False  # one argument, two ciphertext runes: impossible
            seen[a] = c
    return True


def sigma_points(perm: Sequence[int]) -> list[tuple[int, int]]:
    """Points of sigma pinned by the two words sharing a ciphertext rune.

    base_1 = base_0 o g^2 o sigma, so where c1[k] == c0[j] the arguments must
    match: g^2(sigma(g^(k mod 5)(p1[k]))) = g^(j mod 5)(p0[j]).
    """
    plain0, cipher0 = CRIB[0]
    plain1, cipher1 = CRIB[1]
    args0 = arguments(perm, plain0)
    runes0 = [INDEX[r] for r in cipher0]
    inv2 = {v: i for i, v in enumerate(power(perm, 2))}
    out = []
    for k, r in enumerate(cipher1):
        c = INDEX[r]
        if c not in runes0:
            continue
        target = args0[runes0.index(c)]
        source = power(perm, k % 5)[BY_NAME[plain1[k]]]
        out.append((source, inv2[target]))
    return out


def forbidden_counts(perm: Sequence[int]) -> list[int]:
    """How many sigma values each source is DENIED by a mismatching ciphertext.

    Where c1[k] differs from c0[j], base_0 cannot receive the same argument from
    both, so sigma(source_k) is forbidden one value per such j.
    """
    plain0, cipher0 = CRIB[0]
    plain1, cipher1 = CRIB[1]
    args0 = arguments(perm, plain0)
    runes0 = [INDEX[r] for r in cipher0]
    inv2 = {v: i for i, v in enumerate(power(perm, 2))}
    out = []
    for r in cipher1:
        c = INDEX[r]
        denied = {inv2[a] for a, c0 in zip(args0, runes0) if c0 != c}
        out.append(len(denied))
    return out


def main() -> None:
    print((__doc__ or "").split("\n\n")[1].strip(), "\n")
    print("the crib, position by position:")
    for plain, cipher in CRIB:
        print(f"   plain  {'·'.join(plain)}")
        print(f"   cipher {'·'.join(ENGLISH[INDEX[r]] for r in cipher)}")
    shared = [
        (k, ENGLISH[INDEX[CRIB[1][1][k]]])
        for k in range(len(CRIB[1][1]))
        if CRIB[1][1][k] in CRIB[0][1] and CRIB[0][1].index(CRIB[1][1][k]) == k
    ]
    print(f"\nsame ciphertext at the same position in both words: {shared}")

    kept = 0
    pinned: list[int] = []
    denied: list[int] = []
    for _ in range(TRIALS):
        g = order5(random.Random(random.getrandbits(64)))
        if not survives(g):
            continue
        kept += 1
        pinned.append(len(sigma_points(g)))
        denied.append(sum(forbidden_counts(g)))
    rate = kept / TRIALS
    print(f"\n=== filtering power on g ({TRIALS:,} random order-5 permutations)")
    print(f"  consistent with the crib : {kept:,}  ({rate:.4%})")
    if rate:
        print(f"  the crib removes a factor of {1 / rate:.2f} of the g space")
    if pinned:
        avg = sum(pinned) / len(pinned)
        print("\n=== what a surviving g then pins of sigma")
        print(
            f"  points of sigma determined: {min(pinned)}-{max(pinned)}, mean {avg:.2f}"
        )
        print("  a point pinned is a factor of 29 off sigma's 29! arrangements,")
        print(f"  so {avg:.2f} points is a factor of about {29**avg:.0f}")
        avg_denied = sum(denied) / len(denied)
        print(
            f"\n  values additionally FORBIDDEN across the other sources: "
            f"{avg_denied:.1f} on average"
        )
        # three sources remain free; each loses roughly avg_denied/3 of 29 options
        left = max(1.0, 29 - avg_denied / 3)
        extra = (29 / left) ** 3
        print(f"  which is a further factor of about {extra:.1f}")
        print(
            f"\n  TOTAL reduction on (g, sigma): "
            f"{(1 / rate) * 29**avg * extra:,.0f}-fold"
        )
        print(
            f"  the joint space is about 1e48, so this leaves about "
            f"{1e48 / ((1 / rate) * 29**avg * extra):.1e}"
        )


if __name__ == "__main__":
    main()
