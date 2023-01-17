#!/usr/bin/env python3

"""
"""

import itertools
import random
import math
from scipy.stats import poisson

from aldegonde.structures import alphabet, sequence, cicada3301
from aldegonde.stats import ioc, repeats, doublets, dist, ngrams
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor, primes, totient, modular
from aldegonde.analysis import kappa, isomorph, friedman
from aldegonde.algorithm import autokey


def deltastream(runes: list[int], skip: int = 1) -> list[int]:
    """
    deltastream mod MAX
    DIFF = C_K+1 - C_K % MAX
    """
    diff = []
    for i in range(0, len(runes) - skip):
        diff.append((runes[i + skip] + runes[i]) % 29)
    return diff


#with open("data/page54-55.txt") as f:
with open("data/page0-58.txt") as f:
    lp = f.read()

segments = lp.split("$")
#segments = [lp]
z = segments[0:10]
#z = segments[0:1]
#z = segments[9]
y = ["".join(z)]


#priem = primes.primes(10000)
#priem.remove(29)
#tot = []
#for i in range(0,len(y[0])+2):
#    tot.append(totient.phi_func(i))


print(f"{len(segments)} segments")
for i, s in enumerate(y):
    if len(s) == 0:
        continue
    print(f"\n\nNEW SEGMENT {i} **************")
    seg = sequence.Sequence.fromstr(text=s, alphabet=cicada3301.CICADA_ALPHABET)

    #l = []
    #for i, e in enumerate(seq):
    #    l.append((e+tot[i])%29)

    #seg = sequence.Sequence.fromlist(data=l, alphabet=cicada3301.CICADA_ALPHABET)

    for skip in range(1, 2):
        # print(f"skip={skip}")
        if len(seg) == 0:
            print("EMPTY SEGMENT {i}")
            continue
        # print(f"source: {s}")
        print(f"full alphabet: {seg.alphabet}")
        used = "".join([seg.alphabet[r] for r in set(seg.data)])
        print(f"used alphabet: {used} {len(set(seg.data))} symbols")
        # print(f"ciphertext: {seg.elements}")
        print(f"length: {len(seg)} runes")
        cicada3301.print_all(seg, limit=30)
        dist.print_dist(seg)
        ioc.print_ioc_statistics(seg)
        bigram_diagram.print_bigram_diagram(seg)
        bigram_diagram.print_bigram_diagram(seg, skip=2)
        doublets.print_doublets_statistics(seg)
        doublets.print_doublets_statistics(seg, skip=2)
        repeats.print_repeat_statistics(seg, minimum=2)
        kappa.print_kappa(seg)
        friedman.friedman_test(seg)
        reps = repeats.repeat2(seg, minimum=5)
        diffs = []
        for key in reps.keys():
            positions = reps[key]
            for v in itertools.combinations(positions, 2):
                print(
                    f"repeat: {key} loc={v[1]},{v[0]} diff={abs(v[1]-v[0])} factors={factor.prime_factors(abs(v[1]-v[0]))}"
                )

        print("\n")
        # isomorph.print_isomorph_statistics(seg)

        #slide = ioc.sliding_window_ioc(seg, window=100)
        #for i, e in enumerate(slide):
        #    print(f"{i:5d} {e:.3f}")
