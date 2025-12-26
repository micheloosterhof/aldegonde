#!/usr/bin/env python3
"""Liber Primus analysis script.

This script performs cryptanalysis on Liber Primus segments using various
statistical methods including IOC, Kappa test, Friedman test, and repeat analysis.
"""

import math
import os

from scipy.stats import poisson

from aldegonde import auto, c3301, pasc
from aldegonde.analysis import friedman
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor
from aldegonde.stats import dist, entropy, ioc, kappa, repeats


def deltastream(runes: list[int], skip: int = 1) -> list[int]:
    """Calculate delta stream mod 29.

    DIFF = C_K+1 - C_K % MAX
    """
    diff = []
    for i in range(0, len(runes) - skip):
        diff.append((runes[i + skip] - runes[i]) % 29)
    return diff


def main() -> None:
    """Main analysis function."""
    # Get the data directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "..", "data", "page0-58.txt")

    with open(data_file) as f:
        lp = f.read()

    segments = lp.split("$")
    z = segments[0:10]

    print(f"{len(segments)} segments")
    for i, s in enumerate(z):
        if len(s) == 0:
            continue
        print(f"\n\nNEW SEGMENT {i} **************")

        raw = "".join([x for x in s if x in c3301.CICADA_ALPHABET])

        print("RAW:")
        c3301.print_all(raw, limit=30)

        VIG = pasc.vigenere_tr(c3301.CICADA_ALPHABET)
        BOF = pasc.beaufort_tr(c3301.CICADA_ALPHABET)

        aut = "".join(
            auto.ciphertext_autokey_decrypt(
                raw, primer=c3301.CICADA_ALPHABET[0], tr=BOF
            )
        )

        FIRFUMFERENFE = "ᚠᛁᚱᚠᚢᛗᚠᛖᚱᛖᚾᚠᛖ"
        seg = "".join(pasc.pasc_decrypt(aut, keyword=FIRFUMFERENFE, tr=BOF))

        seg = raw
        print("SEG:")
        c3301.print_all(seg, limit=30)

        for skip in range(1, 2):
            if len(seg) == 0:
                print("EMPTY SEGMENT {i}")
                continue
            print(f"used alphabet: {set(seg)} ({len(set(seg))} symbols)")
            print(f"length: {len(seg)} symbols")
            print(f"   prime factors =: {factor.prime_factors(len(seg))}")
            print(f"   factor pairs  =: {factor.factor_pairs(len(seg))[1:-1]}")
            dist.print_dist(seg)
            entropy.shannon_entropy(seg)
            ioc.print_ioc_statistics(seg, alphabetsize=29)
            bigram_diagram.print_auto_bigram_diagram(
                seg, alphabet=c3301.CICADA_ALPHABET
            )
            kappa.print_kappa(seg, trace=True)
            friedman.friedman_test(seg, maxperiod=34)
            repeats.print_repeat_statistics(seg, minimum=2)
            repeats.print_repeat_positions(seg, minimum=5)


if __name__ == "__main__":
    main()
