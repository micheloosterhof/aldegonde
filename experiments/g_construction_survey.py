#!/usr/bin/env python3
# ABOUTME: Surveys structured 5x5-grid constructions for the letter step g,
# ABOUTME: asking whether any small-parameter family reaches the required
# ABOUTME: within-word diagonal (~0.0063) or whether only annealing does.
"""Can a structured construction produce g, or must g be designed?

The attack is now purely enumerative over (g, sigma)
(`no-known-plaintext-foothold.md`: the landscape has no gradient), so
everything depends on whether g comes from a family small enough to
enumerate. `g-from-5x5-grid.md` proposes 25 runes in a 5x5 grid with
each column rotated — giving five 5-cycles + 4 fixed runes — and records
that keyword fills fail the diagonal requirement (0.023 vs 0.0063).

This surveys the family properly: for each rune ORDERING (gematria order,
prime-value order, reversed, keyword-mixed) and each FILL pattern
(row-major, column-major, boustrophedon), it enumerates all C(29,4)
choices of fixed runes and all per-column rotation offsets, and reports
the minimum achievable diagonal against the required band. If the whole
structured family floors out well above 0.0063, then g cannot be
keyword- or order-derived: it must be tuned against the language's
bigram table directly, which is itself a strong statement about the
designer and about what enumeration must cover.
"""

from __future__ import annotations

import itertools
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from aldegonde import c3301
from lp_corpus import load_clean
from sigma_algebraic_floor import tables

M = 29
TARGET = 0.0063
BAND = (0.004, 0.009)   # plausible range for the g diagonal


def orderings(rng):
    """Candidate rune orderings for filling the grid."""
    base = list(range(M))
    yield "gematria order", base
    yield "reversed", base[::-1]
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
              59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
    yield "prime-value order", sorted(base, key=lambda i: primes[i])
    yield "prime-value desc", sorted(base, key=lambda i: -primes[i])
    eng = c3301.CICADA_ENGLISH_ALPHABET
    yield "english-alphabetical", sorted(base, key=lambda i: eng[i])
    for kw in ("DIUINITY", "CIRCUMFERENCE", "INSTAR", "PARABLE", "PRIMES",
               "TOTIENT", "AETHEREAL", "MOBIUS", "SHADOW", "WISDOM"):
        seq, seen = [], set()
        for ch in kw:
            for i, name in enumerate(eng):
                if name == ch and i not in seen:
                    seq.append(i)
                    seen.add(i)
        seq += [i for i in base if i not in seen]
        yield f"keyword {kw}", seq


def fills():
    yield "row-major", lambda cells: [cells[r * 5:(r + 1) * 5]
                                      for r in range(5)]
    yield "column-major", lambda cells: [[cells[c * 5 + r] for c in range(5)]
                                         for r in range(5)]

    def boustro(cells):
        rows = []
        for r in range(5):
            row = cells[r * 5:(r + 1) * 5]
            rows.append(row if r % 2 == 0 else row[::-1])
        return rows
    yield "boustrophedon", boustro


def build_g(grid, offsets):
    """Columns become 5-cycles with the given per-column rotation."""
    g = list(range(M))
    for c in range(5):
        col = [grid[r][c] for r in range(5)]
        k = offsets[c]
        for r in range(5):
            g[col[r]] = col[(r + k) % 5]
    return g


def diag(T, g):
    return sum(T[g[y]][y] for y in range(M))


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    words = [d[k] for k in sorted(d)]
    lens = [len(w) for w in words]

    sys.path.insert(0, str(ROOT / "experiments"))
    from d5_partial_leak import to_runeglish
    from doublet_position_profile import IDX_ENG
    from ea_direction_test import PROSE_CACHE, prose_words
    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if r:
            pools.setdefault(len(r), []).append(r)
    _, within = tables(lens, pools, rng)

    print(f"required g diagonal ~{TARGET} (band {BAND[0]}-{BAND[1]}); "
          f"random order-5 permutation gives ~0.034\n")
    offset_sets = list(itertools.product([1, 2, 3, 4], repeat=5))
    fixed_choices = list(itertools.combinations(range(M), 4))
    print(f"search space per ordering x fill: {len(fixed_choices)} fixed-rune "
          f"choices x {len(offset_sets)} rotation sets = "
          f"{len(fixed_choices) * len(offset_sets):,}")

    # The diagonal decomposes as a sum over the 4 fixed runes plus one
    # independent term per column, so the best rotation can be chosen per
    # column instead of scanning 4^5 combinations — exact, and 50x faster.
    selfrep = np.array([within[y][y] for y in range(M)])

    def best_grid_diag(grid):
        total = 0.0
        for c in range(5):
            col = [grid[r][c] for r in range(5)]
            total += min(sum(within[col[(r + k) % 5]][col[r]]
                             for r in range(5)) for k in (1, 2, 3, 4))
        return total

    overall = []
    for oname, order in orderings(rng):
        for fname, fill in fills():
            best = (9.9, None)
            for fixed in fixed_choices:
                fx = selfrep[list(fixed)].sum()
                if fx >= best[0]:
                    continue
                cells = [x for x in order if x not in fixed]
                v = fx + best_grid_diag(fill(cells))
                if v < best[0]:
                    best = (v, fixed)
            overall.append((best[0], oname, fname))
            print(f"  {oname:<22} {fname:<14} min diagonal {best[0]:.4f}"
                  + ("  <-- IN BAND" if BAND[0] <= best[0] <= BAND[1] else ""))
    overall.sort()
    print(f"\nbest structured construction: {overall[0][0]:.4f} "
          f"({overall[0][1]}, {overall[0][2]})")
    print(f"required: {TARGET:.4f}")
    if overall[0][0] > BAND[1]:
        print("=> NO structured grid construction reaches the required "
              "diagonal:\n   g cannot be order- or keyword-derived; it must "
              "be tuned\n   against the bigram table directly.")


if __name__ == "__main__":
    main()
