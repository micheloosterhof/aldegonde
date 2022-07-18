import random
import math

from scipy.stats import poisson

from ..structures import alphabet, sequence
from ..stats import ioc, repeats, doublets
from ..grams import bigram_diagram
from ..algorithm import autokey


def isomorph(ciphertext: sequence.Sequence) -> str:
    """
    Input is a piece of ciphertext as a list of int
    Output is this normalized as an isomorph, it's output as a string for easy comparison in alphabet A-Z
    Example ATTACK and EFFECT both normalize to ABBACD
    TODO: raise exception when we go beyond Z
    """
    output = ""
    letter = "A"
    mapping: dict[int, str] = {}
    for r in ciphertext:
        if r not in mapping:
            mapping[r] = letter
            letter = chr(ord(letter) + 1)
        output = output + mapping[r]
    return output


def print_isomorph_statistics(seq: sequence.Sequence, trace: bool = False) -> None:
    """
    Look for isomorphs in the sequence.
    Isomorphs are sequences that have the same number of unique characters:
    CDDE and LKKY are isomorphs, that can be generalized to the pattern ABBC
    This function collects all isomorphs
    """
    startlength = 4
    endlength = 40
    isos: dict[str, list[int]]  # normalized isomorph as key, list of positions as value

    for length in range(startlength, endlength + 1):
        isos = {}

        for pos in range(0, len(seq) - length):
            iso = isomorph(seq[pos : pos + length])
            if iso in isos:
                isos[iso].append(pos)
            else:
                isos[iso] = [pos]

        counter = 0
        totals = 0
        for key in isos.keys():
            if len(isos[key]) > 1:
                if trace is True:
                    print(f"isomorph {key} at positions: {isos[key]}")
                counter += 1
                totals += len(isos[key])

        if counter == 0:
            print(f"no isomorphs found of length {length}")
            break
        else:
            print(
                f"{counter} distinct isomorphs found of length {length} total: {totals} ",
                end="",
            )

        mu = len(seq) / math.factorial(length - 1)
        mean, var = poisson.stats(mu, loc=0, moments="mv")
        sigmage: float = abs(counter - mean) / math.sqrt(var)
        print(f"[INCORRECT: isomorph={counter} expected={mean:.2f} S={sigmage:.2f}σ]")
