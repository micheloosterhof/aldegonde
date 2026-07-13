#!/usr/bin/env python3
# ABOUTME: Final orbit+walk cipher model, rate-targeted: g-diagonal tuned to the
# ABOUTME: observed LP doublet rate and walk seams to the observed seam rate.
"""Orbit+walk, rate-targeted: the minimal model covering all hard observables.

    c[i] = base_w( g^(j mod 5)( p[i] ) )       j = position in word
    base_{w+1} = base_w o s_{k_w}              s from tuned safe generators

g has order 5 (echo + safe wrap). Its diagonal is tuned TO the observed
within-word doublet rate (0.0063), not to the minimum -- the LP's doublet
class is a mildly rare plaintext bigram set, not the rarest one. The walk
generators are tuned TO the observed seam rate (0.0079). Everything else
(echo, empty middle, flat unigrams/columns, Kasiski silence) is emergent.

Soft observables (dead-time p=0.06, delta residual p=0.04, lag marking LR~4)
are deliberately NOT targeted; they are watch-items, not constraints.
"""

from __future__ import annotations

import random

from stay_slot_cipher import (
    M, battery, cut_words, diag_rate, encipher_v1, gen_plaintext,
    load_trigram, pair_matrices, perm_from_cycles, ppow, tune,
)

SEED = 3301
TARGET_WITHIN = 0.0063
TARGET_SEAM = 0.0079
CHANCE = 1 / M


def main() -> None:
    rng = random.Random(SEED)
    words = cut_words(gen_plaintext(load_trigram(), 40000, rng), rng)
    mats = pair_matrices(words)
    P1 = mats[1][0]

    # g order 5: diagonal AT the observed rate, g^2..4 diagonals at chance (C5)
    def g_obj(g):
        v = 3000.0 * (diag_rate(P1, g) - TARGET_WITHIN) ** 2
        acc = g
        for d in (2, 3, 4):
            acc = [g[x] for x in acc]
            v += 40.0 * (diag_rate(mats[d][0], acc) - CHANCE) ** 2
        return v

    g = min((tune(perm_from_cycles([5] * 5 + [1] * 4, rng), g_obj, rng)
             for _ in range(4)), key=g_obj)
    gp = [ppow(g, k) for k in range(5)]
    print(f"g diagonal: {diag_rate(P1, g):.4f} (target {TARGET_WITHIN})")

    # walk generators: seam diagonals AT the observed seam rate
    def seam_obj(s):
        v = 0.0
        for a in range(5):
            rel = [gp[a][s[x]] for x in range(M)]
            v += (diag_rate(P1, rel) - TARGET_SEAM) ** 2
        return v

    steps = [tune(perm_from_cycles([9, 7, 7, 3, 3], rng), seam_obj, rng,
                  iters=12000) for _ in range(2)]
    stepkey = [rng.randrange(2) for _ in range(4096)]
    base0 = list(range(M))
    rng.shuffle(base0)

    battery("FINAL ORBIT+WALK (rate-targeted)",
            encipher_v1(words, g, base0, steps, stepkey, rng))


if __name__ == "__main__":
    main()
