# ABOUTME: Replaces the DJU-BEI full-identity test with the six-point agreement
# ABOUTME: the observation actually supports, and re-runs the construction sweep.
"""The DJU-BEI filter has been 1e22 times too strict.

`repeated-phrase-dju-bei.md` states what the repeat pins: "Both words are 3
runes, so the within-word phase reaches only g^0, g^1, g^2: the SIX AGREEING
RUNES say nothing directly about g^3 or g^4."

Six points. But `walk_verifier.djubei_returns` tests

    np.array_equal(Ms[DJU], Ms[BEI])

which demands all twenty-nine. A random pair agrees on six given points with
probability 29^-6 = 1.7e-9; on all 29 with probability 1/29! = 1.1e-31. The
filter every search has run is stricter than its evidence by a factor of 1.5e22,
and would reject the true key unless the walk happens to return to its exact
state -- a strictly stronger claim than the observation supports.

What the repeat actually says: the ciphertext word at 1477 equals the one at
2926, so base_1477 and base_2926 agree at that word's three arguments, and
likewise base_1478 / base_2927 at three more. Since base_w = base_0 o M_w and
base_0 is injective, that is

    M_1477 and M_2926 agree at 3 points,  M_1478 and M_2927 at 3 points

with the points unknown, because the plaintext is unknown. A candidate passes if
each relative permutation fixes at least three runes -- necessary rather than
sufficient, but honest, and admitting the candidates the exact test threw away.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from construction_search import HEAVY_DOUBLERS, crib_ok, keywords  # noqa: E402
from construction_sweep2 import disk, grid, layouts  # noqa: E402
from walk_verifier import BEI, DJU, compose, inverse, load_words, order  # noqa: E402

M = 29
IDENT = np.arange(M)
NEEDED = 3  # runes per word that must agree; both words are 3 runes long


def relative(Ms: list[np.ndarray], a: int, b: int) -> np.ndarray:
    return compose(inverse(Ms[a]), Ms[b])


def products(g: np.ndarray, sigma: np.ndarray, lengths: list[int]) -> list[np.ndarray]:
    gp = [IDENT]
    for _ in range(4):
        gp.append(compose(g, gp[-1]))
    out = [IDENT]
    cur = IDENT
    for L in lengths:
        cur = compose(cur, compose(gp[(L - 1) % 5], sigma))
        out.append(cur)
    return out


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    words = load_words()
    lengths = [len(w) for w in words]
    print(
        f"DJU at word {DJU} ({len(words[DJU])} runes), "
        f"BEI at {DJU + 1} ({len(words[DJU + 1])} runes)"
    )
    print(
        f"repeat at {BEI} ({len(words[BEI])} runes) and "
        f"{BEI + 1} ({len(words[BEI + 1])} runes)\n"
    )

    lays = layouts(keywords(limit))
    g_pool = []
    for _name, layout in lays:
        for by_column in (True, False):
            for rotate in (1, 2, 3, 4):
                g = grid(layout, by_column=by_column, rotate=rotate, snake=False)
                if order(g) != 5:
                    continue
                if {i for i in range(M) if g[i] == i} & HEAVY_DOUBLERS:
                    continue
                ok, pinned = crib_ok(g)
                if ok:
                    g_pool.append(
                        (f"{_name}/{'col' if by_column else 'row'}{rotate}", g, pinned)
                    )
    sigmas = [(f"{n}/+{s}", disk(layout, s)) for n, layout in lays for s in range(1, M)]
    print(f"g candidates {len(g_pool):,}  sigma candidates {len(sigmas):,}")

    both: Counter[tuple[int, int]] = Counter()
    survivors = []
    pairs = 0
    for gtag, g, pinned in g_pool:
        for stag, sigma in sigmas:
            if any(sigma[s] != t for s, t in pinned.items()):
                continue
            pairs += 1
            Ms = products(g, sigma, lengths)
            r1 = relative(Ms, DJU, BEI)
            r2 = relative(Ms, DJU + 1, BEI + 1)
            f1 = int(np.sum(r1 == IDENT))
            f2 = int(np.sum(r2 == IDENT))
            both[(min(f1, 3), min(f2, 3))] += 1
            if f1 >= NEEDED and f2 >= NEEDED:
                survivors.append((gtag, stag, f1, f2))
    print(f"crib-consistent (g, sigma) pairs scored: {pairs:,}\n")
    print("agreement counts, capped at 3 (the number each word needs)")
    print(f"  {'':>6}" + "".join(f"{j:>9}" for j in range(4)))
    for i in range(4):
        row = "".join(f"{both.get((i, j), 0):>9,}" for j in range(4))
        print(f"  {i:>6}{row}")
    print(f"\npairs meeting the six-point requirement: {len(survivors)}")
    for gtag, stag, f1, f2 in survivors[:20]:
        print(f"   g={gtag:<28} sigma={stag:<20} agree {f1}/{f2}")
    if not survivors:
        print("   none -- even the weakened filter is not satisfied here")


if __name__ == "__main__":
    main()
