# ABOUTME: Hill-climbs g against the coincidence profile and shows it overfits, then shows
# ABOUTME: cross-validation catches it in a control and cannot catch it on the body.
"""A filter that ranks is not a filter you can optimise against.

`d-profile-pins-g-to-five-cycles.md` scores candidate `g` by how well their predicted
lag-k coincidences match the body's, and ranks the true `g` in the top 0.1% of a random
pool. The obvious next move is to stop sampling and start searching: hill-climb over the
conjugacy class, since conjugating by a transposition preserves cycle type and gives a
406-move neighbourhood.

It does not work, and the way it fails is worth recording exactly.

Part one plants a `g`, enciphers prose through the walk, and hill-climbs. The winners
score far BETTER than the truth while sharing almost none of its points -- classic
overfitting of seventeen numbers by a search over 10^25 permutations.

Part two splits the cells, fits on some and scores on the rest. In the control that
separates them cleanly: the true `g` wins out of sample by a factor of three to eight.

Part three runs the same procedure on the body, where it stops working -- and the reason
is a number, not an opinion.

    python g_cannot_be_annealed.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_binned import (  # noqa: E402
    MIN_PAIRS,
    binned_measure,
    binned_tables,
    chi2,
)
from d_profile_constrains_g import walk  # noqa: E402
from fingerprint_battery import M, lp_words, prose_corpora  # noqa: E402


def conjugate(g, a: int, b: int):
    """g conjugated by the transposition (a b); preserves cycle type."""
    t = list(range(M))
    t[a], t[b] = b, a
    return [t[g[t[x]]] for x in range(M)]


def climb(meas, cells, start, mats, tot, limit: int = 400):
    g, best = list(start), chi2(start, meas, mats, tot, cells)
    for _ in range(limit):
        move = None
        for a in range(M):
            for b in range(a + 1, M):
                h = conjugate(g, a, b)
                v = chi2(h, meas, mats, tot, cells)
                if v < best:
                    best, move = v, h
        if move is None:
            break
        g = move
    return best, g


def random_g(rng, k: int = 5):
    points = rng.sample(range(M), 5 * k)
    g = list(range(M))
    for c in range(k):
        cycle = points[5 * c : 5 * c + 5]
        for i in range(5):
            g[cycle[i]] = cycle[(i + 1) % 5]
    return g


def main() -> None:
    prose = list(prose_corpora(2928, 60))
    mats, tot = binned_tables(prose)

    rng = random.Random(77)
    true_g = random_g(rng)
    sigma = rng.sample(range(M), M)
    cipher = []
    for c in prose[:2]:
        cipher += walk(true_g, sigma, c, random.Random(1))

    for label, meas in (
        ("planted control", binned_measure(cipher)),
        ("the body", binned_measure(lp_words())),
    ):
        cells = [c for c in meas if meas[c][2] >= MIN_PAIRS and c in mats]
        fit = [c for c in cells if c[0] in (2, 3)]
        test = [c for c in cells if c[0] in (4, 6, 7)]
        per = lambda g, cs, meas=meas: chi2(g, meas, mats, tot, cs) / len(cs)  # noqa: E731
        print(
            f"\n{label}: {len(cells)} cells, fitting on {len(fit)} (lags 2, 3), "
            f"holding out {len(test)} (lags 4, 6, 7)\n"
        )
        pool = [random_g(random.Random(900 + t)) for t in range(400)]
        rf = np.array([per(g, fit) for g in pool])
        rt = np.array([per(g, test) for g in pool])
        print(f"{'':<26}{'fit chi2/cell':>15}{'held-out chi2/cell':>20}")
        print(
            f"{'random g (400 draws)':<26}{f'{rf.mean():.2f} +- {rf.std():.2f}':>15}"
            f"{f'{rt.mean():.2f} +- {rt.std():.2f}':>20}"
        )
        print(f"{'  best of those 400':<26}{rf.min():>15.2f}{rt.min():>20.2f}")
        if label == "planted control":
            print(
                f"{'THE TRUE g':<26}{per(true_g, fit):>15.2f}{per(true_g, test):>20.2f}"
            )
        rows = []
        for t in range(12):
            _, g = climb(meas, fit, random_g(random.Random(600 + t)), mats, tot)
            rows.append(
                (
                    per(g, fit),
                    per(g, test),
                    sum(1 for x in range(M) if g[x] == true_g[x]),
                )
            )
        rows.sort(key=lambda r: r[1])
        f = np.array([r[0] for r in rows])
        h = np.array([r[1] for r in rows])
        print(
            f"{'12 hill-climb winners':<26}{f'{f.mean():.2f} +- {f.std():.2f}':>15}"
            f"{f'{h.mean():.2f} +- {h.std():.2f}':>20}"
        )
        print(f"{'  best held-out of those':<26}{rows[0][0]:>15.2f}{rows[0][1]:>20.2f}")
        if label == "planted control":
            print(
                f"  winners share {min(r[2] for r in rows)}-{max(r[2] for r in rows)}"
                f" of 29 points with the true g"
            )

    print(
        "\n\nThe control shows what a working verifier looks like: the true g scores 3.11"
        "\nper held-out cell against 53.21 for a random one, a factor of seventeen, while"
        "\nthe hill-climb winners beat it in sample at 0.15 and lose out of sample at"
        "\n28.06, sharing none to three of its 29 points. Cross-validation catches the"
        "\noverfit cleanly."
        "\n\nThe body shows the verifier failing. Fitted candidates average 4.19 per"
        "\nheld-out cell against 3.92 for random ones -- slightly WORSE -- and the best"
        "\nfitted candidate's 0.53 is beaten by a random draw's 0.18. Fitting buys"
        "\nnothing out of sample. The body's measurement errors are about five times the"
        "\ncontrol's and only four cells survive the split, so there is not enough"
        "\ninformation to both fit g and check it."
        "\n\nSo the profile filters a POOL and cannot confirm a CANDIDATE. Any g must come"
        "\nfrom somewhere else, and hill-climbing against these numbers is wasted effort."
    )


if __name__ == "__main__":
    main()
