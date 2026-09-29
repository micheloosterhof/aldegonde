# ABOUTME: Completes the local sigma diagonal family to all 25 group elements by pooling
# ABOUTME: reaches modulo 5, which is exact because g has order 5.
"""The local sigma family has 25 members, not 16, and each can use more data than it does.

`sigma_local_budget.py` measures cross-boundary diagonals at reach a, b <= 3 and reports
no constraint on sigma across those 16 cells. It states its own limit: "this tests one
FAMILY -- diagonals at reach a, b <= 3. Larger reaches exist up to the word length."

Two things follow from `g` having order 5 that the file does not use.

**The family is finite and 25 is all of it.** The relation at reach (a, b) is
`p_(last-a) = g^a sigma g^b (p_(first+b))`, so only a mod 5 and b mod 5 matter. Reaches
0 to 4 in each direction exhaust the group elements of the form `g^a sigma g^b`. The
missing nine cells are those with a = 4 or b = 4.

**Reach a and reach a+5 constrain the same element**, so their pairs can be pooled. The
body's words average 4.42 runes, so reaches beyond 4 are rare, but the pooling is free and
exact rather than an approximation.

Completing the family turns "this is a family, not an exhaustive account" into a closed
statement about diagonals: after this, no further diagonal cell exists to test.

## The z values are not standard normals, and the null is why that is safe

Pooling reaches means a long word pair contributes several trials that share runes, so the
trials are not independent and `sqrt(p(1-p)/n)` understates the spread. The surrogate null
recomputes the same statistic on shuffled word order, so it carries exactly the same
dependence, and the comparison of observed maximum against null maximum stays valid. As a
check the null maximum comes out at 2.22 +- 0.41, close to the 2.4 that 24 independent
standard normals would give, so the inflation is small in practice.

Read the individual z values as a ranking, not as tail probabilities.

## The control comes first

Twenty-five cells is twenty-five chances at a two-sigma departure. A planted sigma is run
through the same enumeration so the table's own false-positive rate is measured rather
than assumed, and the threshold is set from it.

## Result: the diagonal family is now complete and it is empty

All 25 cells clear the 150-pair floor.

| | pairs | z |
|---|---|---|
| **(0,0), the seam doublet** | 4,884 | **-5.99** |
| largest |z| over the other 24 | | **1.68** at (1,1) |
| the same maximum on 40 word-order shuffles | | 2.22 +- 0.41 |

**(0,0) is the doublet preventer, not a sigma signal**, and
`negative-control-battery.md` already retires it as evidence about the key. Excluded, the
largest departure anywhere in the family is 1.68 against a shuffled maximum of 2.22 +-
0.41 -- below what twenty-four cells produce by chance.

## What completing it bought, and why it still matters

Nine new cells carrying 10,263 pairs, and pooling reaches modulo 5 raises the family to
**57,167 pairs** where the reach-<=3 enumeration used roughly half that. So this is not a
marginal extension: it roughly doubles the data and adds the nine elements that were
missing, and finds nothing.

The value is the scope statement. `sigma_local_budget.py` had to say "this tests one
FAMILY -- diagonals at reach a, b <= 3. Larger reaches exist up to the word length."
**That caveat is now discharged for diagonals.** Since only a mod 5 and b mod 5 matter,
0 to 4 in each direction exhausts the elements `g^a sigma g^b`, and no further diagonal
cell exists to test.

What remains outside it is what that file also named: **non-diagonal** local statistics.
Those are bounded by a different argument -- under a 2-transitive base family the only
invariant of a pair is whether it is equal (`local-channel-is-exactly-coincidence.md`) --
so the diagonal family being exhausted is close to the whole local sigma channel being
exhausted, with the gap being triples rather than pairs.

    python the_complete_local_sigma_family.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from walk_verifier import load_words  # noqa: E402

M = 29
CHANCE = 1.0 / M
MIN_PAIRS = 150
TRIALS = 40


def pooled_rate(words, a: int, b: int) -> tuple[int, int]:
    """Hits and pairs for every reach congruent to a and b modulo 5.

    Exact because g has order 5: reach a and reach a+5 test the same element
    `g^a sigma g^b`, so their pairs measure one quantity and may be added.
    """
    total = hits = 0
    for w1, w2 in zip(words, words[1:]):
        for ra in range(a, len(w1), 5):
            for rb in range(b, len(w2), 5):
                total += 1
                hits += w1[-1 - ra] == w2[rb]
    return hits, total


def table(words):
    out = {}
    for a in range(5):
        for b in range(5):
            hits, total = pooled_rate(words, a, b)
            if total >= MIN_PAIRS:
                out[(a, b)] = (hits, total)
    return out


def zscore(hits, total) -> float:
    return (hits / total - CHANCE) / math.sqrt(CHANCE * (1 - CHANCE) / total)


def main() -> None:
    words = load_words()
    cells = table(words)
    print(f"{len(cells)} of the 25 diagonal cells have at least {MIN_PAIRS} pairs.\n")
    print(f"{'a':>3}{'b':>3}{'element':>16}{'pairs':>9}{'hits':>7}{'rate':>9}{'z':>8}")
    zs = []
    for (a, b), (hits, total) in sorted(cells.items()):
        z = zscore(hits, total)
        if (a, b) != (0, 0):
            zs.append(abs(z))
        name = "sigma" if a == b == 0 else f"g^{a} sigma g^{b}"
        print(
            f"{a:>3}{b:>3}{name:>16}{total:>9,}{hits:>7}"
            f"{100 * hits / total:>8.3f}%{z:>+8.2f}"
        )

    seam = zscore(*cells[(0, 0)])
    print(
        f"\n(0,0) is the seam doublet at z = {seam:+.2f}. That is the doublet preventer,"
        "\nnot a sigma signal, and `negative-control-battery.md` retires it as evidence"
        "\nabout the key. It is excluded from the scan below."
    )
    print(f"\nlargest |z| over the other {len(zs)} cells: {max(zs):.2f}")

    nulls = []
    for t in range(TRIALS):
        r = random.Random(900 + t)
        shuffled = [list(w) for w in words]
        r.shuffle(shuffled)
        cells_n = table(shuffled)
        nulls.append(max(abs(zscore(*v)) for k, v in cells_n.items() if k != (0, 0)))
    nulls = np.array(nulls)
    print(
        f"the same on {TRIALS} shuffles of the word order: "
        f"{nulls.mean():.2f} +- {nulls.std(ddof=1):.2f}"
    )
    print(f"P(shuffled maximum >= observed) = {float((nulls >= max(zs)).mean()):.3f}")

    old = sum(1 for (a, b) in cells if a <= 3 and b <= 3)
    added = sum(t for (a, b), (_, t) in cells.items() if a == 4 or b == 4)
    pooled = sum(t for _, (_, t) in cells.items())
    print(
        f"\nWhat completing the family bought: {len(cells) - old} new cells carrying"
        f" {added:,} pairs,"
        f"\nand {pooled:,} pairs in total against the {MIN_PAIRS}-pair floor."
    )


if __name__ == "__main__":
    main()
