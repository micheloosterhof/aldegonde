#!/usr/bin/env python3

"""
"""

import itertools
import random
import math
from scipy.stats import poisson

from aldegonde import pasc, masc, auto, c3301
from aldegonde.stats import print_ioc_statistics, print_kappa
from aldegonde.stats import repeats, dist, ngrams, entropy, isomorph, position
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor, primes, totient, modular, moebius
from aldegonde.analysis import friedman, kasiski, krakup, indepth, coincidence


def runes_only(text: str) -> str:
    """Keep only Cicada runes, dropping separators and Latin annotations."""
    return "".join(ch for ch in text if ch in c3301.CICADA_ALPHABET)


def deltastream(runes: list[int], skip: int = 1) -> list[int]:
    """
    deltastream mod MAX
    DIFF = C_K+1 - C_K % MAX
    """
    diff = []
    for i in range(0, len(runes) - skip):
        diff.append((runes[i + skip] - runes[i]) % 29)
    return diff


# with open("data/page54-55.txt") as f:
with open("data/page0-56.txt") as f:
    lp = f.read()

segments = lp.split("$")
# segments = [lp]
z = segments[0:10]
# z = segments[0:1]
# z = segments[9]
y = ["".join(z)]


print(f"{len(segments)} segments")

# Structural units for in-depth and position tests, same scope as the analysis
source = "".join(z)
words = [w for w in (runes_only(w) for w in source.split("-")) if w]
lines = [l for l in (runes_only(l) for l in source.split("/")) if l]
sections = [s for s in (runes_only(s) for s in z) if s]

print("\n=== IN-DEPTH ALIGNMENT (shared keystream at unit boundaries) ===")
for units, name in ((words, "words"), (lines, "lines"), (sections, "sections")):
    for align in ("left", "right"):
        r = indepth.alignment_coincidence(
            units, alphabetsize=29, align=align, min_length=5
        )
        print(
            f"  {name:8s} {align:5s}: hits={r.hits} opp={r.opportunities} "
            f"exp={r.expected:.1f} z={r.z_score:+.2f}"
        )

print("\n=== POSITION-IN-WORD frequency chi-square ===")
for r in position.position_frequency_chi2(words, min_count=100):
    print(f"  pos={r.position} n={r.n} chi2={r.chi2:.1f} p={r.pvalue:.4f}")

for i, s in enumerate(y):
    if len(s) == 0:
        continue
    print(f"\n\nNEW SEGMENT {i} **************")

    raw = "".join([x for x in s if x in c3301.CICADA_ALPHABET])

    print("RAW:")
    c3301.print_all(raw, limit=30)

    VIG = pasc.vigenere_tr(c3301.CICADA_ALPHABET)
    BOF = pasc.beaufort_tr(c3301.CICADA_ALPHABET)

    aut = "".join(
        auto.ciphertext_autokey_decrypt(raw, primer=c3301.CICADA_ALPHABET[0], tr=BOF)
    )

    FIRFUMFERENFE = "ᚠᛁᚱᚠᚢᛗᚠᛖᚱᛖᚾᚠᛖ"
    seg = "".join(pasc.pasc_decrypt(aut, keyword=FIRFUMFERENFE, tr=BOF))

    seg = raw
    print("SEG:")
    c3301.print_all(seg, limit=30)

    for skip in range(1, 2):
        # print(f"skip={skip}")
        if len(seg) == 0:
            print("EMPTY SEGMENT {i}")
            continue
        # print(f"source: {s}")
        # print(f"\nfull alphabet: {c3301.CICADA_ALPHABET}")
        # used = "".join([c3301.CICADA_ALPHABET[r] for r in set(seg)])
        print(f"used alphabet: {set(seg)} ({len(set(seg))} symbols)")
        # print(f"ciphertext: {seg.elements}")
        print(f"length: {len(seg)} symbols")
        print(f"   prime factors =: {factor.prime_factors(len(seg))}")
        print(f"   factor pairs  =: {factor.factor_pairs(len(seg))[1:-1]}")
        # c3301.print_all(seg, limit=30)
        dist.print_dist(seg)
        entropy.shannon_entropy(seg)
        print_ioc_statistics(seg, alphabetsize=29)
        bigram_diagram.print_auto_bigram_diagram(seg, alphabet=c3301.CICADA_ALPHABET)
        # bigram_diagram.print_bigram_diagram(seg, aut, alphabet=c3301.CICADA_ALPHABET)
        print_kappa(seg, trace=False)
        print_kappa(seg, length=2, trace=False)  # digraphic kappa
        print_kappa(seg, length=3, trace=False)  # trigraphic kappa
        for length in range(1, 5):
            print(f"kasiski ngram length={length}:")
            kasiski.print_kasiski_statistics(seg, min_length=length, max_length=length)
        print("higher-order coincidence (observed/expected joint lag matches):")
        for lag in range(2, 11):
            seps = sorted({1, lag - 1})
            jc = coincidence.joint_coincidence(seg, lag, seps)
            parts = " ".join(
                f"sep{s}={jc[s].observed}/{jc[s].expected:.1f}" for s in seps
            )
            print(f"  lag={lag:2d}: {parts}")
        friedman.friedman_test(seg, maxperiod=34)
        # friedman.friedman_test_with_interrupter(seg, alphabet=c3301.CICADA_ALPHABET, maxperiod=34)
        repeats.print_repeat_statistics(seg, minimum=2)
        repeats.print_repeat_positions(seg, minimum=5)
        # isomorph.print_isomorph_statistics(seg)

        # KRAKUP: Cyclic phenomena in nonhomogeneous material
        krakup.print_krakup_analysis(seg, min_period=2, max_period=40, window_size=100, step=10)

        # slide = ioc.sliding_window_ioc(seg, window=100)
        # for i, e in enumerate(slide):
        #    print(f"{i:5d} {e:.3f}")
