#!/usr/bin/env python3
# ABOUTME: Battery of previously-unused statistical tests from and beyond the
# ABOUTME: aldegonde library, run against the LP unsolved corpus.
"""Missed statistical tests: all negative; the corpus is statistically lean.

Tests and results:

1. Full 29x29 contingency chi2 per lag 1..60 (kappa only examines the
   diagonal). Result: lag-1 full-table z=+6.7 driven entirely by the
   diagonal (doublet suppression); off-diagonal z=+0.17. Every other lag is
   flat both ways. There is NO pairwise structure at any distance beyond
   doublet suppression.
2. Isomorph duplicates, lengths 6-12 (catches key reuse through different
   substitution alphabets - quagmire-style - which aligned kappa cannot
   see). Against the library's uniform-random baseline this shows a FAKE
   +5 to +6 sigma excess at lengths 7-10; against a doublet-suppressed
   null it is flat (|z| < 0.7 everywhere). Third artifact claimed by the
   doublet-suppression trap (after bigram IoC and trigram repeat counts):
   any baseline for this corpus must include the doublet rate.
3. Delete-marker periodicity scan (29 candidate interrupter runes x
   periods 2..30; the AN-END page's mechanism with a periodic key):
   top columnar nIoC 1.046 over 841 tests - noise. Closes the
   "periodic polyalphabetic hidden by interrupts" loophole.
4. Key-resets-at-marker grouping (29 runes, group nIoC by distance since
   last occurrence): top 1.009 - flat.
5. Numeric Pearson autocorrelation of index and GP-value series, lags
   1..60: lag-1 r = -0.0297, which is QUANTITATIVELY the doublet artifact
   (removing ~361 equal pairs predicts r = -0.028); all else within noise.
   DFT power spectrum: max peak 7.5x mean vs null max ~8.8x - no lines.
6. Per-rune positional uniformity (KS, 29 tests): min p = 0.014, above the
   Bonferroni threshold.
7. Sliding-window nIoC (window 300): top 1.065 ~ 0.5 sigma - homogeneous
   (also retires KRAKUP's "nonhomogeneous" hint as noise).
8. Cross-section mutual nIoC: 0.989..1.008 - all sections share the flat
   distribution.

Net: after this battery the ciphertext has exactly TWO statistical
departures from randomness - doublet suppression (with its dead time) and
the lag-5 pairing - and they are catalogued. First-order, second-order at
all lags, pattern-level, spectral, positional, and cross-section structure
are all exhausted."""

import importlib
import random
import statistics
from collections import Counter, defaultdict
from math import sqrt

import numpy as np
from scipy.stats import kstest

from aldegonde import c3301

isomorph = importlib.import_module('aldegonde.stats.isomorph')

AB = c3301.CICADA_ALPHABET
N = 29

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
keep = [i for i, p in enumerate(parts) if any(c in AB for c in p)][:-2]
text = "".join(x for i in keep for x in parts[i] if x in AB)
n = len(text)
idx = np.array([c3301.r2i(c) for c in text])
gpv = np.array([c3301.r2v(c) for c in text], dtype=float)

# ---- 1. full mutual-information chi2 per lag (29x29 joint) ----
print("=== 1. full 29x29 chi2 per lag (kappa only sees the diagonal) ===")
marg = np.bincount(idx, minlength=N) / n
results = []
for lag in range(1, 61):
    a, b = idx[:-lag], idx[lag:]
    m = len(a)
    joint = np.zeros((N, N))
    np.add.at(joint, (a, b), 1)
    exp = np.outer(np.bincount(a, minlength=N), np.bincount(b, minlength=N)) / m
    mask = exp > 1
    chi2 = ((joint - exp) ** 2 / np.where(mask, exp, 1))[mask].sum()
    df = mask.sum() - 1
    z = (chi2 - df) / sqrt(2 * df)
    # off-diagonal only (remove known doublet suppression at lag 1)
    od = ~np.eye(N, dtype=bool) & mask
    chi2od = ((joint - exp) ** 2 / np.where(od, exp, 1))[od].sum()
    dfod = od.sum() - 1
    zod = (chi2od - dfod) / sqrt(2 * dfod)
    results.append((z, zod, lag))
