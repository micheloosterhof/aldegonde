# ABOUTME: Splits the doublet suppression by word boundary and shows the split
# ABOUTME: carries no information, which puts the walk model under strain.
"""The doublet deficit does not know where the word boundaries are.

The Liber Primus suppresses adjacent equal runes to about a fifth of the chance
rate; `c3301.low_doublet_null` already treats that as a known property to null
out. Under the walk model it is not noise but key material, and it splits
cleanly in two.

Inside a word base_w is a single bijection, so

    c_k == c_k+1   <=>   p_k == g(p_k+1)

Across a word boundary, with j the last rune of word w and e = (L_w - 1) mod 5,

    c_j   = base_w(g^e(p_j))
    c_j+1 = base_w+1(p_j+1) = base_w(g^e(sigma(p_j+1)))
    c_j == c_j+1   <=>   p_j == sigma(p_j+1)

because g^e and base_w cancel. So the boundary doublets depend on sigma ALONE --
not on the word length, not on the base, not on g. Both statements are verified
exactly against a planted key by `test_boundary_doublets`.

That should give two filters of identical form on unrelated permutations:

    within a word    63 / 10,028 = 0.628%     constrains g
    across boundary  23 /  2,927 = 0.786%     constrains sigma
    chance                        = 3.448%

sigma is scored by the boundary letter statistics, which come from an English
word list carried into runeglish: the predicted count is
N * sum_b P_final(sigma(b)) * P_initial(b), and the extremes over all sigma are
found exactly by solving the assignment problem rather than by sampling.

The result is negative, and it is the reason this file exists. The two rates
agree to within z = 0.9 of a single uniform rate -- the doublets fall without
regard to the boundaries. g and sigma are unrelated permutations with no reason
to suppress by the same factor, so the walk would need both to be independently
near-optimal doublet-avoiders AND to coincide. The simpler reading is one global
suppression that the walk does not model, in which case a filter built on the
doublet count is fitting an artifact rather than the key.
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words, perm_from_cycles  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}


def boundary_distributions() -> tuple[np.ndarray, np.ndarray]:
    """Frequency-weighted first-rune and last-rune distributions of English words."""
    try:
        from wordfreq import top_n_list, word_frequency
    except ImportError:
        print("wordfreq is not installed; install the experiments extra")
        raise
    first = np.zeros(M)
    last = np.zeros(M)
    for word in top_n_list("en", 30000):
        if not word.isalpha():
            continue
        runes = english_to_runeglish(word.upper())
        runes = "".join(ch for ch in runes if ch in IDX)
        if not runes:
            continue
        w = word_frequency(word, "en")
        first[IDX[runes[0]]] += w
        last[IDX[runes[-1]]] += w
    return first / first.sum(), last / last.sum()


def counts(words: list[list[int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    """Within-word and across-boundary adjacent pairs, and how many are doublets."""
    wi_t = sum(len(w) - 1 for w in words)
    wi_h = sum(1 for w in words for k in range(len(w) - 1) if w[k] == w[k + 1])
    ac_t = ac_h = 0
    for a, b in zip(words, words[1:]):
        if a and b:
            ac_t += 1
            ac_h += a[-1] == b[0]
    return (wi_t, wi_h), (ac_t, ac_h)


def predict(last: np.ndarray, first: np.ndarray, npairs: int, s: np.ndarray) -> float:
    """Expected boundary doublets if the step permutation is s."""
    return npairs * float(sum(last[s[b]] * first[b] for b in range(M)))


def main() -> None:
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    words = load_words()
    (wi_t, wi_h), (ac_t, ac_h) = counts(words)
    print(f"within a word    {wi_h:>5} / {wi_t:>6} = {100 * wi_h / wi_t:.3f}%   -> g")
    print(
        f"across boundary  {ac_h:>5} / {ac_t:>6} = {100 * ac_h / ac_t:.3f}%   -> sigma"
    )
    print(f"chance                            = {100 / M:.3f}%\n")

    first, last = boundary_distributions()
    top = sorted(range(M), key=lambda i: -first[i])[:5]
    bot = sorted(range(M), key=lambda i: -last[i])[:5]
    A = c3301.CICADA_ALPHABET
    print(f"commonest word-initial runes: {' '.join(A[i] for i in top)}")
    print(f"commonest word-final runes:   {' '.join(A[i] for i in bot)}\n")

    rng = random.Random(3301)
    sample = [
        predict(last, first, ac_t, np.array(perm_from_cycles([29], rng)))
        for _ in range(trials)
    ]
    mu, sd = statistics.mean(sample), statistics.stdev(sample)

    # exact best and worst sigma: an assignment problem, cost C[a][b] = last[a]*first[b]
    C = np.outer(last, first)
    r, c = linear_sum_assignment(C)
    lo = ac_t * float(C[r, c].sum())
    r, c = linear_sum_assignment(-C)
    hi = ac_t * float(C[r, c].sum())

    print(
        f"boundary doublets predicted by a random 29-cycle sigma: {mu:.1f} +- {sd:.1f}"
    )
    print(f"  observed {ac_h}   z = {(ac_h - mu) / sd:+.2f}")
    print(f"  the least any sigma can predict: {lo:.1f}   the most: {hi:.1f}")
    below = sum(1 for v in sample if v <= ac_h)
    print(
        f"  random sigma predicting <= {ac_h}: {below} of {trials} ({100 * below / trials:.2f}%)"
    )
    print(f"  observed sits {100 * (ac_h - lo) / lo:.0f}% above the absolute optimum\n")

    # Do the doublets know where the word boundaries are? Under the walk they must:
    # the within-word rate is set by g and the boundary rate by sigma, and those are
    # unrelated permutations, so the two rates have no reason to agree.
    tot_h, tot_t = wi_h + ac_h, wi_t + ac_t
    print("but if doublets simply fall uniformly, ignoring the boundaries:")
    for name, (t, h) in (("within", (wi_t, wi_h)), ("across", (ac_t, ac_h))):
        exp = tot_h * t / tot_t
        sd = (exp * (1 - t / tot_t)) ** 0.5
        print(
            f"  {name:>6}: observed {h:>3}, expected {exp:>5.1f} +- {sd:.1f}"
            f"   z = {(h - exp) / sd:+.2f}"
        )
    print("\nThe split carries no information: one uniform suppression of 0.664%,")
    print("cut arbitrarily in two. To produce that, the walk needs g and sigma to")
    print("be independently near-optimal doublet-avoiders (each below 1 in 4,000)")
    print("AND to land on the same rate by coincidence. Two unrelated permutations")
    print("have no reason to agree. Either the pair was co-designed to defeat this")
    print("statistic, or the suppression is one global mechanism the walk does not")
    print("model -- and the filter built on it is fitting an artifact.")


if __name__ == "__main__":
    main()
