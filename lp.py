#!/usr/bin/env python3

"""
"""

from aldegonde.structures import alphabet, sequence, cicada3301
from aldegonde.stats import ioc, repeats, doublets
from aldegonde.grams import bigram_diagram
from aldegonde.analysis import kasiski


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


# with open("liber-primus__transcription--master.txt") as f:
with open("page0-58.txt") as f:
    lp = f.read()

segments = lp.split("&")
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
    print(f"alphabet: {seg.alphabet}")
    # print(f"ciphertext: {seg.elements}")
    print(f"length: {len(seg)} runes")
    print(f"ioc={ioc.ioc(seg):.3f} nioc={ioc.normalized_ioc(seg):.3f}")
    cicada3301.print_all(seg, limit=30)
    bigram_diagram.print_bigram_diagram(seg)
    doublets.print_doublets_statistics(seg)
    doublets.print_doublets_statistics(seg, skip=2)
    repeats.print_repeat_statistics(seg, min=2)
    kasiski.print_kappa(seg)
    reps=repeats.repeat2(seg, min=5)
    diffs=[]
    for key in reps.keys():
        positions = reps[key]
        print(f"examining {key}: {reps[key]}")
        for i in range(1, len(positions)):
            diff = positions[i] - positions[i-1]
            print(f"diff = {diff}")
            diffs.append(diff)
   
