#!/usr/bin/env python3

# IDEAS: simmulated annealing
# IDEAS: steepest ascent (is practical? 28x27=756 evaluations)

from typing import TypeVar

from aldegonde import masc
from aldegonde.stats import compare

T = TypeVar("T")

CAE="WTLPHDCRTPAXIIATVGTTCQPAADURAPNVJBQNQJINDJHWDJASHTTLWPIWTRPCSDIDSPNVJBQNWTRPCLPAZXCIDBPCNQDDZHLXIWWXHEDCTNEPAEDZTNIDDPCSXUNDJWPKTPWTPGIIWTCVJBQNHPEPGIDUNDJVJBQN"

DISCO="MFFTUEFUYQOMQEMDIMEQXQOFQPRADFTQRAGDFTFUYQMEPUOFMFADMZPIMEOAYUZSFAEBMUZFARUZUETFTQIMDAZFTQIMKTQIMEYQFNKMYNMEEMPADERDAYOADPANMITATMPPQEQDFQPSQZQDMXBAYBQKFTQKUZRADYQPTUYFTMFUFIAGXPNQQMEUQEFFAFMWQFTQOUFKMFZUSTFNQOMGEQFTQQZQYKTMPNKFTQZZAWZAIXQPSQARPUEOAADARFTQZUSTFXURQADARFTQNAASUQ"

WLA="WLALYWPWLYWPJRLKHWLJRVMWPJRSLKWLWWLYZ"
KLY="KLYJKPMCLDUFXAESCZFRSSZZADLEESPKZZ"



CT = WLA.replace(" ", "").replace(",", "").replace(".", "").replace("\n", "")

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def brute():
    """
    bruteforce all shifts
    """
    out: list[tuple[int, str, float]] = []
    for shift in range(len(alphabet)):
        key = masc.shiftedkey(alphabet, shift)
        pt = "".join(masc.masc_decrypt(CT, key))
        score = compare.quadgramscore(pt)
        out.append(tuple([shift,pt,score]))
    for p in sorted(out, key=lambda x: x[2]):
        print(p)


if __name__ == "__main__":
    brute()
