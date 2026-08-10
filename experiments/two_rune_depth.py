# ABOUTME: Tests whether the two positions of 2-rune ciphertext words agree
# ABOUTME: together, which a shared-base schedule forces and a rich walk does not.
"""If many 2-rune words are THE, do their ciphertext bigrams repeat?

For a 2-rune word at word index w the walk gives

    C = ( base_w(p0), base_w(g(p1)) )

Take two such words w and v. Agreement at a position means

    base_w(x) = base_v(x)   <=>   x is a fixed point of h = base_v^-1 base_w

so whether the two positions agree *together* is decided by the fixed-point
structure of the group the base differences live in:

  * Shift-like schedules (Vigenere, Quagmire, any conjugated shift
    K s_k K^-1): h is fixed-point-free unless the two shifts are equal. Two
    THE instances therefore agree at BOTH positions or NEITHER. With ~29
    shifts, a fraction ~1/29 of THE-THE pairs collide completely, which is a
    large and obvious excess of repeated bigrams.

  * A rich walk with ~2,928 distinct bases: base equality is essentially
    absent (DJU-BEI is the single observed state return), and distinct bases
    behave like unrelated permutations, so the two positions agree
    independently at ~1/29 each. No excess.

So the excess of double agreements over the product of the single-position
rates separates the two, and it does not require knowing which words are THE.
The measurement is inverted at the end into a bound on how many 2-rune word
pairs can share a base at all.

The null permutes the second runes across 2-rune words, which destroys any
link between the positions while preserving both marginals exactly.
"""

from __future__ import annotations

import random
import re
import statistics
from collections import Counter
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
BOUNDARY = c3301.MARK_CHARS + "%&$" + c3301.NUMERAL_CHARS
N_RUNES = 29
TRIALS = 20000
SEED = 3301
# Register estimate: THE is exactly TH-E in runeglish and 2-rune words are
# dominated by a few function words (README constraint 3).
THE_SHARE = (75, 108)


def two_rune_words() -> list[tuple[int, int]]:
    text = "$".join(CORPUS.read_text().split("$")[:10])
    alphabet: dict[str, int] = {}
    words, cur = [], []
    for char in text:
        if RUNE.match(char):
            cur.append(alphabet.setdefault(char, len(alphabet)))
        elif char in BOUNDARY and cur:
            if len(cur) == 2:
                words.append((cur[0], cur[1]))
            cur = []
    if len(cur) == 2:
        words.append((cur[0], cur[1]))
    return words


def agreement_rates(words: list[tuple[int, int]]) -> tuple[float, float, float]:
    """Pair rates: agree at position 0, at position 1, at both."""
    n = len(words)
    pairs = n * (n - 1) / 2
    c0 = Counter(a for a, _ in words)
    c1 = Counter(b for _, b in words)
    both = Counter(words)
    p0 = sum(v * (v - 1) / 2 for v in c0.values()) / pairs
    p1 = sum(v * (v - 1) / 2 for v in c1.values()) / pairs
    p01 = sum(v * (v - 1) / 2 for v in both.values()) / pairs
    return p0, p1, p01


def main() -> None:
    rng = random.Random(SEED)
    words = two_rune_words()
    n = len(words)
    pairs = n * (n - 1) // 2
    p0, p1, p01 = agreement_rates(words)
    exp = p0 * p1
    print(f"{n} two-rune words in the clean corpus -> {pairs} pairs\n")

    print(f"{'':34}{'rate':>10}{'count':>10}")
    print(f"{'agree at position 0':34}{p0:>10.5f}{p0 * pairs:>10.1f}")
    print(f"{'agree at position 1':34}{p1:>10.5f}{p1 * pairs:>10.1f}")
    print(f"{'agree at BOTH (observed)':34}{p01:>10.5f}{p01 * pairs:>10.1f}")
    print(f"{'agree at BOTH (independent)':34}{exp:>10.5f}{exp * pairs:>10.1f}")

    seconds = [b for _, b in words]
    null = []
    for _ in range(TRIALS):
        rng.shuffle(seconds)
        null.append(agreement_rates([(a, b) for (a, _), b in zip(words, seconds)])[2])
    mu, sd = statistics.mean(null), statistics.pstdev(null)
    z = (p01 - mu) / sd
    beat = sum(1 for v in null if v >= p01)
    print(f"\npermutation null (second runes reshuffled, {TRIALS} draws)")
    print(f"   both-agree rate {mu:.5f} +- {sd:.5f}   observed {p01:.5f}")
    print(f"   z = {z:+.2f},  p = {(beat + 1) / (TRIALS + 1):.4f}")

    print("\nconditional: P(position 1 agrees | position 0 agrees)")
    print(f"   observed   {p01 / p0:.5f}")
    print(f"   unconditional P(position 1 agrees) {p1:.5f}")
    print("   a shared-base schedule forces these two to diverge sharply")

    print("\nwhat a shift-like schedule would predict")
    print(f"   {THE_SHARE[0]}-{THE_SHARE[1]} of the {n} are THE, but the argument "
          "does not need that count:")
    print("   ANY repeated 2-rune plaintext collides fully when the shifts match.")
    # README: 2-rune words are 22.8% of register tokens, top-8 function words 69%.
    # Given 8 words summing to 0.69, sum p^2 is minimised when they are equal,
    # so this is a rigorous LOWER bound on the same-plaintext pair rate.
    same_pt = 8 * (0.69 / 8) ** 2
    same_pairs = same_pt * pairs
    collide = same_pairs / N_RUNES
    print(f"   top-8 cover 69% -> same-plaintext pair rate >= {same_pt:.4f} "
          f"({same_pairs:.0f} of {pairs} pairs)")
    print(f"   with {N_RUNES} shifts, >= {collide:.0f} of those collide at BOTH "
          "positions")
    print(f"   predicted both-agree >= {exp * pairs + collide:.0f}, "
          f"observed {p01 * pairs:.0f}  ->  excluded at "
          f"{(exp * pairs + collide - p01 * pairs) / (sd * pairs):.0f} sigma")

    # Invert: how many pairs can share a base before the excess would show?
    excess = (p01 - mu) * pairs
    ceiling = 2 * sd * pairs
    print(f"\nbound on base reuse: observed excess is {excess:+.1f} pairs, "
          f"2 sigma is {ceiling:.1f}")
    print(f"   at most ~{ceiling:.0f} of {pairs} pairs share a base, so the "
          f"same-plaintext collision")
    print(f"   rate is below {ceiling / same_pairs:.2e} against the "
          f"{1 / N_RUNES:.3f} a 29-shift schedule needs")
    print(f"   -> the base must take >= ~{same_pairs / ceiling:.0f} effective "
          f"values; there are only {n} two-rune words")
    print("      and 2,928 words in the corpus, so the base essentially never repeats.")


if __name__ == "__main__":
    main()
