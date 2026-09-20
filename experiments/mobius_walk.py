# ABOUTME: Tests the walk with both steps drawn from PGL(2,29) on the 30-point
# ABOUTME: projective line, the one algebraic family that contains order-5 elements.
"""A walk whose letter step and space step are both fractional-linear maps.

`order5_algebraic_routes.py` shows that no operation on 29 symbols has order 5, and
that the fractional-linear maps on the 30-point projective line do: 1,624 of them,
all with cycle type 5^6. If the cipher is algebraic at all, that is the only place
its period-5 step can come from, and the alphabet then holds 30 symbols.

Both diagonals the corpus fixes are reachable inside that family, which no arithmetic
family on 29 symbols managed (`sigma-power-step.md`: affine floors at 0.0122 against
an observed seam of 0.0079). Measured on prose:

    order-5 Mobius g   min within-word doublet diagonal 0.0040   (observed 0.0063)
    any Mobius sigma   min seam diagonal                0.0076   (observed 0.0079)

Keeping only the maps whose diagonal lands inside the observed 95% interval leaves
28 letter steps and 64 space steps, so the whole family is 1,792 complete keys. Every
one is scored here with the base_0-free verifier at 30 points.

The extra point is written as a word separator when the cipher emits it, which is the
only fate left: a skip is not uniquely decodable (`order5_algebraic_routes.py` finds
a collision for every base tried), and a distinct written symbol would occupy 1/30 of
the stream against the 1.3% the marks occupy.

**Result (2026-09-20): the enumeration is INCONCLUSIVE, and the family is disfavoured
on word lengths instead.** All 1,792 keys score at most 1.000 where a planted key of
the family reaches 1.765 and wrong keys reach 1.019, so nothing decrypts. But that run
is not a refutation, because it clocks the walk with the word lengths as transcribed,
and every one of the 28 candidates predicts that 135 to 359 of those boundaries are
cipher output rather than real spaces (minimum 134.6, median 257.3). Under any of
these keys the step exponents `(L-1) mod 5` are wrong at 5 to 12% of boundaries, which
is exactly the kind of wrong clock that makes a sweep unable to find a key it contains.
Testing them properly needs the merge positions, which are unknown.

What does argue against the family is the short-word deficit. Roughly 250 spurious
breaks would split 250 words into 500 fragments, and fragments are short. The corpus
already holds far FEWER 2-rune words than English (15.9% against 23.7%, z about -10,
`two-rune-deficit.md`); removing the fragments to recover the true words would push
that share lower still and deepen an anomaly that is already the sharpest in the
corpus. The family predicts the opposite of what the word lengths show.

Run with no arguments for the self-test, `--run` for the enumeration.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies  # noqa: E402
from compact_state_models import prose_corpora  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from order5_algebraic_routes import (  # noqa: E402
    INFINITY,
    cycle_of,
    order_of,
    projective_group,
)
from walk_score_kernel import Windows, score_sigmas  # noqa: E402

POINTS = 30
WINDOW_WORDS = 200
WINDOW_STARTS = (419, 806, 2181)
# 95% intervals of the observed counts: 63 of 10,028 within words, 23 of 2,927 seams
D1_BAND = (0.0033, 0.0121)
SEAM_BAND = (0.0050, 0.0118)
MISSING = np.log(1e-9)  # the plaintext never holds the extra point


def lp_words() -> list[list[int]]:
    stream, wid = load_clean()
    words: list[list[int]] = [[] for _ in range(wid[-1] + 1)]
    for rune, w in zip(stream, wid):
        words[w].append(rune)
    return words


def plaintext_tables(draws: int = 40) -> tuple[np.ndarray, np.ndarray]:
    """Within-word adjacent and cross-word (final x initial) tables on 30 points."""
    adjacent = np.zeros((POINTS, POINTS))
    cross = np.zeros((POINTS, POINTS))
    for plain in prose_corpora(2928, draws):
        for word in plain:
            for x, y in zip(word, word[1:]):
                adjacent[x, y] += 1
        for before, after in zip(plain, plain[1:]):
            if before and after:
                cross[before[-1], after[0]] += 1
    return adjacent / adjacent.sum(), cross / cross.sum()


def diagonal(table: np.ndarray, perm: list[int]) -> float:
    """The rate of the relation `perm` on `table`: sum_y table[perm(y)][y]."""
    return float(sum(table[perm[y], y] for y in range(POINTS)))


def candidates() -> tuple[list[list[int]], list[list[int]], np.ndarray]:
    """Order-5 letter steps and space steps whose diagonals match the corpus."""
    adjacent, cross = plaintext_tables()
    group = [list(p) for p in projective_group()]
    letter = [
        g
        for g in group
        if order_of(g) == 5 and D1_BAND[0] <= diagonal(adjacent, g) <= D1_BAND[1]
    ]
    space = [s for s in group if SEAM_BAND[0] <= diagonal(cross, s) <= SEAM_BAND[1]]
    return letter, space, adjacent


def separator_rate(g: list[int], frequencies: np.ndarray) -> float:
    """Share of positions whose ciphertext is the extra point, base chosen freely."""
    return min(
        sum(frequencies[x] for x in cycle_of(g, start)) / 5 for start in range(POINTS)
    )


def powers(g: list[int]) -> list[list[int]]:
    out = [list(range(POINTS))]
    for _ in range(4):
        out.append([g[x] for x in out[-1]])
    return out


def score_table() -> np.ndarray:
    """Log plaintext frequencies over 30 points; the extra point never occurs."""
    return np.append(log_frequencies(), MISSING).astype(np.float32)


def self_test() -> None:
    letter, space, adjacent = candidates()
    print(f"order-5 letter steps inside the doublet band: {len(letter)}")
    print(f"space steps inside the seam band:             {len(space)}")
    assert letter and space, "the bands should not be empty"
    for g in letter:
        assert order_of(g) == 5, "a letter step must have order 5"
        assert g[INFINITY] != INFINITY, "an order-5 Mobius map moves the extra point"

    # the verifier must separate a planted key of this family from the rest
    logf = score_table()
    g, sigma = letter[0], space[0]
    rng = np.random.default_rng(3301)
    plain = prose_corpora(2928, 1)[0]
    base0 = rng.permutation(POINTS)
    gp = powers(g)
    cipher, base = [], list(base0)
    for word in plain:
        cipher.append([base[gp[j % 5][p]] for j, p in enumerate(word)])
        step = [gp[(len(word) - 1) % 5][sigma[x]] for x in range(POINTS)]
        base = [base[step[x]] for x in range(POINTS)]
    windows = Windows([cipher[a : a + WINDOW_WORDS] for a in WINDOW_STARTS])
    trials = np.array(
        [sigma] + [rng.permutation(POINTS).tolist() for _ in range(400)], dtype=np.int8
    )
    scores = score_sigmas(gp, trials, windows, logf, points=POINTS)
    print(
        f"planted key {scores[0]:.3f}; best of 400 wrong space steps {scores[1:].max():.3f}"
    )
    assert scores[0] > scores[1:].max() + 0.2, "the verifier misses a planted key"
    print("self-test passed")


def run() -> None:
    letter, space, _adjacent = candidates()
    logf = score_table()
    frequencies = np.append(np.exp(log_frequencies()), 0.0)
    words = lp_words()
    windows = Windows([words[a : a + WINDOW_WORDS] for a in WINDOW_STARTS])
    trials = np.array(space, dtype=np.int8)
    print(
        f"{len(letter)} letter steps x {len(space)} space steps = {len(letter) * len(space):,} keys"
    )
    print(
        "a wrong key scores about 0.5 nats/rune on these windows, a true key about 1.2\n"
    )
    rows = []
    for g in letter:
        scores = score_sigmas(powers(g), trials, windows, logf, points=POINTS)
        best = int(scores.argmax())
        rows.append((float(scores[best]), g, space[best]))
    rows.sort(reverse=True, key=lambda r: r[0])
    print(f"{'score':>8}{'separators implied':>22}{'letter step (first 8 images)':>34}")
    for score, g, _sigma in rows[:10]:
        implied = separator_rate(g, frequencies) * sum(len(w) for w in words)
        print(f"{score:>8.3f}{implied:>22.1f}{str(g[:8]):>34}")
    top = rows[0][0]
    print(f"\nbest score {top:.3f} over {len(letter) * len(space):,} keys")
    print("a planted key of this family scores 1.765, a wrong one up to 1.019\n")
    print("INCONCLUSIVE: every candidate implies 135-359 of the transcribed word")
    print("boundaries are cipher output, so this run clocks the walk wrongly at 5-12%")
    print("of them. See the docstring for the word-length argument against the family.")


if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    else:
        self_test()
