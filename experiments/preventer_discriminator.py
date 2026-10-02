# ABOUTME: Asks whether the battery can tell the three preventer shapes apart at all,
# ABOUTME: by scoring model against model instead of model against corpus.
"""Landing four cells is only evidence if something else fails them.

`models-on-the-informative-cells.md` now records the substitution preventer landing all
four reachable informative cells. That is the best result in the directory, and it is
worth exactly nothing until the obvious question is answered: **would the clock-dodging
shapes have landed them too?**

The battery has been run one way throughout -- model against corpus, cell by cell, asking
whether the corpus is a plausible draw. This runs it the other way. Generate corpora under
each preventer family, and for every cell measure how far apart the families sit:

    separation = |mean_A - mean_B| / pooled sd

A cell with separation near zero cannot distinguish the shapes whatever the corpus says.
A cell with large separation is a real discriminator, and then the corpus picks a side.

Three shapes, all of them the same walk with the same g and sigma, differing only in what
happens on a would-be repeat:

    dodge           re-run the clock                         (doublet-dodge-walk.md)
    probabilistic   re-run it with probability phi           (probabilistic-preventer.md)
    substitution    emit tau(c) instead                      (substitution-preventer)

The probabilistic phi is tuned so its doublet rate matches the substitution's, so the
comparison is at equal d1w and no cell separates them merely by construction.

Falsifiable either way. If cells separate, the 4-of-4 result selects a shape. If they do
not, the result is about the walk and says nothing about the preventer.

    python preventer_discriminator.py [--draws 60]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import generator as dodge_generator  # noqa: E402
from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    fingerprint,
    lp_words,
    prose_corpora,
)
from probabilistic_preventer import preventer as prob_preventer  # noqa: E402
from substitution_preventer import preventer as sub_preventer  # noqa: E402
from substitution_preventer import tau_fixing  # noqa: E402

REACHABLE = ("d1w", "seam", "doublet_gap_min", "d6w")


def sample(gen, draws: int, seed: int) -> list[dict[str, float]]:
    rng = random.Random(seed)
    return [fingerprint(gen(p, rng)) for p in prose_corpora(2928, draws)]


def column(sims, key) -> np.ndarray:
    v = np.array([s[key] for s in sims], dtype=float)
    return v[np.isfinite(v)]


def separation(a: np.ndarray, b: np.ndarray) -> float:
    """Standardised distance between two model distributions on one cell."""
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    if pooled < 1e-12:
        return 0.0 if abs(a.mean() - b.mean()) < 1e-12 else float("inf")
    return abs(a.mean() - b.mean()) / pooled


def tail(v: np.ndarray, x: float) -> float:
    """The battery's own empirical two-sided tail."""
    if len(v) == 0:
        return float("nan")
    below = float((v <= x).mean())
    t = 2 * min(below, 1 - below + 1 / len(v))
    if v.std() < 1e-12 and abs(v.mean() - x) < 1e-9:
        return 1.0
    return t


def tune_phi(g, sigma, target: float, draws: int) -> float:
    """The skip probability that reproduces a given doublet rate."""
    lo, hi = 0.0, 1.0
    for _ in range(8):
        mid = (lo + hi) / 2
        d1 = column(sample(prob_preventer(g, sigma, mid), draws, 5), "d1w").mean()
        if d1 > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main() -> None:
    draws = 60
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = fingerprint(lp_words())
    rng = random.Random(11)
    g = order5_fixing(rng.sample(range(M), 4), rng)
    sigma = rng.sample(range(M), M)
    tau = tau_fixing(rng.sample(range(M), 8), rng)

    sub = sample(sub_preventer(g, sigma, tau), draws, 3301)
    target = column(sub, "d1w").mean()
    phi = tune_phi(g, sigma, target, max(12, draws // 4))
    print(f"substitution d1w {target:.4f}; probabilistic tuned to phi = {phi:.3f}\n")

    models = {
        "substitution": sub,
        "probabilistic": sample(prob_preventer(g, sigma, phi), draws, 3301),
        "dodge": sample(dodge_generator(g, sigma), draws, 3301),
    }

    print(f"{draws} corpora per shape. Separation is |mean_A - mean_B| / pooled sd.\n")
    head = f"{'cell':<16}{'corpus':>10}"
    for name in models:
        head += f"{name[:9]:>11}"
    head += f"{'sep s-p':>9}{'sep s-d':>9}"
    print(head)
    rows = []
    for key in lp:
        cols = {n: column(s, key) for n, s in models.items()}
        if any(len(c) < 2 for c in cols.values()):
            continue
        sp = separation(cols["substitution"], cols["probabilistic"])
        sd = separation(cols["substitution"], cols["dodge"])
        line = f"{key:<16}{lp[key]:>10.4f}"
        for n in models:
            t = tail(cols[n], lp[key])
            mark = " " if t > 0.05 else "*"
            line += f"{cols[n].mean():>10.4f}{mark}"
        line += f"{sp:>9.2f}{sd:>9.2f}"
        print(line)
        rows.append((key, sp, sd))

    print("\n* = the corpus falls outside the model's 0.05 empirical tail.")

    disc = [(k, sp, sd) for k, sp, sd in rows if max(sp, sd) > 1.0]
    print(f"\ncells separating the shapes at sep > 1.0: {len(disc)} of {len(rows)}")
    for k, sp, sd in sorted(disc, key=lambda r: -max(r[1], r[2])):
        which = []
        if sp > 1.0:
            which.append(f"sub/prob {sp:.1f}")
        if sd > 1.0:
            which.append(f"sub/dodge {sd:.1f}")
        star = " (reachable informative)" if k in REACHABLE else ""
        print(f"  {k:<16} {', '.join(which)}{star}")

    among = [k for k, sp, sd in rows if k in REACHABLE and max(sp, sd) > 1.0]
    print(
        f"\nOf the four reachable informative cells, {len(among)} separate the shapes: "
        f"{', '.join(among) if among else 'none'}."
    )


if __name__ == "__main__":
    main()
