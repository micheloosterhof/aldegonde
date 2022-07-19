"""
    Example ATTACK and EFFECT both normalize to ABBACD
   
    length 1: A (1)
    length 2: AA | AB (2)
    length 3: AAA | AAB ABA ABB | ABC (5)
    length 4: AAAA | AAAB AABA AABB ABAA ABAB ABBA ABBB | AABC AACB ABAC ABBC ABCA ABCB ABCC ABCA ABCB ABCC | ABCD

    sum:     2^(length-1) + 2^(length-2)


"""
import functools
import itertools
import math
import random
import statistics

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


def all_isomorphs(ciphertext: sequence.Sequence, length: int) -> dict[str, list[int]]:
    """
    Return all isomorphs of a particular length from a sequence
    """
    isos: dict[
        str, list[int]
    ] = {}  # normalized isomorph as key, list of positions as value
    isos = {}

    for pos in range(0, len(ciphertext) - length):
        iso = isomorph(ciphertext[pos : pos + length])
        if iso in isos:
            isos[iso].append(pos)
        else:
            isos[iso] = [pos]
    return isos


def random_isomorph_statistics(
    sequencelength: int, isomorphlength: int, samples: int = 20, trace: bool = False
) -> tuple[float, float]:
    """
    Returns the mean and stdev of distinct isomorphs and mean and stdev of total isomorphs
    """
    distincts: Dict[int, list[int]] = {}
    totals: Dict[int, list[int]] = {}

    for test in range(0, samples):
        # create random samples
        r: list[int] = []
        for i in range(0, sequencelength):
            r.append(random.randrange(0, 29))

        isos = all_isomorphs(r, isomorphlength)
        distinct = 0
        total = 0
        for key in isos.keys():
            if len(isos[key]) > 1:
                distinct += 1
                total += len(isos[key])

        if isomorphlength in distincts:
            distincts[isomorphlength].append(distinct)
            totals[isomorphlength].append(total)
        else:
            distincts[isomorphlength] = [distinct]
            totals[isomorphlength] = [total]

    # TODO: we're assuming a normal distribution here, this may not be correct
    meandistinct = statistics.mean(distincts[isomorphlength])
    stdevdistinct = statistics.stdev(distincts[isomorphlength])
    meantotal = statistics.mean(totals[isomorphlength])
    stdevtotal = statistics.stdev(totals[isomorphlength])
    return (meandistinct, stdevdistinct, meantotal, stdevtotal)


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
        isos = all_isomorphs(seq, length)
        counter = 0
        totals = 0
        for key in isos.keys():
            if len(isos[key]) > 1:
                if trace is True:
                    print(f"isomorph {key} at positions: {isos[key]}")
                counter += 1
                totals += len(isos[key])

        (avgdistinct, stdevdistinct, avgtotal, stdevtotal) = random_isomorph_statistics(
            sequencelength=len(seq), isomorphlength=length
        )

        if counter == 0 and avgdistinct == 0:
            print(f"no isomorphs found of length {length}")
            break
        else:
            print(f"isomorphs length {length:2d}: distinct isomorphs:", end=" ")
            print(
                f"{counter:3d} (avg: {avgdistinct:6.2f}, S={abs(avgdistinct-counter)/stdevdistinct:4.2f}σ)",
                end=" ",
            )
            print(
                f"total: {totals:4d} (avg: {avgtotal:7.2f} S={abs(avgtotal-totals)/stdevtotal:4.2f}σ) ",
            )
