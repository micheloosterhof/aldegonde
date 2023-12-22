#!/usr/bin/env python3

from collections.abc import Callable, Sequence
import random
import copy
from typing import NamedTuple, TypeVar

from aldegonde import masc
from aldegonde.stats import compare, ngrams

T = TypeVar("T")

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

AFF = "HAGDGKDJKQNDFICEIVZOSABBNWIJIDIBWIDIBWSTITIDWTABDJKPDNIDGDIJDWZTJSYDNKGDJSPKCPSJDIFSIJZDNKGDKVOGNKPDNWYIDWUIGIYKQNDOGIKBKVYIVDNWGEKPPWJFJIXWIVZGAJWTKXWPIGGWVQWJGGWDGIKBDNIDZIOTSJIDNJWWNSAJDSAJIDNJWWNSAJDSAJDNWUWIDNWJGDIJDWZQWDDKVQJSAQNDNWDKVOGNKPUIGDSGGWZKTVSDTSJDNWCSAJIQWSTDNWTWIJBWGGCJWUDNWYKVVSUUSABZFWBSGDDNWYKVVSUUSABZFWBSGDDNWGNKPGWDQJSAVZSVDNWGNSJWSTDNKGAVCNIJDWZZWGWJDKGBWUKDNQKBBKQIVDNWGEKPPWJDSSDNWYKBBKSVIKJWIVZNKGUKTWDNWYSXKWGDIJDNWPJSTWGGSJIVZYIJOIVVNWJWSVQKBBKQIVGKGBW"

CRIB = "OYFSTGLYYRSBXPTCLLIRSBSLZANYSGYNXXPFYXTONWRTVYRAYLDJRYLQOWLBLSOCLSLTTFSQIYLVRTRNSNGFSLUICNTRELNYQSFSVLQRTINTFCOLVWSRVRFSRGRGFRCLQWLZNJCQZFHLJIZNJCQSOBNYRBWOAFVHONTCLLIFSQNGOLSIYNOLTOLQCNJQCP"

CT = CRIB.replace(" ", "").replace(",", "").replace(".", "").replace("\n", "")


def brute_affine():
    """
    bruteforce all shifts
    """
    out: list[tuple[int, int, str, float]] = []
    for shift in range(len(alphabet)):
        for multiplier in range(len(alphabet)):
            try:
                key = masc.affinekey(alphabet, multiplier, shift)
                pt = "".join(masc.masc_decrypt(CT, key))
                score = compare.quadgramscore(pt)
                out.append(tuple([multiplier,shift,pt,score]))
            except:
                pass
    for p in sorted(out, key=lambda x: x[3]):
        print(p)


if __name__ == "__main__":
    brute_affine()
