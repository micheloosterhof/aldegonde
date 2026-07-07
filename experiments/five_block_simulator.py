#!/usr/bin/env python3
# ABOUTME: Generative simulator for the five-block boundary hypothesis with a
# ABOUTME: parameter grid search against the full LP statistical fingerprint.
"""Five-block boundary cipher simulator.

Implements the mechanism shape of `hypotheses/five-block-boundary.md`:

- The keystream is produced in rounds of ~5 values (lengths 4/5/6 with a
  drift probability, so boundaries have no fixed global phase).
- Within a round, consecutive ciphertext outputs are forced distinct
  (re-draw on would-be doublet); across round boundaries no constraint.
  This alone predicts the doublet rate (1/5)(1/29) parameter-free.
- After an emitted doublet, doublets are banned for the next 5 positions
  (dead time), matching the observed minimum gap of 6 and the ~18:1
  likelihood preference for a shifted-geometric gap law.
- Two candidate echo mechanisms for the lag-5 d1/d4 structure:
    qA: at a boundary, copy a random ADJACENT slot pair (j, j+1) of the
        previous round's keys into the new round (-> d1-shaped events);
    qB: copy the EDGE slots (first, last) (-> d4-shaped events);
    e:  on avoidance re-draw, emit C[i-5] when legal (output echo).

A grid search scores each parameter set against the observed fingerprint
(doublet rate, triplets, nIoC, mono kappa-5, d1..d5 pair counts).
"""

import importlib.util
import random
import statistics
from collections.abc import Callable

_spec = importlib.util.spec_from_file_location(
    "mf", "experiments/mechanism_fingerprint.py")
assert _spec is not None and _spec.loader is not None
mf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mf)

MOD = 29
i2r = mf.i2r
r2i = mf.r2i

TARGET = {"doublet%": 0.664, "triplets": 0.0, "nIoC": 1.000, "monoK5": 1.073,
          "d1": 29.0, "d2": 15.0, "d3": 14.0, "d4": 28.0}
# tolerances ~ sampling sd at corpus size
SCALE = {"doublet%": 0.09, "triplets": 1.0, "nIoC": 0.006, "monoK5": 0.035,
         "d1": 4.2, "d2": 4.2, "d3": 4.2, "d4": 4.2}


def make_five_block(qa: float, qb: float, e: float,
                    drift: float = 0.15) -> Callable[[str, list[int]], str]:
    """Five-block cipher with echo parameters qa, qb, e."""

    def enc(pt: str, wl: list[int]) -> str:
        out: list[str] = []
        prev_keys: list[int] = []
        keys: list[int] = []
        pos = 0
        dead = 0  # positions remaining with doublet ban after emitted doublet

        for ch in pt:
            if pos >= len(keys):
                # start a new round
                length = 5
                u = random.random()
                if u < drift / 2:
                    length = 4
                elif u < drift:
                    length = 6
                new = [random.randrange(MOD) for _ in range(length)]
                if prev_keys:
                    if random.random() < qa and min(length, len(prev_keys)) >= 2:
                        j = random.randrange(min(length, len(prev_keys)) - 1)
                        new[j] = prev_keys[j]
                        new[j + 1] = prev_keys[j + 1]
                    if random.random() < qb:
                        new[0] = prev_keys[0]
                        new[-1] = prev_keys[-1]
                prev_keys = keys if keys else new
                keys = new
                pos = 0
                boundary = True
            else:
                boundary = False

            p = r2i(ch)
            c = (p + keys[pos]) % MOD
            enforce = (not boundary) or dead > 0
            if enforce and out and i2r(c) == out[-1]:
                # avoidance: optional output echo, else re-draw key
                echoed = False
                if e > 0 and len(out) >= 5 and random.random() < e:
                    cand = r2i(out[-5])
                    if i2r(cand) != out[-1]:
                        c = cand
                        echoed = True
                if not echoed:
                    while True:
                        k = random.randrange(MOD)
                        c = (p + k) % MOD
                        if i2r(c) != out[-1]:
                            keys[pos] = k
                            break
            if out and i2r(c) == out[-1]:
                dead = 5
            elif dead > 0:
                dead -= 1
            out.append(i2r(c))
            pos += 1
        return "".join(out)

    return enc


