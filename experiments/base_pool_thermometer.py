# ABOUTME: Reads the size of the base pool off the two word-repeat counts, and shows that
# ABOUTME: the corpus's `identical` and `returns` point at pools an order of magnitude apart.
"""Two counts in the corpus measure the same quantity and disagree.

A cipher that draws its word alphabet from a pool of N produces repeated ciphertext
words when the plaintext word and the alphabet both recur. Both battery cells count
that event at different resolutions:

    identical   pairs of equal words of 3 runes or more          corpus: 17
    returns     pairs of equal two-word phrases, 6 runes or more corpus:  1

Both fall as N grows, at different rates, so each reads off a pool size. If the cipher
is a single walk they must agree. `dju-bei-stands-alone.md` records the qualitative
tension -- one long repeat, no short companions -- and this puts a number on it.

The method is a calibration curve, not a model fit: generate corpora at a ladder of
pool sizes, take the median of each count, and invert. Errors come from the spread at
each rung, so a count that is a single event gets an honestly wide interval.

    python base_pool_thermometer.py [--draws 40]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import recurrence_counts  # noqa: E402
from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, lp_words, ppow, prose_corpora  # noqa: E402

LADDER = (29, 60, 100, 200, 300, 500, 800, 1300, 2000, 2928)


def pooled_cipher(g, period: int):
    """One alphabet per word drawn from a closed pool of `period` permutations."""

    def generate(plain, rng):
        gp = [ppow(g, k) for k in range(5)]
        pool = [rng.sample(range(M), M) for _ in range(period)]
        order = [rng.randrange(period) for _ in plain]
        out, clock = [], 0
        for w, word in enumerate(plain):
            base = pool[order[w]]
            cw = []
            for p in word:
                cw.append(base[gp[clock % 5][p]])
                clock += 1
            out.append(cw)
        return out

    return generate


def invert(curve: dict[int, np.ndarray], value: float) -> tuple[float, float, float]:
    """Pool sizes whose median, 10th and 90th percentile cross `value`.

    Returned as (point, low, high) in pool units; the interval is wide wherever the
    count is small, which is the honest answer for a statistic of one event.
    """
    pools = sorted(curve)

    def cross(stat) -> float:
        ys = [stat(curve[p]) for p in pools]
        for i in range(len(pools) - 1):
            a, b = ys[i], ys[i + 1]
            if (a - value) * (b - value) <= 0 and abs(a - b) > 1e-12:
                t = (a - value) / (a - b)
                return pools[i] + t * (pools[i + 1] - pools[i])
        return float("inf") if ys[-1] > value else float(pools[0])

    point = cross(np.median)
    # a high count means a small pool, so the 90th percentile bounds the pool below
    return point, cross(lambda v: np.percentile(v, 90)), cross(
        lambda v: np.percentile(v, 10)
    )


def main() -> None:
    draws = 40
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = recurrence_counts(lp_words())
    corpora = list(prose_corpora(2928, draws))
    rng = random.Random(77)
    g = order5_fixing(rng.sample(range(M), 4), rng)

    print(f"corpus: identical {lp['identical']}, long {lp['long']}, "
          f"returns {lp['returns']}\n")
    print(f"{'pool':>7}{'identical':>22}{'returns':>20}")
    print(f"{'':>7}{'median [10th, 90th]':>22}{'median [10th, 90th]':>20}")
    curves: dict[str, dict[int, np.ndarray]] = {"identical": {}, "returns": {}}
    for period in LADDER:
        r = random.Random(3301)
        rows = [recurrence_counts(pooled_cipher(g, period)(p, r)) for p in corpora]
        for key in curves:
            v = np.array([row[key] for row in rows], float)
            curves[key][period] = v
        i_v, r_v = curves["identical"][period], curves["returns"][period]
        print(
            f"{period:>7}"
            f"{f'{np.median(i_v):.1f} [{np.percentile(i_v, 10):.0f}, {np.percentile(i_v, 90):.0f}]':>22}"
            f"{f'{np.median(r_v):.2f} [{np.percentile(r_v, 10):.0f}, {np.percentile(r_v, 90):.0f}]':>20}"
        )

    print("\nPool size implied by each count:")
    for key in ("identical", "returns"):
        point, low, high = invert(curves[key], lp[key])
        fmt = lambda x: "inf" if x == float("inf") else f"{x:,.0f}"  # noqa: E731
        print(f"  {key:<11} {lp[key]:>5.0f}  ->  pool {fmt(point)}  "
              f"[{fmt(low)}, {fmt(high)}]")

    print(
        "\nIf one walk produced the body, the two intervals must overlap. Where they do"
        "\nnot, either DJU-BEI is a chance ciphertext coincidence rather than a state"
        "\nreturn, or the base pool is not the same throughout the body."
    )


if __name__ == "__main__":
    main()
