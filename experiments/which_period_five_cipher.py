# ABOUTME: Asks what cipher family the within-word lag-5 channel actually pins, and shows
# ABOUTME: a globally periodic key is excluded while a per-word one is not.
"""Does the lag-5 evidence favour a Quagmire-style period-5 key, or rule it out?

Neither. It pins **period five inside a word** and is blind to which period-5 cipher does
it -- but it excludes the version whose key does not restart at each word.

## Every period-5 scheme makes the same prediction here

If positions i and i+5 share an alphabet then `c_i = c_(i+5)` exactly when
`p_i = p_(i+5)`, and the same holds for digraphs and trigraphs. Vigenere with a five-long
key, a Quagmire with a five-long key, and the length-clocked walk with g of order 5 are
**observationally identical** on this channel. It sees that the alphabets repeat with
period five; it cannot see how the five alphabets relate to one another -- shifts of a
common alphabet in the first two, powers of one permutation in the third.

## Triplets: yes, and they are there

    order      observed   H0 expects   English   H1 expects   LR
    monograph       104        72.6      1.7x        122.0    117 : 1
    digraph           9         1.53     4.7x          7.26   3,885 : 1
    trigraph          1         0.03    28.6x          0.86    12.5 : 1

Those three cannot be multiplied -- the digraph hits are a subset of the monograph hits.
Conditioning each order on the one below makes them independent, and then they do:

    step 1  monograph count                                      265 : 1
    step 2  digraph | monograph count   9 vs 3.15 / 5.28       12.4 : 1
    step 3  trigraph | digraph count    1 vs 0.036 / 1.32      10.3 : 1
    -------------------------------------------------------------------
    chain                                                    33,850 : 1
    without step 3                                            3,295 : 1

**Step 3 swings on one word.** Had the trigraph count been zero the step would read
0.28 : 1 *against*. The honest figure is a few thousand to one, with a hint of more.

## What is excluded: a key that does not restart at each word

A globally periodic key of period five makes the same prediction **across** word
boundaries, because the alphabet at absolute position i repeats every five runes
regardless of where words begin. The whole-stream lag-5 coincidence would then equal the
plaintext rate:

    whole-stream lag-5 observed        479 of 12,951   = 0.0370
    a globally periodic key predicts   0.0614          -> 796 hits
    no shared alphabet predicts        0.0345          -> 447 hits

The observation sits **-11.6 sigma** from the globally periodic prediction. A plain
period-5 Vigenere or Quagmire over the running text is dead, which `kappa-spectrum.md`
already concluded from the kappa spectrum; this is the same verdict from the plaintext
side, with the alternative quantified rather than only the null.

## So the shape is fixed and the mechanism is not

What the corpus supports: **five alphabets cycling inside each word, re-based at every
word boundary.** A Quagmire whose key restarts per word fits exactly. So does the walk.
Separating them needs the relationship between the five alphabets, which equality
coincidence cannot see -- that is the local-channel theorem, not a gap in effort.

    python which_period_five_cipher.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ngram_kappa_inside_a_word import body_words, english_words  # noqa: E402

LAG = 5
MOD = 29
MONOGRAPH_LR = 265.0  # from how_proven_is_the_shared_alphabet.py, drift-adjusted


def cell(words, n: int) -> tuple[int, int]:
    """(hits, eligible positions) for an n-gram repeat at distance LAG inside a word."""
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - LAG - n + 1):
            pairs += 1
            hits += all(w[i + j] == w[i + LAG + j] for j in range(n))
    return hits, pairs


def conditional(body_cell, body_below, english_cell, english_below):
    """LR for one order given the order below it, with the clustering taken from English."""
    hb, pb = body_cell
    hb_low, pb_low = body_below
    he, pe = english_cell
    he_low, pe_low = english_below
    flat = pb * (hb_low / pb_low) ** 2
    english_flat = pe * (he_low / pe_low) ** 2
    clustering = he / english_flat
    lr = np.exp(
        stats.poisson.logpmf(hb, flat * clustering) - stats.poisson.logpmf(hb, flat)
    )
    return flat, clustering, float(lr)


def main() -> None:
    rng = random.Random(3301)
    body, english = body_words(), english_words(rng)
    b = {n: cell(body, n) for n in (1, 2, 3)}
    e = {n: cell(english, n) for n in (1, 2, 3)}

    print("Unconditional cells. These cannot be multiplied -- they nest.\n")
    print(f"{'order':<12}{'observed':>10}{'H0':>10}{'English':>10}{'H1':>10}{'LR':>12}")
    for n, name in ((1, "monograph"), (2, "digraph"), (3, "trigraph")):
        hb, pb = b[n]
        he, pe = e[n]
        p0, p1 = 1 / MOD**n, he / pe
        lr = np.exp(
            stats.poisson.logpmf(hb, pb * p1) - stats.poisson.logpmf(hb, pb * p0)
        )
        print(
            f"{name:<12}{hb:>10}{pb * p0:>10.2f}{p1 / p0:>9.1f}x{pb * p1:>10.2f}"
            f"{lr:>10.1f} : 1"
        )

    print("\nConditioning each order on the one below makes them independent.\n")
    chain = MONOGRAPH_LR
    print(f"{'step':<34}{'H0':>8}{'H1':>8}{'seen':>6}{'LR':>12}")
    print(
        f"{'1  monograph count':<34}{'':>8}{'':>8}{b[1][0]:>6}{MONOGRAPH_LR:>10.1f} : 1"
    )
    for n, label in (
        (2, "2  digraph | monograph count"),
        (3, "3  trigraph | digraph count"),
    ):
        flat, clustering, lr = conditional(b[n], b[n - 1], e[n], e[n - 1])
        chain *= lr
        print(
            f"{label:<34}{flat:>8.3f}{flat * clustering:>8.2f}{b[n][0]:>6}{lr:>10.1f} : 1"
        )
    flat, clustering, _ = conditional(b[3], b[2], e[3], e[2])
    had_zero = np.exp(
        stats.poisson.logpmf(0, flat * clustering) - stats.poisson.logpmf(0, flat)
    )
    print(
        f"\n   chain {chain:,.0f} : 1     without step 3 {chain / _:,.0f} : 1"
        if False
        else ""
    )
    without = MONOGRAPH_LR * conditional(b[2], b[1], e[2], e[1])[2]
    print(f"   chain = {chain:,.0f} : 1        without step 3 = {without:,.0f} : 1")
    print(
        f"   step 3 rests on one word: at a count of zero it would read"
        f" {had_zero:.2f} : 1 against."
    )

    print("\nA key that does NOT restart at each word.\n")
    body_flat = "".join(body)
    english_flat = [x for w in english for x in w]
    seen = sum(body_flat[i] == body_flat[i + LAG] for i in range(len(body_flat) - LAG))
    slots = len(body_flat) - LAG
    plain = sum(
        english_flat[i] == english_flat[i + LAG] for i in range(len(english_flat) - LAG)
    ) / (len(english_flat) - LAG)
    z = (seen - slots * plain) / np.sqrt(slots * plain * (1 - plain))
    print(
        f"   whole-stream lag-5 observed      {seen} of {slots:,} = {seen / slots:.4f}"
    )
    print(
        f"   a globally periodic key predicts {plain:.4f} -> {slots * plain:.0f} hits"
    )
    print(
        f"   no shared alphabet predicts      {1 / MOD:.4f} -> {slots / MOD:.0f} hits"
    )
    print(f"   observed is {z:+.1f} sigma from the globally periodic prediction\n")
    print(
        "Five alphabets cycling inside each word, re-based at every word boundary."
        "\nA Quagmire whose key restarts per word fits exactly, and so does the walk."
    )


if __name__ == "__main__":
    main()
