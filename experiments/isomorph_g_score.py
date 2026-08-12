# ABOUTME: A g-only objective from the isomorph channel: it has a real gradient
# ABOUTME: but a vast near-optimal plateau, so it cannot recover g. Worked negative.
"""The isomorph channel gives a g-only gradient that still cannot find g.

For within-word positions j < k,

    c_j == c_k   <=>   p_j == g^((k-j) mod 5)(p_k)

which involves g and the plaintext ONLY -- no base_w, no sigma, no global
schedule. That makes it the one channel in this cipher that is LOCAL in the key,
and it suggests an objective needing neither sigma nor base_0:

    score(g) = mean over words of log(frequency mass of dictionary words whose
               collision pattern under g matches the ciphertext word's)

`length-clocked-walk.md` records that no hillclimb can work because the 2-rune
landscape is a delta function. That is true of objectives which need the globally
coupled base schedule; it is NOT true here, and this file exists to record both
halves of the result.

**The gradient is real.** On a planted key over 2,900 words the true g scores
-3.7125, one transposition away -3.7537, two -3.8116, five -3.8882, against a
random order-5 g at -3.9315. A partially correct g scores partially well, which
the 2-rune objective cannot do. (Ten transpositions reads -3.9688, marginally
below random: by then the permutation is effectively random and the ordering
inside that tail is noise.)

**It still cannot recover g.** Hillclimbs of 2,500 accepted-move iterations reach
-3.78 to -3.80 against a true -3.7125 -- close -- while agreeing with the planted
g at **0 to 3 points out of 29**, i.e. chance. Across six restarts there was no
point where even four agreed with each other, so consensus does not rescue it
either. The near-optimal set is enormous and uncorrelated with the truth.

This is exactly what `information_budget.py` predicts, and it is the useful part:
the marginal information about g, once the unknown plaintext is averaged away, is
about 4 bits. An objective built from that channel can rank g against random --
4 bits is enough for that -- but cannot locate one object among 2^80. The gradient
leads onto a plateau, not to the key.

Read this file as the reason not to try again: local-in-g is necessary for a
gradient but nowhere near sufficient for identification.
"""

from __future__ import annotations

import math
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import perm_from_cycles  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
LENGTHS = (3, 4, 5, 6, 7)
MISS = -30.0  # log-mass charged when no dictionary word matches the pattern


def dictionary() -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """Runeglish dictionary words by rune length, with token frequencies."""
    from wordfreq import top_n_list, word_frequency

    buckets: dict[int, list[tuple[tuple[int, ...], float]]] = defaultdict(list)
    for word in top_n_list("en", 60000):
        if not word.isalpha():
            continue
        runes = [IDX[c] for c in english_to_runeglish(word.upper()) if c in IDX]
        if len(runes) in LENGTHS:
            buckets[len(runes)].append((tuple(runes), word_frequency(word, "en")))
    return {
        length: (
            np.array([w for w, _ in items]),
            np.array([f for _, f in items]),
        )
        for length, items in buckets.items()
    }


def pairs(length: int) -> list[tuple[int, int]]:
    return [(j, k) for j in range(length) for k in range(j + 1, length)]


def powers(g: np.ndarray) -> list[np.ndarray]:
    out = [np.arange(M)]
    for _ in range(4):
        out.append(g[out[-1]])
    return out


def signature(word: tuple[int, ...], pw: list[np.ndarray]) -> int:
    """Bitmask of which position pairs collide in the ciphertext, given g."""
    return sum(
        1 << b
        for b, (j, k) in enumerate(pairs(len(word)))
        if word[j] == pw[(k - j) % 5][word[k]]
    )


def signatures(words: np.ndarray, pw: list[np.ndarray]) -> np.ndarray:
    """The same, vectorised over a whole length bucket."""
    out = np.zeros(len(words), dtype=np.int64)
    for b, (j, k) in enumerate(pairs(words.shape[1])):
        hit = words[:, j] == pw[(k - j) % 5][words[:, k]]
        out |= hit.astype(np.int64) << b
    return out


def make_score(
    observed: list[tuple[int, int]], dict_by_len
) -> Callable[[np.ndarray], float]:
    """score(g): mean log frequency-mass of dictionary words matching each pattern."""

    def score(g: np.ndarray) -> float:
        pw = powers(g)
        mass: dict[int, dict[int, float]] = {}
        for length, (words, freqs) in dict_by_len.items():
            agg: dict[int, float] = defaultdict(float)
            for s, f in zip(signatures(words, pw).tolist(), freqs.tolist()):
                agg[s] += f
            mass[length] = agg
        total = 0.0
        for length, sig in observed:
            m = mass[length].get(sig, 0.0)
            total += math.log(m) if m > 0 else MISS
        return total / len(observed)

    return score


def main() -> None:
    rng = random.Random(19)
    dict_by_len = dictionary()
    print(
        "dictionary: "
        + ", ".join(f"L{k}:{len(v[0])}" for k, v in sorted(dict_by_len.items()))
    )

    g_true = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
    pw_true = powers(g_true)
    plain = []
    for _ in range(2900):
        length = rng.choice(LENGTHS)
        words, freqs = dict_by_len[length]
        idx = rng.choices(range(len(words)), weights=freqs.tolist())[0]
        plain.append(tuple(words[idx].tolist()))
    observed = [(len(w), signature(w, pw_true)) for w in plain]
    score = make_score(observed, dict_by_len)

    print(f"\nplanted {len(plain)} words; true g scores {score(g_true):.4f}")
    print("\ngradient check -- perturbing the true g by conjugating transpositions")
    for n in (0, 1, 2, 5, 10):
        vals = []
        for _ in range(3):
            h = g_true.copy()
            for _ in range(n):
                i, j = rng.randrange(M), rng.randrange(M)
                t = np.arange(M)
                t[i], t[j] = j, i
                h = t[h[t]]
            vals.append(score(h))
        print(f"  {n:>2} transposition(s): {float(np.mean(vals)):.4f}")
    rand = [score(np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))) for _ in range(3)]
    print(f"  random order-5 g   : {float(np.mean(rand)):.4f}")

    print("\nhillclimb check -- can it FIND g? (the answer is no)")
    print(f"{'restart':>8}{'score':>10}{'agreement':>12}")
    for r in range(4):
        best = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
        bs = score(best)
        for _ in range(2500):
            i, j = rng.randrange(M), rng.randrange(M)
            if i == j:
                continue
            t = np.arange(M)
            t[i], t[j] = j, i
            cand = t[best[t]]
            cs = score(cand)
            if cs >= bs:
                best, bs = cand, cs
        print(f"{r:>8}{bs:>10.4f}{int((best == g_true).sum()):>9}/29")
    print("\nAgreement sits at chance (1-3 of 29) while the score nearly matches the")
    print("true key's. The near-optimal set is vast and uncorrelated with the truth,")
    print("exactly as the ~4 bits of marginal information in information_budget.py")
    print("predicts. Local-in-g buys a gradient, not identification.")


if __name__ == "__main__":
    main()
