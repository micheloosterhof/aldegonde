#!/usr/bin/env python3
# ABOUTME: Full-battery simulation of the Quagmire (mixed-alphabet Vigenere)
# ABOUTME: step inside the length-clocked walk, against LP and the order-5-g
# ABOUTME: model — including its discriminating no-fixed-point prediction.
"""Does a mixed-alphabet Vigenere step reproduce the LP fingerprint?

`mixed-alphabet-vigenere.md` proposes replacing the order-5 permutation
`g` with conjugated shifts K(add delta)K^-1 sharing one mixed alphabet
K, five offsets summing to 0 mod 29. It clears the doublet floor on
paper; this runs it end to end.

Faithful to the hypothesis, K is KEYWORD-DERIVED (its selling point is a
small human key), and the offsets are chosen to land the doublet rate on
the observed 0.0063 rather than at the achievable floor — the
over-annealing mistake made once already in this investigation.

Reports the d1-d10 within-word profile, seam rate, unigram nIoC,
triplets and kappa against the LP and against an order-5-g run, and
checks the discriminator: conjugated shifts are fixed-point-free, so
d2/d3/d4 must sit at background with no leak.
"""

from __future__ import annotations

import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from aldegonde import c3301
from d5_partial_leak import to_runeglish
from doublet_position_profile import IDX_ENG
from ea_direction_test import PROSE_CACHE, prose_words
from lp_corpus import load_clean
from sigma_algebraic_floor import tables

M = 29
MAXD = 10
TARGET_D1 = 0.0063
TARGET_SEAM = 0.0079
RUNS = 10
ENG = c3301.CICADA_ENGLISH_ALPHABET


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def inverse(p):
    q = [0] * M
    for i, v in enumerate(p):
        q[v] = i
    return q


def keyword_alphabet(kw):
    seq, seen = [], set()
    for ch in kw:
        for i, name in enumerate(ENG):
            if name == ch and i not in seen:
                seq.append(i)
                seen.add(i)
    return seq + [i for i in range(M) if i not in seen]


def conj_shift(K, t):
    """H(t) = K . (add t) . K^-1 as a permutation array."""
    pos = inverse(K)
    return [K[(pos[x] + t) % M] for x in range(M)]


def offset_costs(K, T):
    return [sum(T[conj_shift(K, t)[x]][x] for x in range(M))
            for t in range(M)]


def pick_schedule(costs, weights, target):
    """Five offsets summing to 0 mod 29 whose weighted cost is closest to
    the target (offsets may repeat; heaviest phases get cheapest)."""
    best = (9e9, None)
    order = sorted(range(5), key=lambda p: -weights[p])
    cheap = sorted(range(M), key=lambda t: costs[t])[:8]
    for a in cheap:
        for b in cheap:
            for c in cheap:
                for e in cheap:
                    f = (-(a + b + c + e)) % M
                    ds = [a, b, c, e, f]
                    cost = sum(weights[order[i]] * costs[ds[i]]
                               for i in range(5))
                    if abs(cost - target) < abs(best[0] - target):
                        sched = [0] * 5
                        for i, p in enumerate(order):
                            sched[p] = ds[i]
                        best = (cost, sched)
    return best


def rand_order5(rng):
    pts = list(range(M))
    rng.shuffle(pts)
    g = list(range(M))
    for c in range(5):
        cy = pts[c * 5:(c + 1) * 5]
        for i in range(5):
            g[cy[i]] = cy[(i + 1) % 5]
    return g


def conjugate(p, a, b):
    t = list(range(M))
    t[a], t[b] = b, a
    return [t[p[t[x]]] for x in range(M)]


def anneal_to(p, T, target, rng, iters=4000, order5=True):
    def obj(q):
        return abs(sum(T[q[y]][y] for y in range(M)) - target)
    cur, best, bp = obj(p), obj(p), p[:]
    for _ in range(iters):
        a, b = rng.sample(range(M), 2)
        if order5:
            q = conjugate(p, a, b)
        else:
            q = p[:]
            q[a], q[b] = q[b], q[a]
        v = obj(q)
        if v < cur or rng.random() < 0.03:
            p, cur = q, v
            if v < best:
                best, bp = v, q[:]
    return bp


