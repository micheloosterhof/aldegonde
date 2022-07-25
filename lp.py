#!/usr/bin/env python3

"""
"""

import random
import math
from scipy.stats import poisson

from aldegonde.structures import alphabet, sequence, cicada3301
from aldegonde.stats import ioc, repeats, doublets, dist
from aldegonde.grams import bigram_diagram
from aldegonde.analysis import kappa, isomorph
from aldegonde.algorithm import autokey

def try_totient(runes: list[int]):
    """ """
    from aldegonde.lib import phi_func

    out = []
    count = 1
    for r in runes:
        out.append((r - phi_func(count)) % 29)
        count += 1
    print(f"ENGLISH ioc={ioc.ioc(out):.3f} nioc={ioc.normalized_ioc(out):.3f}")
    cicada3301.english_output(out, limit=30)


# with open("data/page54-55.txt") as f:
with open("data/page0-58.txt") as f:
    lp = f.read()

# segments = lp.split("&")
segments = [lp]
print(f"{len(segments)} segments")
for i, s in enumerate(segments):
    if len(s) == 0:
        continue
    print(f"\n\nNEW SEGMENT {i} **************")

    seg = sequence.Sequence(s, alphabet=cicada3301.CICADA_ALPHABET)
    if len(seg) == 0:
        print("EMPTY SEGMENT {i}")
        continue
    # print(f"source: {s}")
    print(f"full alphabet: {seg.alphabet}")
    used = "".join([seg.alphabet[r] for r in set(seg.data)])
    print(f"used alphabet: {used} {len(set(seg.data))} items")
    # print(f"ciphertext: {seg.elements}")
    print(f"length: {len(seg)} runes")
    cicada3301.print_all(seg, limit=30)
    dist.print_dist(seg)
    print(f"ioc={ioc.ioc(seg):.3f} nioc={ioc.normalized_ioc(seg):.3f}")
    bigram_diagram.print_bigram_diagram(seg)
    bigram_diagram.bigram_diagram_skip(seg, skip=2)
    doublets.print_doublets_statistics(seg)
    doublets.print_doublets_statistics(seg, skip=2)
    repeats.print_repeat_statistics(seg, min=2)
    kappa.print_kappa(seg)
    reps = repeats.repeat2(seg, min=5)
    diffs = []
    for key in reps.keys():
        positions = reps[key]
        print(f"examining {key}: {reps[key]}")
        for i in range(1, len(positions)):
            diff = positions[i] - positions[i - 1]
            print(f"diff = {diff}")
            diffs.append(diff)
    isomorph.print_isomorph_statistics(seg)
