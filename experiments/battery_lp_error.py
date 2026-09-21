# ABOUTME: Re-tests battery cells counting the LP's OWN sampling error, which
# ABOUTME: fingerprint_battery omits -- it treats the corpus value as exact.
"""How many battery misses survive the LP's own error bar?

`fingerprint_battery.compare` scores a cell by where the LP's value falls in the spread
of the MODEL over prose draws. That treats the corpus as exact. It is not: `d6w` rests
on 31 coincidences in 1,267 pairs, `identical` on 17 word pairs, `returns` on one event.

The LP is one sample of whatever produced it, so a fair test needs its sampling error
too, and each cell is re-tested against the combined spread:

    z = (model - LP) / sqrt(model_sd^2 + LP_sd^2)

**Where the LP's error comes from, and where it deliberately does not.** The coincidence
rates are binomial in their own pair counts, which this measures directly. The counting
cells are treated as Poisson in their own counts, which is approximate because the pairs
are not independent, but it is the right order and it is honest about one event being
worth +-1.

A moving-block bootstrap was tried first for all cells and is WRONG for the repeat
counters. Blocks are resampled with replacement, a duplicated block matches itself, and
every repeat statistic explodes: it put a spread of 179.6 on `returns`, whose LP value
is 1. `identical` read 176.8 and `long` 119.1. Those numbers are an artifact of the
method. The cells with no sound estimate here are reported as such rather than given a
number.

This is not a criticism of any single verdict. It changes the arithmetic for every model
scored in this directory, and it changes it most for the thinnest cells, which are the
ones the hypothesis files lean on hardest.

Run with no arguments.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from distance6_power import split_pairs  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import fingerprint, lp_words  # noqa: E402
from pure_quagmire_restart import matched_register  # noqa: E402
from quagmire_odometer import draw, encipher  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

MODEL_DRAWS = 40
COUNTS = ("triplets", "returns", "identical", "long")
# cells whose LP sampling error this script does not estimate: they are continuous
# functions of the whole corpus with no pair count to read an error off, and the block
# bootstrap that would give one manufactures repeats
NO_ESTIMATE = (
    "ioc",
    "entropy",
    "bigram_chi2",
    "kappa_max_z",
    "doublet_pos",
    "doublet_gap_min",
    "clock",
)


def lp_errors(words) -> dict[str, float]:
    """The LP's own sampling error per cell, by the route each cell admits."""
    out: dict[str, float] = {}
    cells = fingerprint(words)
    for d in range(1, 7):
        (hits, pairs), _cross = split_pairs(words, d)
        rate = hits / pairs
        out[f"d{d}w"] = math.sqrt(rate * (1 - rate) / pairs)
    # the seam is one trial per word boundary; d5x is the cross-word distance-5 pairs
    boundaries = len(words) - 1
    seam = cells["seam"]
    out["seam"] = math.sqrt(seam * (1 - seam) / boundaries)
    _within, (xhits, xpairs) = split_pairs(words, 5)
    xrate = xhits / xpairs if xpairs else 0.0
    out["d5x"] = math.sqrt(xrate * (1 - xrate) / xpairs) if xpairs else float("nan")
    for key in COUNTS:
        out[key] = math.sqrt(max(cells[key], 1.0))  # one event is worth +-1
    return out


def main() -> None:
    rng = random.Random(3301)
    lp = lp_words()
    cells = fingerprint(lp)
    errors = lp_errors(lp)

    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _t, _f = load_register(PROSE_CACHE)
    K, offsets, start = draw(rng)
    print(f"odometer model, {MODEL_DRAWS} draws on a length-matched register")
    print(f"schedule {offsets}, nothing fitted\n")
    model = [
        fingerprint(encipher(matched_register(rng, lens, pools), K, offsets, start))
        for _ in range(MODEL_DRAWS)
    ]

    print(
        f"{'cell':<16}{'LP':>10}{'LP sd':>9}{'model':>10}{'sd':>9}"
        f"{'z now':>8}{'z with LP':>11}   verdict"
    )
    flipped, still = [], []
    for key in cells:
        values = np.array([m[key] for m in model])
        mean, sd = float(values.mean()), float(values.std())
        old = (mean - cells[key]) / sd if sd > 1e-12 else float("nan")
        if key in NO_ESTIMATE:
            print(
                f"{key:<16}{cells[key]:>10.4f}{'--':>9}{mean:>10.4f}{sd:>9.4f}"
                f"{old:>8.2f}{'--':>11}   no LP error estimated"
            )
            continue
        lp_sd = errors[key]
        both = math.hypot(sd, lp_sd)
        new = (mean - cells[key]) / both if both > 1e-12 else 0.0
        was, now = abs(old) > 2, abs(new) > 2
        verdict = "miss" if now else ("was a miss, now lands" if was else "lands")
        (flipped if was and not now else still if now else []).append(key)
        print(
            f"{key:<16}{cells[key]:>10.4f}{lp_sd:>9.4f}{mean:>10.4f}{sd:>9.4f}"
            f"{old:>8.2f}{new:>11.2f}   {verdict}"
        )
    print(
        f"\nstop being misses once the LP's error counts: {', '.join(flipped) or 'none'}"
    )
    print(f"still misses: {', '.join(still) or 'none'}")
    assert errors["d6w"] > 0.003, (
        "d6w rests on 31 coincidences; its error bar must be large, which is the point"
    )


if __name__ == "__main__":
    main()
