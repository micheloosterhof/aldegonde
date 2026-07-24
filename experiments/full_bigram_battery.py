#!/usr/bin/env python3
# ABOUTME: Complete 29x29 adjacent-bigram battery on the clean corpus against
# ABOUTME: the doublet-suppression-aware null: matrix flatness, cell extremes,
# ABOUTME: antisymmetry, within/cross-word homogeneity, splits, phase strata.
"""Full bigram analysis of the clean corpus.

The adjacency matrix has one known structure (the suppressed diagonal, 86
vs 447) and three documented artifact traps (bigram IoC, trigram repeats,
isomorphs, seam pair-IoC) from testing density statistics against
suppression-blind nulls. This battery tests everything against the
library's doublet_shuffle null at the observed rate, overlaying the real
word-length structure on each surrogate so within/cross-word statistics
are honest:

  A. off-diagonal flatness: chi2 and max/min per-cell z (extremes judged
     against the null's own max/min distribution).
  B. direction: antisymmetry M[a][b] vs M[b][a].
  C. boundary decomposition: are the within-word and cross-word bigram
     matrices the same distribution (chi2 homogeneity)?
  D. successor/predecessor conditional splits: nIoC per conditioning
     rune (the depth-1 split, doublet-aware).
  E. phase stratification: bigram matrix homogeneity across within-word
     adjacency positions (pairs starting at j = 0,1,2,3,4+).
  F. record: top and bottom cells for reference.

Walk prediction: nothing anywhere — the adjacent relation collapses to
the tuned g-diagonal (equality only); off-diagonal cells see a fresh
permutation per word and per phase.
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

from aldegonde.stats.nulls import doublet_shuffle
from lp_corpus import ALPHABET, load_clean

M = 29
TRIALS = 400


def stats(stream: list[int], wid: list[int], pos: list[int]):
    n = len(stream)
    mat = np.zeros((M, M))
    within = np.zeros((M, M))
    cross = np.zeros((M, M))
    phase = [np.zeros((M, M)) for _ in range(5)]
    for i in range(n - 1):
        a, b = stream[i], stream[i + 1]
        mat[a][b] += 1
        if wid[i] == wid[i + 1]:
            within[a][b] += 1
            phase[min(pos[i], 4)][a][b] += 1
        else:
            cross[a][b] += 1

    row = mat.sum(1)
    col = mat.sum(0)
    tot = mat.sum()
    off = ~np.eye(M, dtype=bool)
    # off-diagonal expectation from marginals, renormalized off-diagonal
    e = np.outer(row, col) / tot
    scale = mat[off].sum() / e[off].sum()
    e_off = e * scale
    z = (mat - e_off) / np.sqrt(e_off)
    chi2_off = float((z[off] ** 2).sum())
    zmax, zmin = float(z[off].max()), float(z[off].min())

    anti = 0.0
    for a in range(M):
        for b in range(a + 1, M):
            s = mat[a][b] + mat[b][a]
            if s:
                anti += (mat[a][b] - mat[b][a]) ** 2 / s
    # within vs cross homogeneity (off-diagonal cells with enough mass)
    wsum, csum = within[off].sum(), cross[off].sum()
    exp_pair = (within + cross) * 0
    hom = 0.0
    for a in range(M):
        for b in range(M):
            if a == b:
                continue
            t = within[a][b] + cross[a][b]
            if t < 5:
                continue
            ew, ec = t * wsum / (wsum + csum), t * csum / (wsum + csum)
            hom += (within[a][b] - ew) ** 2 / ew + (cross[a][b] - ec) ** 2 / ec

    def split_mean(axis: int) -> float:
        vals = []
        for r in range(M):
            v = mat[r] if axis == 0 else mat[:, r]
            nn = v.sum()
            if nn < 20:
                continue
            vals.append(float((v * (v - 1)).sum() / (nn * (nn - 1)) * M))
        return float(np.mean(vals))

    # phase homogeneity: each phase matrix vs pooled within matrix
    ph = 0.0
    pooled = within
    psum = pooled.sum()
    for p in range(5):
        s = phase[p].sum()
        if not s:
            continue
        for a in range(M):
            for b in range(M):
                ep = pooled[a][b] * s / psum
                if ep >= 3:
                    ph += (phase[p][a][b] - ep) ** 2 / ep
    return (chi2_off, zmax, zmin, anti, hom, split_mean(0), split_mean(1),
            ph, mat)


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    pos = []
    last = None
    p = 0
    for w in wid:
        p = p + 1 if w == last else 0
        last = w
        pos.append(p)
    dbl_rate = sum(1 for i in range(len(stream) - 1)
                   if stream[i] == stream[i + 1]) / (len(stream) - 1)
    null_model = doublet_shuffle(dbl_rate)

    obs = stats(stream, wid, pos)
    names = ("off-diag chi2 (812 cells)", "max cell z", "min cell z",
             "antisymmetry chi2", "within-vs-cross homogeneity chi2",
             "mean successor split nIoC", "mean predecessor split nIoC",
             "phase homogeneity chi2")
    null_vals = [[] for _ in names]
    for _ in range(TRIALS):
        surr = list(null_model(stream, rng))
        s = stats(surr, wid, pos)
        for k in range(len(names)):
            null_vals[k].append(s[k])

    print(f"clean corpus: {len(stream)} runes, doublet rate {dbl_rate:.4f}; "
          f"null = doublet_shuffle at that rate, {TRIALS} surrogates, real "
          f"word structure overlaid\n")
    for k, name in enumerate(names):
        arr = np.array(null_vals[k])
        o = obs[k]
        z = (o - arr.mean()) / arr.std()
        p_hi = float((arr >= o).mean())
        p_lo = float((arr <= o).mean())
        print(f"  {name:<34} obs {o:>9.3f}  null {arr.mean():>9.3f} "
              f"± {arr.std():>7.3f}  z {z:+5.2f}  p(hi/lo) "
              f"{p_hi:.3f}/{p_lo:.3f}")

    mat = obs[-1]
    off_cells = [(int(mat[a][b]), a, b) for a in range(M) for b in range(M)
                 if a != b]
    off_cells.sort(reverse=True)
    fmt = lambda c: f"{ALPHABET[c[1]]}{ALPHABET[c[2]]}={c[0]}"
    print(f"\n  top cells: {', '.join(fmt(c) for c in off_cells[:5])} "
          f"(uniform expectation {12955 / 841:.1f})")
    print(f"  bottom cells: {', '.join(fmt(c) for c in off_cells[-5:])}")


if __name__ == "__main__":
    main()
