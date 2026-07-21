#!/usr/bin/env python3
# ABOUTME: Minimum doublet rate of the advance disk via the assignment problem,
# ABOUTME: testing whether the advance can be built doublet-free (hold-only doublets).
"""If the advance step is a permutation g applied every letter, an advance-step
ciphertext doublet needs plaintext bigram (g(x), x). The advance-doublet rate is

    rate(g) = (1 / T) * sum_x  M[g(x)][x]

where M[a][b] = count of plaintext bigram "ab". Minimizing this over permutations
g is a linear assignment problem (Hungarian). If the minimum is ~0, the advance
disk can be arranged essentially doublet-free, so the observed LP doublet rate
(0.0063) cannot come from the advance -- it must come from the 1-in-5 HOLD, which
passes plaintext doublets through unchanged: (1/5)*plaintext-doublet.

We also report the cycle structure of the optimal g (can it be five 5-cycles, the
grid form?) and how the naive Gematria-order diagonal compares.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from aldegonde import c3301

ALPH = c3301.CICADA_ALPHABET
N = len(ALPH)
R2I = {r: i for i, r in enumerate(ALPH)}
BIGRAM_FILE = "src/aldegonde/data/ngrams/runeglish/bigrams.txt"


def load_bigram_matrix() -> np.ndarray:
    """M[a][b] = count of plaintext bigram (a then b)."""
    m = np.zeros((N, N), dtype=float)
    with open(BIGRAM_FILE) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2:
                continue
            gram, cnt = parts
            if len(gram) != 2 or gram[0] not in R2I or gram[1] not in R2I:
                continue
            m[R2I[gram[0]]][R2I[gram[1]]] = float(cnt)
    return m


def diag_rate(m: np.ndarray, g: list[int]) -> float:
    """Advance-doublet rate for permutation g: (1/T) sum_x M[g(x)][x]."""
    total = m.sum()
    return sum(m[g[x]][x] for x in range(N)) / total


def cycle_structure(g: list[int]) -> list[int]:
    seen = [False] * N
    lengths = []
    for start in range(N):
        if seen[start]:
            continue
        length = 0
        x = start
        while not seen[x]:
            seen[x] = True
            x = g[x]
            length += 1
        lengths.append(length)
    return sorted(lengths, reverse=True)


def cycles_to_perm(cyclens: list[int], layout: list[int]) -> list[int]:
    """Build g on the runes in `layout` (a permutation of 0..N-1); the first
    sum(cyclens) runes form cycles of the given lengths, the rest are fixed."""
    g = list(range(N))
    p = 0
    for clen in cyclens:
        cyc = layout[p:p + clen]
        for k in range(clen):
            g[cyc[k]] = cyc[(k + 1) % clen]
        p += clen
    return g


def anneal_cycletype(
    m: np.ndarray, cyclens: list[int], seed: int, restarts: int = 20,
    iters: int = 40000,
) -> tuple[float, list[int]]:
    """Minimize the advance diagonal over all permutations with the given cycle
    lengths (rest fixed), via simulated annealing with restarts. Deterministic."""
    import random

    rng = random.Random(seed)
    best_rate = 1.0
    best_g = list(range(N))
    for rs in range(restarts):
        layout = list(range(N))
        rng.shuffle(layout)
        cur_rate = diag_rate(m, cycles_to_perm(cyclens, layout))
        for i in range(iters):
            temp = 0.02 * (1 - i / iters)  # linear cooling
            a, b = rng.randrange(N), rng.randrange(N)
            layout[a], layout[b] = layout[b], layout[a]
            r = diag_rate(m, cycles_to_perm(cyclens, layout))
            if r <= cur_rate or rng.random() < 2.718 ** (-(r - cur_rate) / temp):
                cur_rate = r
                if r < best_rate:
                    best_rate = r
                    best_g = cycles_to_perm(cyclens, layout)
            else:
                layout[a], layout[b] = layout[b], layout[a]
    return best_rate, best_g


def main() -> None:
    m = load_bigram_matrix()
    total = m.sum()
    chance = 1.0 / N

    # Plaintext doublet rate (the diagonal of M): p[i]=p[i-1].
    plain_doublet = np.trace(m) / total

    # Cost[x][r] = M[r][x] = prob that choosing g(x)=r contributes.
    # Minimize sum_x Cost[x][g(x)]  -> assignment on Cost.
    cost = m.T.copy()
    col_ind, row_ind = linear_sum_assignment(cost)  # col_ind = x, row_ind = g(x)
    g_min = [0] * N
    for x, r in zip(col_ind, row_ind):
        g_min[x] = r
    min_rate = diag_rate(m, g_min)

    # Maximum (worst) diagonal, for scale.
    row_ind_max, col_ind_max = linear_sum_assignment(cost, maximize=True)
    g_max = [0] * N
    for x, r in zip(row_ind_max, col_ind_max):
        g_max[x] = r
    max_rate = diag_rate(m, g_max)

    # Naive Gematria-order identity-ish "shift by 1 in gematria order" disk.
    g_shift = [(x + 1) % N for x in range(N)]
    shift_rate = diag_rate(m, g_shift)

    # How many diagonal cells in g_min are effectively zero (< chance/100)?
    tiny = chance / 100.0
    zeros = sum((m[g_min[x]][x] / total) < tiny for x in range(N))
    fixed = sum(g_min[x] == x for x in range(N))

    print(f"corpus bigram total: {total:.3e}")
    print(f"chance doublet rate (1/29):        {chance:.4f}")
    print(f"plaintext doublet rate (trace):    {plain_doublet:.4f}")
    print(f"  -> hold-only prediction /5:      {plain_doublet / 5:.4f}")
    print(f"LP observed within-word doublet:   0.0063")
    print()
    print(f"advance-disk diagonal rate:")
    print(f"  MIN (optimal assignment):        {min_rate:.6f}")
    print(f"  gematria shift-by-1 disk:        {shift_rate:.4f}")
    print(f"  MAX (worst assignment):          {max_rate:.4f}")
    print()
    print(f"optimal g: cycle structure = {cycle_structure(g_min)}")
    print(f"  fixed points: {fixed}, near-zero diagonal cells (<{tiny:.1e}): "
          f"{zeros}/{N}")
    print()
    r5, g5 = anneal_cycletype(m, [5, 5, 5, 5, 5], seed=3301)
    print(f"order-5 advance (five 5-cycles + 4 fixed) -- grid/g^5=id model:")
    print(f"  annealed MIN diagonal rate:      {r5:.6f}   ({cycle_structure(g5)})")
    r4, g4 = anneal_cycletype(m, [4, 4, 4, 4, 4, 4, 4], seed=3301)
    hold4 = 0.8 * r4 + 0.2 * plain_doublet
    print(f"order-4 advance (seven 4-cycles + 1 fixed) -- stay-slot/hold model:")
    print(f"  annealed MIN diagonal rate:      {r4:.6f}   ({cycle_structure(g4)})")
    print(f"  total with 1-in-5 hold (4/5 adv + 1/5 plain): {hold4:.4f}")
    print()
    print("Discriminator: order-5 diagonal IS the doublet rate (no hold); if its")
    print("floor > 0.0063 the pure-grid model is refuted. Order-4+hold total is")
    print("(4/5)adv+(1/5)plain; if ~0.0063 the stay-slot model fits.")


if __name__ == "__main__":
    main()
