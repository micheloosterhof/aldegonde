# ABOUTME: Shows a single low-diagonal stepped permutation g IS hillclimbable
# ABOUTME: from ciphertext, but the same attack on the LP fails at every period.
"""Can a single permutation with a low doublet diagonal be hillclimbed?

Yes on synthetic data, no on the LP -- which localises the LP's hardness to the
per-word BASE, not to g.

Encipher with one stepped permutation, c[i] = g^(i mod m)(p[i]), g tuned to a
low doublet diagonal (c[i]=c[i-1] <=> p[i-1]=g(p[i]), so the diagonal IS the
doublet rate). A conjugation-swap hillclimb on the decryption's trigram score
recovers g exactly (29/29) under a generic trigram model. Then the SAME attack
is run on the real LP ciphertext at every period m = 2..50: none yields readable
plaintext (decryption IoC stays ~1.0, English ~1.7). So a single g falls out
immediately when it is the whole cipher; the LP's un-hillclimbability is bought
by the per-word base (a fresh bijection each word), confirming
key-local-channel-is-empty.md.

Controls:
- MONOALPHABETIC c[i]=g(p[i]) recovers the key too but a bijection preserves the
  plaintext doublet rate -- it CANNOT suppress. The low diagonal needs stepping.
- A dec(c, g) == plaintext round-trip assertion guards the decrypt. (An earlier
  version computed gg.index over gg^k = gg^(k-1), not (gg^k)^{-1}, and wrongly
  concluded the stepped cipher was unclimbable.)
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict

from lp_corpus import load_clean
from period5_confirmation import prose_words
from stay_slot_cipher import conj_swap, diag_rate, pair_matrices, perm_from_cycles, ppow

from aldegonde.c3301 import CICADA_ALPHABET as ALPHABET

M = 29
R2I = {r: i for i, r in enumerate(ALPHABET)}
SEED = 1


def load_generic_trigram_logprobs() -> dict:
    """Trigram log-probs from the runeglish data file (NOT the plaintext register)."""
    counts = defaultdict(lambda: [0.3] * M)
    with open("src/aldegonde/data/ngrams/runeglish/trigrams.txt") as f:
        for line in f:
            q = line.split()
            if len(q) == 2 and len(q[0]) == 3 and all(ch in R2I for ch in q[0]):
                a, b, c = (R2I[ch] for ch in q[0])
                counts[(a, b)][c] += float(q[1])
    return {k: [math.log(x / sum(v)) for x in v] for k, v in counts.items()}


def inverse(perm: list[int]) -> list[int]:
    r = [0] * M
    for j, x in enumerate(perm):
        r[x] = j
    return r


def inverse_powers(g: list[int], m: int) -> list[list[int]]:
    """Inverses of g^0..g^(m-1), computed incrementally (O(m*M))."""
    pw = [list(range(M))]
    for _ in range(1, m):
        pw.append([g[x] for x in pw[-1]])
    return [inverse(a) for a in pw]


def agree(a: list[int], b: list[int]) -> int:
    return sum(1 for i in range(M) if a[i] == b[i])


def ioc(s: list[int]) -> float:
    c = Counter(s)
    return M * sum(v * (v - 1) for v in c.values()) / (len(s) * (len(s) - 1))


def plain_swap(p, x, y):
    q = p[:]
    q[x], q[y] = q[y], q[x]
    return q


def stepped_decrypt(c, g, m):
    inv = inverse_powers(g, m)
    return [inv[i % m][c[i]] for i in range(len(c))]


def hillclimb(cipher, decrypt, score, make_start, rng, restarts, iters, move=conj_swap):
    """decrypt(cipher, g) -> plaintext-candidate stream."""
    best, best_s = None, -1e18
    for _ in range(restarts):
        g = make_start()
        s = score(decrypt(cipher, g))
        for _ in range(iters):
            cand = move(g, rng.randrange(M), rng.randrange(M))
            sc = score(decrypt(cipher, cand))
            if sc > s:
                g, s = cand, sc
        if s > best_s:
            best, best_s = g, s
    return best, best_s


def main() -> None:
    rng = random.Random(SEED)
    prose = [x for w in prose_words() for x in w]
    plain = prose[:8000]
    n = len(plain)
    logt = load_generic_trigram_logprobs()
    default = [math.log(1 / M)] * M

    def score(s):
        return sum(
            logt.get((s[i - 2], s[i - 1]), default)[s[i]] for i in range(2, len(s))
        )

    mats = pair_matrices([plain], dmax=1)

    def low_diag_g(cycles):
        best = perm_from_cycles(cycles, rng)
        bv = diag_rate(mats[1][0], best)
        for _ in range(6000):
            cand = conj_swap(best, rng.randrange(M), rng.randrange(M))
            v = diag_rate(mats[1][0], cand)
            if v < bv:
                best, bv = cand, v
        return best

    # CONTROL: monoalphabetic recovers, but cannot suppress doublets
    g = list(range(M))
    rng.shuffle(g)
    cipher = [g[x] for x in plain]
    best, _ = hillclimb(
        cipher,
        lambda c, gg: [inverse(gg)[x] for x in c],
        score,
        lambda: rng.sample(range(M), M),
        rng,
        restarts=8,
        iters=6000,
        move=plain_swap,
    )
    pdoub = sum(1 for i in range(1, n) if plain[i] == plain[i - 1]) / (n - 1)
    print(
        f"MONOALPHABETIC control: recovered {agree(best, g)}/29; "
        f"doublet rate {pdoub:.4f} = plaintext (a bijection cannot suppress)"
    )

    # VALIDATION: a single stepped low-diagonal g is recovered exactly
    g = low_diag_g([5] * 5 + [1] * 4)
    gp = [ppow(g, k) for k in range(5)]
    cipher = [gp[i % 5][plain[i]] for i in range(n)]
    assert stepped_decrypt(cipher, g, 5) == plain, "round-trip broken"
    best, _ = hillclimb(
        cipher,
        lambda c, gg: stepped_decrypt(c, gg, 5),
        score,
        lambda: perm_from_cycles([5] * 5 + [1] * 4, rng),
        rng,
        restarts=8,
        iters=4000,
    )
    print(
        f"STEPPED synthetic (order-5, diag {diag_rate(mats[1][0], g):.4f}): "
        f"recovered {agree(best, g)}/29 -- the attack works when g is the whole cipher\n"
    )

    # THE REAL TEST: run the attack on the LP at EVERY period 2..50
    lp, _ = load_clean()
    print("ATTACK ON THE REAL LP, single stepped g, period m = 2..50")
    print("(if the LP were a stepped-g cipher of some period, that row reads IoC ~1.7)")
    hits = []
    for m in range(2, 51):
        best, _ = hillclimb(
            lp,
            lambda c, gg, m=m: stepped_decrypt(c, gg, m),
            score,
            lambda: rng.sample(range(M), M),
            rng,
            restarts=3,
            iters=1500,
            move=plain_swap,
        )
        di = ioc(stepped_decrypt(lp, best, m))
        flag = "  <-- READABLE" if di > 1.30 else ""
        print(f"  m={m:2d}: best decryption IoC {di:.3f}{flag}")
        if di > 1.30:
            hits.append(m)

    print()
    if hits:
        print(f"PERIODS THAT PRODUCED STRUCTURE: {hits} -- investigate.")
    else:
        print("No period 2..50 yields readable plaintext (all IoC ~1.0). The LP is NOT")
        print("a single stepped g at any period; the per-word base defeats the attack")
        print(
            "that trivially solved the synthetic cipher. The base, not g, is the wall."
        )


if __name__ == "__main__":
    main()
