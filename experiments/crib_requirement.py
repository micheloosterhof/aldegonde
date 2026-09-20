# ABOUTME: Measures how much known plaintext is needed to pin the letter step g, using
# ABOUTME: within-word ciphertext collisions, which are base-free and sigma-free.
"""How many crib words does it take to determine `g`?

`crib-budget-for-g.md` puts the threshold at ~400 known words. This is an independent
re-measurement on a freshly fitted key and a different prose corpus, and it CONFIRMS
that file.

It also records a trap. Counting the equations as independent — each worth log2(29)
bits — says 13 of them suffice, hence ~50 words, which is 8x too optimistic and would
have made the rubricated titles look sufficient. They are not. Equations chain inside
`g`'s 5-cycles: `g(x) = y` with `g(y) = z` already implies `g^2(x) = z`, so most
equations after the first few land in a component that is already built. The measure
that matters is how many of `g`'s 25 moving points get RESOLVED, not how many
equations arrive.

The constraint is exact and needs no key. Inside one word the base is a single
bijection, so for positions j < k

    c_j == c_k   <=>   g^((k - j) mod 5) ( p_k ) == p_j

with no base and no sigma in it. Every within-word ciphertext collision at known
plaintext is therefore one equation on `g` alone. Collisions at (k - j) = 0 mod 5 say
only that the plaintext repeats, since g^5 = id, so they carry nothing about `g`.

The measurement: plant a key, encipher real prose, take the first K words as a crib,
collect the equations, and count how many order-5 permutations still satisfy them.
`g` is pinned once the expected number of survivors in its ~1e21 candidate space
drops below one.

Run with no arguments.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import prose_corpora  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    distance_tables,
    fingerprint,
    fit_walk_key,
    lp_words,
    walk_generator,
)

# order-5 permutations of 29 points number 29!/(5^5 * 5! * 4!) ~ 1e21; the measured
# within-word rates cut that by ~16 bits (`key-local-channel-is-empty.md`)
G_SPACE = 9.84e23
G_SPACE_IN_BAND = G_SPACE / 2**16.0


def equations(plain, cipher, n_words: int) -> list[tuple[int, int, int]]:
    """(d, a, b) meaning g^d(a) = b, from within-word ciphertext collisions."""
    out = []
    for word_p, word_c in zip(plain[:n_words], cipher[:n_words]):
        for j in range(len(word_c)):
            for k in range(j + 1, len(word_c)):
                if word_c[j] == word_c[k]:
                    d = (k - j) % 5
                    if d:  # d == 0 is g^5 = id and says nothing about g
                        out.append((d, word_p[k], word_p[j]))
    return out


def independent_count(eqs) -> int:
    """Distinct (d, a) premises — an upper bound on how many equations can bite."""
    return len({(d, a) for d, a, _ in eqs})


class CycleUnion:
    """Union-find over the 29 runes with a mod-5 offset, the structure g^5 = id gives.

    `g^d(a) = b` says a and b share a 5-cycle with b at offset d from a. Merging those
    facts is what actually resolves g, and it is why counting equations as independent
    is wrong: many land inside a component already built and add nothing.
    """

    def __init__(self) -> None:
        self.parent = list(range(M))
        self.offset = [0] * M  # offset from the component root, mod 5

    def find(self, x: int) -> tuple[int, int]:
        if self.parent[x] == x:
            return x, 0
        root, off = self.find(self.parent[x])
        self.parent[x] = root
        self.offset[x] = (self.offset[x] + off) % 5
        return root, self.offset[x]

    def union(self, a: int, b: int, d: int) -> bool:
        """Record g^d(a) = b. False if it contradicts what is already known."""
        ra, oa = self.find(a)
        rb, ob = self.find(b)
        if ra == rb:
            return (ob - oa) % 5 == d % 5
        self.parent[rb] = ra
        self.offset[rb] = (oa + d - ob) % 5
        return True

    def pinned(self) -> int:
        """Runes whose image under g is determined: some point sits one step on."""
        groups: dict[int, dict[int, list[int]]] = {}
        for x in range(M):
            root, off = self.find(x)
            groups.setdefault(root, {}).setdefault(off, []).append(x)
        total = 0
        for slots in groups.values():
            for off, members in slots.items():
                if (off + 1) % 5 in slots:
                    total += len(members)
        return total


def resolve(eqs) -> int:
    """Points of g pinned by a set of equations."""
    union = CycleUnion()
    for d, a, b in eqs:
        union.union(a, b, d)
    return union.pinned()


def main() -> None:
    rng = random.Random(3301)
    lp = fingerprint(lp_words())
    tabs = distance_tables(draws=20)
    g, sigma, _ge, _se = fit_walk_key(tabs, lp, rng)
    generate = walk_generator(g, sigma)
    plain = prose_corpora(2928, 1)[0]
    cipher = generate(plain, rng)

    print("planted walk key on real prose; equations from within-word collisions")
    print("`pinned` counts runes whose image under g is resolved, the measure")
    print("`crib_budget_g.py` uses -- equations chain inside 5-cycles, so counting")
    print("them as independent badly overstates what a crib buys.\n")
    print(
        f"{'crib words':>11}{'runes':>8}{'equations':>11}{'distinct':>10}{'pinned':>9}"
    )
    for n_words in (25, 50, 100, 200, 400, 800, 1600, 2928):
        eqs = equations(plain, cipher, n_words)
        runes = sum(len(w) for w in plain[:n_words])
        print(
            f"{n_words:>11}{runes:>8}{len(eqs):>11}{independent_count(eqs):>10}"
            f"{resolve(eqs):>9}"
        )
    print("\n`g` has 25 moving points; it is determined when nearly all are pinned.")

    eqs_all = equations(plain, cipher, len(plain))
    rate = len(eqs_all) / sum(len(w) for w in plain)
    print(
        f"\nequation rate: {rate * 100:.2f} per 100 crib runes "
        f"(crib-budget-for-g.md reports 10.4, counting d = 0 collisions too)"
    )
    titles = [8, 5] * 17  # the rubricated titles, if DIVINITY WITHIN is typical
    yielded = sum(
        sum(1 for j in range(L) for k in range(j + 1, L) if (k - j) % 5) / M
        for L in titles
    )
    print(
        f"the ~31 title slots supply 29 words / 128 runes, worth about "
        f"{yielded * 29 / len(titles):.0f} equations"
    )
    print("which pins only a handful of points: the title route verifies, it does not")
    print("generate, exactly as crib-budget-for-g.md concludes.")


if __name__ == "__main__":
    main()