def extended_fingerprint(s: str) -> dict[str, float]:
    """Standard fingerprint plus d5 and doublet positional checks."""
    fp: dict[str, float] = mf.fingerprint(s)
    n = len(s)
    mv = [s[i] == s[i + 5] for i in range(n - 5)]
    m = len(mv)
    fp["d5"] = sum(1 for i in range(m - 5) if mv[i] and mv[i + 5])
    dpos = [i for i in range(n - 1) if s[i] == s[i + 1]]
    gaps = [b - a for a, b in zip(dpos, dpos[1:])]
    fp["mingap"] = min(gaps) if gaps else 0
    return fp


def score(fp: dict[str, float]) -> float:
    """Weighted squared distance to the observed fingerprint."""
    return sum(((fp[k] - TARGET[k]) / SCALE[k]) ** 2 for k in TARGET)


def main() -> None:
    """Grid search the echo parameters against the LP fingerprint."""
    text, wlens = mf.load_corpus()
    gen = mf.build_markov()
    n = len(text)

    obs = extended_fingerprint(text)
    print("target (observed LP):", {k: round(v, 3) for k, v in obs.items()})

    grid_qa = [0.0, 0.25, 0.5, 1.0]
    grid_qb = [0.0, 0.25, 0.5, 1.0]
    grid_e = [0.0, 0.05, 0.1, 0.2]
    reps = 3
    results = []
    for qa in grid_qa:
        for qb in grid_qb:
            for e in grid_e:
                enc = make_five_block(qa, qb, e)
                fps = [extended_fingerprint(enc(gen(n), wlens))
                       for _ in range(reps)]
                avg = {k: statistics.mean(f[k] for f in fps) for k in fps[0]}
                results.append((score(avg), qa, qb, e, avg))
    results.sort(key=lambda x: x[0])

    print(f"\n{'qa':>4s} {'qb':>4s} {'e':>5s} {'scr':>6s} {'dbl%':>5s} "
          f"{'trip':>4s} {'nIoC':>6s} {'mK5':>5s} "
          f"{'d1':>4s} {'d2':>4s} {'d3':>4s} {'d4':>4s} {'d5':>4s} {'mgap':>4s}")
    for sc, qa, qb, e, a in results[:10]:
        print(f"{qa:4.2f} {qb:4.2f} {e:5.2f} {sc:6.1f} {a['doublet%']:5.2f} "
              f"{a['triplets']:4.1f} {a['nIoC']:6.3f} {a['monoK5']:5.3f} "
              f"{a['d1']:4.0f} {a['d2']:4.0f} {a['d3']:4.0f} {a['d4']:4.0f} "
              f"{a['d5']:4.0f} {a['mingap']:4.0f}")
    print("...worst 3:")
    for sc, qa, qb, e, a in results[-3:]:
        print(f"{qa:4.2f} {qb:4.2f} {e:5.2f} {sc:6.1f} {a['doublet%']:5.2f} "
              f"{a['triplets']:4.1f} {a['nIoC']:6.3f} {a['monoK5']:5.3f} "
              f"{a['d1']:4.0f} {a['d2']:4.0f} {a['d3']:4.0f} {a['d4']:4.0f} "
              f"{a['d5']:4.0f} {a['mingap']:4.0f}")

    # rerun the best setting with more reps for stable estimates
    sc, qa, qb, e, _ = results[0]
    enc = make_five_block(qa, qb, e)
    fps = [extended_fingerprint(enc(gen(n), wlens)) for _ in range(8)]
    avg = {k: statistics.mean(f[k] for f in fps) for k in fps[0]}
    sd = {k: statistics.stdev(f[k] for f in fps) for k in fps[0]}
    print(f"\nbest setting qa={qa} qb={qb} e={e}, 8 reps:")
    for k in ("doublet%", "triplets", "nIoC", "monoK5",
              "d1", "d2", "d3", "d4", "d5", "mingap"):
        tgt = obs.get(k, float("nan"))
        print(f"  {k:9s}: sim {avg[k]:7.3f} +/- {sd[k]:5.3f}   LP {tgt:7.3f}")


if __name__ == "__main__":
    main()
