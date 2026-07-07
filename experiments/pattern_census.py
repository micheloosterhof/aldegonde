#!/usr/bin/env python3
"""Pattern census of the unsolved LP beyond doublet suppression.

Null model: stationary first-order Markov chain over 29 symbols with
P(next == cur) = observed doublet rate, all other transitions equal.
Under this null, doublet suppression is fully accounted for; any
deviation in higher-order pattern counts is NEW structure.

Also: full autocorrelation (kappa at every shift) with outlier scan.
"""

import math
from collections import Counter, defaultdict

import numpy as np

from anomaly_scan import parse

N = 29


def pattern_class(t):
    """Canonical isomorph pattern, e.g. (4,7,4) -> 'ABA'."""
    m = {}
    out = []
    for x in t:
        if x not in m:
            m[x] = chr(ord("A") + len(m))
        out.append(m[x])
    return "".join(out)


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    # drop section 17 (solved plaintext parable)
    plain = sections[-1]
    cipher = stream[: len(stream) - len(plain)]
    n = len(cipher)
    print(f"cipher stream: {n} runes (excluded {len(plain)} parable runes)")

    dbl = sum(1 for a, b in zip(cipher, cipher[1:]) if a == b)
    p_dd = dbl / (n - 1)
    print(f"doublets: {dbl}, per-opportunity rate {p_dd:.5f}")

    for L in (3, 4, 5):
        print(f"\n=== pattern census length {L} ===")
        obs = Counter()
        for i in range(n - L + 1):
            obs[pattern_class(cipher[i : i + L])] += 1
        tot = n - L + 1
        # enumerate all pattern classes of length L
        pats = set(obs)
        # also include classes with zero observations
        def gen(prefix, k):
            if len(prefix) == L:
                pats.add("".join(prefix))
                return
            for j in range(k + 1):
                gen(prefix + [chr(ord("A") + j)], max(k, j + 1))
        gen([], 0)
        rows = []
        for pat in sorted(pats):
            # P(one concrete labeling) under the Markov null, times the
            # number of injective labelings (falling factorial of 29).
            k = len(set(pat))
            nseq = 1.0
            for i in range(k):
                nseq *= (N - i)
            p = 1.0 / N
            for i in range(1, L):
                p *= p_dd if pat[i] == pat[i - 1] else (1 - p_dd) / 28
            exp = tot * p * nseq
            o = obs[pat]
            sd = math.sqrt(exp) if exp > 0 else 0.0
            z = (o - exp) / sd if sd > 0 else float("nan")
            rows.append((pat, o, exp, z))
        for pat, o, exp, z in rows:
            flag = " ***" if abs(z) > 4 else (" *" if abs(z) > 3 else "")
            print(f"  {pat}: obs={o:6d} exp={exp:10.1f} z={z:+6.2f}{flag}")

    print("\n=== full autocorrelation (kappa at every shift) ===")
    arr = np.array(cipher, dtype=np.int8)
    zs = []
    worst = []
    for shift in range(1, n // 2):
        m = n - shift
        hits = int(np.count_nonzero(arr[:-shift] == arr[shift:]))
        exp = m / N
        sd = math.sqrt(m * (1 / N) * (1 - 1 / N))
        z = (hits - exp) / sd
        zs.append(z)
        worst.append((abs(z), shift, hits, exp, z))
    zs = np.array(zs)
    print(f"shifts tested: {len(zs)}, mean z={zs.mean():+.3f}, sd={zs.std():.3f}")
    print(f"max |z| expected under null for {len(zs)} trials: ~{math.sqrt(2*math.log(len(zs))):.2f}")
    worst.sort(reverse=True)
    print("top 12 shifts by |z|:")
    for absz, shift, hits, exp, z in worst[:12]:
        print(f"  shift {shift:5d}: hits={hits} exp={exp:.1f} z={z:+.2f}")
    neg = (zs < -3).sum()
    pos = (zs > 3).sum()
    print(f"shifts with z<-3: {neg}, z>+3: {pos}")


if __name__ == "__main__":
    main()
