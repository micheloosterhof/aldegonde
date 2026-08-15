# ABOUTME: Tests whether g is FIXED across words or varies per word (g_w). A per-word
# ABOUTME: g_w tuned only on d1 averages the d4/d6 cells to chance; a fixed g need not.
"""Is the letter-step g the same permutation every word, or a per-word family g_w?

`length-clocked-walk.md` flags this as open: g is fixed "by parsimony, not proof",
and a per-word g_w is invisible to every battery PROVIDED each g_w has order 5 and
a rare d1 diagonal. This tests the one place the proviso bites: the d4 lean and d6
dip.

Within-word distance-d coincidence <=> p[i] = g^d(p[i+d]) (base cancels). Under a
per-word g_w, the corpus d4 rate is the AVERAGE over ~470 words of diag(P4, g_w^4),
and d6 of diag(P6, g_w). Each g_w is tuned only on d1 (the doublet suppression),
which does not fix its d4/d6 diagonals, so averaging over many independent g_w
concentrates both cells near their g-ensemble mean. A single FIXED g does not
average -- the designer's one g can sit at the observed d4=0.0410 lean and
d6=0.0245 dip.

So: simulate per-word g_w (a pool of order-5, d1~0.0063 permutations, assigned
independently per word) on the same-author register plaintext, and see whether the
LP's d4 lean / d6 dip fall inside the resulting distribution. CAVEAT: the register
is a proxy for the (unknown) LP plaintext, so the d4/d6 tables are approximate;
this is a likelihood test, not a proof, and it is mild by construction.

Outcome: INCONCLUSIVE. Words are too short (<1 d4 pair per word), so the per-word
average never concentrates -- H_FIXED and H_PERWORD give the same d4/d6
distribution and the LP sits ~1.7 sigma / -0.3 sigma from both. The d4/d6 cells
cannot distinguish fixed g from per-word g_w; #4 stays invisible, confirming the
repo's "g fixed by parsimony, not proof".
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
D1_TARGET = 0.0063  # the LP within-word doublet rate
LP_D4 = 0.0410  # observed within-word distance-4 coincidence rate
LP_D6 = 0.0245  # observed within-word distance-6 coincidence rate


def within_word_pairs(words: list[list[int]], d: int) -> list[tuple[int, int]]:
    """(p[i], p[i+d]) for every within-word distance-d pair."""
    out = []
    for w in words:
        for i in range(len(w) - d):
            out.append((w[i], w[i + d]))
    return out


def coinc(pairs: list[tuple[int, int]], rel: list[int]) -> int:
    """Count of pairs with a == rel(b): g^d coincidences on real pairs."""
    return sum(1 for a, b in pairs if a == rel[b])


def rate(pairs: list[tuple[int, int]], rel: list[int]) -> float:
    """Fraction of pairs with a == rel(b): the g^d diagonal read on real pairs."""
    return coinc(pairs, rel) / len(pairs)


def tune_pool(p1, rng: random.Random, size: int) -> list[list[int]]:
    """Order-5 permutations tuned to d1 diagonal ~ D1_TARGET on the plaintext table."""
    pool = []
    for _ in range(size):
        g = tune(
            perm_from_cycles([5] * 5 + [1] * 4, rng),
            lambda cand: abs(diag_rate(p1, cand) - D1_TARGET),
            rng,
            iters=8000,
        )
        pool.append(g)
    return pool


def main() -> None:
    rng = random.Random(1)
    words = [list(w) for seg in register_segments_with_words() for w in seg]
    stream = [x for w in words for x in w]
    p1 = pair_matrices([stream], dmax=1)[1][0]

    d4_pairs_by_word = [within_word_pairs([w], 4) for w in words]
    d6_pairs_by_word = [within_word_pairs([w], 6) for w in words]
    n4 = sum(len(p) for p in d4_pairs_by_word)
    n6 = sum(len(p) for p in d6_pairs_by_word)

    pool = tune_pool(p1, rng, size=40)
    d1s = [diag_rate(p1, g) for g in pool]
    print(f"pool: {len(pool)} order-5 g tuned to d1~{D1_TARGET}: mean d1 {sum(d1s) / len(d1s):.4f}")
    print(f"register: {len(words)} words, {n4} d4 pairs, {n6} d6 pairs\n")

    # per-g single-permutation d4/d6 (the H_FIXED spread: one g, no averaging)
    all_d4 = within_word_pairs(words, 4)
    all_d6 = within_word_pairs(words, 6)
    fixed_d4 = [rate(all_d4, ppow(g, 4)) for g in pool]
    fixed_d6 = [rate(all_d6, g) for g in pool]

    def stats(xs):
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5
        return m, sd

    fm4, fs4 = stats(fixed_d4)
    fm6, fs6 = stats(fixed_d6)
    print("H_FIXED (one g, tuned on d1 only) -- single-permutation spread:")
    print(f"  d4 {fm4:.4f} +/- {fs4:.4f}   d6 {fm6:.4f} +/- {fs6:.4f}")

    # H_PERWORD: assign an independent pool g to each word, average the cells
    draws = 400
    pw_d4, pw_d6 = [], []
    for _ in range(draws):
        gws = [rng.choice(pool) for _ in words]
        c4 = sum(coinc(pr, ppow(g, 4)) for g, pr in zip(gws, d4_pairs_by_word))
        c6 = sum(coinc(pr, g) for g, pr in zip(gws, d6_pairs_by_word))
        pw_d4.append(c4 / n4)
        pw_d6.append(c6 / n6)
    pm4, ps4 = stats(pw_d4)
    pm6, ps6 = stats(pw_d6)
    print("\nH_PERWORD (independent g_w per word) -- concentrated by averaging:")
    print(f"  d4 {pm4:.4f} +/- {ps4:.4f}   d6 {pm6:.4f} +/- {ps6:.4f}")

    print(f"\nLP observed:  d4 {LP_D4:.4f}   d6 {LP_D6:.4f}")
    z4 = (LP_D4 - pm4) / ps4
    z6 = (LP_D6 - pm6) / ps6
    print(f"LP vs H_PERWORD:  d4 z = {z4:+.1f}   d6 z = {z6:+.1f}  (register proxy)")
    print(
        f"\nVERDICT: inconclusive -- the handle is underpowered. H_FIXED (d4 {fm4:.4f}"
        f"+/-{fs4:.4f})\nand H_PERWORD (d4 {pm4:.4f}+/-{ps4:.4f}) are statistically the "
        "SAME distribution:\nwords are too short (<1 d4 pair/word), so the per-word average"
        " never concentrates\naway from a fixed g. The d4/d6 cells cannot distinguish"
        " fixed g from per-word g_w,\nso #4 stays invisible -- confirming length-clocked-walk.md's"
        ' "fixed by parsimony,\nnot proof". A real per-word test would need a long-word'
        " corpus that does not exist."
    )


if __name__ == "__main__":
    main()
