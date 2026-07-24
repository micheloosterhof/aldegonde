#!/usr/bin/env python3
# ABOUTME: Full-battery simulation of the length-clocked walk with tuned
# ABOUTME: mixed-census g (annealed by conjugation, preserving cycle type):
# ABOUTME: the promotion test for mixed-cycle-progression.md's live subfamily.
"""Do tuned mixed-census walks reproduce the LP fingerprint?

For each candidate cycle census, build g with that census, anneal its
adjacent diagonal LOW by conjugation moves (which preserve the census),
then run the walk

    c[j] = base_w(g^j(p[j])),   base_{w+1} = base_w . g^(L-1) . sigma

on register plaintext cut to the LP word-length structure, with a fresh
random mixed sigma and base_0 per run. Measures, against the LP targets:
the within-word d1-d10 profile (does the d6 dip appear from inheritance?
does d5 come out partial? how short does d4 fall?), the seam doublet
rate, unigram flatness, global kappa 1-8, triplets, and the uniformity
of doubled-rune identities (a fixed rune's doublet leaks must stay
base-scrambled). Also reports each census's annealed diagonal floor
(replacing the five-5-cycle-only floor of advance_doublet_floor.py).
"""

from __future__ import annotations

import math
import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish
from doublet_position_profile import IDX_ENG
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words
from lp_corpus import load_clean
from sigma_power_kill import compose

M = 29
MAXD = 10
RUNS = 12

CENSUSES = [
    ("Michel 4x5+2x4+1f", (5, 5, 5, 5, 4, 4, 1)),
    ("leader 7+3x5+4+3f", (7, 5, 5, 5, 4, 1, 1, 1)),
    ("prime 2x7+3x5", (7, 7, 5, 5, 5)),
    ("standard 5x5+4f", (5, 5, 5, 5, 5, 1, 1, 1, 1)),
]


def make_g(census, rng):
    pts = list(range(M))
    rng.shuffle(pts)
    g = list(range(M))
    i = 0
    for L in census:
        cyc = pts[i:i + L]
        i += L
        for k in range(L):
            g[cyc[k]] = cyc[(k + 1) % L]
    return g


def conjugate(g, a, b):
    t = list(range(M))
    t[a], t[b] = b, a
    return [t[g[t[x]]] for x in range(M)]


def anneal(g, T1, rng, iters=6000):
    def diag(gg):
        return sum(T1[gg[y]][y] for y in range(M))
    cur = diag(g)
    best_g, best = g[:], cur
    temp = 0.004
    for it in range(iters):
        a, b = rng.sample(range(M), 2)
        g2 = conjugate(g, a, b)
        v = diag(g2)
        if v < cur or rng.random() < math.exp(-(v - cur) / temp):
            g, cur = g2, v
            if v < best:
                best_g, best = g2[:], v
        temp *= 0.9995
    return best_g, best


def battery(words_ct):
    m: Counter = Counter()
    s: Counter = Counter()
    stream = []
    dbl_vals = []
    seam_d = seam_n = 0
    prev_last = None
    for w in words_ct:
        if prev_last is not None:
            seam_n += 1
            seam_d += prev_last == w[0]
        prev_last = w[-1]
        stream.extend(w)
        L = len(w)
        for j in range(L):
            for d in range(1, min(MAXD + 1, L - j)):
                s[d] += 1
                m[d] += w[j] == w[j + d]
                if d == 1 and w[j] == w[j + 1]:
                    dbl_vals.append(w[j])
    prof = {d: m[d] / s[d] for d in s}
    c = Counter(stream)
    n = len(stream)
    uni = sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * M
    kap = {}
    for d in range(1, 9):
        hits = sum(1 for i in range(n - d) if stream[i] == stream[i + d])
        kap[d] = hits / (n - d) * M
    trip = sum(1 for i in range(n - 2)
               if stream[i] == stream[i + 1] == stream[i + 2])
    e = len(dbl_vals) / M if dbl_vals else 0
    chi_dbl = (sum((v - e) ** 2 / e for v in
                   np.bincount(dbl_vals, minlength=M)) if e else 0.0)
    return prof, seam_d / seam_n, uni, kap, trip, chi_dbl


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    words_d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        words_d.setdefault(w, []).append(stream[i])
    lp_words = [words_d[k] for k in sorted(words_d)]
    lp_lens = [len(w) for w in lp_words]
    lp_prof, lp_seam, lp_uni, lp_kap, lp_trip, lp_chi = battery(lp_words)

    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    if not prose_path.exists():
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    prose = [IDX_ENG[t] for w in prose_words(prose_path)
             for t in to_runeglish(w)]

    # adjacent within-word bigram table for annealing
    T1 = np.zeros((M, M))
    for _ in range(20):
        off = rng.randrange(len(prose) - sum(lp_lens))
        pos = off
        for L in lp_lens:
            w = prose[pos:pos + L]
            pos += L
            for j in range(L - 1):
                T1[w[j]][w[j + 1]] += 1
    T1 /= T1.sum()

    hdr = ("".join(f"{f'd{d}':>7}" for d in range(1, MAXD + 1))
           + f"{'seam':>7}{'uni':>7}{'trip':>5}{'dblchi':>7}")
    print(f"{'model':<20}" + hdr)
    print(f"{'LP observed':<20}"
          + "".join(f"{lp_prof.get(d, 0):>7.4f}" for d in range(1, MAXD + 1))
          + f"{lp_seam:>7.4f}{lp_uni:>7.3f}{lp_trip:>5}{lp_chi:>7.1f}")

    for name, census in CENSUSES:
        order = 1
        for L in set(census):
            order = order * L // math.gcd(order, L)
        acc = None
        floors = []
        seams, unis, trips, chis = [], [], [], []
        prof_acc: Counter = Counter()
        prof_n: Counter = Counter()
        for _ in range(RUNS):
            g = make_g(census, rng)
            g, floor = anneal(g, T1, rng)
            floors.append(floor)
            gp = [list(range(M))]
            for _ in range(order - 1):
                gp.append(compose(g, gp[-1]))
            sigma = list(range(M))
            rng.shuffle(sigma)
            base = list(range(M))
            rng.shuffle(base)
            off = rng.randrange(len(prose) - sum(lp_lens))
            pos = off
            ct = []
            for L in lp_lens:
                w = prose[pos:pos + L]
                pos += L
                ct.append([base[gp[j % order][p]] for j, p in enumerate(w)])
                base = compose(base, compose(gp[(L - 1) % order], sigma))
            prof, seam, uni, kap, trip, chi = battery(ct)
            for d, v in prof.items():
                prof_acc[d] += v
                prof_n[d] += 1
            seams.append(seam)
            unis.append(uni)
            trips.append(trip)
            chis.append(chi)
        print(f"{name:<20}"
              + "".join(f"{prof_acc[d] / prof_n[d]:>7.4f}"
                        if prof_n[d] else f"{'·':>7}"
                        for d in range(1, MAXD + 1))
              + f"{np.mean(seams):>7.4f}{np.mean(unis):>7.3f}"
              + f"{np.mean(trips):>5.0f}{np.mean(chis):>7.1f}")
        print(f"{'':<20}  annealed diagonal floor: "
              f"{np.mean(floors):.4f} ± {np.std(floors):.4f} "
              f"(order {order}; LP needs ~0.003-0.005 after fixed-point leak)")


if __name__ == "__main__":
    main()
