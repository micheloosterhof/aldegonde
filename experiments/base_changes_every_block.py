# ABOUTME: Uses the cross-block lag-5 leak to show the base changes at essentially every
# ABOUTME: block edge, closing the reading that it changes at some larger unit.
"""If the base survived a block edge, the plaintext would leak straight across it.

`g` has order 5, so two runes five apart are enciphered by the same power of `g`. If they
also share a BASE they coincide at the plaintext rate; if the base changed between them
they coincide at chance. So the cross-block lag-5 rate is a direct readout of how often
the base survives an edge -- and it needs no key.

That matters because `the-base-step-may-act-on-the-left.md` leaves open the reading that
the base changes at some unit other than the block. If it changed only every N blocks, a
fraction (N-1)/N of edges would carry an unchanged base and the leak would show.

Two planted walks bracket the answer: one that steps the base at every block and one that
never does.

    python base_changes_every_block.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, compose, lp_words, ppow, prose_corpora  # noqa: E402

CHANCE = 1 / M


def rates(words, lag: int) -> tuple[tuple[float, float, int], tuple[float, float, int]]:
    """(within-block, across-an-edge) coincidence at a lag, with errors."""
    stream, owner = [], []
    for i, w in enumerate(words):
        for r in w:
            stream.append(r)
            owner.append(i)
    inside_h = inside_p = cross_h = cross_p = 0
    for i in range(len(stream) - lag):
        if owner[i] == owner[i + lag]:
            inside_p += 1
            inside_h += stream[i] == stream[i + lag]
        else:
            cross_p += 1
            cross_h += stream[i] == stream[i + lag]
    out = []
    for h, p in ((inside_h, inside_p), (cross_h, cross_p)):
        r = h / p
        out.append((r, math.sqrt(r * (1 - r) / p), p))
    return out[0], out[1]


def walk(g, sigma, plain, rng, change: bool):
    gp = [ppow(g, i) for i in range(5)]
    base = rng.sample(range(M), M)
    out, clock = [], 0
    for word in plain:
        cw = []
        for p in word:
            cw.append(base[gp[clock % 5][p]])
            clock += 1
        out.append(cw)
        if change:
            base = compose(base, compose(gp[(clock - 1) % 5], sigma))
    return out


def main() -> None:
    rk = random.Random(19)
    g = order5_fixing(rk.sample(range(M), 4), rk)
    sigma = rk.sample(range(M), M)
    plain = next(iter(prose_corpora(2928, 1)))

    print(f"lag-5 coincidence, within a block and across a block edge. "
          f"chance {CHANCE:.4f}\n")
    print(f"{'corpus':<38}{'within block':>22}{'across an edge':>24}")
    rows = {}
    for label, words in (
        ("planted walk, base steps every block", walk(g, sigma, plain,
                                                      random.Random(2), True)),
        ("planted walk, base never steps", walk(g, sigma, plain,
                                                random.Random(2), False)),
        ("THE BODY", lp_words()),
    ):
        inside, cross = rates(words, 5)
        rows[label] = cross
        print(f"{label:<38}"
              f"{f'{inside[0]:.4f} +- {inside[1]:.4f}':>22}"
              f"{f'{cross[0]:.4f} +- {cross[1]:.4f}':>24}")

    steps = rows["planted walk, base steps every block"]
    fixed = rows["planted walk, base never steps"]
    body = rows["THE BODY"]
    print(f"\nthe body against 'base steps every block': "
          f"z = {(body[0] - steps[0]) / math.sqrt(body[1] ** 2 + steps[1] ** 2):+.2f}")
    print(f"the body against 'base never steps':       "
          f"z = {(body[0] - fixed[0]) / math.sqrt(body[1] ** 2 + fixed[1] ** 2):+.2f}")

    leak = fixed[0] - steps[0]
    frac = (body[0] - steps[0]) / leak
    err = math.sqrt(body[1] ** 2 + steps[1] ** 2) / leak
    print(f"\nA surviving base leaks {leak:.4f} of coincidence. The body's excess over"
          f"\nthe stepping walk is {body[0] - steps[0]:+.4f}, so the fraction of edges"
          f"\nthat carry an unchanged base is {frac:+.3f} +- {err:.3f}, with a 95% upper"
          f"\nbound of {frac + 1.96 * err:.2f}.")
    print(
        "\nSo the base changes at essentially every block edge. A rule that stepped it"
        "\nonly every second block would leave half the edges unchanged and is excluded"
        "\nmany times over. The reading that the cipher's unit is larger than the block"
        "\n-- a phrase ending in a heavier mark, a line, a page -- is closed."
    )


if __name__ == "__main__":
    main()
