# ABOUTME: A preventer that substitutes the emitted rune on collision instead of perturbing
# ABOUTME: the clock, which is the one shape the seam-to-d1w ratio leaves open.
"""The ratio says the rule's FAILURES must be context-free. This is a rule like that.

`seam-to-d1w-ratio-is-a-constraint.md` shows the whole clock-perturbing family failing one
test: the corpus suppresses repeats equally inside a word and across a boundary, ratio
1.25 +- 0.30, while every dodge gives at least 1.91. The reason is structural -- inside a
word a would-be repeat needs `g(p_j) = p_(j-1)` and the rule's failures are
schedule-determined, while at a seam they are chance -- and it names the direction to
look: a rule whose residual collision probability is the same in both contexts.

So substitute instead of skipping. On a would-be repeat, emit `tau(c)` for a fixed
permutation tau rather than re-running the clock:

    c = base(g^j(p));   if c == previous:  c = tau(c)

A doublet then survives exactly when `tau(c) = c`, so the rate is (fixed points of tau)/29
times the would-be rate -- **the same factor in both contexts**. The rate is set by how
many points tau holds still, which is one integer of key, and the ratio should fall out
near 1 rather than being fitted.

REFUTED (September 2026), by a measurement that needs no key. A doublet survives this
rule exactly when tau fixes the emitted rune, so every surviving doublet is a fixed point
of tau. The body's 86 survivors use 28 of the 29 runes, which forces |fix(tau)| >= 28,
while the 81% suppression rate forces |fix(tau)| ~ 5.6. No permutation does both. See
`survivors-use-every-rune.md` and `experiments/which_runes_survive.py`. The file is kept
because the seam-ratio reasoning that motivated it is still sound and still needs a
candidate that satisfies it.

    python substitution_preventer.py [--draws 60]
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    compose,
    fingerprint,
    lp_words,
    ppow,
    prose_corpora,
)

INFORMATIVE = ("d1w", "seam", "doublet_gap_min", "d6w", "returns")


def tau_fixing(keep: list[int], rng: random.Random) -> list[int]:
    """A permutation whose fixed points are exactly `keep`, deranged elsewhere."""
    movers = [x for x in range(M) if x not in keep]
    shuffled = movers[:]
    while len(movers) > 1 and any(a == b for a, b in zip(movers, shuffled)):
        rng.shuffle(shuffled)
    tau = list(range(M))
    for a, b in zip(movers, shuffled):
        tau[a] = b
    return tau


def preventer(g, sigma, tau):
    def generate(plain, rng):
        gp = [ppow(g, k) for k in range(5)]
        base = rng.sample(range(M), M)
        out, clock, previous = [], 0, None
        for word in plain:
            cw = []
            for p in word:
                c = base[gp[clock % 5][p]]
                if c == previous:
                    c = tau[c]
                cw.append(c)
                previous = c
                clock += 1
            out.append(cw)
            base = compose(base, compose(gp[(clock - 1) % 5], sigma))
        return out

    return generate


def score(gen, lp, draws: int):
    rng = random.Random(3301)
    sims = [fingerprint(gen(p, rng)) for p in prose_corpora(2928, draws)]
    out = {}
    for k in INFORMATIVE:
        v = np.array([s[k] for s in sims])
        below = float((v <= lp[k]).mean())
        tail = 2 * min(below, 1 - below + 1 / len(v))
        if float(v.std()) < 1e-12 and abs(float(v.mean()) - lp[k]) < 1e-9:
            tail = 1.0
        out[k] = (float(v.mean()), tail)
    return out


def main() -> None:
    draws = 60
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = fingerprint(lp_words())
    ratio = lp["seam"] / lp["d1w"]
    se = ratio * math.sqrt(1 / 63 + 1 / 23)
    print(f"corpus: d1w {lp['d1w']:.4f}, seam {lp['seam']:.4f}, "
          f"ratio {ratio:.2f} +- {se:.2f}\n")

    rng = random.Random(11)
    g = order5_fixing(rng.sample(range(M), 4), rng)
    sigma = rng.sample(range(M), M)
    print(f"{'tau fixes':>10}{'d1w':>10}{'seam':>10}{'seam/d1w':>10}"
          f"{'gap_min':>10}{'d6w':>10}{'lands':>8}")
    for f in (0, 2, 4, 6, 8, 12):
        tau = tau_fixing(rng.sample(range(M), f), rng)
        r = score(preventer(g, sigma, tau), lp, draws)
        landed = sum(1 for k in INFORMATIVE if r[k][1] > 0.05)
        rr = r["seam"][0] / r["d1w"][0] if r["d1w"][0] else float("inf")
        print(f"{f:>10}{r['d1w'][0]:>10.4f}{r['seam'][0]:>10.4f}{rr:>10.2f}"
              f"{r['doublet_gap_min'][0]:>10.2f}{r['d6w'][0]:>10.4f}{f'{landed}/5':>8}")
    print(
        "\nThe rate is set by how many points tau holds still. The ratio is not fitted:"
        "\nit falls out of the mechanism, because the residual collision probability is"
        "\nthe same inside a word and across a seam."
    )


if __name__ == "__main__":
    main()
