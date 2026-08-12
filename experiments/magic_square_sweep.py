# ABOUTME: Sweeps the magic-square-ordered grid family for g and finds no enrichment
# ABOUTME: over random order-5 permutations, refuting it as a search shortcut.
"""The book's 5x5 magic square does not supply g.

`magic-square-grid-key.md` proposed that the 5x5 magic square printed at master
lines 179-183 (fully magic at 3301) supplies the fill order for the 5x5 rune grid
of `g-from-5x5-grid.md`, removing that construction's largest freedom and leaving
only C(29,4) fixed-rune choices x 4 rotations x 2 axes = 190,008 candidates.

**Filter.** Since g has order 5 (`period5_confirmation.py`), distance d tests
g^(d mod 5) on the distance-d within-word plaintext table, so EVERY distance is a
g-only constraint -- not just the doublet:

    d   power   observed
    1   g^1     0.628%       5   g^0     4.920%
    2   g^2     3.473%       6   g^1     2.447%
    3   g^3     3.702%       7   g^2     4.208%
    4   g^4     4.098%

**Result.** Requiring all seven within 2 sigma leaves exactly ONE candidate:
fixed = (1, 8, 10, 24), rotation 4, column-wise. The cascade is 190,008 -> 74 -> 33
-> 30 -> 5 -> 5 -> 5 -> 1.

**But the control kills it.** 400,000 RANDOM order-5 permutations pass the same
seven cuts at 0.00125%, which over a family of 190,008 predicts **2.4** survivors.
Finding 1 is not enrichment -- it is slightly fewer than chance. The
magic-square-ordered family behaves exactly like random order-5 permutations, so it
supplies no search advantage, which was the whole point of using a structured
family. Same conclusion the repo already reached for keyword grids: structure
supplies no low diagonal.

**Byproduct, and it corrects `information_budget.py`.** The seven distance
constraints together cut the space by 1/0.00125% = 80,000x, i.e. **16.3 bits** about
g -- not the 4.0 bits the doublet count alone gives. The budget understated the
key-local channel by a factor of four. It does not change the conclusion: 16.3 bits
against g's 79.7 leaves 63 bits, about 1e19 candidates, still far beyond
enumeration, and sigma's 97.9 bits are untouched. But the figure should be 16, not 4.

Scope: this tests the canonical tie-break only. The square has twelve duplicated
values, so up to 2^12 fill orders exist; a different tie-break is a different family.
Given the complete absence of enrichment there is little reason to try them.
"""

from __future__ import annotations

import itertools
import random
import re
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from magic_square import extract  # noqa: E402
from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words, order, perm_from_cycles  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
PROSE = Path(tempfile.gettempdir()) / "pg1342.txt"
SIGMA = 2.0
MIN_PAIRS = 500
CONTROL = 400000


def observed_rates(words: list[list[int]]) -> dict[int, tuple[float, float]]:
    out = {}
    for d in range(1, 10):
        total = hits = 0
        for w in words:
            for j in range(len(w) - d):
                total += 1
                hits += w[j] == w[j + d]
        if total > MIN_PAIRS:
            r = hits / total
            out[d] = (r, (r * (1 - r) / total) ** 0.5)
    return out


def plaintext_tables(distances) -> dict[int, np.ndarray]:
    if not PROSE.exists():
        import urllib.request

        urllib.request.urlretrieve(  # noqa: S310
            "https://www.gutenberg.org/files/1342/1342-0.txt", PROSE
        )
    body = PROSE.read_text(errors="ignore")
    body = body[body.find("It is a truth universally") :]
    words = []
    for w in re.findall(r"[A-Za-z]+", body):
        r = [IDX[c] for c in english_to_runeglish(w.upper()) if c in IDX]
        if r:
            words.append(r)
    out = {}
    for d in distances:
        T = np.zeros((M, M))
        for w in words:
            for j in range(len(w) - d):
                T[w[j]][w[j + d]] += 1
        out[d] = T / T.sum()
    return out


def powers(g: np.ndarray) -> list[np.ndarray]:
    ps = [np.arange(M)]
    for _ in range(4):
        ps.append(g[ps[-1]])
    return ps


def fits(g: np.ndarray, obs, tables) -> bool:
    ps = powers(g)
    for d, (r, se) in obs.items():
        pred = float(sum(tables[d][ps[d % 5][b]][b] for b in range(M)))
        if abs(pred - r) > SIGMA * se:
            return False
    return True


def main() -> None:
    lp = load_words()
    obs = observed_rates(lp)
    tables = plaintext_tables(obs)
    square = extract()
    ranked = [
        i
        for _v, i in sorted((v, i) for i, v in enumerate(v for r in square for v in r))
    ]

    def build(fixed: set[int], rot: int, *, by_col: bool) -> np.ndarray:
        movers = [r for r in range(M) if r not in fixed]
        cells = [0] * 25
        for slot, rune in zip(ranked, movers):
            cells[slot] = rune
        perm = np.arange(M)
        for a in range(5):
            cyc = (
                [cells[r * 5 + a] for r in range(5)]
                if by_col
                else [cells[a * 5 + c] for c in range(5)]
            )
            for i, x in enumerate(cyc):
                perm[x] = cyc[(i + rot) % 5]
        return perm

    print(
        f"{len(obs)} g-only distance constraints at {SIGMA} sigma: "
        + ", ".join(f"d{d}(g^{d % 5})" for d in obs)
    )
    survivors = []
    tested = 0
    for fixed in itertools.combinations(range(M), 4):
        fs = set(fixed)
        for rot in (1, 2, 3, 4):
            for by_col in (True, False):
                g = build(fs, rot, by_col=by_col)
                tested += 1
                if order(g) == 5 and fits(g, obs, tables):
                    survivors.append((fixed, rot, by_col))
    print(f"\nmagic-square family: {tested:,} candidates -> {len(survivors)} survivors")
    for fixed, rot, by_col in survivors:
        print(f"  fixed={fixed} rot={rot} {'col' if by_col else 'row'}")

    rng = random.Random(4242)
    passed = 0
    for _ in range(CONTROL):
        g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
        passed += fits(g, obs, tables)
    rate = passed / CONTROL
    print(
        f"\ncontrol: {CONTROL:,} random order-5 permutations pass at {100 * rate:.5f}%"
    )
    print(f"  which predicts {rate * tested:.1f} survivors in a family of {tested:,}")
    verdict = (
        "NO enrichment -- refuted"
        if rate * tested > 0.3 * max(len(survivors), 1)
        else "enriched"
    )
    print(f"  observed {len(survivors)}  ->  {verdict}")
    if rate > 0:
        import math

        print(
            f"\nbyproduct: the {len(obs)} constraints cut by {1 / rate:,.0f}x = "
            f"{math.log2(1 / rate):.1f} bits about g"
        )
        print("  information_budget.py credits the doublet count with 4.0 bits;")
        print("  the full distance set is worth four times that, and still not enough.")


if __name__ == "__main__":
    main()
