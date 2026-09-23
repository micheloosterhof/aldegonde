# ABOUTME: Tests whether the per-word base is a function of the previous ciphertext word,
# ABOUTME: which would make the key visible, and excludes every form of it.
"""A ciphertext autokey at the word level would hand us the key. It is not there.

The per-word base is a general permutation taking at least 949 values
(`what_the_five_alphabets_are.py`, `alphabet_count_bound.py`). Where do those values come
from? A **ciphertext autokey** is the one answer that would make them recoverable: if the
base for word w is some function of word w-1's ciphertext, the key is written on the page.

It is also sharply falsifiable. Two words whose predecessors are identical would get
identical bases, and two words that share a base coincide at matched positions at the
**plaintext** rate rather than at chance.

    H1  a shared base   0.0794   (measured on English, matched positions)
    H0  no shared base  0.0345   (chance)

## Result: every form is excluded

    if the base is a function of        pairs     seen      H0       H1   z vs H1
    the whole previous word               742       30      26       59      -3.9
    its last rune                     465,312   16,160  16,045   36,943    -112.7
    its first rune                    465,053   15,999  16,036   36,923    -113.5
    its last two runes                 15,881      548     548    1,261     -20.9
    its length                      1,986,954   68,441  68,516  157,754    -234.4

Every row sits on H0 and nowhere near H1.

**The first row is the general test.** It does not assume anything about the function: any
deterministic rule whatever -- a shift, a keyed alphabet, a hash -- gives identical bases to
words with identical predecessors. It is also the weakest row, because only 742 word pairs
in the body share an identical preceding ciphertext word. Even so the arms are far enough
apart that it prices at **7,312 : 1 against**.

## The literal positional autokey is separately dead

If `c_i(w) = p_i(w) + c_i(w-1) mod 29`, then subtracting the previous word rune by rune
recovers the plaintext, so the difference stream would read as language:

    difference stream   9,296 runes   IoC = 0.03447
    flat                              0.03448
    English runeglish                 0.0794

**Flat to four decimal places.**

## What is not excluded

A base that depends on the previous word **and** on something else -- an absolute position,
a page, a running counter -- would not give identical bases to identical predecessors, and
this test says nothing about it. What is excluded is the previous word acting alone.

    python is_the_base_a_ciphertext_autokey.py
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
ENGLISH_WORDS = 30_000

FEATURES = (
    ("the whole previous word", lambda p: p),
    ("its last rune", lambda p: p[-1]),
    ("its first rune", lambda p: p[0]),
    ("its last two runes", lambda p: p[-2:]),
    ("its length", lambda p: len(p)),
)


def matched_position(words, key=None):
    """(coincidences, pairs) at matched positions, optionally only within a key class."""
    columns = defaultdict(list)
    for w, tag in words:
        if key is not None and tag is None:
            continue
        for i, ch in enumerate(w):
            columns[(i, tag)].append(ch)
    hits = pairs = 0
    for column in columns.values():
        n = len(column)
        if n < 2:
            continue
        pairs += n * (n - 1) // 2
        hits += sum(v * (v - 1) // 2 for v in Counter(column).values())
    return hits, pairs


def main() -> None:
    rng = random.Random(3301)
    body = body_words()
    previous = [None, *body[:-1]]

    english = english_words(rng)[:ENGLISH_WORDS]
    shared_hits, shared_pairs = matched_position([(w, 0) for w in english])
    p1 = shared_hits / shared_pairs
    p0 = 1 / MOD
    print(f"H1  a shared base   {p1:.4f}   (English, matched positions)")
    print(f"H0  no shared base  {p0:.4f}   (chance)\n")

    print(
        f"{'if the base is a function of':<30}{'pairs':>11}{'seen':>9}"
        f"{'H0':>9}{'H1':>9}{'z vs H1':>10}"
    )
    for label, feature in FEATURES:
        tagged = [
            (w, feature(p) if p is not None else None) for w, p in zip(body, previous)
        ]
        hits, pairs = matched_position(tagged, key=feature)
        if pairs < 50:
            continue
        expected = pairs * p1
        z = (hits - expected) / np.sqrt(expected * (1 - p1))
        print(
            f"{label:<30}{pairs:>11,}{hits:>9,}{pairs * p0:>9,.0f}"
            f"{expected:>9,.0f}{z:>+10.1f}"
        )
        if label.startswith("the whole"):
            ratio = np.exp(
                stats.binom.logpmf(hits, pairs, p0)
                - stats.binom.logpmf(hits, pairs, p1)
            )
            general = f"{ratio:,.0f} : 1 against"

    print(
        "\nThe first row is the general test: any deterministic rule whatever gives"
        "\nidentical bases to words with identical predecessors. It is also the weakest,"
        f"\nsince only that many pairs qualify -- and it still prices at {general}.\n"
    )

    index = {ch: i for i, ch in enumerate(sorted({c for w in body for c in w}))}
    stream = [
        (index[w[i]] - index[p[i]]) % MOD
        for w, p in zip(body, previous)
        if p is not None
        for i in range(min(len(w), len(p)))
    ]
    counts = Counter(stream)
    n = len(stream)
    ioc = sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))
    print("Literal positional autokey: c_i(w) = p_i(w) + c_i(w-1) mod 29\n")
    print(f"   difference stream   {n:,} runes   IoC = {ioc:.5f}")
    print(f"   flat                            {p0:.5f}")
    print(f"   English runeglish               {p1:.4f}")
    print(
        "\n   Subtracting the previous word rune by rune would recover the plaintext."
        "\n   It recovers nothing."
    )


if __name__ == "__main__":
    main()
