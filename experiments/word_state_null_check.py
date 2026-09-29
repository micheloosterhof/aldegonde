# ABOUTME: Honest nulls for the bucketed word-state tests: empirical surrogate
# ABOUTME: spread instead of binomial z, and a register-realistic planted control.
"""Self-audit of word_state_sweep.py and its siblings.

Two methodological problems with what those scripts report:

1. BINOMIAL VARIANCE IS WRONG. Pooled coincidence counts sum over C(n,2) pairs
   that SHARE runes, so the pairs are not independent and the true variance
   exceeds the binomial. Every |z| quoted from those scripts is therefore
   inflated. The fix is an empirical null: run the identical statistic over
   doublet-preserving surrogates and use their spread.

2. THE PLANTED CONTROLS USED UNREALISTIC PLAINTEXT. The synthetic plaintext was
   far more peaked than runeglish (nIoC up to 7.9 against ~1.75), so the
   reported detection z values overstate real-world power by roughly an order
   of magnitude. The fix is to plant against a runeglish-like unigram
   distribution.

This script redoes both properly. It does not change any verdict -- the cells
were either ~0 or enormous -- but the numbers should be quotable.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

from aldegonde.stats.nulls import doublet_shuffle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from word_state_sweep import N, load_rich, pooled  # noqa: E402

TARGET_NIOC = 1.75  # runeglish plaintext


def runeglish_weights() -> np.ndarray:
    """Unigram weights whose coincidence matches runeglish nIoC ~1.75."""
    lo, hi = 0.0, 4.0
    for _ in range(60):
        s = (lo + hi) / 2
        w = np.array([1.0 / (1 + k) ** s for k in range(N)])
        w /= w.sum()
        if (w @ w) * N < TARGET_NIOC:
            lo = s
        else:
            hi = s
    w = np.array([1.0 / (1 + k) ** ((lo + hi) / 2) for k in range(N)])
    return w / w.sum()


def keyset(a, state: str, mod: int, q: int, phase: str) -> np.ndarray:
    sv = {"w": a["w"], "A": a["A"], "A+w": a["A"] + a["w"], "A-w": a["A"] - a["w"]}[
        state
    ]
    pv = (a["j"] if phase == "reset" else a["i"]) % q
    return (sv % mod) * q + pv


def main() -> None:
    a = load_rich()
    stream = a["rune"]
    print(f"corpus {len(stream)} runes\n")

    cells = [
        ("w", 29, 5, "reset", "the 29-word disk"),
        ("A", 29, 5, "reset", "letter-clocked disk"),
        ("A+w", 46, 5, "cont", "sweep's strongest cell"),
        ("w", 29, 5, "cont", "29-disk, continuous phase"),
    ]

    # --- empirical null: doublet-preserving surrogates -----------------------
    rate = sum(1 for x, y in zip(stream, stream[1:]) if x == y) / (len(stream) - 1)
    resample = doublet_shuffle(rate)
    rng = random.Random(20260819)
    NS = 300
    surro = [np.asarray(resample(list(stream), rng), dtype=np.int64) for _ in range(NS)]

    print(f"{'cell':<34} {'nIoC':>7} {'z_binom':>9} {'z_empir':>9}  {'ratio':>6}")
    for state, mod, q, phase, label in cells:
        keys = keyset(a, state, mod, q, phase)
        h, t = pooled(stream, keys)
        obs = h / t
        null = np.array([pooled(s, keys)[0] / t for s in surro])
        mu, sd = null.mean(), null.std()
        zb = (h - t / N) / math.sqrt(t * (1 / N) * (1 - 1 / N))
        ze = (obs - mu) / sd
        print(
            f"{label:<34} {obs * N:>7.3f} {zb:>+9.2f} {ze:>+9.2f}  {abs(zb / ze):>6.2f}x"
        )

    print(
        "\n  ratio = how much the binomial z overstates the honest empirical z.\n"
        "  Verdicts are unchanged (all cells sit at chance), but the inflated\n"
        "  figures should not be quoted."
    )

    # --- register-realistic planted control ---------------------------------
    print("\n--- planted control with runeglish-like plaintext ---")
    w = runeglish_weights()
    print(f"  planted plaintext nIoC = {(w @ w) * N:.3f} (target {TARGET_NIOC})")
    pool = np.random.default_rng(5)
    pt = pool.choice(N, size=len(stream), p=w)

    rnd = random.Random(3301)
    pts = list(range(N))
    rnd.shuffle(pts)
    g = list(range(N))
    for c in range(5):
        cyc = pts[5 * c : 5 * c + 5]
        for k in range(5):
            g[cyc[k]] = cyc[(k + 1) % 5]
    gp = [list(range(N))]
    for _ in range(4):
        gp.append([g[x] for x in gp[-1]])
    order = list(range(N))
    rnd.shuffle(order)
    disk = list(range(N))
    for k in range(N):
        disk[order[k]] = order[(k + 1) % N]
    dp = [list(range(N))]
    for _ in range(N - 1):
        dp.append([disk[x] for x in dp[-1]])

    st = a["w"] % 29
    ph = a["j"] % 5
    planted = np.array([dp[st[k]][gp[ph[k]][pt[k]]] for k in range(len(pt))])
    keys = keyset(a, "w", 29, 5, "reset")
    h, t = pooled(planted, keys)
    null = np.array([pooled(s, keys)[0] / t for s in surro])
    ze = (h / t - null.mean()) / null.std()
    print(
        f"  detected at the true cell: nIoC {h / t * N:.3f}   empirical z = {ze:+.1f}"
    )
    wrong = keyset(a, "w", 23, 5, "reset")
    h2, t2 = pooled(planted, wrong)
    null2 = np.array([pooled(s, wrong)[0] / t2 for s in surro])
    print(
        f"  at a wrong modulus 23:     nIoC {h2 / t2 * N:.3f}   "
        f"empirical z = {(h2 / t2 - null2.mean()) / null2.std():+.1f}"
    )
    print(
        "\n  With realistic plaintext the control still detects overwhelmingly,\n"
        "  so the negatives stand -- but the honest power figure is this one."
    )


if __name__ == "__main__":
    main()
