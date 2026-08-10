#!/usr/bin/env python3
# ABOUTME: Tests ciphertext-autokey (alphabet driven by previous ciphertext rune)
# ABOUTME: by grouping each rune by its predecessor and checking within-group IoC.
"""If the cipher were CIPHERTEXT-autokey -- c[i] = TR[c[i-1]][p[i]], the alphabet
selected by the previous (public) ciphertext rune -- then grouping positions by
c[i-lag] fixes the alphabet within each group, so the plaintext roughness shows
through: within-group ciphertext IoC ~ 1.8, even though the pooled ciphertext is
flat (1.0). Positional-progressive (our model) predicts flat within-group.

This matters because ciphertext-autokey has a PUBLIC keystream (the ciphertext),
which would collapse the unknowns to just the tabula recta. Result: flat within
every previous-rune group -> ciphertext-autokey is refuted, the keystream is not
the ciphertext. (Plaintext-autokey, with a hidden keystream, is not testable this
way and gives no such shortcut.)
"""

from __future__ import annotations

from collections import Counter, defaultdict

from experiments.within_word_position_decomposition import load_words

M = 29


def ioc(counts: Counter) -> tuple[int, int]:
    n = sum(counts.values())
    return sum(v * (v - 1) for v in counts.values()), n * (n - 1)


def main() -> None:
    words = load_words()
    print("within-word IoC of c[i] grouped by a previous ciphertext rune")
    print("(ciphertext-autokey => ~1.8; positional/plaintext-driven => ~1.0)\n")
    for lag, label in [(1, "c[i-1]"), (2, "c[i-2]"), (5, "c[i-5] (same phase)")]:
        groups: dict[int, Counter] = defaultdict(Counter)
        for w in words:
            for i in range(lag, len(w)):
                groups[w[i - lag]][w[i]] += 1
        tm = te = 0
        for c in groups.values():
            m, e = ioc(c)
            tm += m
            te += e
        pooled = M * tm / te if te else 0.0
        print(f"  group by {label:<20} within-group IoC = {pooled:.3f}")
    print("\nflat within-group => alphabet is NOT selected by the ciphertext.")


if __name__ == "__main__":
    main()
