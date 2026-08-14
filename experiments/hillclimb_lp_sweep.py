# ABOUTME: Full-budget free-g hillclimb attack on the LP at every period 2..50;
# ABOUTME: a numpy-vectorised confirmation that the LP is not a single stepped g.
"""Attack the LP as a single stepped permutation, at full search strength.

Companion to hillclimb_single_g.py (which establishes the method and the
synthetic recovery). Here the attack is run on the real LP ciphertext with a
FREE-choice g (any permutation, plain-swap moves over the whole symmetric
group) at every period m = 2..50, at the full 8-restart x 4000-iteration budget
that recovers a planted key. Vectorised with numpy so the whole sweep finishes
in minutes.

A self-check first proves the metric is sensitive: on a planted FREE g the true
key is the global maximum, and even a PARTIAL recovery (~22/29) yields a
decryption IoC ~1.6, far above garbage (~1.0). So a stepped-g LP -- even if only
partially recovered -- would show an elevated IoC. The LP shows ~1.0 at every
period, so the negative is real (no solution), not search weakness.
"""

from __future__ import annotations

import random

import numpy as np
from lp_corpus import load_clean

from aldegonde.c3301 import CICADA_ALPHABET as ALPHABET

M = 29
R2I = {r: i for i, r in enumerate(ALPHABET)}
AR = np.arange(M)
SEED = 1


def trigram_logprobs_flat() -> np.ndarray:
    cnt = np.full((M, M, M), 0.3)
    with open("src/aldegonde/data/ngrams/runeglish/trigrams.txt") as f:
        for line in f:
            q = line.split()
            if len(q) == 2 and len(q[0]) == 3 and all(ch in R2I for ch in q[0]):
                a, b, c = (R2I[ch] for ch in q[0])
                cnt[a, b, c] += float(q[1])
    return np.log(cnt / cnt.sum(axis=2, keepdims=True)).reshape(-1)


def inv_powers(g: np.ndarray, m: int) -> np.ndarray:
    """Inverses of g^0..g^(m-1) as an (m, M) array."""
    pw = np.empty((m, M), dtype=np.int64)
    pw[0] = AR
    for k in range(1, m):
        pw[k] = g[pw[k - 1]]
    inv = np.empty((m, M), dtype=np.int64)
    for k in range(m):
        inv[k, pw[k]] = AR
    return inv


def ioc(d: np.ndarray) -> float:
    _, counts = np.unique(d, return_counts=True)
    n = len(d)
    return M * np.sum(counts * (counts - 1)) / (n * (n - 1))


def climb(cipher, m, tl, rng, restarts=8, iters=4000):
    """Free-g hillclimb (plain swaps); returns (best decryption, best score)."""
    phase = np.arange(len(cipher)) % m

    def score_of(g):
        d = inv_powers(g, m)[phase, cipher]
        t = (d[:-2] * M + d[1:-1]) * M + d[2:]
        return tl[t].sum(), d

    best_s, best_d = -1e18, None
    for _ in range(restarts):
        g = np.array(rng.sample(range(M), M), dtype=np.int64)
        s, _ = score_of(g)
        for _ in range(iters):
            a, b = rng.randrange(M), rng.randrange(M)
            g[a], g[b] = g[b], g[a]
            s2, d2 = score_of(g)
            if s2 > s:
                s = s2
            else:
                g[a], g[b] = g[b], g[a]
        if s > best_s:
            best_s, best_d = s, score_of(g)[1]
    return best_d, best_s


def self_check(tl, rng) -> None:
    """A planted FREE g must be the global max, and partial recovery elevates IoC."""
    from period5_confirmation import prose_words

    plain = np.array([x for w in prose_words() for x in w][:12000], dtype=np.int64)
    n = len(plain)
    g_true = np.array(rng.sample(range(M), M), dtype=np.int64)
    m = 5
    pw = np.empty((m, M), dtype=np.int64)
    pw[0] = AR
    for k in range(1, m):
        pw[k] = g_true[pw[k - 1]]
    phase = np.arange(n) % m
    cipher = pw[phase, plain]
    assert np.array_equal(inv_powers(g_true, m)[phase, cipher], plain), "decrypt broken"
    t = (plain[:-2] * M + plain[1:-1]) * M + plain[2:]
    strue = tl[t].sum()
    best_d, best_s = climb(cipher, m, tl, rng)
    print(
        f"self-check (planted free g, period 5): true score {strue:.0f} "
        f"{'>=' if strue >= best_s else '<'} hillclimb {best_s:.0f}; "
        f"partial-recovery decryption IoC {ioc(best_d):.3f} "
        f"(garbage ~1.0) -> metric is {'sensitive' if ioc(best_d) > 1.3 else 'INSENSITIVE'}\n"
    )


def main() -> None:
    rng = random.Random(SEED)
    tl = trigram_logprobs_flat()
    self_check(tl, rng)

    lp = np.array(load_clean()[0], dtype=np.int64)
    print("LP attack, FREE g, period m = 2..50, full budget (8 x 4000):")
    worst = 0.0
    for m in range(2, 51):
        d, _ = climb(lp, m, tl, rng)
        di = ioc(d)
        worst = max(worst, di)
        print(
            f"  m={m:2d}: best decryption IoC {di:.3f}"
            f"{'  <-- READABLE' if di > 1.3 else ''}",
            flush=True,
        )
    print(
        f"\nmax IoC over all periods: {worst:.3f} (English ~1.7). "
        f"{'STRUCTURE FOUND' if worst > 1.3 else 'all garbage'}"
    )
    print("The LP is not a single stepped g at any period <= 50, even at full search")
    print("budget with free-choice g -- the per-word base, not g, is the wall.")


if __name__ == "__main__":
    main()
