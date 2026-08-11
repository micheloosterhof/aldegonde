# ABOUTME: Discriminates order-5-g (advance every letter) from stay-slot (order-4
# ABOUTME: + 1-in-5 hold) by enciphering real runeglish words and matching d1-d6.
"""Both mechanisms reproduce the d5 echo and pass the coincidence battery, and
both give d1 != d6 (the g-relation acts on different skip-gram statistics at
different distances). The discriminator is the FULL within-word d1-d6 profile
when each mechanism enciphers REAL runeglish words (which carry the genuine
distance-6 skip-gram structure that observed d6=0.0245 depends on -- a trigram
generator cannot).

Within a word c[j] = base(g^e(p[j])); coincidence c[i]=c[i+d] is invariant to
the per-word base and sigma (bijections applied uniformly inside the word), so
we drop them and apply only g / the hold schedule.

  v1 (order-5-g):  e_j = j mod 5, advance every letter, g^5 = id.
  v2 (stay-slot):  advance a rich order-4 g4 four-in-five, HOLD once at a keyed
                   per-word slot r_w; net over the 5-window is g4^4 = id.

Observed LP within-word profile:
  d1 0.0064  d2 0.0347  d3 0.0370  d4 0.0410  d5 0.0492  d6 0.0245
"""

from __future__ import annotations

import random
from collections import defaultdict

from aldegonde import c3301
from experiments.d5_partial_leak import to_runeglish
from experiments.stay_slot_cipher import (
    diag_rate,
    pair_matrices,
    perm_from_cycles,
    ppow,
    tune,
)

ALPH = c3301.CICADA_ALPHABET
M = len(ALPH)
TOKEN2I = {tok: i for i, tok in enumerate(c3301.CICADA_ENGLISH_ALPHABET)}
DICT = "/usr/share/dict/web2"
SEED = 3301
# LP word-length distribution (stay_slot_cipher.LEN_DIST) to match d-pair weights
LEN_DIST = {
    1: 99,
    2: 465,
    3: 726,
    4: 514,
    5: 318,
    6: 252,
    7: 214,
    8: 159,
    9: 77,
    10: 51,
    11: 28,
    12: 18,
    13: 4,
    14: 3,
}
OBSERVED = {1: 0.0064, 2: 0.0347, 3: 0.0370, 4: 0.0410, 5: 0.0492, 6: 0.0245}


def real_words(rng: random.Random, scale: int = 30) -> list[list[int]]:
    """Real runeglish words grouped by length, sampled to match LEN_DIST*scale."""
    by_len: dict[int, list[list[int]]] = defaultdict(list)
    with open(DICT) as f:
        for line in f:
            w = line.strip()
            if not w.isalpha():
                continue
            r = [TOKEN2I[x] for x in to_runeglish(w.upper()) if x in TOKEN2I]
            if 1 <= len(r) <= 14:
                by_len[len(r)].append(r)
    out: list[list[int]] = []
    for length, count in LEN_DIST.items():
        pool = by_len.get(length, [])
        if not pool:
            continue
        out += [pool[rng.randrange(len(pool))] for _ in range(count * scale)]
    rng.shuffle(out)
    return out


def profile(words: list[list[int]], dmax: int = 6) -> dict[int, float]:
    """Within-word coincidence rate at each distance."""
    m = [0] * (dmax + 1)
    e = [0] * (dmax + 1)
    for w in words:
        for d in range(1, dmax + 1):
            for i in range(len(w) - d):
                e[d] += 1
                m[d] += w[i] == w[i + d]
    return {d: (m[d] / e[d] if e[d] else 0.0) for d in range(1, dmax + 1)}


def enc_v1(words: list[list[int]], g5: list[int]) -> list[list[int]]:
    gp = [ppow(g5, k) for k in range(5)]
    return [[gp[j % 5][p] for j, p in enumerate(w)] for w in words]


def enc_v2(
    words: list[list[int]], g4: list[int], rng: random.Random
) -> list[list[int]]:
    g4p = [ppow(g4, k) for k in range(4)]
    out = []
    for w in words:
        r = rng.randrange(5)  # per-word hold slot
        e = 0
        cw = []
        for j, p in enumerate(w):
            if j > 0 and j % 5 != r:
                e = (e + 1) % 4
            cw.append(g4p[e][p])
        out.append(cw)
    return out


def tune_g(
    words: list[list[int]],
    cyclens: list[int],
    rng: random.Random,
    dshoulder: tuple[int, ...],
) -> list[int]:
    """Minimize the d1 diagonal while keeping the g^d shoulder diagonals near
    chance (reproducing observed d2/d3/d4 ~ chance)."""
    mats = pair_matrices(words, dmax=max(dshoulder))
    p1 = mats[1][0]
    chance = 1 / M

    def obj(g: list[int]) -> float:
        v = diag_rate(p1, g) * 3.0
        acc = g
        for d in dshoulder:
            acc = [g[x] for x in acc]
            v += 40.0 * (diag_rate(mats[d][0], acc) - chance) ** 2
        return v

    return min(
        (tune(perm_from_cycles(cyclens, rng), obj, rng) for _ in range(4)), key=obj
    )


def show(label: str, prof: dict[int, float]) -> None:
    cells = "  ".join(f"d{d} {prof[d]:.4f}" for d in range(1, 7))
    print(f"  {label:<16} {cells}")


def main() -> None:
    rng = random.Random(SEED)
    words = real_words(rng)
    print(f"real runeglish words: {len(words)} (matched to LP length distribution)\n")

    g5 = tune_g(words, [5] * 5 + [1] * 4, rng, (2, 3, 4))
    g4 = tune_g(words, [4] * 7 + [1], rng, (2, 3))

    prof_pt = profile(words)
    prof_v1 = profile(enc_v1(words, g5))
    prof_v2 = profile(enc_v2(words, g4, rng))

    print("within-word coincidence profile (chance = 0.0345):")
    show("plaintext", prof_pt)
    show("v1 order-5-g", prof_v1)
    show("v2 stay-slot", prof_v2)
    show("LP observed", OBSERVED)

    print("\nfit to LP (sum of squared error over d1..d6, x1e4):")
    for label, prof in (("v1 order-5-g", prof_v1), ("v2 stay-slot", prof_v2)):
        sse = sum((prof[d] - OBSERVED[d]) ** 2 for d in range(1, 7)) * 1e4
        print(f"  {label:<16} SSE={sse:.3f}")

    print("\nkey cells -- d5 echo and d6:")
    print(
        f"  plaintext d5 {prof_pt[5]:.4f} (the full-leak ceiling), d6 {prof_pt[6]:.4f}"
    )
    print("  LP d5 0.0492, d6 0.0245")


if __name__ == "__main__":
    main()
