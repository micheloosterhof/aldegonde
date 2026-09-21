# ABOUTME: Calibrates the seam-to-within-word doublet ratio against g's graph mass, turning
# ABOUTME: it into a measurement of the letter step rather than a model comparison.
"""The ratio is a readout of g. This is the dial it is attached to.

`seam-to-d1w-ratio-is-a-constraint.md` retracts an exclusion and keeps a measurement: under
a preventer that substitutes on collision, the seam doublet rate is context-free while the
within-word rate tracks

    mass(g) = sum_x P(previous = g(x), current = x)

the mass g's graph carries on the plaintext adjacent-bigram table. Three points showed the
ratio spanning 0.52 to 9.77. This calibrates it across eighteen order-5 permutations drawn
evenly from the mass range of four thousand, and inverts it on the corpus.

The relation is an inverse law, `ratio = a / mass`, because the numerator -- the seam rate
-- does not depend on g at all.

    python g_graph_mass.py [--draws 25]

Twenty-five corpora suffice here: this estimates MEANS, not the battery's land/miss
decision, which needs forty (`battery-cell-counts-are-not-evidence.md`).
"""

from __future__ import annotations

import math
import random
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, fingerprint, lp_words, prose_corpora  # noqa: E402
from substitution_preventer import preventer, tau_fixing  # noqa: E402


def bigram_table(plain) -> np.ndarray:
    """P(previous = x, current = y), indexed [current][previous]."""
    tab = np.zeros((M, M))
    for w in plain:
        for i in range(len(w) - 1):
            tab[w[i + 1]][w[i]] += 1
    return tab / tab.sum()


def main() -> None:
    draws = 25
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = fingerprint(lp_words())
    corpora = prose_corpora(2928, draws)
    tab = bigram_table(corpora[0])
    rng = random.Random(4)

    pool = []
    for _ in range(4000):
        g = order5_fixing(rng.sample(range(M), 4), rng)
        pool.append((sum(tab[x][g[x]] for x in range(M)), g))
    pool.sort(key=lambda t: t[0])
    masses = [m for m, _ in pool]
    print(f"mass over 4,000 random order-5 permutations: min {masses[0]:.4f}, "
          f"median {masses[len(masses) // 2]:.4f}, max {masses[-1]:.4f}")
    print(f"chance, if g's graph were unrelated to the table: 1/29 = {1 / M:.4f}\n")

    sigma = rng.sample(range(M), M)
    tau = tau_fixing(rng.sample(range(M), 8), rng)
    xs, ys = [], []
    print(f"{'mass':>9}{'ratio':>9}{'d1w':>9}")
    for i in [int(i * (len(pool) - 1) / 17) for i in range(18)]:
        m, g = pool[i]
        r = random.Random(3301)
        sims = [fingerprint(preventer(g, sigma, tau)(p, r)) for p in corpora]
        d1 = statistics.mean(s["d1w"] for s in sims)
        seam = statistics.mean(s["seam"] for s in sims)
        xs.append(m)
        ys.append(seam / d1)
        print(f"{m:>9.4f}{seam / d1:>9.3f}{d1:>9.4f}")

    a = statistics.mean(x * y for x, y in zip(xs, ys))
    print(f"\nfit: ratio = {a:.5f} / mass   (the numerator is the seam rate, g-free)")

    ratio = lp["seam"] / lp["d1w"]
    se = ratio * math.sqrt(1 / 63 + 1 / 23)
    print(f"\ncorpus ratio {ratio:.2f} +- {se:.2f}, from 63 within-word doublets and 23 at"
          " the seam")
    for label, rr in (("+1 sigma", ratio + se), ("point", ratio), ("-1 sigma", ratio - se)):
        mm = a / rr
        frac = sum(1 for x in masses if x <= mm) / len(masses)
        print(f"  {label:<9} ratio {rr:>5.2f} -> mass {mm:.4f}  "
              f"({frac:.1%} of random order-5 g lie below)")
    print(
        "\nSo g's graph carries about 0.026 of the plaintext bigram mass, below the 0.0345"
        "\nan unrelated graph would carry: g's arcs avoid common adjacencies slightly. The"
        "\none-sigma interval spans the 16th to the 60th percentile of random order-5"
        "\npermutations, which is about 1.2 bits -- modest, and the first measurement of"
        "\ng's GRAPH rather than its cycle count."
    )


if __name__ == "__main__":
    main()
