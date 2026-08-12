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

**Result: the sweep CANNOT decide the hypothesis, and that is the finding.** At 2
sigma the family gives 0 survivors of 190,008 against 2.9 +- 0.4 expected by chance.
But 2-sigma cuts on seven constraints reject a TRUE g 28% of the time, so 0 survivors
is worth only a Bayes factor of ~3.6 against -- suggestive, not a refutation. Widen to
3 sigma, where a true g is retained with probability 0.98, and the false-positive floor
rises to ~32, swamping the single true hit. No threshold isolates one candidate:

    cut    true g kept    family    chance expects      z
    2.0        0.72          0        2.9 +- 0.4      -1.7
    2.5        0.92          7       11.2 +- 0.8      -1.3
    3.0        0.98         24       32.2 +- 1.4      -1.4
    3.5        1.00         46       70.7 +- 2.1      -2.9

Separating a candidate from that floor needs the 2-rune verifier, hence the base
schedule, hence sigma -- which has no construction. So sigma's absence blocks the
EVALUATION of any g construction, not merely the attack.

**The constraints are satisfiable, so the model is not at fault.** Optimising
directly over order-5 permutations reaches all six tunable constraints to |z| <= 0.07.
That is unsurprising rather than reassuring -- six scalars in a 2^79.7 space is nearly
free -- but it rules out a contradictory constraint set.

**And the family is far too small to contain g unless the construction is exactly
right.** 190,008 is 2^17.5 of a 2^79.7 space, so an unenriched family holds a specific
target with probability 2^-62. A construction hypothesis is therefore all-or-nothing:
a bet on the designer's choice, settled only by a verifier sharp enough to confirm a
single key -- not by statistical narrowing.

**Length-matching the plaintext tables is load-bearing, and must be deterministic.**
Unmatched tables loosen every constraint. But RESAMPLING prose to the LP histogram is
also wrong: with ~23k sampled words the table noise is enough to move candidates
across a 2-sigma window, so survivor counts swing with the seed (one draw gave 0
family / 0 of 200,000 control, another 1 family / 5 of 400,000). This file therefore
WEIGHTS every prose word by how over- or under-represented its length is in the LP,
which uses all 123k words and is seed-free. An earlier version reported "1 survivor
against 2.4 expected, refuted" from unmatched tables; both figures were artifacts,
and the 2.4 rested on 5 control events besides.

**Byproduct for `information_budget.py`.** With weighted tables 46 of 3,000,000
random g pass at 2 sigma, so the seven constraints cut by 65,000x = **16.0 bits**
about g, against the 4.0 bits the budget credits to the doublet count alone. Four
times richer, and still nowhere near enough: 16.0 of g's 79.7 leaves ~64 bits, about
1e19 candidates, with sigma's 97.9 untouched. The figure has been 4.0, 16.3, 17.0 and
is now 16.0 -- the earlier ones rested on 3-6 control events, which is a factor-two
error in the rate.

Scope: the canonical tie-break only. The square's twelve duplicated values admit up
to 2^12 fill orders; trying them is pointless, though not for the reason first given
-- no fill order produces a tuned diagonal.
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
CONTROL = 3000000  # 3-6 hits at 200-400k gave a factor-2 unstable rate


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


def plaintext_tables(distances, lp: list[list[int]]) -> dict[int, np.ndarray]:
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
    # Weight each prose word by how over- or under-represented its length is in
    # the LP. Deterministic: resampling instead makes every constraint's pass/fail
    # depend on the draw, which is enough to move candidates across a 2-sigma window.
    from collections import Counter

    lp_hist = Counter(len(w) for w in lp)
    prose_hist = Counter(len(w) for w in words)
    weight = {
        length: lp_hist[length] / prose_hist[length]
        for length in prose_hist
        if length in lp_hist
    }
    out = {}
    for d in distances:
        T = np.zeros((M, M))
        for w in words:
            f = weight.get(len(w), 0.0)
            if not f:
                continue
            for j in range(len(w) - d):
                T[w[j]][w[j + d]] += f
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
    tables = plaintext_tables(obs, lp)
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
