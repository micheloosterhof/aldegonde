# ABOUTME: Tests the walk's STEP RULE itself by scoring the DJU-BEI base return
# ABOUTME: under seven alternative rules, not just the published one.
"""Is the step rule right? Score the base return under alternatives.

Two sweeps have now found the base-return statistic behaving exactly like a
random permutation across every grid-and-disk construction. That has two
readings: the construction family is wrong, or the STEP RULE is.

DJU-BEI rests on two things of very different standing. That the phrase recurs
at words 1477 and 2926 is an observation. That

    base_{w+1} = base_w o g^((L_w - 1) mod 5) o sigma

is the mechanism is a hypothesis, and every search so far has assumed it. If the
rule is wrong the return test rejects the true key along with everything else,
and no amount of widening the construction space can help.

So vary the rule. Under the right one, the true key makes the base return
exactly, and near-misses should pile up above the Poisson(1) floor that a random
permutation gives. A rule whose score distribution lifts off that floor is
evidence about the mechanism -- which is worth more than another refuted family.

The crib is applied only through its model-light half: within a word base_w is
one bijection, so the arguments g^(k mod 5)(p_k) must be distinct where the
ciphertext runes are. The sigma-pinning half assumes the published rule and is
deliberately left out, so it cannot bias the comparison.
"""

from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from typing import TYPE_CHECKING

from construction_search import (  # noqa: E402
    HEAVY_DOUBLERS,
    crib_ok,
    keywords,
)
from construction_sweep2 import disk, grid, layouts  # noqa: E402
from walk_verifier import BEI, DJU, compose, inverse, load_words, order  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Callable

M = 29
IDENT = np.arange(M)

# each rule maps (g powers, sigma, word length) to the step applied after a word
RULES: dict[str, Callable[[list[np.ndarray], np.ndarray, int], np.ndarray]] = {
    "g^((L-1)%5) o sigma  [published]": lambda gp, s, L: compose(gp[(L - 1) % 5], s),
    "sigma o g^((L-1)%5)": lambda gp, s, L: compose(s, gp[(L - 1) % 5]),
    "g^(L%5) o sigma": lambda gp, s, L: compose(gp[L % 5], s),
    "sigma o g^(L%5)": lambda gp, s, L: compose(s, gp[L % 5]),
    "sigma alone": lambda gp, s, L: s,
    "g^((L-1)%5) alone": lambda gp, s, L: gp[(L - 1) % 5],
    "g^(-(L-1)%5) o sigma": lambda gp, s, L: compose(gp[(-(L - 1)) % 5], s),
}


def return_score(
    g: np.ndarray, sigma: np.ndarray, lengths: list[int], rule: Callable
) -> int:
    """Fixed points of M_DJU^-1 o M_BEI under this step rule; 29 = exact return."""
    gp = [IDENT]
    for _ in range(4):
        gp.append(compose(g, gp[-1]))
    cur = IDENT
    at_dju = at_bei = None
    for w, L in enumerate(lengths):
        if w == DJU:
            at_dju = cur
        if w == BEI:
            at_bei = cur
            break
        cur = compose(cur, rule(gp, sigma, L))
    if at_dju is None or at_bei is None:
        return 0
    return int(np.sum(compose(inverse(at_dju), at_bei) == IDENT))


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    words = load_words()
    lengths = [len(w) for w in words]
    lays = layouts(keywords(limit))

    g_pool: list[np.ndarray] = []
    for _name, layout in lays:
        for by_column in (True, False):
            for rotate in (1, 2):
                g = grid(layout, by_column=by_column, rotate=rotate, snake=False)
                if order(g) != 5:
                    continue
                if {i for i in range(M) if g[i] == i} & HEAVY_DOUBLERS:
                    continue
                if not crib_ok(g)[0]:
                    continue
                g_pool.append(g)
    sigmas = [disk(layout, step) for _n, layout in lays[:40] for step in (1, 2, 3)]
    print(
        f"g candidates {len(g_pool)}, sigma candidates {len(sigmas)}, "
        f"pairs per rule {len(g_pool) * len(sigmas):,}\n"
    )

    print(f"{'step rule':<34}{'mean fp':>9}{'max':>6}{'>=5':>7}{'>=10':>7}")
    for name, rule in RULES.items():
        scores: Counter[int] = Counter()
        for g in g_pool:
            for s in sigmas:
                scores[return_score(g, s, lengths, rule)] += 1
        total = sum(scores.values())
        mean = sum(k * n for k, n in scores.items()) / total
        hi5 = sum(n for k, n in scores.items() if k >= 5)
        hi10 = sum(n for k, n in scores.items() if k >= 10)
        print(f"{name:<34}{mean:>9.3f}{max(scores):>6}{hi5:>7}{hi10:>7}")
    print(
        f"\na random permutation gives mean 1.000; P(fp>=5) = "
        f"{sum(1 / math.e / math.factorial(k) for k in range(5, 30)):.4f}"
    )
    print("a rule whose mean or tail lifts off that floor is telling us about")
    print("the mechanism, not about any particular key")


if __name__ == "__main__":
    main()
