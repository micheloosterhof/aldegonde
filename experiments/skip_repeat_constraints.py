# ABOUTME: Generalises the doublet constraint on g to every within-word distance,
# ABOUTME: giving three simultaneous tests on g, g^2 and g^3 at once.
"""The doublet filter is one member of a five-member family.

Within a word base_w is a single bijection, so for positions j < k at distance
d = k - j,

    c_j == c_k   <=>   g^(j mod 5)(p_j) == g^(k mod 5)(p_k)   <=>   p_j == g^d(p_k)

with d read mod 5. Three consequences worth separating:

  d = 1   the doublet case, the one distance where the corpus departs from
          chance at all
  d = 5   g^0 is the identity, so c_j == c_k <=> p_j == p_k: this is exactly the
          "same alphabet at distance 5" theory, already known
  d = 2,3,4  three further constraints, on g^2, g^3, g^4, that nothing has used

Every one of them is free of base_0 and of sigma, and all four constrain the
SAME g -- g has order 5, so its powers are not independent unknowns. A candidate
must predict all of the observed repeat counts, not just the doublet count.

What the corpus actually shows is that only d=1 carries anything: d=2 and d=3
sit on the random-g mean to within z = 0.1, so they neither confirm nor refute a
candidate. The d=1 deficit is real, but `boundary_doublet_sigma` shows it is a
uniform property of the whole stream rather than a fact about g.

The plaintext distance-d pair distribution comes from the shipped runeglish
tables: d=1 is the bigram table outright, d=2 marginalises the middle rune out
of the trigrams, d=3 marginalises the middle two out of the quadgrams. d=4 would
need pentagrams, which are not shipped, so it is reported as unavailable rather
than guessed at.
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import load_words, perm_from_cycles  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.stats.compare import loadgrams  # noqa: E402

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
DISTANCES = (1, 2, 3)
TABLE = {1: "bigrams.txt", 2: "trigrams.txt", 3: "quadgrams.txt"}


def pair_matrix(d: int) -> np.ndarray:
    """P[a, b] = probability plaintext holds a then b at distance d, within a word."""
    grams = loadgrams("aldegonde.data.ngrams.runeglish", TABLE[d])
    P = np.zeros((M, M))
    width = d + 1
    for gram, n in grams.items():
        if len(gram) != width:
            continue
        a, b = gram[0], gram[-1]
        if a in IDX and b in IDX:
            P[IDX[a], IDX[b]] += n
    return P / P.sum()


def observed_repeats(words: list[list[int]], d: int) -> tuple[int, int]:
    """Within-word pairs at distance d, and how many of them are equal runes."""
    total = hits = 0
    for w in words:
        for j in range(len(w) - d):
            total += 1
            if w[j] == w[j + d]:
                hits += 1
    return total, hits


def predict(P: np.ndarray, npairs: int, gd: np.ndarray) -> float:
    """Expected equal-rune count at this distance if the power of g is gd."""
    return npairs * sum(P[gd[b], b] for b in range(M))


def power(g: np.ndarray, k: int) -> np.ndarray:
    out = np.arange(M)
    for _ in range(k):
        out = g[out]
    return out


def main() -> None:
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    words = load_words()
    rng = random.Random(3301)
    print(f"corpus: {len(words):,} words\n")

    tables = {d: pair_matrix(d) for d in DISTANCES}
    counts = {d: observed_repeats(words, d) for d in DISTANCES}

    # what a random order-5 g predicts at each distance, for reference
    randoms: dict[int, list[float]] = {d: [] for d in DISTANCES}
    for _ in range(trials):
        g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
        for d in DISTANCES:
            randoms[d].append(predict(tables[d], counts[d][0], power(g, d)))

    print(f"{'d':>2}{'pairs':>9}{'observed':>10}{'random g':>18}{'z':>8}")
    for d in DISTANCES:
        npairs, hits = counts[d]
        mu = statistics.mean(randoms[d])
        sd = statistics.stdev(randoms[d])
        z = (hits - mu) / sd
        print(f"{d:>2}{npairs:>9,}{hits:>10}{mu:>11.0f} +-{sd:>4.0f}{z:>8.1f}")

    print("\nd=4 needs pentagrams, which are not shipped: unavailable")
    print("d=5 is g^0 = identity, so it tests the plaintext directly, not g")

    # How low can any order-5 g drive each count? Conjugation by a transposition
    # preserves the cycle type, so the hillclimb stays inside the order-5 class.
    print(f"\n{'d':>2}{'lowest any g reaches':>24}")
    for d in DISTANCES:
        P, (npairs, hits) = tables[d], counts[d]
        lo = None
        for _ in range(trials // 10):
            g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
            for _ in range(300):
                i, j = rng.randrange(M), rng.randrange(M)
                t = np.arange(M)
                t[i], t[j] = j, i
                h = t[g[t]]
                if predict(P, npairs, power(h, d)) < predict(P, npairs, power(g, d)):
                    g = h
            v = predict(P, npairs, power(g, d))
            lo = v if lo is None else min(lo, v)
        assert lo is not None
        reach = "reachable" if lo <= hits else "OUT OF REACH"
        print(f"{d:>2}{lo:>24.0f}   observed {hits} is {reach}")


if __name__ == "__main__":
    main()
