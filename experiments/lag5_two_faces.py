# ABOUTME: RETRACTED demo of a walk + copy overlay. The overlay is
# ABOUTME: information-theoretically incoherent; see plaintext_lag5_pairing.py.
"""RETRACTED. This composed the length-clocked walk with a back-reference copy
overlay (overwrite C[i] with C[i-5]) and appeared to produce both lag-5 faces.
The overlay is NOT a valid cipher: overwriting C[i] destroys the information of
the current plaintext rune P[i]. The only coherent copy fires where P[i]=P[i-5],
which under g^5=id is already the walk's echo -- not a separate mechanism.

The correct analysis is in experiments/plaintext_lag5_pairing.py: the d1 face is
real plaintext morphology passed through the echo (no overlay), and the d4 face
is absent from plaintext and remains unexplained. This script is kept only to
document the retracted approach; do not build on it.
"""

from __future__ import annotations

import random
from collections import Counter

from stay_slot_cipher import (
    M,
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
CHANCE = 1 / M


def encipher(words, g, base0, sigma):
    gp = [ppow(g, k) for k in range(5)]
    base = base0[:]
    out = []
    for w in words:
        out.append([base[gp[j % 5][p]] for j, p in enumerate(w)])
        a = (len(w) - 1) % 5
        step = [gp[a][sigma[x]] for x in range(M)]
        base = [base[step[x]] for x in range(M)]
    return out


def flatten_with_bounds(cipher_words):
    flat, word_of = [], []
    for wi, w in enumerate(cipher_words):
        for r in w:
            flat.append(r)
            word_of.append(wi)
    return flat, word_of


def copy_overlay(flat, word_of, rate, rng):
    """Back-reference copy events: with prob `rate` at each eligible position i
    (i>=5), copy C[i-5] to C[i]. Creates lag-5 matches that cluster as {1,4}
    pairs because copies fire at frame edges. Avoid making a doublet."""
    out = flat[:]
    i = 5
    while i < len(out):
        if rng.random() < rate and out[i] != out[i - 5]:
            cand = out[i - 5]
            if cand != out[i - 1] and (i + 1 >= len(out) or cand != out[i + 1]):
                out[i] = cand
                # one paired partner, balanced between a d1 neighbour (i+1) and
                # a d4 neighbour (i-4) so the {1,4} excess is symmetric as in LP
                part = i + 1 if rng.random() < 0.5 else i - 4
                if 5 <= part < len(out):
                    c2 = out[part - 5]
                    if c2 != out[part - 1] and (
                        part + 1 >= len(out) or c2 != out[part + 1]
                    ):
                        out[part] = c2
                i += 5
                continue
        i += 1
    return out


def stats(flat, word_of):
    n = len(flat)
    doub = sum(1 for i in range(n - 1) if flat[i] == flat[i + 1])
    trip = sum(1 for i in range(n - 2) if flat[i] == flat[i + 1] == flat[i + 2])
    freq = Counter(flat)
    nioc = M * sum(c * (c - 1) for c in freq.values()) / (n * (n - 1))
    # within-word d5 IoC
    ww = tot = 0
    starts: dict[int, list[int]] = {}
    for i, w in enumerate(word_of):
        starts.setdefault(w, []).append(i)
    for _w, idxs in starts.items():
        for k in range(len(idxs) - 5):
            if idxs[k + 5] - idxs[k] == 5:
                tot += 1
                if flat[idxs[k]] == flat[idxs[k + 5]]:
                    ww += 1
    d5_ioc = (ww / tot) / CHANCE if tot else 0.0
    # lag-5 match-pair separations
    matches = [i for i in range(n - 5) if flat[i] == flat[i + 5]]
    seps = Counter(b - a for a, b in zip(matches, matches[1:]))
    return {
        "doublets": doub,
        "triplets": trip,
        "nioc": round(nioc, 3),
        "d5_ioc": round(d5_ioc, 2),
        "pairs": {d: seps[d] for d in (1, 2, 3, 4, 5, 6)},
        "lag5_matches": len(matches),
    }


def main() -> None:
    rng = random.Random(SEED)
    words = cut_words(gen_plaintext(load_trigram(), 13000, rng), rng)
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
    sigma = tune(
        perm_from_cycles([9, 7, 7, 3, 3], rng),
        lambda s: (diag_rate(P1, s) - 0.0079) ** 2,
        rng,
        iters=10000,
    )
    base0 = list(range(M))
    rng.shuffle(base0)

    cipher_words = encipher(words, g, base0, sigma)
    flat, word_of = flatten_with_bounds(cipher_words)

    print(
        "LP targets (12,956 runes): doublets 86, triplets 0, nIoC 1.00, "
        "d5_ioc 1.43; lag-5 pairs d1 29, d4 28, d2/d3/d5 ~14 (at chance)"
    )
    print("Selectivity test: does d1,d4 >> d2,d3,d5? (LP: yes; that's the anomaly)\n")

    def show(label, flat_):
        s = stats(flat_, word_of)
        p = s["pairs"]
        chance = (p[2] + p[3] + p[5]) / 3
        print(
            f"{label}: doub {s['doublets']} trip {s['triplets']} nIoC {s['nioc']} "
            f"d5_ioc {s['d5_ioc']} | pairs {p} | "
            f"d1+d4={p[1] + p[4]} vs 2*(d2,d3,d5 mean)={2 * chance:.0f}"
        )

    show("walk alone                ", flat)
    for rate in (0.001, 0.002, 0.004):
        ov = copy_overlay(flat, word_of, rate, random.Random(SEED + 1))
        show(f"walk + copy overlay r={rate:.3f}", ov)


if __name__ == "__main__":
    main()
