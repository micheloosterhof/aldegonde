#!/usr/bin/env python3
# ABOUTME: Systematic census of the seam channel — the (last rune of word w,
# ABOUTME: first rune of word w+1) bigram — against the word-order permutation
# ABOUTME: null: matrix flatness, repeats, conditional splits, length classes.
"""Seam bigram battery.

The 2,927 word seams each contribute one (c_last, c_first) bigram. The
walk predicts: at a seam, (c_last, c_first) = (psi(p_last),
psi(sigma(p_first))) under a common per-word permutation psi, so apart
from the suppressed diagonal (seam doublet iff p_last = sigma(p_first),
rate 0.0079) every seam statistic should be flat, and the diagonal rate
should be INDEPENDENT of the previous word's length class (the g and
length factors cancel). Anything non-flat here is new structure.

Tests (null = 2,000 permutations of word order, which preserves every
word-internal statistic and the last/first marginals but breaks seam
pairing):
  A. seam matrix: off-diagonal chi2, diagonal count.
  B. repeated seam bigrams: pair-distribution IoC and max cell count.
  C. conditional split: nIoC of first-runes grouped by the preceding
     last rune (and the reverse) — an English-like leak would show ~1.7.
  D. diagonal rate by previous-word length mod 5 (walk: flat).
  E. marginals: last-rune and first-rune uniformity.
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lp_corpus import load_clean

M = 29


def nioc(vals: list[int]) -> float:
    n = len(vals)
    if n < 2:
        return 1.0
    c = Counter(vals)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * M


def pair_ioc(pairs: list[tuple[int, int]]) -> float:
    n = len(pairs)
    c = Counter(pairs)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * M * M


def seam_stats(words: list[list[int]]):
    seams = [(words[i][-1], words[i + 1][0]) for i in range(len(words) - 1)]
    lasts = [a for a, _ in seams]
    firsts = [b for _, b in seams]
    diag = sum(1 for a, b in seams if a == b)
    # off-diagonal chi2
    mat = Counter(seams)
    off = [mat[(a, b)] for a in range(M) for b in range(M) if a != b]
    e = (len(seams) - diag) / (M * M - M)
    chi2_off = sum((o - e) ** 2 / e for o in off)
    pioc = pair_ioc(seams)
    maxcell = max(mat.values())
    # conditional splits
    by_last: dict[int, list[int]] = {}
    by_first: dict[int, list[int]] = {}
    for a, b in seams:
        by_last.setdefault(a, []).append(b)
        by_first.setdefault(b, []).append(a)

    def split(groups: dict[int, list[int]]) -> tuple[float, float]:
        vals = [nioc(v) for v in groups.values() if len(v) >= 20]
        return float(np.mean(vals)), float(np.max(vals))

    mean_fwd, max_fwd = split(by_last)
    mean_rev, max_rev = split(by_first)
    return (diag, chi2_off, pioc, maxcell, mean_fwd, max_fwd,
            mean_rev, max_rev, lasts, firsts)


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    words_d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        words_d.setdefault(w, []).append(stream[i])
    words = [words_d[k] for k in sorted(words_d)]

    (diag, chi2_off, pioc, maxcell, mean_fwd, max_fwd, mean_rev, max_rev,
     lasts, firsts) = seam_stats(words)
    nseams = len(words) - 1
    print(f"seams: {nseams}")

    # permutation null
    null = {k: [] for k in ("diag", "chi2", "pioc", "maxcell",
                            "mfwd", "xfwd", "mrev", "xrev")}
    perm = words[:]
    for _ in range(2000):
        rng.shuffle(perm)
        d, c2, pi, mx, mf, xf, mr, xr, _, _ = seam_stats(perm)
        for k, v in zip(null, (d, c2, pi, mx, mf, xf, mr, xr)):
            null[k].append(v)

    def rep(name: str, obs: float, key: str, note: str = "") -> None:
        arr = np.array(null[key])
        mu, sd = arr.mean(), arr.std()
        p_hi = float((arr >= obs).mean())
        p_lo = float((arr <= obs).mean())
        print(f"  {name:<38} obs {obs:>8.3f}  null {mu:8.3f} ± {sd:6.3f}  "
              f"z {(obs - mu) / sd:+5.2f}  p(hi/lo) {p_hi:.3f}/{p_lo:.3f}"
              f"  {note}")

    print("\nA/B. seam matrix vs word-order permutation null:")
    rep("diagonal (cross-word doublets)", diag, "diag",
        "(the seam suppression itself, vs random word pairing)")
    rep("off-diagonal chi2", chi2_off, "chi2")
    rep("pair-distribution IoC (x841)", pioc, "pioc")
    rep("max repeated seam bigram", maxcell, "maxcell")

    print("\nC. conditional splits (nIoC; English-like leak would be ~1.7):")
    rep("mean nIoC of first|last groups", mean_fwd, "mfwd")
    rep("max  nIoC of first|last groups", max_fwd, "xfwd")
    rep("mean nIoC of last|first groups", mean_rev, "mrev")
    rep("max  nIoC of last|first groups", max_rev, "xrev")

    print("\nD. seam diagonal rate by previous-word length mod 5 (walk: flat):")
    bylen: Counter = Counter()
    dbylen: Counter = Counter()
    for i in range(nseams):
        cls = (len(words[i]) - 1) % 5
        bylen[cls] += 1
        dbylen[cls] += words[i][-1] == words[i + 1][0]
    p0 = diag / nseams
    for cls in range(5):
        o, n_ = dbylen[cls], bylen[cls]
        sd = (n_ * p0 * (1 - p0)) ** 0.5
        print(f"  (L-1)%5={cls}: {o:>3}/{n_:>4} = {o / n_:.4f} "
              f"(z vs pooled {(o - n_ * p0) / sd:+.2f})")

    print("\nE. marginals:")
    for name, vals in (("last runes", lasts), ("first runes", firsts)):
        c = Counter(vals)
        e = len(vals) / M
        chi2 = sum((c[r] - e) ** 2 / e for r in range(M))
        print(f"  {name}: chi2 {chi2:.1f} (28 df, ~28 expected under uniform)")

    # F. review decomposition: what drives the pair-IoC lean — diagonal
    # deficit, marginal non-uniformity, or genuine off-diagonal clumping?
    def offdiag_pioc(ws: list[list[int]]) -> float:
        seams = [(ws[i][-1], ws[i + 1][0]) for i in range(len(ws) - 1)
                 if ws[i][-1] != ws[i + 1][0]]
        return pair_ioc(seams)

    obs_off = offdiag_pioc(words)
    null_off = []
    for _ in range(500):
        rng.shuffle(perm)
        null_off.append(offdiag_pioc(perm))
    arr = np.array(null_off)
    print("\nF. off-diagonal-only pair IoC (isolates clumping from the "
          "diagonal deficit):")
    print(f"  obs {obs_off:.4f}  null {arr.mean():.4f} ± {arr.std():.4f}  "
          f"z {(obs_off - arr.mean()) / arr.std():+.2f}")

    # G. deeper conditionals across the seam (d=2 reach in both directions)
    def cond_split(pairs: list[tuple[int, int]]) -> float:
        groups: dict[int, list[int]] = {}
        for a, b in pairs:
            groups.setdefault(a, []).append(b)
        vals = [nioc(v) for v in groups.values() if len(v) >= 20]
        return float(np.mean(vals))

    def deep_pairs(ws: list[list[int]]):
        p2f, l2s = [], []
        for i in range(len(ws) - 1):
            if len(ws[i]) >= 2:
                p2f.append((ws[i][-2], ws[i + 1][0]))
            if len(ws[i + 1]) >= 2:
                l2s.append((ws[i][-1], ws[i + 1][1]))
        return cond_split(p2f), cond_split(l2s)

    obs_p2f, obs_l2s = deep_pairs(words)
    n_p2f, n_l2s = [], []
    for _ in range(500):
        rng.shuffle(perm)
        a, b = deep_pairs(perm)
        n_p2f.append(a)
        n_l2s.append(b)
    for name, obs, arr in (("first | second-to-last", obs_p2f,
                            np.array(n_p2f)),
                           ("second | last", obs_l2s, np.array(n_l2s))):
        print(f"G. mean nIoC {name:<24} obs {obs:.4f}  "
              f"null {arr.mean():.4f} ± {arr.std():.4f}  "
              f"z {(obs - arr.mean()) / arr.std():+.2f}")


if __name__ == "__main__":
    main()
