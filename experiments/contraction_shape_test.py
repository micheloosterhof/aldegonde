# ABOUTME: Tests whether the four LP apostrophes sit at linguistically valid
# ABOUTME: contraction positions, or land where decorative marks would.
"""The apostrophe positions are a decoration-vs-language probe.

An English contraction constrains where an apostrophe may sit inside a word:
the tail (what follows the mark) is one rune for 'S/'D/'T and two for
'RE/'VE/'LL, and the stem must be a real word. A mark scattered for visual
effect carries no such constraint.

All four observed marks have a one-rune tail on a short host word. This script
measures how often that happens by chance under two nulls:

  A. position-only  - host words fixed, mark at a uniform internal slot
  B. word+position  - host word drawn from the clean corpus too

Null A isolates the placement; null B adds the observation that contraction
hosts are short (lengths 4, 3, 3, 4 against a corpus mean of 4.42).
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lp_corpus import load_clean  # noqa: E402

TRIALS = 200_000
SEED = 3301

# Observed: (host word length, runes after the apostrophe), in page order
# 4.jpg MXIW, 21.jpg AEOY, 35.jpg PET, 41.jpg XLJC
OBSERVED = [(4, 1), (3, 1), (3, 1), (4, 1)]


def word_lengths() -> list[int]:
    """Word lengths of the clean corpus (sections 0-9)."""
    _, word_id = load_clean()
    return list(Counter(word_id).values())


def tail_is_one(length: int, rng: random.Random) -> bool:
    """Place a mark at a uniform internal slot; does exactly one rune follow?"""
    # internal slots leave 1..length-1 runes after the mark
    return rng.randint(1, length - 1) == 1


def main() -> None:
    rng = random.Random(SEED)
    lengths = word_lengths()
    n_words = len(lengths)
    mean = sum(lengths) / n_words
    print(f"clean corpus: {n_words} words, mean length {mean:.2f}")
    print(f"observed hosts: lengths {[l for l, _ in OBSERVED]}, all with a 1-rune tail\n")

    # words of length 1 have no internal slot and cannot host a mark
    hostable = [l for l in lengths if l >= 2]
    print(f"{len(hostable)} words are long enough to host a mark\n")

    hits_a = hits_b = 0
    for _ in range(TRIALS):
        if all(tail_is_one(l, rng) for l, _ in OBSERVED):
            hits_a += 1
        drawn = [rng.choice(hostable) for _ in OBSERVED]
        if all(tail_is_one(l, rng) for l in drawn) and all(
            d <= 4 for d in drawn
        ):
            hits_b += 1

    exact_a = 1.0
    for length, _ in OBSERVED:
        exact_a *= 1 / (length - 1)

    print("null A (position only, host words fixed)")
    print(f"   all four with a 1-rune tail: p = {hits_a / TRIALS:.4f} "
          f"(exact {exact_a:.4f} = 1 in {1 / exact_a:.0f})")
    print("null B (word and position drawn)")
    print(f"   all four short AND 1-rune tail: p = {hits_b / TRIALS:.5f}")


if __name__ == "__main__":
    main()