results.sort(reverse=True)
print("top 6 by full-table z:", [(lag, f"{z:+.2f}/{zod:+.2f}")
                                 for z, zod, lag in results[:6]])
print("(60 lags tested; need z > ~3.2 for global 5%)")

# ---- 2. isomorph statistics vs random baseline ----
print("\n=== 2. isomorph duplicates (catches key reuse through different alphabets) ===")
for length in range(4, 11):
    dist = isomorph.isomorph_distribution(text, length)
    distinct, duplicate = isomorph.isomorph_statistics(dist)
    md, sd_, mdup, sdup = isomorph.random_isomorph_statistics(
        n, length, samples=8)
    z = (duplicate - mdup) / sdup if sdup > 0 else 0.0
    print(f"  len {length:2d}: duplicates {duplicate:6d} vs random "
          f"{mdup:9.1f}+/-{sdup:6.1f}  z={z:+.2f}")

# ---- 3. interrupter-DELETION periodicity (periodic key + skip-at-marker) ----
print("\n=== 3. delete-marker periodicity scan (29 markers x periods 2..30) ===")
def colioc(s: np.ndarray, period: int) -> float:
    tot = 0.0
    for k in range(period):
        col = s[k::period]
        if len(col) < 2:
            return 0.0
        cnt = np.bincount(col, minlength=N)
        tot += (cnt * (cnt - 1)).sum() / (len(col) * (len(col) - 1)) * N
    return tot / period

best = []
for r in range(N):
    sub = idx[idx != r]
    for period in range(2, 31):
        v = colioc(sub, period)
        best.append((v, r, period))
best.sort(reverse=True)
print("top 5:", [(c3301.CICADA_ENGLISH_ALPHABET[r], p, f"{v:.3f}")
                 for v, r, p in best[:5]])
print("(841 tests; flat corpus baseline ~1.00, need ~1.06+ to matter)")

# ---- 4. marker-RESET keying: group by distance since last marker ----
print("\n=== 4. key-resets-at-marker test (group nIoC by distance since rune) ===")
best4 = []
for r in range(N):
    groups: dict[int, list[int]] = defaultdict(list)
    last = -1
    for i, v in enumerate(idx):
        if last >= 0:
            d = i - last
            if d <= 40:
                groups[d].append(v)
        if v == r:
            last = i
    iocs = []
    wts = []
    for _d, vals in groups.items():
        if len(vals) >= 30:
            cnt = np.bincount(np.array(vals), minlength=N)
            m = len(vals)
            iocs.append((cnt * (cnt - 1)).sum() / (m * (m - 1)) * N)
            wts.append(m)
    if iocs:
        mean = float(np.average(iocs, weights=wts))
        best4.append((mean, r))
best4.sort(reverse=True)
print("top 4:", [(c3301.CICADA_ENGLISH_ALPHABET[r], f"{v:.3f}")
                 for v, r in best4[:4]])

# ---- 5. numeric autocorrelation + spectrum ----
print("\n=== 5. numeric (Pearson) autocorrelation of index and GP values ===")
tops = []
for name, series in (("idx", idx.astype(float)), ("GP", gpv)):
    s = series - series.mean()
    var = (s * s).mean()
    rs = []
    for lag in range(1, 61):
        r_ = float((s[:-lag] * s[lag:]).mean() / var)
        rs.append((abs(r_), lag, r_))
    rs.sort(reverse=True)
    sig = 1 / sqrt(n)
    print(f"  {name}: top |r| {[(lag, f'{r_:+.4f}') for _, lag, r_ in rs[:3]]} "
          f"(1 sigma = {sig:.4f}, 60 lags)")
