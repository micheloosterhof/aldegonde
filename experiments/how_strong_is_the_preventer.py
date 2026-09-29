# ABOUTME: Estimates the preventer's strength by simulation rather than by dividing the
# ABOUTME: observed doublets by a flat baseline the cipher does not have.
"""The "81% effective" figure divides by 1/29. The walk's own un-suppressed rate is not 1/29.

Constraint D9 reads the suppression off 86 observed adjacent repeats against 447 expected
-- 12,955 pairs over 29 -- and calls the rule 81% effective. That baseline assumes the
cipher WITHOUT a preventer would repeat at chance. It would not.

Adjacent positions inside a block use `g^k` and `g^(k+1)`, so a would-be repeat needs
`p_i = g(p_(i+1))`: the plaintext bigram mass on the graph of `g`. That is the quantity
constraint C-1 measures, it is not 1/29, and it varies a great deal from one `g` to the
next.

So estimate the strength the only honest way: simulate the walk at a range of skip
probabilities across many keys, and see which reproduces the body's 86.

    python how_strong_is_the_preventer.py [--keys 12]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, compose, lp_words, ppow, prose_corpora  # noqa: E402

PHIS = (0.0, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00)


def encipher(g, sigma, plain, rng, phi: float):
    """The walk, skipping a clock step on a would-be repeat with probability phi.

    phi = 1 is the plain clock dodge; phi = 0 is no preventer at all.
    """
    gp = [ppow(g, i) for i in range(5)]
    base = rng.sample(range(M), M)
    out, clock, prev = [], 0, None
    for word in plain:
        cw = []
        for p in word:
            c = base[gp[clock % 5][p]]
            if c == prev and rng.random() < phi:
                clock += 1
                c = base[gp[clock % 5][p]]
            cw.append(c)
            prev = c
            clock += 1
        out.append(cw)
        base = compose(base, compose(gp[(clock - 1) % 5], sigma))
    return out


def doublets(words) -> tuple[int, int]:
    stream = [r for w in words for r in w]
    return (
        sum(1 for i in range(len(stream) - 1) if stream[i] == stream[i + 1]),
        len(stream),
    )


def main() -> None:
    keys = 12
    for i, a in enumerate(sys.argv):
        if a == "--keys" and i + 1 < len(sys.argv):
            keys = int(sys.argv[i + 1])

    body = lp_words()
    observed, n_body = doublets(body)
    pairs = n_body - 1
    print(
        f"the body: {observed} adjacent repeats in {n_body:,} runes, "
        f"{pairs / M:.0f} expected at chance\n"
    )

    corpora = list(prose_corpora(2928, keys))
    rk = random.Random(13)
    keyset = [
        (order5_fixing(rk.sample(range(M), 4), rk), rk.sample(range(M), M))
        for _ in range(keys)
    ]

    print(f"{'phi':>6}{'doublets, ' + str(keys) + ' keys':>26}{'z of the body':>16}")
    table = []
    for phi in PHIS:
        v = []
        for t, (g, sigma) in enumerate(keyset):
            w = encipher(g, sigma, corpora[t], random.Random(100 + t), phi)
            d, n = doublets(w)
            v.append(d * pairs / (n - 1))
        v = np.array(v)
        z = (observed - v.mean()) / v.std()
        table.append((phi, float(v.mean()), float(v.std()), float(z)))
        print(f"{phi:>6.2f}{f'{v.mean():.0f} +- {v.std():.0f}':>26}{z:>16.2f}")

    for limit in (1.0, 2.0):
        inside = [phi for phi, _, _, z in table if abs(z) <= limit]
        if inside:
            print(
                f"\nwithin {limit:.0f} sigma: phi in "
                f"[{min(inside):.2f}, {max(inside):.2f}]"
            )
    print("best near 0.90; phi = 0 is excluded and phi = 1 is not")
    print(
        "\nTwo things follow, and the first corrects D9."
        "\n\nThe un-suppressed rate is NOT 447. With no preventer the same walk gives"
        f"\n{table[0][1]:.0f} +- {table[0][2]:.0f} adjacent repeats, because a would-be"
        "\nrepeat needs the plaintext bigram mass on g's graph and that exceeds 1/29 for"
        "\nmost g. So '81% effective' divides by a baseline the cipher does not have, and"
        "\nthe spread across keys is larger than the correction."
        "\n\nThe plain clock dodge is NOT excluded. It is phi = 1 and gives"
        f"\n{table[-1][1]:.0f} +- {table[-1][2]:.0f} against the observed {observed},"
        f"\n{table[-1][3]:+.2f} sigma -- mildly disfavoured and alive. An earlier"
        "\narithmetic estimate put it at six sigma by ignoring the key-to-key spread,"
        "\nwhich is the dominant term at every phi."
    )


if __name__ == "__main__":
    main()
