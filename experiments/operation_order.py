# ABOUTME: Tests the operation order fork g-inner c=base(g^j(p)) vs g-outer
# ABOUTME: c=g^j(base(p)); the doublet suppression decides it, it is not a convention.
"""Is the letter-walk g applied INSIDE the per-word base, or OUTSIDE it?

The model is written g-inner: c[i] = base_w(g^(j mod 5)(p[i])). The alternative
g-outer c[i] = g^(j mod 5)(base_w(p[i])) is sometimes called an unobservable
reparametrization, but it is not -- the doublet suppression decides it.

g-inner: within a word the base cancels in a coincidence, so the doublet
relation is p[i] = g(p[i+1]) with g FIXED -- a designer tunes g's diagonal on
the plaintext adjacent-bigram table as low as wanted (the LP sits at 0.0063).

g-outer: the doublet relation is base_w(p[i]) = g(base_w(p[i+1])), i.e. the
effective letter-step is R_w = base_w^-1 . g . base_w -- a CONJUGATE of g that
changes every word. Conjugating by the fresh per-word base randomises g's tuned
diagonal, so no tuning survives and the doublet rate floors near chance:

    floor ~ P(plaintext doublet) . 4/29  +  P(non-doublet) . 25/812  ~ 0.031

(4/29 = P a value is a fixed point of g; 25/812 = P(u = g(v)) for u != v, g of
cycle type 5^5 1^4). 0.031 is 5x the observed 0.0063 and unreachable by any g.
So the order is observable and the LP is g-inner; simulation confirms.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from stay_slot_cipher import (  # noqa: E402, I001
    diag_rate,
    pair_matrices,
    perm_from_cycles,
    ppow,
    tune,
)
from word_base_plaintext_closure import register_segments_with_words  # noqa: E402

M = 29


def rand_perm(rng: random.Random) -> list[int]:
    p = list(range(M))
    rng.shuffle(p)
    return p


def within_word_doublet_rate(ct_words: list[list[int]]) -> float:
    dbl = tot = 0
    for w in ct_words:
        for i in range(len(w) - 1):
            tot += 1
            dbl += w[i] == w[i + 1]
    return dbl / tot


def encipher(words: list[list[int]], gpows: list[list[int]], rng, *, outer: bool):
    out = []
    for w in words:
        base = rand_perm(rng)
        if outer:  # c = g^j(base(p))
            out.append([gpows[j % 5][base[p]] for j, p in enumerate(w)])
        else:  # c = base(g^j(p))
            out.append([base[gpows[j % 5][p]] for j, p in enumerate(w)])
    return out


def theoretical_outer_floor(words: list[list[int]]) -> float:
    dbl = tot = 0
    for w in words:
        for i in range(len(w) - 1):
            tot += 1
            dbl += 1 if w[i] == w[i + 1] else 0
    p_doublet = dbl / tot
    return p_doublet * (4 / M) + (1 - p_doublet) * (25 / (M * (M - 1)))


def main() -> None:
    rng = random.Random(1)
    words = [list(w) for seg in register_segments_with_words() for w in seg]

    # tune g (order 5, cycle type 5^5 1^4) to a low doublet diagonal, LP-like
    p1 = pair_matrices([[x for w in words for x in w]], dmax=1)[1][0]
    g = tune(
        perm_from_cycles([5] * 5 + [1] * 4, rng),
        lambda cand: diag_rate(p1, cand),
        rng,
        iters=20000,
    )
    gpows = [ppow(g, k) for k in range(5)]
    print(f"tuned g diagonal on the register d1 table: {diag_rate(p1, g):.4f}")
    print("(LP observed within-word doublet rate: 0.0063)\n")

    # average over several fresh base draws to pin each rate
    inner = [
        within_word_doublet_rate(encipher(words, gpows, rng, outer=False))
        for _ in range(20)
    ]
    outer = [
        within_word_doublet_rate(encipher(words, gpows, rng, outer=True))
        for _ in range(20)
    ]
    inner_m = sum(inner) / len(inner)
    outer_m = sum(outer) / len(outer)

    print(
        f"g-INNER  c=base(g^j(p)):  within-word doublet rate {inner_m:.4f}  (base cancels -> = g's diagonal)"
    )
    print(
        f"g-OUTER  c=g^j(base(p)):  within-word doublet rate {outer_m:.4f}  (theory floor {theoretical_outer_floor(words):.4f})"
    )
    print()
    print("g-inner matches the LP's 0.0063 and is tunable arbitrarily low;")
    print(
        f"g-outer floors at ~{outer_m:.3f}, {outer_m / 0.0063:.0f}x the observed rate -- unreachable."
    )
    assert outer_m > 10 * inner_m, "expected g-outer to floor far above g-inner"
    print("\nVerdict: the operation order IS observable; the LP requires g-INNER.")


if __name__ == "__main__":
    main()
