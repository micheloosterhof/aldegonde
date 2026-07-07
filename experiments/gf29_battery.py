#!/usr/bin/env python3
"""GF(29)* battery: the delta stream as the multiplicative group.

The nonzero deltas {1..28} are exactly GF(29)* (cyclic, order 28 = phi(29));
the suppressed value 0 is the one element that would break invertibility —
the doublet rule reads as group closure. In discrete-log coordinates
L[t] = dlog_2(delta[t]) in Z28, multiplicative structure becomes additive:

  - L mod 2  = Legendre symbol (quadratic residue character) of delta
  - L mod 4 / 7 / 14 = quartic / septic / half power-residue characters
  - linear functionals in L = monomial relations delta[t+d] * delta[t]^a
  - multiplicative lagged Fibonacci delta[t] = delta[t-a]*delta[t-b]
    = 3-term linear relation in L

IoC / kappa / contingency are relabeling-invariant and already covered by
the J battery; everything here is NOT relabeling-invariant and is new.
"""

import math
from collections import Counter

import numpy as np
from scipy.stats import chi2 as chi2_dist

from anomaly_scan import parse

N = 29
M = 28


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain], dtype=np.int64)
    n = len(cipher)

    delta = (cipher[1:] - cipher[:-1]) % N
    d = delta[delta != 0]
    # discrete log base 2 (primitive root mod 29)
    dl = np.zeros(N, dtype=np.int64)
    x = 1
    for k in range(M):
        dl[x] = k
        x = (x * 2) % N
    L = dl[d]
    nl = len(L)
    print(f"L stream (dlog of nonzero deltas): {nl} symbols in Z28")

    print("\n=== POWER-RESIDUE CHARACTERS ===")
    for mod, name in ((2, "Legendre (QR)"), (4, "quartic"), (7, "septic"),
                      (14, "half")):
        P_ = L % mod
        c = np.bincount(P_, minlength=mod)
        stat = ((c - nl / mod) ** 2 / (nl / mod)).sum()
        pm = chi2_dist.sf(stat, mod - 1)
        # kappa all shifts
        zmax, smax = 0.0, 0
        for s in range(1, nl // 2):
            m_ = nl - s
            hits = int(np.count_nonzero(P_[:-s] == P_[s:]))
            z = (hits - m_ / mod) / math.sqrt(m_ * (1 / mod) * (1 - 1 / mod))
            if abs(z) > abs(zmax):
                zmax, smax = z, s
        print(f"  L mod {mod:2d} ({name}): marginal chi2={stat:.1f} p={pm:.3f}; "
              f"kappa max |z|={zmax:+.2f} at shift {smax} "
              f"(exp max ~{math.sqrt(2 * math.log(nl // 2)):.1f})")
    # Legendre runs test
    q = (L % 2).astype(np.int64)
    runs = 1 + int(np.count_nonzero(q[1:] != q[:-1]))
    n1 = int(q.sum())
    n0 = nl - n1
    mu = 1 + 2 * n0 * n1 / nl
    var = 2 * n0 * n1 * (2 * n0 * n1 - nl) / (nl ** 2 * (nl - 1))
    print(f"  Legendre runs: {runs} (exp {mu:.0f}, z={(runs - mu) / math.sqrt(var):+.2f})")

    print("\n=== MONOMIAL FUNCTIONALS delta[t+d] * delta[t]^a ===")
    hits = []
    ntests = 0
    for dd in range(1, 21):
        x = L[:-dd]
        y = L[dd:]
        m_ = len(x)
        for a in range(1, M):
            f = (y + a * x) % M
            c = np.bincount(f, minlength=M)
            stat = ((c - m_ / M) ** 2 / (m_ / M)).sum()
            p = chi2_dist.sf(stat, M - 1)
            ntests += 1
            if p < 1e-4:
                hits.append((p, dd, a, stat))
    print(f"  {ntests} tests; significant at p<1e-4: "
          f"{[(dd, a, round(s,1)) for p, dd, a, s in sorted(hits)] if hits else 'none'}")

    print("\n=== MULTIPLICATIVE LAGGED-FIBONACCI (3-term in L) ===")
    worst = []
    ntests = 0
    for a_ in range(1, 13):
        for b_ in range(a_ + 1, 14):
            base = L[: nl - b_]
            xa = L[a_ : nl - b_ + a_]
            xb = L[b_:]
            m_ = len(base)
            for s1 in (1, M - 1):
                for s2 in (1, M - 1):
                    f = (base + s1 * xa + s2 * xb) % M
                    c = np.bincount(f, minlength=M)
                    stat = ((c - m_ / M) ** 2 / (m_ / M)).sum()
                    ntests += 1
                    worst.append((stat, a_, b_, s1, s2))
            worst.sort(reverse=True)
            worst = worst[:4]
    thresh = chi2_dist.isf(0.01 / ntests, M - 1)
    print(f"  {ntests} tests, Bonferroni chi2 threshold {thresh:.1f}")
    for stat, a_, b_, s1, s2 in worst:
        print(f"    lags ({a_},{b_}) signs ({'+' if s1==1 else '-'},"
              f"{'+' if s2==1 else '-'}): chi2={stat:.1f}"
              f"{' ***' if stat > thresh else ''}")

    print("\n=== DFT ON L (multiplicative characters x all frequencies) ===")
    peaks = []
    for mlt in range(1, M):
        x = np.exp(2j * np.pi * mlt * L / M)
        X = np.fft.fft(x)
        power = np.abs(X[1 : nl // 2]) ** 2 / nl
        t = int(np.argmax(power))
        peaks.append((float(power[t]), mlt, t + 1))
    peaks.sort(reverse=True)
    nbins = (M - 1) * (nl // 2 - 1)
    print(f"  threshold ~{math.log(nbins) + 3:.1f}; "
          f"top: {[(round(pw,1), mlt, f) for pw, mlt, f in peaks[:5]]}")

    print("\n=== POSITION FUNCTIONALS L[t] - a*t mod 28 (geometric keystreams) ===")
    idx = np.arange(nl)
    sig = []
    for a in range(1, M):
        f = (L - a * idx) % M
        c = np.bincount(f, minlength=M)
        stat = ((c - nl / M) ** 2 / (nl / M)).sum()
        p = chi2_dist.sf(stat, M - 1)
        if p < 1e-3:
            sig.append((p, a))
    print(f"  significant (p<1e-3 of 27): {sig if sig else 'none'}")


if __name__ == "__main__":
    main()
