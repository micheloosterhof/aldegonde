#!/usr/bin/env python3
# ABOUTME: Final LP cipher model: per-word order-5 orbit with a phase-absorbing
# ABOUTME: free-group walk; every hard statistical observable from one mechanism.
"""Phase-absorbing orbit+walk: the complete model.

    c[i]       = base_w( g^(j mod 5)( p[i] ) )        j = position in word
    base_{w+1} = base_w o g^((len_w - 1) mod 5) o sigma_{k_w}

- g: mixed permutation of ORDER 5, diagonal on English bigrams tuned to the
  observed within-word doublet rate (0.0063). Order 5 makes the within-word
  wrap safe and gives the sharp d5 echo (g^5 = id).
- sigma_k: FREE mixed permutations (full-group walk -> flat unigrams, flat
  columns, no periodicity, Kasiski-silent, key-state returns possible).
  The g^((len_w-1) mod 5) factor ABSORBS the outgoing phase, so the seam
  relation is the constant diagonal sigma at every boundary -- one tunable
  number, set to the observed seam rate (0.0079). Computable from the
  previous word's length, so decryption is progressive.

Doublets are inherent bigram-class effects (g-diagonal within words,
sigma-diagonal at seams), boundary-blind by construction. Soft observables
(dead-time p=0.06, delta residual p=0.04, lag marking LR~4) are not
targeted; they are watch-items.
"""

from __future__ import annotations

import random

from stay_slot_cipher import (
    M,
    battery,
    cut_words,
    diag_rate,
    gen_plaintext,
    load_trigram,
    pair_matrices,
    perm_from_cycles,
    ppow,
    tune,
)

SEED = 3301
TARGET_WITHIN = 0.0063
TARGET_SEAM = 0.0079
CHANCE = 1 / M


def encipher(words, g, base0, sigmas, stepkey):
    gp = [ppow(g, k) for k in range(5)]
    base = base0[:]
    out = []
    for wi, w in enumerate(words):
        out.append([base[gp[j % 5][p]] for j, p in enumerate(w)])
        a = (len(w) - 1) % 5
        sig = sigmas[stepkey[wi % len(stepkey)]]
        step = [gp[a][sig[x]] for x in range(M)]  # g^a o sigma
        base = [base[step[x]] for x in range(M)]
    return out


def main() -> None:
    rng = random.Random(SEED)
    words = cut_words(gen_plaintext(load_trigram(), 40000, rng), rng)
    mats = pair_matrices(words)
    P1 = mats[1][0]

    def g_obj(g):
        v = 3000.0 * (diag_rate(P1, g) - TARGET_WITHIN) ** 2
        acc = g
        for d in (2, 3, 4):
            acc = [g[x] for x in acc]
            v += 40.0 * (diag_rate(mats[d][0], acc) - CHANCE) ** 2
        return v

    g = min(
        (tune(perm_from_cycles([5] * 5 + [1] * 4, rng), g_obj, rng) for _ in range(4)),
        key=g_obj,
    )

    def s_obj(s):
        return (diag_rate(P1, s) - TARGET_SEAM) ** 2

    sigmas = [
        tune(perm_from_cycles([9, 7, 7, 3, 3], rng), s_obj, rng, iters=10000)
        for _ in range(2)
    ]
    print(
        f"g diagonal {diag_rate(P1, g):.4f} (target {TARGET_WITHIN}); "
        f"sigma diagonals {[f'{diag_rate(P1, s):.4f}' for s in sigmas]} "
        f"(target {TARGET_SEAM})"
    )

    stepkey = [rng.randrange(2) for _ in range(4096)]
    base0 = list(range(M))
    rng.shuffle(base0)
    battery("PHASE-ABSORBING ORBIT+WALK", encipher(words, g, base0, sigmas, stepkey))


if __name__ == "__main__":
    main()
