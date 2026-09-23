# ABOUTME: Answers what the five within-word alphabets are: shifts or unrelated, whether
# ABOUTME: the per-word re-basing is a shift, and whether a shuffled continuous key fits.
"""Three questions about the five alphabets, with two answers and one impossibility.

`which_period_five_cipher.py` fixes the shape: five alphabets cycling inside each word,
re-based at every word boundary. That leaves three questions about the mechanism.

## 1. Are the five alphabets one alphabet shifted five ways? UNDECIDABLE

Inside a word the only thing visible is whether two runes are equal, and that depends on
the five alphabets only through the composite permutation tau_k = A_r^-1 A_(r+k). The
coincidence rate at lag d is then the diagonal mass of the plaintext distance-d bigram
matrix under tau_(d mod 5).

Under "one alphabet shifted five ways" tau_k is a pure shift; otherwise it is an arbitrary
permutation. **The two ensembles sit on top of each other:**

    lag   body rate     shift ensemble              arbitrary permutations
      2      0.0348     0.0221-0.0546  sd 0.0069    0.0344  sd 0.0085
      3      0.0371     0.0245-0.0595  sd 0.0087    0.0347  sd 0.0073
      4      0.0405     0.0216-0.0560  sd 0.0085    0.0345  sd 0.0068
      6      0.0248     0.0231-0.0660  sd 0.0097    0.0345  sd 0.0077
      7      0.0410     0.0205-0.0569  sd 0.0084    0.0346  sd 0.0077

Same centre, same spread, same range. No observed value is evidence either way, and this
is not a sample-size problem: the base family is 27-transitive
(`key-local-channel-is-empty.md`), so the equality pattern is the **only** base-invariant
statistic of any tuple up to 27 runes, and the longest body word is 14. There is no other
statistic to reach for.

## 2. Is the per-word re-basing a shift of a common alphabet? NO

Already answered by `affine_triple_invariant.py` and not re-derived here. For an affine
base the ratio (c_c - c_a)/(c_b - c_a) cancels the multiplier and the offset, so it
survives the re-basing and carries plaintext structure.

    body, 3,357 within-word triples    chi2 = 89.7 on 28 df
    planted affine bases               620 to 1,252   median 848
    planted general bases              31.5 to 141.2  median 82.2

The body sits on the general-base median. **The per-word base is a general permutation,
not a shift and not affine**, which kills the whole AGL(1,29) family -- the one that would
have collapsed the base key space from 29! to 812.

This is also why question 1 is closed rather than merely hard. A shift-structured re-basing
would have left additive traces that expose the five alphabets; a general one does not.

## 3. A continuous key with the words shuffled afterwards? EXCLUDED

The model: a single period-5 key running through the plaintext, the words then transposed,
the doublet preventer applied on top. It explains the within-word period 5, and it explains
why nothing survives across word boundaries -- the shuffle scrambles each word's entry
phase.

It also makes a prediction the general model does not. There would be **no per-word base at
all**, only five entry phases, so two words sharing a phase would use identical alphabets
and coincide at matched positions at the plaintext rate.

    English word-aligned coincidence (the same-phase rate)       0.0794
    a five-phase model predicts 0.2 x 0.0794 + 0.8 x 0.0345   =  0.0435
    the body, 13.5M word pairs at matched positions               0.0344
    chance                                                        0.0345

    observed 464,370 hits against 586,927 predicted     z = -164

**Dead.** Word-aligned coincidence does not move off chance at all, so there is no small
set of shared alphabets. Whatever re-bases each word takes many more than five values,
which is the same conclusion `alphabet_count_bound.py` reaches from the other direction.

    python what_the_five_alphabets_are.py
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ngram_kappa_inside_a_word import body_words, english_words  # noqa: E402

MOD = 29
PHASES = 5
DRAWS = 2000


def aligned_kappa(words) -> tuple[int, int]:
    """Coincidences over all word pairs at matched positions from the word start."""
    columns: dict[int, list] = {}
    for w in words:
        for i, ch in enumerate(w):
            columns.setdefault(i, []).append(ch)
    hits = pairs = 0
    for column in columns.values():
        counts = Counter(column)
        n = len(column)
        pairs += n * (n - 1) // 2
        hits += sum(v * (v - 1) // 2 for v in counts.values())
    return hits, pairs


def within_word_rate(words, lag: int) -> float:
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - lag):
            pairs += 1
            hits += w[i] == w[i + lag]
    return hits / pairs


def ensembles(english, lag: int, rng):
    """Diagonal mass of the distance-`lag` bigram matrix under shifts and permutations."""
    counts = np.zeros((MOD, MOD))
    for w in english:
        for i in range(len(w) - lag):
            counts[w[i], w[i + lag]] += 1
    counts /= counts.sum()
    shifts = np.array(
        [sum(counts[(x + s) % MOD, x] for x in range(MOD)) for s in range(MOD)]
    )
    perms = np.array(
        [
            sum(counts[t[x], x] for x in range(MOD))
            for t in (rng.sample(range(MOD), MOD) for _ in range(DRAWS))
        ]
    )
    return shifts, perms


def main() -> None:
    rng = random.Random(3301)
    body, english = body_words(), english_words(rng)

    print("1. Are the five alphabets one alphabet shifted five ways?\n")
    print(
        f"{'lag':>4}{'body rate':>11}{'shift ensemble':>30}"
        f"{'arbitrary permutations':>28}"
    )
    for lag in (2, 3, 4, 6, 7):
        shifts, perms = ensembles(english, lag, rng)
        print(
            f"{lag:>4}{within_word_rate(body, lag):>11.4f}"
            f"{f'{shifts.min():.4f}-{shifts.max():.4f}  sd {shifts.std():.4f}':>30}"
            f"{f'{perms.mean():.4f}  sd {perms.std(ddof=1):.4f}':>28}"
        )
    print(
        "\n  Same centre, same spread, same range: no observed value is evidence either"
        "\n  way. The base family is 27-transitive, so the equality pattern is the only"
        "\n  base-invariant statistic of any tuple up to 27 runes and the longest body"
        f"\n  word is {max(len(w) for w in body)}. UNDECIDABLE, by theorem rather than by sample size.\n"
    )

    print(
        "2. Is the per-word re-basing a shift? Answered in affine_triple_invariant.py:"
    )
    print("   chi2 = 89.7, against a general-base median of 82.2 and an affine")
    print("   median of 848. The base is a general permutation. NO.\n")

    print("3. A continuous period-5 key with the words shuffled afterwards.\n")
    he, pe = aligned_kappa(english[:30000])
    hb, pb = aligned_kappa(body)
    same_phase = he / pe
    predicted = same_phase / PHASES + (1 - 1 / PHASES) / MOD
    sd = np.sqrt(pb * predicted * (1 - predicted))
    print(
        f"   English word-aligned coincidence, the same-phase rate   {same_phase:.4f}"
    )
    print(
        f"   a {PHASES}-phase model predicts {1 / PHASES:.1f} x {same_phase:.4f}"
        f" + {1 - 1 / PHASES:.1f} x {1 / MOD:.4f}  =  {predicted:.4f}"
    )
    print(f"   the body, {pb:,} word pairs at matched positions        {hb / pb:.4f}")
    print(f"   chance                                                  {1 / MOD:.4f}\n")
    print(
        f"   observed {hb:,} against {pb * predicted:,.0f} predicted   z = {(hb - pb * predicted) / sd:+.0f}"
    )
    print(
        "\n   Word-aligned coincidence does not move off chance, so there is no small set"
        "\n   of shared alphabets. Whatever re-bases each word takes many more than five"
        "\n   values. EXCLUDED."
    )


if __name__ == "__main__":
    main()
