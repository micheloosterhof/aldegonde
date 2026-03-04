#!/usr/bin/env python3

"""
Liber Primus analysis: length-1 primer ciphertext autokey variant.
Uses 1-based indexing where EA rune = 29 % 29 = 0.
"""

import itertools
import random
import math
from collections import defaultdict
from scipy.stats import poisson

from aldegonde import pasc, masc, auto, c3301
from aldegonde.stats import print_ioc_statistics, print_kappa
from aldegonde.stats import repeats, dist, ngrams, entropy, isomorph
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor, primes, totient, modular, moebius
from aldegonde.analysis import friedman, krakup


def deltastream(runes: list[int], skip: int = 1) -> list[int]:
    """
    deltastream mod MAX
    DIFF = C_K+1 - C_K % MAX
    """
    diff = []
    for i in range(0, len(runes) - skip):
        diff.append((runes[i + skip] - runes[i]) % 29)
    return diff


def onebased_vigenere_tr(alphabet: list[str]) -> pasc.TR[str]:
    """Vigenere TR with 1-based indexing.

    val(rune) = (index + 1) % 29, so EA (index 28) = 29 % 29 = 0.
    C_index = (key_index + plain_index + 1) % 29
    """
    N = len(alphabet)
    tr: pasc.TR[str] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            # 1-based: val = (idx+1)%N, result_val = (val_k + val_p) % N
            # result_idx = (result_val - 1) % N = (i + j + 1) % N
            tr[key][e] = alphabet[(i + j + 1) % N]
    return tr


def onebased_beaufort_tr(alphabet: list[str]) -> pasc.TR[str]:
    """Beaufort TR with 1-based indexing.

    val(rune) = (index + 1) % 29, so EA (index 28) = 29 % 29 = 0.
    C_index = (key_index - plain_index - 1) % 29
    """
    N = len(alphabet)
    tr: pasc.TR[str] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            # 1-based Beaufort: result_val = (val_k - val_p) % N
            # result_idx = (result_val - 1) % N = (i - j - 1) % N
            tr[key][e] = alphabet[(i - j - 1) % N]
    return tr


def onebased_variantbeaufort_tr(alphabet: list[str]) -> pasc.TR[str]:
    """Variant Beaufort TR with 1-based indexing.

    val(rune) = (index + 1) % 29, so EA (index 28) = 29 % 29 = 0.
    C_index = (plain_index - key_index - 1) % 29
    """
    N = len(alphabet)
    tr: pasc.TR[str] = defaultdict(dict)
    for i, key in enumerate(alphabet):
        for j, e in enumerate(alphabet):
            tr[key][e] = alphabet[(j - i - 1) % N]
    return tr


# with open("data/page54-55.txt") as f:
with open("data/page0-58.txt") as f:
    lp = f.read()

segments = lp.split("$")
# segments = [lp]
z = segments[0:10]
# z = segments[0:1]
# z = segments[9]
y = ["".join(z)]

# Build 1-based indexed tabula rectae
VIG1 = onebased_vigenere_tr(c3301.CICADA_ALPHABET)
BOF1 = onebased_beaufort_tr(c3301.CICADA_ALPHABET)
VBF1 = onebased_variantbeaufort_tr(c3301.CICADA_ALPHABET)

# Also keep standard TRs for comparison
VIG = pasc.vigenere_tr(c3301.CICADA_ALPHABET)
BOF = pasc.beaufort_tr(c3301.CICADA_ALPHABET)

print(f"{len(segments)} segments")
for i, s in enumerate(y):
    if len(s) == 0:
        continue
    print(f"\n\nNEW SEGMENT {i} **************")

    raw = "".join([x for x in s if x in c3301.CICADA_ALPHABET])

    print("RAW:")
    c3301.print_all(raw, limit=30)
    print(f"length: {len(raw)} symbols")

    # Try all 29 length-1 primers with ciphertext autokey
    # Score with runeglish quadgram fitness
    print("\n=== CIPHERTEXT AUTOKEY WITH 1-BASED INDEXING ===")
    print("(val(rune) = (index+1) % 29, EA = 0)\n")

    results: list[tuple[float, str, str, str]] = []

    for tr_name, tr in [("Vigenere-1", VIG1), ("Beaufort-1", BOF1), ("VariantBeaufort-1", VBF1),
                         ("Vigenere-0", VIG), ("Beaufort-0", BOF)]:
        for pidx, primer_rune in enumerate(c3301.CICADA_ALPHABET):
            try:
                dec = "".join(
                    auto.ciphertext_autokey_decrypt(raw, primer=primer_rune, tr=tr)
                )
                score = c3301.quadgramscore(dec)
                results.append((score, tr_name, primer_rune, dec))
            except Exception as e:
                pass

    # Sort by score descending (less negative = better)
    results.sort(key=lambda x: x[0], reverse=True)

    print(f"{'Rank':>4} {'Score':>10} {'TR Type':<20} {'Primer':>6} {'English (first 30)':>10}")
    print("-" * 90)
    for rank, (score, tr_name, primer_rune, dec) in enumerate(results[:30], 1):
        pidx = c3301.r2i(primer_rune)
        eng = c3301.CICADA_ENGLISH_ALPHABET[pidx]
        dec_eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in dec[:40])
        print(f"{rank:4d} {score:10.2f} {tr_name:<20} {primer_rune} ({eng:>2} idx={pidx:2d}) {dec_eng}")

    # Run full analysis on the best result
    best_score, best_tr_name, best_primer, seg = results[0]
    best_pidx = c3301.r2i(best_primer)
    best_eng = c3301.CICADA_ENGLISH_ALPHABET[best_pidx]

    print(f"\n\n=== FULL ANALYSIS OF BEST RESULT ===")
    print(f"TR: {best_tr_name}, Primer: {best_primer} ({best_eng}, idx={best_pidx})")
    print(f"Score: {best_score:.2f}\n")

    print("DECRYPTED:")
    c3301.print_all(seg, limit=30)

    if len(seg) == 0:
        print("EMPTY SEGMENT")
        continue
    print(f"used alphabet: {set(seg)} ({len(set(seg))} symbols)")
    print(f"length: {len(seg)} symbols")
    print(f"   prime factors =: {factor.prime_factors(len(seg))}")
    print(f"   factor pairs  =: {factor.factor_pairs(len(seg))[1:-1]}")
    dist.print_dist(seg)
    entropy.shannon_entropy(seg)
    print_ioc_statistics(seg, alphabetsize=29)
    bigram_diagram.print_auto_bigram_diagram(seg, alphabet=c3301.CICADA_ALPHABET)
    print_kappa(seg, trace=False)
    print_kappa(seg, length=2, trace=False)  # digraphic kappa
    print_kappa(seg, length=3, trace=False)  # trigraphic kappa
    friedman.friedman_test(seg, maxperiod=34)
    repeats.print_repeat_statistics(seg, minimum=2)
    repeats.print_repeat_positions(seg, minimum=5)

    # KRAKUP: Cyclic phenomena in nonhomogeneous material
    krakup.print_krakup_analysis(seg, min_period=2, max_period=40, window_size=100, step=10)
