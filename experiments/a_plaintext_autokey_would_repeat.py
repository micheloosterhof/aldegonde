# ABOUTME: Shows a plaintext autokey IS falsifiable -- it multiplies repeated ciphertext
# ABOUTME: words -- and excludes it, correcting the claim that it could not be tested.
"""A plaintext autokey is not unfalsifiable. It leaves repeats, and the repeats are absent.

`the-base-is-not-a-ciphertext-autokey.md` excluded a base that is a function of the
previous **ciphertext** word, then recorded that the **plaintext** version "is
unfalsifiable here for the obvious reason". That is wrong, and the reason it is wrong is
the one thing a plaintext key has that a ciphertext key does not: **plaintext words
repeat, constantly**.

Under a plaintext autokey the base for word w is a function of p_(w-1). English repeats
words, so the same base recurs whenever the same word precedes two others, and two words
sharing a base coincide at matched positions at the plaintext rate. Worse for the
hypothesis, whenever the same plaintext *pair* (p_(w-1), p_w) recurs, the ciphertext word
is **identical**.

## Test A: word-aligned coincidence

    P(two joined English tokens are the same word)          0.00539
    a plaintext autokey predicts 0.00539 x 0.0794 + rest    0.03472
    chance                                                  0.03448
    the body observes                                       0.03439

    predicted 468,903 hits, observed 464,370                z = -6.8

## Test B: repeated ciphertext words, which is far sharper

    observed repeated-word pairs                    230
    chance floor, runes permuted, lengths kept    245.4 +- 15.4    z = -1.00
    a plaintext autokey adds about 245 more        -> 490          z = -16.9

The body's repeated words are **entirely chance**, and they live where chance puts them:
107 pairs among one-rune words, 106 among two-rune, 17 among three-rune against 10.6
expected. That last mild excess is the DJU-BEI family.

## The sharpest form: no long word repeats at all, ever

    words of 4+ runes   1,646 in the body   observed repeats 0   chance 0.19
    words of 5+ runes   1,133               observed repeats 0   chance 0.00
    words of 6+ runes     815               observed repeats 0   chance 0.00

**Not one ciphertext word of four runes or more occurs twice in the whole book.**

If the same plaintext word always enciphered the same way -- which a plaintext autokey
gives whenever its predecessor recurs, and which any scheme with few bases gives outright
-- English word frequencies predict **1,317** repeated pairs among the 4+ words. The
observed count is zero.

    P(0 | 1,317 expected)  =  0
    P(0 |   454 expected)  =  4e-198   (5+ runes)
    P(0 |   161 expected)  =  1e-70    (6+ runes)

## What this is really saying

The per-word base does not repeat in any way tied to the text. It is the same conclusion as
`alphabet_count_bound.py`'s >= 949 alphabets, reached from the plainest possible
observation: **the book never writes the same long word twice.**

    python a_plaintext_autokey_would_repeat.py
"""

from __future__ import annotations

import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ngram_kappa_inside_a_word import body_words, english_words  # noqa: E402

MOD = 29
DRAWS = 400


def matched_position(words):
    columns = defaultdict(list)
    for w in words:
        for i, ch in enumerate(w):
            columns[i].append(ch)
    hits = pairs = 0
    for column in columns.values():
        n = len(column)
        pairs += n * (n - 1) // 2
        hits += sum(v * (v - 1) // 2 for v in Counter(column).values())
    return hits, pairs


def repeat_pairs(words) -> int:
    return sum(v * (v - 1) // 2 for v in Counter(words).values())


def identity_rate(tokens) -> float:
    """P(two tokens drawn at random are the same word)."""
    counts = Counter(tokens)
    n = len(tokens)
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))


def chance_floor(words) -> float:
    lengths = Counter(len(w) for w in words)
    return sum(n * (n - 1) / 2 / MOD**k for k, n in lengths.items())


def main() -> None:
    rng = random.Random(3301)
    body, english = body_words(), english_words(rng)

    shared_hits, shared_pairs = matched_position(english[:30_000])
    p1 = shared_hits / shared_pairs
    p0 = 1 / MOD
    same = identity_rate(english)
    predicted = same * p1 + (1 - same) * p0
    hits, pairs = matched_position(body)
    sd = np.sqrt(pairs * p0 * (1 - p0))
    print("Test A: word-aligned coincidence\n")
    print(f"   P(two joined English tokens are the same word)   {same:.5f}")
    print(f"   a plaintext autokey predicts                     {predicted:.5f}")
    print(f"   chance                                           {p0:.5f}")
    print(f"   the body observes                                {hits / pairs:.5f}")
    print(
        f"   predicted {pairs * predicted:,.0f} hits, observed {hits:,}"
        f"   z = {(hits - pairs * predicted) / sd:+.1f}\n"
    )

    print("Test B: repeated ciphertext words\n")
    lengths = [len(w) for w in body]
    flat = list("".join(body))
    null = []
    for _ in range(DRAWS):
        pool = rng.sample(flat, len(flat))
        out, at = [], 0
        for n in lengths:
            out.append("".join(pool[at : at + n]))
            at += n
        null.append(repeat_pairs(out))
    null = np.array(null, float)
    seen = repeat_pairs(body)
    added = (
        identity_rate(list(zip(english[:-1], english[1:])))
        * len(body)
        * (len(body) - 1)
        / 2
    )
    print(f"   observed repeated-word pairs           {seen}")
    print(
        f"   chance floor, runes permuted        {null.mean():8.1f} +- {null.std(ddof=1):.1f}"
        f"   z = {(seen - null.mean()) / null.std(ddof=1):+.2f}"
    )
    print(
        f"   a plaintext autokey adds about {added:.0f}  -> {null.mean() + added:.0f}"
        f"   z = {(seen - null.mean() - added) / null.std(ddof=1):+.1f}\n"
    )

    print("The sharpest form: long words never repeat at all.\n")
    print(
        f"{'words of':<14}{'in the body':>13}{'repeats':>9}{'chance':>9}{'if fixed':>10}{'P':>12}"
    )
    for floor in (4, 5, 6):
        kept = [w for w in body if len(w) >= floor]
        reference = [w for w in english if len(w) >= floor]
        rate = identity_rate(reference)
        expected = len(kept) * (len(kept) - 1) / 2 * rate
        seen_here = repeat_pairs(kept)
        print(
            f"{f'{floor}+ runes':<14}{len(kept):>13,}{seen_here:>9}"
            f"{chance_floor(kept):>9.2f}{expected:>10,.0f}"
            f"{stats.poisson.cdf(seen_here, expected):>12.1e}"
        )
    print(
        "\nNot one ciphertext word of four runes or more occurs twice in the whole book."
        "\nThe per-word base does not repeat in any way tied to the text."
    )


if __name__ == "__main__":
    main()
