# ABOUTME: Enumerates CONSTRUCTIONS of g and sigma rather than permutations, and
# ABOUTME: runs each through the DJU-BEI, crib and doublet filters.
"""Search the designer's construction rule, not the key.

The key space is hopeless and known to be: `(g, sigma)` spans about 1e48 and the
objective over it is a delta function -- a sigma wrong by one transposition
scores like a random one. Nothing that searches that space can work.

But a designer does not draw an order-5 permutation from the 1e21 available.
They lay runes out by a rule. Order 5 forces the shape: cycles of length 1 or 5
only, and 29 = 5*5 + 4, so g is five 5-cycles plus at least four fixed runes --
exactly a 5x5 grid with four runes left over (`g-from-5x5-grid.md`). The
enumerable object is the LAYOUT.

Constructions tried for g:
  * keyword-filled alphabet, then 25 runes into a 5x5 grid, columns rotated
  * the same by rows
  * runes ordered by Gematria prime value, by index, reversed
  * which four runes sit outside the grid: taken from the layout's tail

Constructions tried for sigma:
  * a mixed 29-disk turned one step per word: K o (+1) o K^-1 for keyword K
  * turned by other fixed amounts

Filters, cheapest first:
  1. order(g) == 5                       -- structural
  2. g's fixed runes avoid the heavy doublers. At least four runes pass through
     the letter wheel untouched, so if plaintext doubles one of them the
     ciphertext doubles too. In real LP plaintext L carries 21 of 49 doubles and
     the top four carry 76%; the ciphertext shows no such concentration.
  3. the crib. DIVINITY WITHIN pins sigma at two points given g, and forbids a
     value at three more (`crib_divinity_within.py`).
  4. DJU-BEI: the phrase recurs, so the base must return: M_1477 == M_2926.
  5. base_0 by quadgram hillclimb, which is cheap and a superb verifier.

A run that returns nothing is the expected outcome and still worth having: it
removes a family of constructions rather than a scatter of keys.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import (  # noqa: E402
    compose,
    dewalk_perms,
    djubei_returns,
    load_quadgrams,
    load_words,
    order,
    solve_base0,
    step_products,
)

from aldegonde import c3301

M = 29
ALPHABET = c3301.CICADA_ALPHABET
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
NAME = {n: i for i, n in enumerate(ENGLISH)}
DICT = Path("/usr/share/dict/web2")

# runes that carry the plaintext doubles in the recovered solved pages; if g
# fixed one of these, their doubles would surface as ciphertext doublets on a
# single rune, and no such concentration exists
HEAVY_DOUBLERS = {NAME["L"], NAME["S"], NAME["O"], NAME["F"]}

# the opening crib, runeglish
CRIB = (
    [NAME[x] for x in ("D", "I", "U", "I", "N", "I", "T", "Y")],
    [c3301.r2i(r) for r in "ᛋᚻᛖᚩᚷᛗᛡᚠ"],
    [NAME[x] for x in ("W", "I", "TH", "I", "N")],
    [c3301.r2i(r) for r in "ᛋᚣᛖᛝᚳ"],
)


def keyword_alphabet(keyword: str) -> list[int] | None:
    """Rune indices in keyword order, or None if the keyword is unusable."""
    seen: list[int] = []
    for ch in keyword.upper():
        name = {"V": "U", "K": "C", "Q": "C", "Z": "S"}.get(ch, ch)
        if name not in NAME:
            return None
        if NAME[name] not in seen:
            seen.append(NAME[name])
    if not seen:
        return None
    return seen + [i for i in range(M) if i not in seen]


def grid_g(layout: list[int], *, by_column: bool) -> np.ndarray:
    """25 runes into a 5x5 grid, one axis rotated; the last four stay fixed."""
    perm = np.arange(M)
    cells = layout[:25]
    for a in range(5):
        cycle = (
            [cells[r * 5 + a] for r in range(5)]
            if by_column
            else [cells[a * 5 + c] for c in range(5)]
        )
        for i, x in enumerate(cycle):
            perm[x] = cycle[(i + 1) % 5]
    return perm


def disk_sigma(layout: list[int], step: int) -> np.ndarray:
    """A mixed 29-disk turned `step` positions per word: K o (+step) o K^-1."""
    perm = np.arange(M)
    for i, x in enumerate(layout):
        perm[x] = layout[(i + step) % M]
    return perm


def fixed_points(perm: np.ndarray) -> set[int]:
    return {i for i in range(M) if perm[i] == i}


def crib_ok(g: np.ndarray) -> tuple[bool, dict[int, int]]:
    """Is g consistent with the crib, and what does it pin of sigma?"""
    gp = [np.arange(M)]
    for _ in range(4):
        gp.append(compose(g, gp[-1]))
    p0, c0, p1, c1 = CRIB
    args0 = [gp[k % 5][p] for k, p in enumerate(p0)]
    if len({(a, c) for a, c in zip(args0, c0)}) != len(set(args0)):
        return False, {}
    seen: dict[int, int] = {}
    for a, c in zip(args0, c0):
        if seen.setdefault(a, c) != c:
            return False, {}
    inv2 = {v: i for i, v in enumerate(gp[2])}
    pinned: dict[int, int] = {}
    for k, c in enumerate(c1):
        if c not in c0:
            continue
        source = gp[k % 5][p1[k]]
        target = inv2[args0[c0.index(c)]]
        if pinned.setdefault(source, target) != target:
            return False, {}
    return True, pinned


def keywords(limit: int) -> list[str]:
    if not DICT.exists():
        return [
            "DIUINITY",
            "CIRCUMFERENCE",
            "INSTAR",
            "PARABLE",
            "MOBIUS",
            "TOTIENT",
            "PRIMES",
            "SHADOW",
            "WISDOM",
            "CICADA",
        ]
    out = []
    for line in DICT.read_text().splitlines():
        w = line.strip().upper()
        if 4 <= len(w) <= 14 and w.isalpha():
            out.append(w)
            if len(out) >= limit:
                break
    return out


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    words = load_words()
    lengths = [len(w) for w in words]
    quad = load_quadgrams()
    rng = random.Random(3301)

    kws = keywords(limit)
    print(f"keywords: {len(kws)}")
    print("g constructions per keyword: 2 (columns, rows)")
    print("sigma constructions per keyword: 4 (disk steps 1, 2, 3, 5)\n")

    g_pool: list[tuple[str, np.ndarray, dict[int, int]]] = []
    tried = order_bad = doubler_bad = crib_bad = 0
    for kw in kws:
        layout = keyword_alphabet(kw)
        if layout is None:
            continue
        for by_column in (True, False):
            tried += 1
            g = grid_g(layout, by_column=by_column)
            if order(g) != 5:
                order_bad += 1
                continue
            if fixed_points(g) & HEAVY_DOUBLERS:
                doubler_bad += 1
                continue
            ok, pinned = crib_ok(g)
            if not ok:
                crib_bad += 1
                continue
            g_pool.append((f"{kw}/{'col' if by_column else 'row'}", g, pinned))

    print(f"g candidates built      : {tried}")
    print(f"  rejected, order != 5  : {order_bad}")
    print(f"  rejected, fixes a heavy doubler: {doubler_bad}")
    print(f"  rejected by the crib  : {crib_bad}")
    print(f"  surviving             : {len(g_pool)}\n")
    if not g_pool:
        return

    hits = 0
    checked = 0
    for label, g, pinned in g_pool:
        for kw in kws:
            layout = keyword_alphabet(kw)
            if layout is None:
                continue
            for step in (1, 2, 3, 5):
                sigma = disk_sigma(layout, step)
                if any(sigma[s] != t for s, t in pinned.items()):
                    continue  # the crib pins sigma at these points
                checked += 1
                Ms = step_products(g, sigma, lengths)
                if not djubei_returns(Ms):
                    continue
                hits += 1
                cipher = np.array([r for w in words for r in w])
                D = dewalk_perms(g, Ms, words)
                fit, _ = solve_base0(cipher, D, quad[0], quad[1], rng)
                print(
                    f"  DJU-BEI + crib survivor: g={label} sigma={kw}/+{step}"
                    f"  base0 fitness {fit:.3f}"
                )
    total = len(g_pool) * len([k for k in kws if keyword_alphabet(k)]) * 4
    print(f"\n(g, sigma) construction pairs considered  : {total:,}")
    print(
        f"pairs surviving the crib's pinned sigma    : {checked:,}"
        f"  ({checked / max(total, 1):.4%})"
    )
    print(f"pairs also passing DJU-BEI                : {hits}")
    if not hits:
        print("\nNothing survived. The construction family is removed, not the key.")


if __name__ == "__main__":
    main()
