# ABOUTME: Uses the key-free d5 plaintext reading to enumerate candidate plaintexts
# ABOUTME: for the most structurally constrained words in the corpus.
"""d5 reads plaintext equality directly, which narrows a handful of words hard.

`period5_confirmation.py` establishes that g has order exactly 5, so within a word

    c_j == c_{j+5}   <=>   p_j == p_{j+5}

with no base, no sigma and no g in it. Every d5 pair is therefore a FREE fact about
the plaintext: 102 known equalities and 1,971 known inequalities over the 806 words
of length >= 6.

Most words gain little from one such fact. But 8 words carry XY..XY -- two
consecutive d5 matches -- and one carries XYZ..XYZ, and requiring a dictionary word
to satisfy every d5 equality AND every d5 inequality in the same word prunes hard:

    word 1987  L=10  p0=p5, p3=p8, p4=p9      4 candidates
    word 2751  L=8   p0=p5, p1=p6, p2=p7     14 candidates
    word  526  L=10  p0=p5, p1=p6            54 candidates
    word 1515  L=10  p0=p5, p1=p6            54 candidates
    word 2168  L=10  p1=p6, p2=p7            67 candidates

Two caveats, both real. The counts of these events are ORDINARY -- against
length-matched prose the LP shows 102 d5 matches (prose 115.2 +- 10.3), 9 XY..XY
(6.6 +- 2.7) and 1 XYZ..XYZ (0.8 +- 0.8), so nothing here is anomalous; the value is
that the STRUCTURE is rare, not that the count is. And the candidate lists depend on
the dictionary: the LP's vocabulary is philosophical and may sit outside a
frequency-ranked English list, so a short list is a lead rather than an answer.

Why it matters for the key. `information_budget.py` sizes the crib route at about 63
contiguous runes. These 8 words total ~70 runes but are NOT contiguous, so each
carries its own unknown base and the crib is weaker per rune. What multiple known
words do give, with no base_0, is injectivity: if M_w(x_j) == M_w'(y_i) then
c_j must equal c'_i. That is a constraint on (g, sigma) alone, and it is the
mechanism `crib_divinity_within.py` already uses -- this file supplies more places
to apply it.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words  # noqa: E402

from aldegonde import c3301  # noqa: E402

IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ALPHA = c3301.CICADA_ALPHABET
DICT_SIZE = 200000
SHOW = 9


def dictionary() -> dict[int, list[tuple[tuple[int, ...], str, float]]]:
    from wordfreq import top_n_list, word_frequency

    out: dict[int, list[tuple[tuple[int, ...], str, float]]] = defaultdict(list)
    for word in top_n_list("en", DICT_SIZE):
        if not word.isalpha():
            continue
        runes = tuple(IDX[c] for c in english_to_runeglish(word.upper()) if c in IDX)
        if runes:
            out[len(runes)].append((runes, word, word_frequency(word, "en")))
    return out


def d5_constraints(
    word: list[int],
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """(equal pairs, unequal pairs) at distance 5 -- all key-free plaintext facts."""
    equal = [(j, j + 5) for j in range(len(word) - 5) if word[j] == word[j + 5]]
    unequal = [(j, j + 5) for j in range(len(word) - 5) if word[j] != word[j + 5]]
    return equal, unequal


def main() -> None:
    words = load_words()
    vocab = dictionary()
    targets = []
    for index, word in enumerate(words):
        doubles = [
            j
            for j in range(len(word) - 6)
            if word[j] == word[j + 5] and word[j + 1] == word[j + 6]
        ]
        if doubles:
            targets.append((index, word))
    print(f"{len(targets)} words carry XY..XY at lag 5 (two consecutive d5 matches)\n")
    for index, word in targets:
        equal, unequal = d5_constraints(word)
        fits = [
            (f, eng)
            for runes, eng, f in vocab.get(len(word), [])
            if all(runes[a] == runes[b] for a, b in equal)
            and all(runes[a] != runes[b] for a, b in unequal)
        ]
        fits.sort(reverse=True)
        needs = ", ".join(f"p{a}=p{b}" for a, b in equal)
        print(
            f"word {index:>5} L={len(word):<3} {''.join(ALPHA[r] for r in word)}"
            f"   requires {needs}"
        )
        listed = ", ".join(eng for _f, eng in fits[:SHOW])
        print(f"    {len(fits)} candidates" + (f": {listed}" if fits else " -- none"))
    print("\nThese constraints need no key: d5 reads plaintext equality directly.")
    print("Counts are ordinary against prose; the VALUE is the narrow structure.")


if __name__ == "__main__":
    main()
