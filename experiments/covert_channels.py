#!/usr/bin/env python3
"""Covert-channel and residual key-structure probes.

J. Doublet channel: the 88 doubled runes (and their gaps) as a hidden
   message — IoC, adjacency, best match to runeglish frequencies under
   all shifts/atbash.
K. Word-counter periodicity on word-INITIAL runes only (key state at
   word start cycling with a period in words).
L. Affine-normalized repeat census (key segments reused under any affine
   transform y = m*x + b).
M. Beaufort-style reuse: common n-grams between the delta stream and its
   negation / reversed negation.
N. Repeated 4/5-gram totals vs doublet-corrected expectation.
"""

import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2 as chi2_dist

from anomaly_scan import parse, ioc
from aldegonde import c3301

N = 29


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain])
    n = len(cipher)
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)

    print("=== J. DOUBLET CHANNEL ===")
    dpos = [i for i in range(n - 1) if cipher[i] == cipher[i + 1]]
    dvals = [int(cipher[i]) for i in dpos]
    print(f"  doubled-rune sequence ({len(dvals)} runes): nIoC={ioc(dvals)*N:.3f}")
    dl = np.diff(dpos)
    gaps29 = (dl % N).tolist()
    print(f"  gaps mod 29 ({len(gaps29)}): nIoC={ioc(gaps29)*N:.3f}")
    # adjacency of doubled runes
    pairs = list(zip(dvals, dvals[1:]))
    eq = sum(1 for a, b in pairs if a == b)
    print(f"  consecutive doubled runes equal: {eq} (exp {len(pairs)/N:.1f})")
    dd = [(b - a) % N for a, b in pairs]
    print(f"  deltas of doubled runes: nIoC={ioc(dd)*N:.3f}")
    # best shift match to runeglish unigram frequencies
    # The unigram file is keyed by rune character: "<rune> <count>"
    fvec = np.zeros(N)
    with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) == 2 and parts[0] in c3301.CICADA_ALPHABET:
                fvec[c3301.r2i(parts[0])] = float(parts[1])
    fvec = fvec / fvec.sum()
    cnt = np.bincount(dvals, minlength=N).astype(float)

    def best_fit(counts):
        best = math.inf
        for s in range(N):
            for flip in (1, -1):
                mapped = np.array([counts[(flip * i + s) % N] for i in range(N)])
                exp = fvec * counts.sum()
                stat = float(np.sum((mapped - exp) ** 2 / np.maximum(exp, 0.1)))
                best = min(best, stat)
        return best

    obs_fit = best_fit(cnt)
    rng = np.random.default_rng(31)
    mcf = [best_fit(np.bincount(rng.integers(0, N, len(dvals)), minlength=N).astype(float))
           for _ in range(300)]
    mcf = np.array(mcf)
    print(f"  best shift/flip chi2 of doubled runes vs runeglish: obs={obs_fit:.1f} "
          f"| uniform-random baseline {mcf.mean():.1f}±{mcf.std():.1f} "
          f"P(<=obs)={(mcf <= obs_fit).mean():.3f}")

    print("\n=== K. WORD-COUNTER PERIODICITY (word-initial runes) ===")
    first = [w[0] for w in cw]
    last = [w[-1] for w in cw]
    for name, seq in (("first", first), ("last", last)):
        best = []
        for k in range(2, 61):
            cols = [[seq[i] for i in range(c, len(seq), k)] for c in range(k)]
            m = float(np.mean([ioc(col) * N for col in cols if len(col) > 20]))
            best.append((m, k))
        best.sort(reverse=True)
        print(f"  {name}-rune word-index periods, top3 nIoC: "
              f"{[(k, round(m, 3)) for m, k in best[:3]]}")

    print("\n=== L. AFFINE-NORMALIZED REPEAT CENSUS ===")
    # canonical form: normalize deltas by first nonzero delta
    inv = [0] * N
    for a in range(1, N):
        for b in range(1, N):
            if (a * b) % N == 1:
                inv[a] = b
    delta = (np.diff(cipher) % N).astype(int)
    for L in (8, 9, 10):
        d = defaultdict(list)
        for i in range(n - L):
            seg = delta[i : i + L - 1]
            nz = next((x for x in seg if x != 0), None)
            if nz is None:
                continue
            m = inv[nz]
            sig = tuple((m * x) % N for x in seg)
            d[sig].append(i)
        reps = {k: v for k, v in d.items() if len(v) > 1}
        npairs = sum(len(v) * (len(v) - 1) // 2 for v in reps.values())
        exp = (n - L) ** 2 / 2 * (N * (N - 1)) / N ** L
        print(f"  affine-class repeated {L}-grams: {npairs} pairs (exp~{exp:.2f})")
        if npairs and L >= 9:
            for k, v in reps.items():
                print(f"    at {v}")

    print("\n=== M. BEAUFORT-STYLE SEGMENT REUSE ===")
    dneg = (-delta) % N
    for L in (6, 7):
        d1 = defaultdict(int)
        for i in range(len(delta) - L + 1):
            d1[tuple(delta[i : i + L])] += 1
        hits = 0
        for i in range(len(dneg) - L + 1):
            t = tuple(dneg[i : i + L])
            if d1.get(t, 0) > 0 and tuple(delta[i:i+L]) != t:
                hits += 1
        exp = (len(delta) - L + 1) ** 2 / N ** L
        print(f"  delta vs -delta common {L}-grams: {hits} (exp~{exp:.2f})")
        rev = dneg[::-1]
        hits = 0
        for i in range(len(rev) - L + 1):
            t = tuple(rev[i : i + L])
            if d1.get(t, 0) > 0:
                hits += 1
        print(f"  delta vs reversed(-delta) common {L}-grams: {hits} (exp~{exp:.2f})")

    print("\n=== N. SHORT REPEAT TOTALS VS CORRECTED EXPECTATION ===")
    # correction: P(two indep positions carry equal k-grams) under the
    # doublet-suppressed null is slightly above 29^-k
    p_dd = 0.00675
    # per-step match prob ratio vs uniform (cf. digraph calc):
    ratio2 = (p_dd ** 2 / N + (1 - p_dd) ** 2 / (N - 1) ** 0) and None
    for L in (4, 5):
        d = defaultdict(int)
        for i in range(n - L + 1):
            d[tuple(int(x) for x in cipher[i : i + L])] += 1
        npairs = sum(v * (v - 1) // 2 for v in d.values())
        m = n - L + 1
        # MC the corrected expectation
        rng = np.random.default_rng(17)
        mc = []
        for _ in range(30):
            out = np.empty(n, dtype=np.int64)
            out[0] = rng.integers(0, N)
            same = rng.random(n) < p_dd
            jump = rng.integers(0, N - 1, n)
            for i in range(1, n):
                out[i] = out[i - 1] if same[i] else (jump[i] if jump[i] < out[i - 1] else jump[i] + 1)
            dd_ = defaultdict(int)
            for i in range(n - L + 1):
                dd_[tuple(int(x) for x in out[i : i + L])] += 1
            mc.append(sum(v * (v - 1) // 2 for v in dd_.values()))
        mc = np.array(mc)
        z = (npairs - mc.mean()) / mc.std()
        print(f"  repeated {L}-gram pairs: obs={npairs} null={mc.mean():.1f}±{mc.std():.1f} z={z:+.2f}")


if __name__ == "__main__":
    main()
