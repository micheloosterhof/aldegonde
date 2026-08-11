# ABOUTME: Searches g by the doublet count it predicts, the one strong filter
# ABOUTME: that needs neither base_0 nor sigma, then scores survivors properly.
"""Search g by what it predicts about doublets, not by enumerating layouts.

Within a word base_w is a single bijection, so a ciphertext doublet means

    c_k == c_{k+1}   <=>   p_k == g(p_{k+1})

and the expected number of within-word doublets is the plaintext bigram mass
lying along g's own graph: N * sum_b P(g(b), b). That involves neither base_0
nor sigma, and it is sharp. Against the shipped runeglish bigram table a random
order-5 permutation predicts 343 +- 97, while the corpus holds 63; none of 4,000
random permutations predicted as low. The lowest any order-5 permutation can
reach is about 17, so 63 is attainable but only in the extreme tail.

That inverts the search. Rather than enumerate layouts and hope one lands in the
tail, anneal directly to the observed count: keep the permutations predicting
near 63 and discard the rest. It is the one constraint found so far that both
discriminates strongly and rests on nothing beyond the walk's within-word
structure -- unlike DJU-BEI, which turned out to be either impossible or vacuous
depending on how it is stated.

Surviving g are then crossed with sigma built to satisfy the crib's two pinned
points, and scored by the quadgram fit of the recovered base_0, which planted-key
work shows is a superb verifier even though it is a useless gradient.
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from construction_search import crib_ok  # noqa: E402
from walk_verifier import (  # noqa: E402
    dewalk_perms,
    load_quadgrams,
    load_words,
    order,
    perm_from_cycles,
    step_products,
)

from aldegonde import c3301  # noqa: E402
from aldegonde.stats.compare import loadgrams  # noqa: E402

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
TARGET_BAND = 8  # +- this many doublets around the observed count


def bigram_matrix() -> np.ndarray:
    grams = loadgrams("aldegonde.data.ngrams.runeglish", "bigrams.txt")
    B = np.zeros((M, M))
    for pair, n in grams.items():
        if len(pair) == 2 and pair[0] in IDX and pair[1] in IDX:
            B[IDX[pair[0]], IDX[pair[1]]] = n
    return B / B.sum()


def anneal_to_target(
    B: np.ndarray, npairs: int, target: int, rng: random.Random, iters: int = 9000
) -> tuple[np.ndarray, float]:
    """An order-5 permutation whose predicted doublet count is near `target`.

    Moves conjugate by a transposition, which preserves cycle type and so keeps
    the order at 5 throughout.
    """
    g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
    predict = lambda p: npairs * sum(B[p[b], b] for b in range(M))  # noqa: E731
    value = predict(g)
    for _ in range(iters):
        i, j = rng.randrange(M), rng.randrange(M)
        if i == j:
            continue
        t = np.arange(M)
        t[i], t[j] = j, i
        h = t[g[t]]
        hv = predict(h)
        if abs(hv - target) <= abs(value - target):
            g, value = h, hv
    return g, value


def cycle_sigma(pinned: dict[int, int], rng: random.Random) -> np.ndarray | None:
    """A 29-cycle honouring the crib's pinned points, or None if impossible."""
    nxt: dict[int, int] = dict(pinned)
    if len(set(nxt.values())) != len(nxt):
        return None
    used_from, used_to = set(nxt), set(nxt.values())
    free_from = [x for x in range(M) if x not in used_from]
    free_to = [x for x in range(M) if x not in used_to]
    for _ in range(200):
        rng.shuffle(free_to)
        trial = dict(nxt)
        ok = True
        for a, b in zip(free_from, free_to):
            if a == b:
                ok = False
                break
            trial[a] = b
        if not ok:
            continue
        # a single 29-cycle, not several disjoint ones
        seen, x = 0, 0
        while True:
            x = trial[x]
            seen += 1
            if x == 0:
                break
            if seen > M:
                break
        if seen == M:
            perm = np.zeros(M, dtype=int)
            for a, b in trial.items():
                perm[a] = b
            return perm
    return None


def main() -> None:
    tries = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    words = load_words()
    lengths = [len(w) for w in words]
    cipher = np.array([r for w in words for r in w])
    npairs = sum(len(w) - 1 for w in words)
    observed = sum(1 for w in words for k in range(len(w) - 1) if w[k] == w[k + 1])
    B = bigram_matrix()
    quad = load_quadgrams()
    rng = random.Random(3301)
    print(f"corpus: {npairs} within-word pairs, {observed} doublets")
    print(f"annealing {tries} order-5 g toward a predicted count of {observed}\n")

    kept: list[tuple[np.ndarray, float, dict[int, int]]] = []
    for _ in range(tries):
        g, value = anneal_to_target(B, npairs, observed, rng)
        if abs(value - observed) > TARGET_BAND or order(g) != 5:
            continue
        ok, pinned = crib_ok(g)
        if ok:
            kept.append((g, value, pinned))
    print(f"g in the doublet band and consistent with the crib: {len(kept)}")
    if not kept:
        print("none -- the band and the crib are jointly unsatisfiable here")
        return

    scored: list[tuple[float, float]] = []
    for g, value, pinned in kept:
        for _ in range(3):
            sigma = cycle_sigma(pinned, rng)
            if sigma is None:
                continue
            Ms = step_products(g, sigma, lengths)
            D = dewalk_perms(g, Ms, words)
            from walk_verifier import solve_base0

            fit, _ = solve_base0(
                cipher, D, quad[0], quad[1], rng, restarts=1, iters=900
            )
            scored.append((fit, value))
    if not scored:
        print("no sigma could honour the pinned points")
        return
    scored.sort(reverse=True)
    fits = [f for f, _ in scored]
    print(f"\nscored {len(scored)} (g, sigma) pairs by base_0 quadgram fit")
    print(
        f"  best {max(fits):.4f}   mean {statistics.mean(fits):.4f}"
        f"   sd {statistics.stdev(fits):.4f}"
    )
    print(
        f"  best z = {(max(fits) - statistics.mean(fits)) / statistics.stdev(fits):+.2f}"
    )
    print("  planted-key reference: true key about -1.3, random about -4.9")
    for fit, value in scored[:5]:
        print(f"     fit {fit:.4f}  predicted doublets {value:.1f}")


if __name__ == "__main__":
    main()
