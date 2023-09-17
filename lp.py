#!/usr/bin/env python3

"""
"""

import itertools
import random
import math
from scipy.stats import poisson

from aldegonde import pasc, masc, auto, c3301
from aldegonde.stats import ioc, repeats, doublets, dist, ngrams, entropy, isomorph
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor, primes, totient, modular
from aldegonde.analysis import kappa, friedman


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
with open("data/page0-58.txt") as f:
    lp = f.read()

segments = lp.split("$")
# segments = [lp]
z = segments[0:10]
# z = segments[0:1]
# z = segments[9]
y = ["".join(z)]


print(f"{len(segments)} segments")
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
        auto.ciphertext_autokey_decrypt(raw, primer=c3301.CICADA_ALPHABET[0], tr=VIG)
    )

    seg = "".join(pasc.pasc_decrypt(aut, keyword="ᚳᛁᚱᚳᚢᛗᚠᛖᚱᛖᚾᚳᛖ", tr=BOF))
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
        # c3301.print_all(seg, limit=30)
        dist.print_dist(seg)
        entropy.shannon_entropy(seg)
        ioc.print_ioc_statistics(seg, alphabetsize=29)
        bigram_diagram.print_auto_bigram_diagram(seg, alphabet=c3301.CICADA_ALPHABET)
        bigram_diagram.print_bigram_diagram(seg, aut, alphabet=c3301.CICADA_ALPHABET)
        for i in range(1, 50):
            doublets.print_doublets_statistics(seg, skip=i, alphabetsize=29)
        kappa.print_kappa(seg, alphabetsize=29, trace=True)
        friedman.friedman_test(seg, maxperiod=34)
        repeats.print_repeat_statistics(seg, minimum=2)
        repeats.print_repeat_positions(seg, minimum=5)
        isomorph.print_isomorph_statistics(seg)

        # slide = ioc.sliding_window_ioc(seg, window=100)
        # for i, e in enumerate(slide):
        #    print(f"{i:5d} {e:.3f}")
