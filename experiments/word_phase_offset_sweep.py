# ABOUTME: Sweeps "g^n in front of every word" -- every phase-offset rule
# ABOUTME: n_w = (a*cumulative_runes + b*word_index) mod 5, crossed with base period.
"""Michel's third variant. Suppose each word starts at a phase offset:

    c[w][j] = base_w . g^(n_w) . g^(j mod 5) (p[w][j])

If n_w is FREE it is unobservable -- it folds straight into base_w, which is
the reparametrisation length-clocked-walk.md already notes. It only becomes
testable when n_w is DETERMINED by a rule. The natural rules are accumulations
of a per-word increment: if word i advances the phase by (L_i + c), then

    n_w = (A_w + c*w) mod 5        A_w = cumulative runes before word w

so the whole family is n_w = (a*A_w + b*w) mod 5 with a, b in 0..4. Notable
members:

    (a=0, b=0)  phase resets every word     -> word_period_phase_ioc.py
    (a=1, b=0)  phase runs continuously     -> word_period_continuous_phase.py
    (a=1, b=4)  the walk's own absorber, n_w = sum(L_i - 1)
    (a=0, b=1)  phase advances one per word regardless of length

Total exponent for a rune is e = (n_w + j) mod 5, and two runes share an
alphabet iff they agree on (w mod P, e). Bucket by that and pool the
coincidence: a true (a, b, P) gives the plaintext rate, everything else 1/29.

25 rules x every base period, with a planted key to prove the sweep can find
a machine before its nulls are believed.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

N = 29
CHANCE = 1.0 / N


def geometry(word_id: list[int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-rune (word index, within-word position, cumulative runes before word)."""
    w = np.asarray(word_id, dtype=np.int64)
    nw = int(w[-1]) + 1
    lens = np.bincount(w, minlength=nw)
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
    j = np.arange(len(w)) - starts[w]
    return w, j, starts[w]


def pooled(codes: np.ndarray, keys: np.ndarray) -> tuple[int, int]:
    """Pooled within-bucket coincidence given per-rune bucket keys."""
    nb = int(keys.max()) + 1
    counts = np.bincount(keys * N + codes, minlength=nb * N)
    sizes = np.bincount(keys, minlength=nb)
    hits = int((counts * (counts - 1) // 2).sum())
    tot = int((sizes * (sizes - 1) // 2).sum())
    return hits, tot


def z(hits: int, tot: int, p: float) -> float:
    return (hits - tot * p) / math.sqrt(tot * p * (1 - p)) if tot else float("nan")


def sweep(
    stream: np.ndarray, w: np.ndarray, j: np.ndarray, aw: np.ndarray, periods
) -> list[tuple[float, int, int, int, int, int]]:
    out = []
    for a in range(5):
        for b in range(5):
            e = (a * aw + b * w + j) % 5
            for P in periods:
                keys = (w % P) * 5 + e
                h, t = pooled(stream, keys)
                if t < 3000:
                    continue
                out.append((z(h, t, CHANCE), a, b, P, h, t))
    out.sort(reverse=True)
    return out


def plant(lens: np.ndarray, a: int, b: int, P: int, rng: random.Random) -> np.ndarray:
    """Encipher iid plaintext with base=disk^(w mod P), phase n_w=(a*A_w+b*w)."""
    pts = list(range(N))
    rng.shuffle(pts)
    g = list(range(N))
    for c in range(5):
        cyc = pts[5 * c : 5 * c + 5]
        for t in range(5):
            g[cyc[t]] = cyc[(t + 1) % 5]
    gp = [list(range(N))]
    for _ in range(4):
        gp.append([g[x] for x in gp[-1]])
    order = list(range(N))
    rng.shuffle(order)
    disk = list(range(N))
    for t in range(N):
        disk[order[t]] = order[(t + 1) % N]
    dp = [list(range(N))]
    for _ in range(N - 1):
        dp.append([disk[x] for x in dp[-1]])
    weights = np.array([1.0 / (1 + k) ** 1.3 for k in range(N)])
    weights /= weights.sum()
    pool = np.random.default_rng(11)
    out = []
    A = 0
    for wi, L in enumerate(lens):
        n = (a * A + b * wi) % 5
        for jj in range(int(L)):
            p = int(pool.choice(N, p=weights))
            out.append(dp[wi % P][gp[(n + jj) % 5][p]])
        A += int(L)
    return np.array(out, dtype=np.int64)


def main() -> None:
    stream_l, word_id = load_clean()
    stream = np.asarray(stream_l, dtype=np.int64)
    w, j, aw = geometry(word_id)
    nw = int(w[-1]) + 1
    lens = np.bincount(w, minlength=nw)
    periods = list(range(2, 121))
    print(f"corpus: {len(stream)} runes, {nw} words")
    print(f"sweeping 25 phase rules x {len(periods)} periods; chance nIoC 1.000\n")

    # --- POSITIVE CONTROL ---------------------------------------------------
    TA, TB, TP = 1, 3, 17
    planted = plant(lens, TA, TB, TP, random.Random(3301))
    res = sweep(planted, w, j, aw, periods)
    zz, a, b, P, h, t = res[0]
    print(f"POSITIVE CONTROL: planted (a={TA}, b={TB}, P={TP})")
    print(f"  sweep top hit: (a={a}, b={b}, P={P})  nIoC {h / t * N:.3f}  z={zz:+.1f}")
    assert (a, b, P) == (TA, TB, TP), f"sweep found {(a, b, P)}, planted {(TA, TB, TP)}"
    print(f"  runner-up: {res[1][1:4]} z={res[1][0]:+.2f}  (should be nowhere near)")
    print("  -> the sweep localises a planted machine exactly\n")

    # --- THE LP -------------------------------------------------------------
    res = sweep(stream, w, j, aw, periods)
    print(f"THE LP: {len(res)} (rule, period) cells swept")
    print("  strongest 8 cells:")
    for zz, a, b, P, h, t in res[:8]:
        print(f"    a={a} b={b} P={P:>3}: nIoC {h / t * N:.3f}  z={zz:+5.2f}")
    mx = max(abs(r[0]) for r in res)
    exp = math.sqrt(2 * math.log(len(res)))
    print(f"\n  scan max |z| = {mx:.2f}; noise expects ~{exp:.2f} for {len(res)} cells")

    print("\n  named members, at P=29:")
    named = {
        (0, 0): "phase resets per word",
        (1, 0): "phase continuous",
        (1, 4): "the walk's own absorber",
        (0, 1): "one step per word",
    }
    for (a, b), label in named.items():
        for zz, aa, bb, P, h, t in res:
            if (aa, bb, P) == (a, b, 29):
                print(
                    f"    a={a} b={b}  {label:<26} nIoC {h / t * N:.3f}  z={zz:+5.2f}"
                )
                break

    best_any_p = {}
    for zz, a, b, P, h, t in res:
        if (a, b) not in best_any_p:
            best_any_p[(a, b)] = (zz, P, h, t)
    print("\n  best period for each rule (25 rules):")
    for (a, b), (zz, P, h, t) in sorted(best_any_p.items(), key=lambda kv: -kv[1][0])[
        :6
    ]:
        print(f"    a={a} b={b}: best P={P:>3}  nIoC {h / t * N:.3f}  z={zz:+5.2f}")


if __name__ == "__main__":
    main()
