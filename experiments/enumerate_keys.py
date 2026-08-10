# ABOUTME: Enumerates structured (g, sigma) length-clocked-walk keys through the
# ABOUTME: walk_verifier cascade and reports the funnel at each filter stage.
"""Structured key families (per g-from-5x5-grid.md and Cicada idiom):

  g : 25 runes in a 5x5 grid, each column rotated by one -> five 5-cycles + 4
      fixed points (order 5). Grids from keyword fills x {row/col major} x
      {which 4 runes are fixed}. Only low-diagonal g (rare-bigram columns) are
      cipher-plausible, so g is also scored on its doublet diagonal.
  sigma : keyword-mixed 29-permutations (standard Cicada key construction),
      restricted to EVEN permutations (parity necessary condition for a
      DJU-BEI state return; see walk_verifier).

The cascade: order(g)==5 -> parity(sigma) -> DJU-BEI full state return ->
diagonal plausibility -> base_0 quadgram solve. Reports how many candidates
survive each stage. A structured pass at the state-return stage would be a
major lead; an empty funnel there is the informative negative that
collision-hunt-single-constraint.md predicts.
"""

from __future__ import annotations

import random

import numpy as np
from walk_verifier import (
    M,
    diagonal_rate,
    djubei_parity_ok,
    djubei_returns,
    load_bigram_matrix,
    load_quadgrams,
    load_words,
    order,
    parity,
    step_products,
    verify,
)

from aldegonde.c3301 import CICADA_ENGLISH_ALPHABET as E

ENG2IDX: dict[str, int] = {}
for i, e in enumerate(E):
    ENG2IDX.setdefault(e, i)
# single-letter english -> rune index, for keyword mixing
LETTER2IDX = {e: i for i, e in enumerate(E) if len(e) == 1}

KEYWORDS = [
    "CICADA", "LIBERPRIMUS", "PRIMES", "TOTIENT", "WISDOM", "INSTAR",
    "PARABLE", "DIVINITY", "CIRCUMFERENCE", "MOBIUS", "EULER", "PRESERVATION",
    "ADHERENCE", "PILGRIMAGE", "ENLIGHTENMENT", "KOAN", "SHADOW", "TUNNELING",
    "EMERGENCE", "TRUTH", "DECEPTION", "CONSUMPTION", "WELCOME", "AUTWXKQZ",
]


def keyword_indices(word: str) -> list[int]:
    """Map an English keyword to distinct rune indices via single-letter runes."""
    out, seen = [], set()
    for ch in word:
        i = LETTER2IDX.get(ch)
        if i is not None and i not in seen:
            seen.add(i)
            out.append(i)
    return out


def mixed_alphabet(word: str) -> np.ndarray:
    """Keyword-mixed permutation of the 29 rune indices."""
    head = keyword_indices(word)
    rest = [i for i in range(M) if i not in head]
    order_ = head + rest
    return np.array(order_)  # perm[position] = rune index at that slot


def grid_g(word: str, *, col_major: bool) -> np.ndarray | None:
    """Build order-5 g: place 25 runes in a 5x5 grid (keyword-led), rotate each
    column down by one -> five 5-cycles; the 4 unplaced runes are fixed."""
    head = keyword_indices(word)
    rest = [i for i in range(M) if i not in head]
    seq = head + rest  # 29 runes; first 25 fill the grid, last 4 fixed
    grid_syms = seq[:25]
    fixed = seq[25:]
    grid = np.array(grid_syms).reshape(5, 5)
    if col_major:
        grid = grid.T
    perm = np.arange(M)
    # columns are 5-cycles: cell (r, c) -> (r+1 mod 5, c)
    for c in range(5):
        col = grid[:, c]
        for r in range(5):
            perm[col[r]] = col[(r + 1) % 5]
    for f in fixed:
        perm[f] = f
    return perm if order(perm) == 5 else None


def main() -> None:
    rng = random.Random(20260723)
    words = load_words()
    lengths = [len(w) for w in words]
    P = load_bigram_matrix()
    quad = load_quadgrams()

    gs = []
    for kw in KEYWORDS:
        for cm in (False, True):
            g = grid_g(kw, col_major=cm)
            if g is not None:
                gs.append((f"{kw}/{'col' if cm else 'row'}", g))
    sigmas = [(kw, mixed_alphabet(kw)) for kw in KEYWORDS]

    n_g = len(gs)
    n_s = len(sigmas)
    print(f"candidates: {n_g} grid-g (order 5) x {n_s} keyword-sigma = {n_g * n_s} pairs")

    # stage funnel
    even_sigma = [(k, s) for k, s in sigmas if parity(s) == 1]
    print(f"stage sigma-parity: {len(even_sigma)}/{n_s} keyword-sigma are even")

    parity_pass = returns = 0
    best_diag = []
    survivors = []
    for gname, g in gs:
        gdiag = diagonal_rate(P, g)
        for sname, sigma in even_sigma:
            if not djubei_parity_ok(g, sigma, lengths):
                continue
            parity_pass += 1
            Ms = step_products(g, sigma, lengths)
            if djubei_returns(Ms):
                returns += 1
                survivors.append((gname, sname, g, sigma))
            best_diag.append((gdiag, diagonal_rate(P, sigma), gname, sname))
    print(f"stage parity-ok: {parity_pass} (g, sigma) pairs pass the parity necessary condition")
    print(f"stage state-return: {returns} pairs achieve full DJU-BEI state return")

    # report the most cipher-plausible g by diagonal (want ~0.006), regardless
    best_diag.sort(key=lambda t: abs(t[0] - 0.006))
    print("\nmost doublet-plausible grid-g (target diagonal ~0.0063):")
    seen = set()
    for gd, _sd, gn, _sn in best_diag:
        if gn in seen:
            continue
        seen.add(gn)
        print(f"  g={gn:20s} diagonal {gd:.4f}")
        if len(seen) >= 6:
            break

    if survivors:
        print(f"\n{len(survivors)} STATE-RETURN survivors -> base_0 quadgram solve:")
        for gname, sname, g, sigma in survivors[:10]:
            res = verify(g, sigma, words, P, quad, rng)
            print(f"  g={gname} sigma={sname}: base_0 fitness {res.get('base0_fitness'):.3f} "
                  f"(Parable ~-3.4, random ~-6.9)")
    else:
        print("\nNo structured (g, sigma) in these families produces a DJU-BEI "
              "state return. Under the full-return assumption, the true key is "
              "not a keyword-grid g with a keyword sigma from this set.")


if __name__ == "__main__":
    main()