def battery(words):
    m, s = Counter(), Counter()
    stream, seam_d, seam_n = [], 0, 0
    prev = None
    for w in words:
        if prev is not None:
            seam_n += 1
            seam_d += prev == w[0]
        prev = w[-1]
        stream.extend(w)
        L = len(w)
        for j in range(L):
            for d in range(1, min(MAXD + 1, L - j)):
                s[d] += 1
                m[d] += w[j] == w[j + d]
    prof = {d: m[d] / s[d] for d in s}
    c = Counter(stream)
    n = len(stream)
    uni = sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * M
    trip = sum(1 for i in range(n - 2)
               if stream[i] == stream[i + 1] == stream[i + 2])
    kap = {}
    for d in (1, 2, 5):
        kap[d] = sum(1 for i in range(n - d)
                     if stream[i] == stream[i + d]) / (n - d) * M
    return prof, seam_d / seam_n, uni, trip, kap


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    lp_words = [d[k] for k in sorted(d)]
    lens = [len(w) for w in lp_words]
    lp_prof, lp_seam, lp_uni, lp_trip, lp_kap = battery(lp_words)

    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if r:
            pools.setdefault(len(r), []).append(r)
    cross, within = tables(lens, pools, rng)

    def corpus():
        out = []
        for L in lens:
            LL = L
            while LL not in pools and LL < max(pools):
                LL += 1
            out.append(rng.choice(pools[LL])[:L])
        return out

    ph = Counter()
    for w in lp_words:
        for j in range(1, len(w)):
            ph[j % 5] += 1
    tot = sum(ph.values())
    weights = [ph[p] / tot for p in range(5)]

    print("keyword-derived K: can a schedule land on the observed 0.0063?")
    chosen = None
    for kw in ("DIUINITY", "CIRCUMFERENCE", "INSTAR", "PARABLE", "WISDOM",
               "PRIMES", "AETHEREAL", "MOBIUS"):
        K = keyword_alphabet(kw)
        costs = offset_costs(K, within)
        cost, sched = pick_schedule(costs, weights, TARGET_D1)
        print(f"  {kw:<14} best-fit schedule cost {cost:.4f}  offsets {sched}")
        if chosen is None or abs(cost - TARGET_D1) < abs(chosen[0]
                                                         - TARGET_D1):
            chosen = (cost, kw, K, sched)
    cost, kw, K, sched = chosen
    print(f"\nusing keyword {kw}, offsets {sched}, predicted d1 {cost:.4f}\n")

    hdr = "".join(f"{f'd{d}':>7}" for d in range(1, MAXD + 1))
    print(f"{'model':<22}{hdr}{'seam':>8}{'uni':>7}{'trip':>6}")
    print(f"{'LP observed':<22}"
          + "".join(f"{lp_prof.get(d, 0):>7.4f}" for d in range(1, MAXD + 1))
          + f"{lp_seam:>8.4f}{lp_uni:>7.3f}{lp_trip:>6}")

    for label in ("quagmire", "order-5 g"):
        acc, cnt = Counter(), Counter()
        seams, unis, trips = [], [], []
        for _ in range(RUNS):
            sigma = anneal_to(
                [x for x in np.random.permutation(M)], cross, TARGET_SEAM,
                rng, order5=False)
            base = list(range(M))
            rng.shuffle(base)
            if label == "quagmire":
                cum = [0]
                for j in range(1, MAXD + 6):
                    cum.append((cum[-1] + sched[(j - 1) % 5]) % M)
                steps = [conj_shift(K, t) for t in cum]
            else:
                g = anneal_to(rand_order5(rng), within, TARGET_D1, rng)
                gp = [list(range(M))]
                for _ in range(MAXD + 5):
                    gp.append(compose(g, gp[-1]))
                steps = [gp[j % 5] for j in range(MAXD + 6)]
            ct = []
            for w in corpus():
                ct.append([base[steps[j][p]] for j, p in enumerate(w)])
                base = compose(base, compose(steps[len(w) - 1], sigma))
            prof, seam, uni, trip, _ = battery(ct)
            for dd, v in prof.items():
                acc[dd] += v
                cnt[dd] += 1
            seams.append(seam)
            unis.append(uni)
            trips.append(trip)
        print(f"{label:<22}"
              + "".join(f"{acc[dd] / cnt[dd]:>7.4f}" if cnt[dd] else f"{'·':>7}"
                        for dd in range(1, MAXD + 1))
              + f"{np.mean(seams):>8.4f}{np.mean(unis):>7.3f}"
              + f"{np.mean(trips):>6.1f}")

    print("\ndiscriminator — conjugated shifts have NO fixed points, so the")
    print("quagmire model must show d2/d3/d4 at background (~0.0345) with no")
    print("leak, while an order-5 g leaks f/29 there from its fixed runes.")


if __name__ == "__main__":
    main()
