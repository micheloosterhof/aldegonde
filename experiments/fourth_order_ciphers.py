#!/usr/bin/env python3
# ABOUTME: Simulates cipher families known or claimed to exhibit 4th-order
# ABOUTME: statistical structure, profiling each by statistical order.
"""Which cipher families show 4th-order structure with flat lower orders?

Historical context: the Zodiac-340 cipher (solved 2020 after 51 years) was
cracked starting from a 4-point statistic - counts of repeated two-symbol
sequences at trial offsets, peaking at offset 19 - which revealed its
transposition geometry. Its homophones kept unigrams and bigram tables
flat; at n=340 the underlying 2nd-order structure was unmeasurable, so the
concentrated 4-point statistic was the only handle. The same statistic
family (P(L,1) in our fourpoint_dragnet) is what flagged LP's lag-5
pairing.

Simulation results at LP corpus length (n ~ 13k):

| mechanism                | dbl%  | nIoC  | 2pt leaks        | 4pt max    |
| LP observed              | 0.66  | 1.000 | flat all lags    | +3.5 @ L5  |
| homophonic+cycling       | 0.07  | 1.004 | z=+232 @ L2 !!   | (2nd-order)|
| homo+cycle+transp(19rows)| 3.50  | 1.006 | z=+356 @ L19 !!  | (2nd-order)|
| keystream-rewind (key)   | 3.39  | 1.000 | flat             | invisible  |
| OTP control              | 3.46  | 1.000 | flat             | none       |

Conclusions:
1. Homophone cycling suppresses doublets (0.07%!) but leaks enormously at
   2nd order; transposition relocates that leak to the geometry lag, still
   2nd order. The "4th-order-only" character of Zodiac-340 was a SAMPLE
   SIZE effect: at n=340 the 2nd-order table (63x63) was unmeasurable and
   only the concentrated repeated-bigram statistic had power. At LP's
   n=13k, our flat 29x29 tables at all lags 1-60 (and flat kappa to 6400,
   which would show the cycling suppression at any geometry lag) EXCLUDE
   the entire homophonic+transposition class.
2. Key-stream rewind (reusing KEY material) is statistically invisible -
   ct coincidences still require pt coincidences. Only CIPHERTEXT-copy
   semantics (back-references, nulls, depth/stutter incidents) produce
   pure 4th-order structure at any text length.
3. Therefore the known cipher families with genuine 4th-order-only
   signatures are: (a) copy/stutter/depth phenomena (operator key reuse
   producing coincidence runs - the object of classical depth-hunting
   since Kullback), and (b) short-text regimes of mechanisms whose
   lower-order leaks are below the noise floor (the Zodiac-340 case).
   LP's lag-5 pairing pattern-matches class (a) - consistent with the
   copy-event/back-reference reading - and class (b) is excluded by the
   corpus's well-powered flat lower orders."""

import importlib.util
import random
import statistics
from math import sqrt

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "mf", "experiments/mechanism_fingerprint.py")
mf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mf)

N = 29
i2r, r2i = mf.i2r, mf.r2i

text, wlens = mf.load_corpus()
n = len(text)
gen = mf.build_markov()

def profile(s: str, lags=(2, 5, 9, 19)) -> dict:
    """1st/2nd/4th-order profile."""
    a = np.array([r2i(c) for c in s])
    m = len(a)
    out = {}
    cnt = np.bincount(a, minlength=N)
    out["nIoC"] = float((cnt * (cnt - 1)).sum() / (m * (m - 1)) * N)
    out["dbl%"] = 100 * float(np.mean(a[:-1] == a[1:]))
    # 2nd order: off-diagonal chi2 z at each lag
    for L in lags:
        x, y = a[:-L], a[L:]
        joint = np.zeros((N, N))
        np.add.at(joint, (x, y), 1)
        exp = np.outer(np.bincount(x, minlength=N),
                       np.bincount(y, minlength=N)) / len(x)
        od = ~np.eye(N, dtype=bool) & (exp > 1)
        chi = ((joint - exp) ** 2 / np.where(od, exp, 1))[od].sum()
        df = od.sum() - 1
        out[f"2pt-L{L}"] = round((chi - df) / sqrt(2 * df), 1)
    # 4th order: P(L,1) repeated-digraph-at-lag z, scan for max over L=2..40
    best = (0.0, 0)
    for L in range(2, 41):
        M = a[:-L] == a[L:]
        pairs = int(np.sum(M[:-1] & M[1:]))
        e = (len(M) - 1) / (N * N)
        z = (pairs - e) / sqrt(e)
        if z > best[0]:
            best = (z, L)
    out["4pt-max"] = f"z={best[0]:+.1f}@L={best[1]}"
    return out

