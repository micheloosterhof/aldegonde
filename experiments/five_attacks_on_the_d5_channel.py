# ABOUTME: Five attempts to break the within-word lag-5 result, four failing and one
# ABOUTME: exposing a contaminated null that had to be replaced.
"""The d5 evidence built the period-5 model, so confirming the model with d5 is circular.

This file attacks the within-word lag-5 coincidence instead of confirming it. Four attacks
fail, one appears to succeed and turns out to rest on a contaminated null, and the honest
residue is a narrower claim than the model makes.

## 1. The word-population confound

Different lags draw from different words: lag-2 pairs come from every word of three runes
or more, lag-5 pairs only from words of six or more. If long words simply coincide more,
lag 5 would look special for a reason that has nothing to do with the number five. Fixing
the population kills the confound.

    min length  words     lag1    lag2    lag3    lag4    lag5    lag6    lag7
             2  2,812   -15.24   +0.13   +0.97   +1.83   +3.69   -1.87   +0.95
             6    815   -11.10   +0.25   +0.19   +1.63   +3.69   -1.87   +0.95
             7    559    -9.68   -0.69   -0.53   +1.42   +3.91   -1.87   +0.95
             8    343    -7.87   -0.04   -0.53   +1.32   +3.88   -2.14   +0.95
             9    187    -6.47   +0.13   +0.20   +1.09   +3.72   -1.61   +0.49
            10    109    -4.93   +0.65   +2.12   +1.04   +3.63   -1.92   -0.12

**Fails.** Lag 5 holds between +3.6 and +3.9 at every population, and its neighbours stay
flat. Longer words do not coincide more -- lag 6 draws from even longer words and is
negative.

## 2. Look-elsewhere across lags

**Fails.** The maximum over lags 2-8 is +3.69 against a surrogate maximum of +0.29 +- 0.67.

## 3. Held-out halves

**Fails.** First half 56 of 1,065 (+3.18), second half 48 of 1,040 (+2.03). The effect is
in both.

## 4. A positional artifact

**Fails.** The excess is at every start position inside the word, not at one:

    start      0     1     2     3     4
    hits      36    27    18    11     7
    expected  28.1  19.3  11.8   6.4   3.8

## 5. The baseline -- this one lands, then falls over

Shuffling the letters **inside each word**, which preserves word length and letter
multiset, is the obvious null. It breaks the result:

    lag                1       2       3       4       5       6       7
    z vs shuffle  -14.04   +5.30   +4.40   +4.26   +5.62   -1.05   +1.76

Lags 2, 3 and 4 are as elevated as lag 5, and "only lag 5 is special" collapses.

**But that null is contaminated by the cipher.** It preserves each word's letter multiset,
and the doublet preventer has already stripped repeated letters out of those multisets --
adjacent repeats are suppressed 82%. So the null sits about 24% below chance at every lag
(190 expected against 250 at lag 2) and manufactures an excess wherever it is used.

A **global** shuffle -- all body runes permuted, word lengths kept -- preserves the
ciphertext letter frequencies and destroys everything else, including the preventer's mark
on the multisets. It lands on 1/29:

    lag      obs   chance   within-word null      z   global null      z
      1       63    346.9     248.5 +- 10.7  -17.28  345.7 +- 18.8  -15.05
      2      252    250.0     190.9 +- 11.3   +5.42  247.8 +- 15.7   +0.27
      3      181    168.4     135.7 +- 10.2   +4.45  168.0 +- 12.6   +1.03
      4      131    111.7      93.0 +-  8.2   +4.65  111.5 +- 10.2   +1.91
      5      104     72.6      61.4 +-  7.6   +5.62   72.7 +-  8.2   +3.81
      6       32     44.5      38.1 +-  5.7   -1.08   44.0 +-  6.1   -1.96
      7       30     25.2      22.2 +-  4.4   +1.78   24.8 +-  4.7   +1.10

Against the clean null only lag 5 survives, at +3.7 (the figure moves by about
0.15 between seeds; the run above and the table here are two draws). The attack fails, and what it leaves
behind is a standing rule: **a within-word shuffle is the wrong null for this corpus**,
because the preventer has already edited the thing it preserves.

## 6. The solved front matter, which decides nothing

Its cipher is not the body's, so it should show no lag-5 excess. It reads +1.70 at lag 5,
with lag 7 higher at +2.37 -- but it has 694 words against 2,895, so the body's own effect
size would only produce about +1.5 there. **Underpowered, and it is reported so that it is
not mistaken for a passed control.**

## What survives, stated narrowly

The excess is real at +3.7 on 104 hits against 72.6. What it pins is that **positions i
and i+5 inside a word share an alphabet**. It does not pin that g is a permutation of
order 5: a five-long keystream restarting at each word predicts exactly the same thing, as
does any scheme giving those two positions the same alphabet. The model is one member of
that family and this channel cannot choose between them.

    python five_attacks_on_the_d5_channel.py
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ngram_kappa_inside_a_word import body_words  # noqa: E402

MOD = 29
LAGS = range(1, 8)
DRAWS = 300


def hits(words, lag: int) -> int:
    return sum(w[i] == w[i + lag] for w in words for i in range(len(w) - lag))


def pairs(words, lag: int) -> int:
    return sum(max(0, len(w) - lag) for w in words)


def within_word_null(words, lag, rng, draws=DRAWS):
    return np.array(
        [
            hits(["".join(rng.sample(w, len(w))) for w in words], lag)
            for _ in range(draws)
        ]
    )


def global_null(words, lag, rng, draws=DRAWS):
    lengths = [len(w) for w in words]
    flat = list("".join(words))

    def regroup(pool):
        out, i = [], 0
        for n in lengths:
            out.append("".join(pool[i : i + n]))
            i += n
        return out

    return np.array(
        [hits(regroup(rng.sample(flat, len(flat))), lag) for _ in range(draws)]
    )


def attack_population(words) -> None:
    print("1. The word-population confound: fix the population, vary the lag.\n")
    print(
        f"{'min length':>11}{'words':>8}"
        + "".join(f"{'lag' + str(k):>9}" for k in LAGS)
    )
    for floor in (2, 6, 7, 8, 9, 10):
        kept = [w for w in words if len(w) >= floor]
        cells = []
        for k in LAGS:
            p = pairs(kept, k)
            expected = p / MOD
            cells.append(
                f"{(hits(kept, k) - expected) / np.sqrt(expected):+9.2f}"
                if p >= 40
                else f"{'--':>9}"
            )
        print(f"{floor:>11}{len(kept):>8}" + "".join(cells))
    print("  Lag 5 holds at every population and its neighbours stay flat.\n")


def attack_lookelsewhere(words, rng) -> None:
    def top(ws):
        best = -99.0
        for k in range(2, 9):
            expected = pairs(ws, k) / MOD
            best = max(best, (hits(ws, k) - expected) / np.sqrt(expected))
        return best

    observed = top(words)
    null = np.array(
        [top(["".join(rng.sample(w, len(w))) for w in words]) for _ in range(2000)]
    )
    print("2. Look-elsewhere over lags 2-8.\n")
    print(f"   observed max {observed:+.2f} against null {null.mean():+.2f}")
    print(f"   +- {null.std(ddof=1):.2f}   P = {np.mean(null >= observed):.4f}\n")


def attack_splits(words) -> None:
    print("3. Held-out halves at lag 5.\n")
    half = len(words) // 2
    for label, part in (("first", words[:half]), ("second", words[half:])):
        p = pairs(part, 5)
        expected = p / MOD
        h = hits(part, 5)
        print(
            f"   {label:<7}{h:>5} of {p:>6}"
            f"   z = {(h - expected) / np.sqrt(expected):+.2f}"
        )
    print()


def attack_position(words) -> None:
    print("4. Is it one position inside the word?\n")
    seen, total = Counter(), Counter()
    for w in words:
        for i in range(len(w) - 5):
            total[i] += 1
            seen[i] += w[i] == w[i + 5]
    print(f"{'start':>8}{'hits':>7}{'pairs':>8}{'expected':>10}")
    for i in sorted(total):
        if total[i] >= 20:
            print(f"{i:>8}{seen[i]:>7}{total[i]:>8}{total[i] / MOD:>10.1f}")
    print("  The excess is spread over every start position.\n")


def attack_baseline(words, rng) -> None:
    print("5. The baseline. A within-word shuffle breaks it, and is contaminated.\n")
    print(
        f"{'lag':>4}{'obs':>7}{'chance':>9}{'within-word null':>22}{'z':>8}"
        f"{'global null':>20}{'z':>8}"
    )
    for k in LAGS:
        h, p = hits(words, k), pairs(words, k)
        wn, gn = within_word_null(words, k, rng), global_null(words, k, rng)
        print(
            f"{k:>4}{h:>7}{p / MOD:>9.1f}"
            f"{f'{wn.mean():.1f} +- {wn.std(ddof=1):.1f}':>22}"
            f"{(h - wn.mean()) / wn.std(ddof=1):>+8.2f}"
            f"{f'{gn.mean():.1f} +- {gn.std(ddof=1):.1f}':>20}"
            f"{(h - gn.mean()) / gn.std(ddof=1):>+8.2f}"
        )
    print(
        "\n  The within-word null preserves each word's letter multiset, and the doublet"
        "\n  preventer has already stripped repeats out of those multisets. It sits 24%"
        "\n  below chance and manufactures an excess at every lag. The global shuffle"
        "\n  keeps only the letter frequencies and word lengths, lands on 1/29, and"
        "\n  leaves lag 5 alone at +3.7.\n"
    )


def main() -> None:
    rng = random.Random(3301)
    words = body_words()
    print(f"the body: {len(words):,} blocks, {sum(map(len, words)):,} runes\n")
    attack_population(words)
    attack_lookelsewhere(words, rng)
    attack_splits(words)
    attack_position(words)
    attack_baseline(words, rng)
    print(
        "What survives is narrow: positions i and i+5 inside a word share an alphabet."
        "\nThat does not pin g as a permutation of order 5 -- a five-long keystream"
        "\nrestarting at each word predicts the same thing, and this channel cannot"
        "\nchoose between them."
    )


if __name__ == "__main__":
    main()
