#!/usr/bin/env python3
"""J-stream battery: the 28-symbol step stream as the inner cipher.

Model (EA-as-ditto): plaintext EA encrypts as "repeat previous ciphertext
rune"; every other plaintext rune encrypts as a keyed step J in the
28-symbol space of non-repeating moves:

    J[t] = (C[i] - C[i-1] - 1) mod 28   for non-doublet steps.

This relabeling is exactly the delta text of autokey-plus-substitution.md
restricted to its 28 live values. The new idea tested here: doublets are
key INTERRUPTERS — if EA consumes no key, deleting the doublet steps
re-aligns a periodic inner key, so periodicity tests must be run on the
COMPRESSED J stream (and, for the EA-consumes-key variant, on the raw
gapped stream). All tests are run in mod-28 arithmetic, plus mod-4 / mod-7
CRT projections (28 = 4 x 7), which no mod-29 test could see.
"""

import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2 as chi2_dist
from scipy.stats import chi2_contingency

from anomaly_scan import parse, ioc

N = 29
M = 28


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain], dtype=np.int64)
    n = len(cipher)

    delta = (cipher[1:] - cipher[:-1]) % N
    nondbl = delta != 0
    J = ((delta[nondbl] - 1) % M).astype(np.int64)  # compressed stream
    rawpos = np.where(nondbl)[0]  # original step index of each J symbol
    nj = len(J)
    print(f"J stream: {nj} symbols over Z{M} (deleted {int((~nondbl).sum())} doublet steps)")
    c = np.bincount(J, minlength=M)
    stat = ((c - nj / M) ** 2 / (nj / M)).sum()
    print(f"marginal: chi2={stat:.1f} p={chi2_dist.sf(stat, M - 1):.4f}, "
          f"nIoC={ioc(J.tolist()) * M:.4f}")

    print("\n=== KAPPA ON COMPRESSED J (EA consumes no key) ===")
    zs = []
    worst = []
    for s in range(1, nj // 2):
        m_ = nj - s
        hits = int(np.count_nonzero(J[:-s] == J[s:]))
        exp = m_ / M
        sd = math.sqrt(m_ * (1 / M) * (1 - 1 / M))
        z = (hits - exp) / sd
        zs.append(z)
        worst.append((abs(z), s, z))
    zs = np.array(zs)
    worst.sort(reverse=True)
    print(f"  {len(zs)} shifts: mean z={zs.mean():+.3f} sd={zs.std():.3f}, "
          f"expected max ~{math.sqrt(2 * math.log(len(zs))):.1f}")
    print(f"  top: {[(s, round(z, 2)) for _, s, z in worst[:5]]}")

    print("\n=== FRIEDMAN (column IoC) ON COMPRESSED J, periods 2..120 ===")
    best = []
    for k in range(2, 121):
        cols = [J[i::k] for i in range(k)]
        mean_ioc = float(np.mean([ioc(col.tolist()) * M for col in cols]))
        best.append((mean_ioc, k))
    best.sort(reverse=True)
    print(f"  top periods: {[(k, round(v, 4)) for v, k in best[:5]]}")
    print(f"  (expected 1.0; sd at k=20 roughly 0.01)")

    print("\n=== KAPPA ON RAW GAPPED J (EA consumes key) ===")
    Jraw = np.full(n - 1, -1, dtype=np.int64)
    Jraw[nondbl] = (delta[nondbl] - 1) % M
    worst = []
    zs = []
    for s in range(1, (n - 1) // 2):
        a = Jraw[:-s]
        b = Jraw[s:]
        ok = (a >= 0) & (b >= 0)
        m_ = int(ok.sum())
        hits = int(np.count_nonzero(a[ok] == b[ok]))
        exp = m_ / M
        sd = math.sqrt(m_ * (1 / M) * (1 - 1 / M))
        z = (hits - exp) / sd
        zs.append(z)
        worst.append((abs(z), s, z))
    zs = np.array(zs)
    worst.sort(reverse=True)
    print(f"  {len(zs)} shifts: mean z={zs.mean():+.3f} sd={zs.std():.3f}")
    print(f"  top: {[(s, round(z, 2)) for _, s, z in worst[:5]]}")

    print("\n=== MOD-4 / MOD-7 CRT PROJECTIONS (compressed J) ===")
    for mod in (4, 7, 14, 2):
        P_ = J % mod
        cc = np.bincount(P_, minlength=mod)
        stat = ((cc - nj / mod) ** 2 / (nj / mod)).sum()
        # kappa all shifts on projection
        zbest = 0.0
        sbest = 0
        for s in range(1, nj // 2):
            m_ = nj - s
            hits = int(np.count_nonzero(P_[:-s] == P_[s:]))
            exp = m_ / mod
            sd = math.sqrt(m_ * (1 / mod) * (1 - 1 / mod))
            z = (hits - exp) / sd
            if abs(z) > abs(zbest):
                zbest, sbest = z, s
        print(f"  mod {mod}: marginal chi2 p={chi2_dist.sf(stat, mod - 1):.3f}, "
              f"kappa max |z|={zbest:+.2f} at shift {sbest} "
              f"(expected max ~{math.sqrt(2 * math.log(nj // 2)):.1f})")

    print("\n=== LINEAR FUNCTIONALS MOD 28 ===")
    hits = []
    for d in range(1, 21):
        x = J[:-d]
        y = J[d:]
        m_ = len(x)
        for a in range(1, M):
            f = (y + a * x) % M
            cc = np.bincount(f, minlength=M)
            stat = ((cc - m_ / M) ** 2 / (m_ / M)).sum()
            p = chi2_dist.sf(stat, M - 1)
            if p < 1e-4:
                hits.append((p, d, a))
    print(f"  significant (p<1e-4 of {20 * 27} tests): {hits if hits else 'none'}")

    print("\n=== PAIRWISE CONTINGENCY J[t] vs J[t+d] ===")
    results = []
    for d in range(1, 51):
        a = J[:-d]
        b = J[d:]
        joint = np.zeros((M, M))
        np.add.at(joint, (a, b), 1)
        stat, p, dof, _ = chi2_contingency(joint + 1e-9)
        results.append((p, d))
    results.sort()
    print(f"  top: {[(d, round(p, 4)) for p, d in results[:4]]} "
          f"(Bonferroni 50 tests at 0.01: 2e-4)")

    print("\n=== DFT ON COMPRESSED J ===")
    peaks = []
    for mlt in range(1, M):
        x = np.exp(2j * np.pi * mlt * J / M)
        X = np.fft.fft(x)
        power = np.abs(X[1 : nj // 2]) ** 2 / nj
        t = np.argmax(power)
        peaks.append((float(power[t]), mlt, int(t + 1)))
    peaks.sort(reverse=True)
    nbins = (M - 1) * (nj // 2 - 1)
    print(f"  threshold ~{math.log(nbins) + 3:.1f}; "
          f"top: {[(round(pw, 1), mlt, f) for pw, mlt, f in peaks[:4]]}")

    print("\n=== J BY POSITION-IN-WORD ===")
    # map each J symbol to the word-position of the step's second rune
    posw = np.full(n, -1, dtype=np.int64)
    k = 0
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)
    idx = 0
    for w in cw:
        for j in range(len(w)):
            posw[idx] = j
            idx += 1
    grouped = defaultdict(list)
    for t, i in enumerate(rawpos):
        p_ = posw[i + 1]
        if p_ >= 0:
            grouped[min(int(p_), 6)].append(int(J[t]))
    for j in sorted(grouped):
        g = grouped[j]
        cc = np.bincount(np.array(g), minlength=M)
        stat = ((cc - len(g) / M) ** 2 / (len(g) / M)).sum()
        print(f"  word-pos {j}: n={len(g)} nIoC={ioc(g) * M:.3f} "
              f"chi2 p={chi2_dist.sf(stat, M - 1):.3f}")

    print("\n=== REPEATED J N-GRAMS (compressed) ===")
    for L in (5, 6, 7):
        d = defaultdict(int)
        for i in range(nj - L + 1):
            d[tuple(J[i : i + L])] += 1
        npairs = sum(v * (v - 1) // 2 for v in d.values())
        exp = (nj - L + 1) ** 2 / 2 / M**L
        print(f"  L={L}: {npairs} pairs (exp~{exp:.2f})")


if __name__ == "__main__":
    main()
