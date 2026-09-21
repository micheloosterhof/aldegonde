# ABOUTME: Scores the live models on the five battery cells that actually discriminate,
# ABOUTME: instead of on a tally that a wrong cipher matches.
"""The battery has five informative cells. This is the comparison they support.

`battery-cell-counts-are-not-evidence.md` calibrates the fingerprint battery against three
deliberately wrong ciphers and finds that twelve of its nineteen cells are passed by
anything polyalphabetic -- twelve being exactly what the live models report for
themselves. Five cells are failed by every wrong model:

    d1w               within-word doublet rate
    seam              doublet rate across a word boundary
    doublet_gap_min   minimum gap between doublets
    d6w               distance-6 within-word coincidence
    returns           state returns

Three of the five are about repeats. So the comparison worth making is on those, and it
has never been made: the files report tallies over all nineteen.

Two live models are scored here against the two wrong ones. The plain walk carries a
per-word base stepping by g^a o sigma with a letter step of order 5 and NO doublet rule;
the dodge adds one rule, skipping an extra clock step whenever the emission would repeat.

    python informative_cell_comparison.py [--draws 60]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from battery_null_calibration import per_rune, per_word  # noqa: E402
from doublet_dodge_walk import encipher as dodge_encipher  # noqa: E402
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
DODGE_KEEP = [3, 16, 21, 26]  # lands all five cells in dodge_three_cells.py


def plain_walk(g, sigma):
    """The walk with no doublet rule: base per word, letter step of order 5."""

    def generate(plain, rng):
        gp = [ppow(g, k) for k in range(5)]
        base = rng.sample(range(M), M)
        out = []
        clock = 0
        for word in plain:
            cw = []
            for p in word:
                cw.append(base[gp[clock % 5][p]])
                clock += 1
            out.append(cw)
            base = compose(base, compose(gp[(clock - 1) % 5], sigma))
        return out

    return generate


def dodge_walk(g, sigma):
    def generate(plain, rng):
        return dodge_encipher(plain, rng.sample(range(M), M), g, sigma)

    return generate


def score(gen, lp, draws: int):
    rng = random.Random(3301)
    sims = [fingerprint(gen(plain, rng)) for plain in prose_corpora(2928, draws)]
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
    rng = random.Random(11)
    g_plain = order5_fixing(rng.sample(range(M), 4), rng)
    sigma = rng.sample(range(M), M)
    g_dodge = order5_fixing(DODGE_KEEP, rng)

    models = [
        ("independent alphabet per rune", per_rune),
        ("one random alphabet per word", per_word),
        ("plain walk, no doublet rule", plain_walk(g_plain, sigma)),
        ("doublet-dodging walk", dodge_walk(g_dodge, rng.sample(range(M), M))),
    ]
    print(f"the five informative cells, {draws} prose corpora each")
    print(f"{'corpus':<32}" + "".join(f"{k:>18}" for k in INFORMATIVE))
    print(f"{'':<32}" + "".join(f"{lp[k]:>18.4f}" for k in INFORMATIVE))
    for name, gen in models:
        res = score(gen, lp, draws)
        cells = "".join(
            f"{res[k][0]:>12.4f}{'  ok' if res[k][1] > 0.05 else ' MISS'}"
            for k in INFORMATIVE
        )
        landed = sum(1 for k in INFORMATIVE if res[k][1] > 0.05)
        print(f"{name:<32}{cells}   {landed}/5")
    print(
        "\nA tally over all nineteen cells cannot separate these; on the five that"
        "\ndiscriminate, it can."
    )


if __name__ == "__main__":
    main()
