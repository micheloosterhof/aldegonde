#!/usr/bin/env python3

"""
"""

from aldegonde.structures import alphabet, sequence, cicada3301
from aldegonde.stats import ioc
from aldegonde.grams import bigram_diagram


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


with open("liber-primus__transcription--master.txt") as f:
    lp = f.read()

segments = lp.split("$")
print(f"{len(segments)} segments")
for s in segments:
    if len(s) == 0:
        continue
    seg = sequence.Sequence(s, alphabet=cicada3301.CICADA_ALPHABET)
    if len(seg) == 0:
        print("EMPTY SEGMENT")
        continue
    print("\n\nNEW SEGMENT **************\n\n")
    # print(f"source: {s}")
    print(f"alphabet: {seg.alphabet}")
    # print(f"ciphertext: {seg.elements}")
    print(f"length: {len(seg)} runes")
    print(f"ioc={ioc.ioc(seg):.3f} nioc={ioc.normalized_ioc(seg):.3f}")
    cicada3301.print_all(seg, limit=30)
    # bigram_diagram.print_bigram_diagram(seg)
