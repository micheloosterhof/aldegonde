#!/usr/bin/env python3
# ABOUTME: Full within-word position-pair battery: match rate and conditional
# ABOUTME: structure for every pair of word positions (first vs second, first
# ABOUTME: vs third, ...), testing the walk's translation-invariance prediction.
"""Within-word position pairs: the (j, k) grid.

The distance profile (d1 suppressed, d2-d4 shoulder, d5 echo) pools over
absolute position. The walk predicts strictly more: c[j] =
base_w(g^(j mod 5)(p[j])), so a match between positions j and k depends
only on the g^(k-j)-diagonal — the same for every j. This battery tests
that translation invariance and the absence of conditional structure:

  A. match rate per position pair (j, k), j < k, all cells with enough
     samples, against doublet_shuffle surrogates overlaid with the real
     word structure;
  B. pooled per-distance rates (should reproduce the known profile);
  C. translation invariance: heterogeneity of the (j, k) cells within
     each distance (chi2 across j at fixed d, observed vs surrogates);
  D. conditional splits: mean nIoC of the rune at k grouped by the rune
     at j, per distance, vs surrogates.
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde.stats.nulls import doublet_shuffle  # noqa: E402, I001
from lp_corpus import load_clean  # noqa: E402

M = 29
MAXPOS = 10
TRIALS = 300
MIN_CELL = 150


def word_list(stream: list[int], wid: list[int]) -> list[list[int]]:
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    return [d[k] for k in sorted(d)]


def batteries(words: list[list[int]]):
    """Per-cell (j,k) matches/samples; per-distance conditional split."""
    m: Counter = Counter()
    s: Counter = Counter()
    cond: dict[int, dict[int, list[int]]] = {}
    for w in words:
        L = len(w)
        for j in range(min(L, MAXPOS)):
            for k in range(j + 1, min(L, MAXPOS)):
                s[(j, k)] += 1
                m[(j, k)] += w[j] == w[k]
                cond.setdefault(k - j, {}).setdefault(w[j], []).append(w[k])
    split = {}
    for d, groups in cond.items():
        vals = []
        for v in groups.values():
            n = len(v)
            if n < 20:
                continue
            c = Counter(v)
            vals.append(sum(x * (x - 1) for x in c.values())
                        / (n * (n - 1)) * M)
        if vals:
            split[d] = float(np.mean(vals))
    return m, s, split


def hetero(m: Counter, s: Counter) -> dict[int, float]:
    """Chi2 across cells within each distance (translation invariance)."""
    out = {}
    for d in range(1, MAXPOS):
        cells = [(m[(j, j + d)], s[(j, j + d)])
                 for j in range(MAXPOS - d) if s[(j, j + d)] >= MIN_CELL]
        tot_m = sum(c[0] for c in cells)
        tot_s = sum(c[1] for c in cells)
        if len(cells) < 2 or not tot_m:
            continue
        p = tot_m / tot_s
        out[d] = sum((mm - ss * p) ** 2 / (ss * p * (1 - p))
                     for mm, ss in cells)
    return out


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    words = word_list(stream, wid)
    dbl_rate = sum(1 for i in range(len(stream) - 1)
                   if stream[i] == stream[i + 1]) / (len(stream) - 1)
    null_model = doublet_shuffle(dbl_rate)

    obs_m, obs_s, obs_split = batteries(words)
    obs_het = hetero(obs_m, obs_s)

    null_cell: dict[tuple[int, int], list[int]] = {}
    null_split: dict[int, list[float]] = {}
    null_het: dict[int, list[float]] = {}
    for _ in range(TRIALS):
        surr = list(null_model(stream, rng))
        sw = word_list(surr, wid)
        nm, ns, nsp = batteries(sw)
        nh = hetero(nm, ns)
        for cell in obs_s:
            null_cell.setdefault(cell, []).append(nm[cell])
        for d, v in nsp.items():
            null_split.setdefault(d, []).append(v)
        for d, v in nh.items():
            null_het.setdefault(d, []).append(v)

    print(f"clean corpus, {len(words)} words; null = doublet_shuffle "
          f"({TRIALS} surrogates, real word structure)\n")

    print("A. match rate per position pair (1-based labels; cells with "
          f">= {MIN_CELL} samples; z vs surrogates):")
    print("  j\\k " + "".join(f"{k + 1:>7}" for k in range(1, MAXPOS)))
    for j in range(MAXPOS - 1):
        row = [f"{j + 1:>5}"]
        any_ = False
        for k in range(1, MAXPOS):
            if k <= j or obs_s.get((j, k), 0) < MIN_CELL:
                row.append(f"{'·':>7}")
                continue
            arr = np.array(null_cell[(j, k)])
            z = (obs_m[(j, k)] - arr.mean()) / arr.std()
            row.append(f"{z:>+7.1f}")
            any_ = True
        if any_:
            print(" ".join(row))

    print("\nB. pooled per-distance rate (known profile check):")
    for d in range(1, MAXPOS):
        mm = sum(obs_m[(j, j + d)] for j in range(MAXPOS - d))
        ss = sum(obs_s[(j, j + d)] for j in range(MAXPOS - d))
        if ss < MIN_CELL:
            continue
        arr = np.array([sum(null_cell[(j, j + d)][t]
                            for j in range(MAXPOS - d)
                            if (j, j + d) in null_cell)
                        for t in range(TRIALS)])
        print(f"  d={d}: {mm:>4}/{ss:>5} = {mm / ss:.4f}  "
              f"null {arr.mean() / ss:.4f}  z {(mm - arr.mean()) / arr.std():+6.2f}")

    print("\nC. translation invariance (chi2 across j at fixed d):")
    for d in sorted(obs_het):
        arr = np.array(null_het[d])
        o = obs_het[d]
        print(f"  d={d}: obs {o:6.2f}  null {arr.mean():6.2f} ± {arr.std():5.2f}"
              f"  z {(o - arr.mean()) / arr.std():+5.2f}  "
              f"p(hi) {float((arr >= o).mean()):.3f}")

    print("\nD. conditional split (mean nIoC of rune-at-k | rune-at-j) by d:")
    for d in sorted(obs_split):
        if d not in null_split:
            continue
        arr = np.array(null_split[d])
        o = obs_split[d]
        print(f"  d={d}: obs {o:.4f}  null {arr.mean():.4f} ± {arr.std():.4f}"
              f"  z {(o - arr.mean()) / arr.std():+5.2f}")


if __name__ == "__main__":
    main()
