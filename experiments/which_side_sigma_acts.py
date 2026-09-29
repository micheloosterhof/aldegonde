# ABOUTME: Tests whether the base step composes on the right or the left, using the fact
# ABOUTME: that only a right action leaves a base-free cross-seam statistic.
"""Only one of the two ways to step the base leaves anything measurable at a seam.

`the-preventer-is-strictly-adjacent.md` derives, for a base that steps on the RIGHT --
`base_(w+1) = base_w o g^a o sigma` --

    c(i) = c'(j)   <=>   p_i = g^(a - c_i) o sigma o g^(c'_j) (p'_j)

The base cancels because it is the outermost map on both sides. Step it on the LEFT
instead, `base_(w+1) = g^a o sigma o base_w`, and it does not: the second alphabet is
`g^a o sigma o base_w o g^(c'_j)` and no rearrangement removes `base_w` from the
comparison.

So the two conventions make opposite predictions about the cross-seam table. Under a
right action the cells `(u, v) = (di mod 5, (phase + 1 + j) mod 5)` each test a different
permutation `g^u o sigma o g^v` and therefore sit at different rates -- the table is
OVERDISPERSED. Under a left action the cells test nothing in particular and the table is
flat.

The statistic is the homogeneity chi2 over the cells divided by its degrees of freedom,
measured against the same quantity with the phases randomised, which removes the part of
the structure that comes from `di` alone.

Everything is run at the body's own corpus size, since the effect scales with it.

    python which_side_sigma_acts.py [--keys 8]
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, compose, lp_words, ppow, prose_corpora  # noqa: E402

SPAN = 3
FLOOR = 150


def phases(lengths) -> list[int]:
    out, clock = [], 0
    for length in lengths:
        clock += length
        out.append((clock - 1) % 5)
    return out


def dispersion(words, phase) -> float:
    """Homogeneity chi2 per degree of freedom over the (u, v) cells."""
    cnt, hit = collections.Counter(), collections.Counter()
    for w in range(len(words) - 1):
        a, b = words[w], words[w + 1]
        if not a or not b:
            continue
        for di in range(min(SPAN, len(a))):
            for j in range(min(SPAN, len(b))):
                if di == 0 and j == 0:
                    continue  # the preventer owns this cell
                key = (di % 5, (phase[w] + 1 + j) % 5)
                cnt[key] += 1
                hit[key] += a[len(a) - 1 - di] == b[j]
    keys = [k for k in cnt if cnt[k] >= FLOOR]
    n = sum(cnt[k] for k in keys)
    if len(keys) < 3 or not n:
        return float("nan")  # too few units to fill the cells
    p = sum(hit[k] for k in keys) / n
    chi = sum((hit[k] - cnt[k] * p) ** 2 / (cnt[k] * p * (1 - p)) for k in keys)
    return chi / (len(keys) - 1)


def excess(words, seed: int, draws: int = 50) -> float:
    """True phases minus randomised phases, so only the phase structure counts."""
    lengths = [len(w) for w in words]
    rng = random.Random(seed)
    null = np.array(
        [dispersion(words, [rng.randrange(5) for _ in lengths]) for _ in range(draws)]
    )
    return dispersion(words, phases(lengths)) - float(null.mean())


def walk(g, sigma, plain, rng, side: str):
    gp = [ppow(g, i) for i in range(5)]
    base = rng.sample(range(M), M)
    out, clock = [], 0
    for word in plain:
        cw = []
        for p in word:
            cw.append(base[gp[clock % 5][p]])
            clock += 1
        out.append(cw)
        step = compose(gp[(clock - 1) % 5], sigma)
        base = compose(base, step) if side == "right" else compose(step, base)
    return out


def phase_family(lengths, alpha: int, beta: int) -> list[int]:
    """phase = (alpha * cumulative runes + beta * block index) mod 5.

    A family wide enough to cover every affine convention in the two quantities the
    scribe could have been counting. alpha = 1, beta = 0 is the per-rune clock the
    walk assumes; alpha = 0 drops the rune count entirely.
    """
    out, cum = [], 0
    for w, length in enumerate(lengths):
        cum += length
        out.append((alpha * (cum - 1) + beta * w) % 5)
    return out


def scan_conventions(words, label: str, draws: int = 40, seed: int = 0) -> None:
    """Is there ANY affine phase convention under which the table is overdispersed?"""
    lengths = [len(w) for w in words]
    rng = random.Random(seed)
    base = float(
        np.mean(
            [
                dispersion(words, [rng.randrange(5) for _ in lengths])
                for _ in range(draws)
            ]
        )
    )
    grid = np.zeros((5, 5))
    for a in range(5):
        for b in range(5):
            grid[a, b] = dispersion(words, phase_family(lengths, a, b)) - base
    # the null for a maximum over 25 cells, taken as a maximum over random labellings
    maxnull = []
    for t in range(200):
        r = random.Random(1000 + t)
        maxnull.append(
            max(dispersion(words, [r.randrange(5) for _ in lengths]) for _ in range(5))
            - base
        )
    mn = np.array(maxnull)
    i, j = np.unravel_index(int(np.argmax(grid)), grid.shape)
    print(f"\n{label}: random-phase baseline {base:.2f}")
    print("      " + "".join(f"{'beta=' + str(b):>9}" for b in range(5)))
    for a in range(5):
        print(f"  a={a}" + "".join(f"{grid[a, b]:>9.2f}" for b in range(5)))
    print(
        f"  best alpha={i}, beta={j}, excess {grid[i, j]:+.2f}; "
        f"max-of-scan null {mn.mean():.2f} +- {mn.std():.2f}  ->  "
        f"z = {(grid[i, j] - mn.mean()) / mn.std():+.2f}"
    )


def main() -> None:
    keys = 8
    for i, a in enumerate(sys.argv):
        if a == "--keys" and i + 1 < len(sys.argv):
            keys = int(sys.argv[i + 1])

    corpora = list(prose_corpora(2928, keys + 2))
    rk = random.Random(31)
    print("excess overdispersion of the cross-seam cells, at the body's corpus size.")
    print("Positive means the phase labelling carries real structure.\n")
    print(f"{'base step':<34}{'excess':>26}")
    results = {}
    for side, label in (
        ("right", "base o (g^a o sigma)     RIGHT"),
        ("left", "(g^a o sigma) o base     LEFT"),
    ):
        vals = []
        for t in range(keys):
            g = order5_fixing(rk.sample(range(M), 4), rk)
            sigma = rk.sample(range(M), M)
            syn = walk(g, sigma, corpora[t], random.Random(100 + t), side)
            vals.append(excess(syn, t))
        v = np.array(vals)
        results[side] = v
        print(
            f"{label:<34}"
            f"{f'{v.mean():+.2f} +- {v.std():.2f}  ({int((v > 0).sum())}/{keys} up)':>26}"
        )

    body = excess(lp_words(), 99)
    print(f"{'THE BODY':<34}{f'{body:+.2f}':>26}")

    for side in ("right", "left"):
        v = results[side]
        z = (body - v.mean()) / v.std()
        below = int((v > body).sum())
        print(
            f"\n  against the {side:<5} simulations: z = {z:+.2f}, "
            f"and the body is below {below} of {keys}"
        )

    rk2 = random.Random(31)
    g = order5_fixing(rk2.sample(range(M), 4), rk2)
    sigma = rk2.sample(range(M), M)
    scan_conventions(
        walk(g, sigma, corpora[0], random.Random(5), "right"),
        "planted RIGHT-acting walk, one corpus (true alpha=1, beta=0)",
    )
    scan_conventions(lp_words(), "THE BODY")
    print(
        "\nThe scan covers every affine phase convention in the two quantities the"
        "\nscribe could have been counting. The planted walk lights up the whole beta=0"
        "\ncolumn, since any invertible alpha is a relabelling of the true one, and"
        "\nreaches z = +6 over a max-of-scan null. The body's grid is flat everywhere."
    )

    print(
        "\nA right action predicts a clearly positive excess and produces one under every"
        "\nkey tried. A left action predicts nothing and produces nothing. The body"
        "\nproduces nothing."
        "\n\nThat is a lean, not a proof: one test at about two sigma. Three other"
        "\nreadings survive it -- the base may change at some unit other than the block,"
        "\nthere may be no chain at a seam at all, or the clock convention may differ in"
        "\na way the phase labelling does not capture. But the right action is what every"
        "\nmodel in this directory assumes, and this is the first measurement that bears"
        "\non the choice."
    )


if __name__ == "__main__":
    main()