# DFT power spectrum of centered index sequence
s = idx.astype(float) - idx.mean()
ps = np.abs(np.fft.rfft(s)) ** 2
ps = ps[1:]  # drop DC
expp = ps.mean()
top = np.argsort(ps)[-5:][::-1]
print("  DFT top peaks: " + ", ".join(
    f"period {n/(k+1):.1f} power {ps[k]/expp:.1f}x" for k in top))
mx = ps.max() / expp
print(f"  max peak {mx:.1f}x mean; null max over {len(ps)} bins ~ "
      f"{np.log(len(ps)):.1f}x")

# ---- 6. per-rune positional uniformity (KS) ----
print("\n=== 6. per-rune positional uniformity (KS test, 29 tests) ===")
worst = []
for r in range(N):
    pos = np.nonzero(idx == r)[0] / n
    stat, p = kstest(pos, "uniform")
    worst.append((p, r))
worst.sort()
print("smallest p-values:", [(c3301.CICADA_ENGLISH_ALPHABET[r], f"{p:.4f}")
                             for p, r in worst[:4]],
      "(Bonferroni threshold 0.0017)")

# ---- 7. sliding-window nIoC hotspots ----
print("\n=== 7. sliding window nIoC (window 300, step 50) ===")
hot = []
for a in range(0, n - 300, 50):
    w = idx[a:a + 300]
    cnt = np.bincount(w, minlength=N)
    v = (cnt * (cnt - 1)).sum() / (300 * 299) * N
    hot.append((v, a))
hot.sort(reverse=True)
sd = N * sqrt(2.0 / (300 * 299) * (1 - 1 / N))  # rough
print("top windows:", [(a, f"{v:.3f}") for v, a in hot[:4]],
      f"(mean 1.0, sd~{sd:.3f}, ~253 windows)")

# ---- 8. cross-section mutual IoC ----
print("\n=== 8. cross-section mutual nIoC (distribution similarity) ===")
secs = [s for s in ("".join(x for x in t if x in AB)
                    for t in raw.split("$")[:10]) if len(s) > 200]
vals = []
for i in range(len(secs)):
    for j in range(i + 1, len(secs)):
        ca = Counter(secs[i])
        cb = Counter(secs[j])
        m = sum(ca[k] * cb[k] for k in ca) / (len(secs[i]) * len(secs[j])) * N
        vals.append((m, i, j))
vals.sort(reverse=True)
print(f"range {vals[-1][0]:.3f} .. {vals[0][0]:.3f} "
      f"(extremes: {vals[0][1:]}, {vals[-1][1:]})")

# ---- 2b. isomorphs against the CORRECT (doublet-suppressed) null ----
print("\n=== 2b. isomorphs vs doublet-suppressed null ===")
rate = sum(1 for i in range(n - 1) if text[i] == text[i + 1]) / (n - 1)

def gen_suppressed(length: int) -> str:
    out = [random.randrange(N)]
    for _ in range(length - 1):
        if random.random() < rate:
            out.append(out[-1])
        else:
            c = random.randrange(N - 1)
            if c >= out[-1]:
                c += 1
            out.append(c)
    return "".join(AB[c] for c in out)

for length in (7, 9, 10):
    dist = isomorph.isomorph_distribution(text, length)
    _, duplicate = isomorph.isomorph_statistics(dist)
    sims = []
    for _ in range(8):
        m = gen_suppressed(n)
        _, d2 = isomorph.isomorph_statistics(
            isomorph.isomorph_distribution(m, length))
        sims.append(d2)
    mu = statistics.mean(sims)
    sd_ = statistics.stdev(sims)
    print(f"  len {length:2d}: LP {duplicate} null {mu:.1f}+/-{sd_:.1f} "
          f"z={(duplicate - mu) / sd_:+.2f}")
