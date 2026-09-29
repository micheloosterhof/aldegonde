# ABOUTME: Enumerates every algebraic operation on 29 symbols and shows which can have
# ABOUTME: order 5, the period the LP requires; the only route needs a 30th point.
"""Which arithmetic operation can supply the order-5 letter step?

`length-clocked-walk.md` records that no shift, multiply or affine map has order 5,
because |GF(29)*| = 28 and 5 does not divide 28. Michel asked whether exponentiation
reaches it. It does not, and the reason is the same one: a power map `x -> x^k` acts
on GF(29)* as multiplication by k in Z/28, so its order divides |(Z/28)*| = 12.

One operation does reach order 5, and it needs a symbol the 29-rune alphabet does not
have. On the projective line P1(F29) -- the 29 residues plus a point at infinity, 30
in all -- the fractional-linear maps `x -> (ax+b)/(cx+d)` form PGL(2,29) of order
29*28*30 = 24,360. Element orders divide 28, divide 30, or equal 29, and **5 divides
30**, so order-5 elements exist. There are 1,624 of them, every one with cycle type
5^6, and **not one fixes the extra point**. So an algebraic order-5 step forces a
30-symbol alphabet and a letter step with no fixed points, where the walk's 29-symbol
`g` has cycle type 5^5 1^4 and four of them.

That is a sharp structural fork, and the rates do not currently support the 30-symbol
side: a uniformly emitted 30th symbol would occupy 1/30 = 3.33% of the stream, while
the cluster marks occupy 1.29% and the word separators 18.6%. So the extra point is
not a symbol the scribe writes. A version in which it is a gap -- a position the
encoder skips rather than emits -- is untested and is the open form of the idea.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

M = 29
INFINITY = M  # the 30th point of the projective line
RUNE = re.compile(r"[ᚠ-᛿]")


def order_of(perm: list[int]) -> int | None:
    identity, current, k = list(range(len(perm))), list(perm), 1
    while current != identity:
        current = [perm[x] for x in current]
        k += 1
        if k > 1000:
            return None
    return k


def cycle_type(perm: list[int]) -> dict[int, int]:
    seen: set[int] = set()
    sizes = []
    for start in range(len(perm)):
        if start in seen:
            continue
        length, x = 0, start
        while x not in seen:
            seen.add(x)
            x = perm[x]
            length += 1
        sizes.append(length)
    return dict(sorted(Counter(sizes).items()))


def power_maps() -> dict[int, list[int]]:
    """x -> x^k on GF(29), a bijection (fixing 0) exactly when gcd(k, 28) = 1."""
    return {
        k: [pow(x, k, M) for x in range(M)] for k in range(1, 28) if gcd(k, 28) == 1
    }


def affine_maps() -> list[list[int]]:
    return [[(a * x + b) % M for x in range(M)] for a in range(1, M) for b in range(M)]


def mobius(a: int, b: int, c: int, d: int) -> list[int]:
    """x -> (ax+b)/(cx+d) on the 30 points of P1(F29)."""
    out = []
    for x in range(M):
        numerator, denominator = (a * x + b) % M, (c * x + d) % M
        out.append(
            INFINITY if denominator == 0 else numerator * pow(denominator, M - 2, M) % M
        )
    out.append(INFINITY if c % M == 0 else a * pow(c, M - 2, M) % M)
    return out


def projective_group() -> list[tuple[int, ...]]:
    """PGL(2,29) as permutations of the 30 points, without duplicates."""
    seen = set()
    for a in range(M):
        for b in range(M):
            for c in range(M):
                for d in range(M):
                    if (a * d - b * c) % M:
                        seen.add(tuple(mobius(a, b, c, d)))
    return sorted(seen)


def mark_rates() -> dict[str, float]:
    """What share of a 30-symbol stream each written mark would occupy."""
    text = (ROOT / "data" / "page0-56.txt").read_text()
    clean = "".join([s for s in text.split("$") if RUNE.search(s)][:10])
    runes = sum(1 for ch in clean if RUNE.match(ch))
    counts = Counter(ch for ch in clean if ch in c3301.MARKS)
    cluster = sum(n for ch, n in counts.items() if ch in c3301.CLUSTER_MARKS)
    separators = sum(n for ch, n in counts.items() if ch in c3301.WORD_MARKS)
    return {
        "runes": runes,
        "cluster marks": cluster / (runes + cluster),
        "word separators": separators / (runes + separators),
    }


def main() -> None:
    print("=== order 5 on 29 symbols: which operations can supply it? ===\n")
    powers = {order_of(p) for p in power_maps().values()}
    affine = {order_of(p) for p in affine_maps()}
    print(f"{'power maps x -> x^k':<34}orders {sorted(powers)}")
    print(f"{'affine maps a*x + b':<34}orders {sorted(affine)}")
    print(f"{'':<34}5 present: {5 in powers or 5 in affine}")
    print("  powers act as multiplication by k in Z/28, so the order divides 12;")
    print("  affine orders divide 28 or equal 29. 5 divides neither.\n")

    print("=== order 5 on 30 points: the projective line ===\n")
    group = projective_group()
    order5 = [p for p in group if order_of(list(p)) == 5]
    types = Counter(tuple(sorted(cycle_type(list(p)).items())) for p in order5)
    fixing = sum(1 for p in order5 if p[INFINITY] == INFINITY)
    print(f"|PGL(2,29)| = 29*28*30 = {len(group):,}")
    print(f"elements of order 5     = {len(order5):,}")
    print(f"cycle types             = {dict(types)}   (six 5-cycles, no fixed points)")
    print(f"fixing the 30th point   = {fixing}")
    print("  so no order-5 Mobius map restricts to the 29 runes: the alphabet must")
    print("  hold 30 symbols, and the letter step is fixed-point-free, where the")
    print("  walk's 29-symbol g has cycle type 5^5 1^4 with four fixed points.\n")

    print("=== is a 30th written symbol consistent with the transcription? ===\n")
    rates = mark_rates()
    print(f"clean corpus: {rates['runes']:,} runes")
    print(f"{'a uniformly emitted 30th symbol':<34}{1 / 30:.4f} of the stream")
    print(f"{'cluster marks (the dot family)':<34}{rates['cluster marks']:.4f}")
    print(f"{'word separators':<34}{rates['word separators']:.4f}")
    print("  neither matches, so the extra point is not a symbol the scribe writes.")
    print("  What is untested: the extra point as a GAP the encoder skips.")


if __name__ == "__main__":
    main()


def cycle_of(perm: list[int], start: int) -> list[int]:
    cycle, x = [], start
    while True:
        cycle.append(x)
        x = perm[x]
        if x == start:
            return cycle


def leak_rates(order5: list[list[int]], frequencies) -> list[float]:
    """Share of positions whose ciphertext is the 30th point, base chosen to minimise it.

    The output is the extra point exactly when the plaintext rune is g^-j(u), with
    u = base^-1(infinity). base is free, so the designer picks the g-cycle of lowest
    total plaintext frequency; the cycle holding infinity carries one free zero term.
    """
    return [
        min(sum(frequencies[x] for x in cycle_of(g, s)) / 5 for s in range(30))
        for g in order5
    ]


def skip_rule_collision(g: list[int], base: list[int]) -> tuple[int, int, int] | None:
    """Two plaintext runes that a skip-on-infinity encoder sends to the same rune.

    The gap reading says the encoder, finding the output is the extra point, advances
    the phase instead of writing. Then the forbidden rune at phase j is emitted under
    phase j+1 -- which is exactly what g(p) would have produced at phase j. The two
    are indistinguishable to a decoder that has only the ciphertext.
    """
    inverse = [0] * 30
    for x, y in enumerate(base):
        inverse[y] = x
    for j in range(5):
        powers = list(range(30))
        for _ in range(j):
            powers = [g[x] for x in powers]
        forbidden = next((p for p in range(M) if base[powers[p]] == INFINITY), None)
        if forbidden is None:
            continue
        stepped = [g[x] for x in powers]
        rival = next(
            (
                q
                for q in range(M)
                if q != forbidden and base[powers[q]] == base[stepped[forbidden]]
            ),
            None,
        )
        if rival is not None:
            return j, forbidden, rival
    return None