# ---- mechanisms ----
def enc_homophonic_cycling(pt: str, wl) -> str:
    """Plaintext squashed to 10 symbols (Zipf-ish via Markov text), 29 ct
    symbols allocated by frequency, strict per-letter cycling."""
    # map 29 runeglish letters onto 10 classes by frequency rank
    freq = {}
    for c in pt:
        freq[c] = freq.get(c, 0) + 1
    ranked = sorted(freq, key=freq.get, reverse=True)
    cls = {c: min(i, 9) for i, c in enumerate(ranked)}
    p10 = [cls[c] for c in pt]
    # allocate 29 ct symbols proportional to class frequency
    cfreq = np.bincount(p10, minlength=10).astype(float)
    alloc = np.maximum(1, np.round(cfreq / cfreq.sum() * N).astype(int))
    while alloc.sum() > N:
        alloc[np.argmax(alloc)] -= 1
    while alloc.sum() < N:
        alloc[np.argmax(cfreq / alloc)] += 1
    pools = []
    sym = 0
    for k in range(10):
        pools.append(list(range(sym, sym + alloc[k])))
        sym += alloc[k]
    ptr = [0] * 10
    out = []
    for p in p10:
        pool = pools[p]
        out.append(i2r(pool[ptr[p] % len(pool)]))
        ptr[p] += 1
    return "".join(out)

def enc_homo_cycle_transpose(pt: str, wl, lag: int = 19) -> str:
    """Transposition with `lag` ROWS: plaintext-adjacent symbols land
    exactly `lag` apart in the ciphertext (the Zodiac-340 geometry)."""
    s = enc_homophonic_cycling(pt, wl)
    cols = len(s) // lag
    s = s[:cols * lag]
    grid = np.array([r2i(c) for c in s]).reshape(lag, cols)
    return "".join(i2r(int(v)) for v in grid.T.flatten())

def enc_keystream_rewind(pt: str, wl, dist: int = 9, prob: float = 0.004) -> str:
    """OTP whose generator occasionally rewinds `dist` steps for 2 outputs."""
    keys = []
    out = []
    for i, c in enumerate(pt):
        if len(keys) > dist and random.random() < prob:
            k1, k2 = keys[-dist], keys[-dist + 1]
            out.append(i2r((r2i(c) + k1) % N))
            keys.append(k1)
            if i + 1 < len(pt):
                out.append(i2r((r2i(pt[i + 1]) + k2) % N))
                keys.append(k2)
            continue
        k = random.randrange(N)
        keys.append(k)
        out.append(i2r((r2i(c) + k) % N))
    return "".join(out[:len(pt)])

print(f"{'mechanism':26s} {'dbl%':>5s} {'nIoC':>6s} "
      f"{'2pt L2':>7s} {'2pt L5':>7s} {'2pt L9':>7s} {'2pt L19':>7s} {'4pt max':>14s}")
mechs = [
    ("LP observed", None),
    ("homophonic+cycling", enc_homophonic_cycling),
    ("homo+cycle+transp(w19)", enc_homo_cycle_transpose),
    ("keystream-rewind(d9)", enc_keystream_rewind),
    ("otp control", lambda pt, wl: "".join(
        i2r((r2i(c) + random.randrange(N)) % N) for c in pt)),
]
for name, fn in mechs:
    if fn is None:
        p = profile(text)
    else:
        ps = [profile(fn(gen(n), wlens)) for _ in range(3)]
        p = {k: (statistics.mean(v[k] for v in ps)
                 if not isinstance(ps[0][k], str) else ps[1][k])
             for k in ps[0]}
    print(f"{name:26s} {p['dbl%']:5.2f} {p['nIoC']:6.3f} "
          f"{p['2pt-L2']:7.1f} {p['2pt-L5']:7.1f} {p['2pt-L9']:7.1f} "
          f"{p['2pt-L19']:7.1f} {p['4pt-max']:>14s}")
