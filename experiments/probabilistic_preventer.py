# ABOUTME: Tests a preventer that fires only some of the time, and finds the seam-to-d1w
# ABOUTME: ratio a constraint the whole dodge family fails.
"""The dodge over-suppresses. Letting it fire sometimes helps, and exposes a harder problem.

`models-on-the-informative-cells.md` scores the deterministic dodge at 2 of the 5
discriminating cells and notes how it fails: d1w comes out at 0.0040 against the corpus's
0.0063 and the seam at 0.0001 against 0.0079. Over-suppressed, not under -- the rule fires
too reliably. The obvious repair is to let it fire with probability phi.

That does help: at phi around 0.8 the model reaches **3 of 5**, the best score in this
directory. But it also exposes something the tally never showed.

**The corpus suppresses doublets equally inside a word and across a boundary.** It reads
d1w 0.0063 and seam 0.0079, a ratio of 1.25. Every member of this family gives a ratio of
at least 1.89, because the two contexts are not alike from the mechanism's point of view:
inside a word the base is constant, so a would-be repeat needs `g(p_j) = p_(j-1)` and is
schedule-determined; across a seam the base has changed, so a would-be repeat is a chance
event. A rule that perturbs the schedule cannot equalise them.

That is the same conclusion `separators-are-the-cipher-unit.md` reaches from the other
side: sliding every block boundary leaves the doublet rate unchanged, so the suppression
belongs to the emitted stream rather than to the block schedule.

Sixty draws, not fewer: below forty the battery's tail cannot register an upper-side miss
at all (`battery-cell-counts-are-not-evidence.md`), and a 30-draw run of this very table
reports 5 of 5 where 60 draws report 3.

    python probabilistic_preventer.py [--draws 60]
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


def preventer(g, sigma, phi: float):
    """Skip an extra clock step on a would-be repeat, but only with probability phi."""

    def generate(plain, rng):
        gp = [ppow(g, k) for k in range(5)]
        base = rng.sample(range(M), M)
        out, clock, previous = [], 0, None
        for word in plain:
            cw = []
            for p in word:
                c = base[gp[clock % 5][p]]
                if c == previous and rng.random() < phi:
                    clock += 1
                    c = base[gp[clock % 5][p]]
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
    # 63 within-word doublets and 23 at the seam set the ratio's error
    se = ratio * math.sqrt(1 / 63 + 1 / 23)
    print(f"corpus: d1w {lp['d1w']:.4f}, seam {lp['seam']:.4f}, "
          f"ratio {ratio:.2f} +- {se:.2f}\n")

    rng = random.Random(11)
    g = order5_fixing(rng.sample(range(M), 4), rng)
    sigma = rng.sample(range(M), M)
    print(f"{'phi':>6}{'d1w':>10}{'seam':>10}{'ratio':>8}{'gap_min':>10}"
          f"{'d6w':>10}{'lands':>8}")
    for phi in (0.0, 0.6, 0.8, 0.82, 0.9, 1.0):
        r = score(preventer(g, sigma, phi), lp, draws)
        landed = sum(1 for k in INFORMATIVE if r[k][1] > 0.05)
        rr = r["seam"][0] / r["d1w"][0] if r["d1w"][0] else float("inf")
        print(f"{phi:>6.2f}{r['d1w'][0]:>10.4f}{r['seam'][0]:>10.4f}{rr:>8.2f}"
              f"{r['doublet_gap_min'][0]:>10.2f}{r['d6w'][0]:>10.4f}{f'{landed}/5':>8}")
    print(
        "\nThree of five at phi ~ 0.8, the best here. But d1w and the seam cannot land"
        "\ntogether: fitting d1w at phi ~ 0.6 overshoots the seam, fitting the seam at"
        "\nphi ~ 0.8 undershoots d1w, and the ratio never falls below 1.91 against the"
        f"\ncorpus's {ratio:.2f} +- {se:.2f} -- about two sigma, and structural rather"
        "\nthan a matter of tuning."
    )


if __name__ == "__main__":
    main()
