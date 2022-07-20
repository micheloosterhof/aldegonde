"""
    Example ATTACK and EFFECT both normalize to ABBACD

    length 1: A (1)
    length 2: AA | AB (2)
    length 3: AAA | AAB ABA ABB | ABC (5)
    length 4: AAAA | AAAB AABA AABB ABAA ABAB ABBA ABBB |
              AABC AACB ABAC ABBC ABCA ABCB ABCC ABCA ABCB ABCC | ABCD
"""
import random
import statistics
from typing import Dict

from ..structures import sequence


def isomorph(ciphertext: sequence.Sequence) -> str:
    """
    Input is a piece of ciphertext as a list of int
    Output is this normalized as an isomorph, as a string for easy comparison in alphabet A-Z
    Example ATTACK and EFFECT both normalize to ABBACD
    TODO: raise exception when we go beyond Z
    """
    output: str = ""
    letter: str = "A"
    mapping: dict[int, str] = {}
    for rune in ciphertext:
        if rune not in mapping:
            mapping[rune] = letter
            letter = chr(ord(letter) + 1)
        output = output + mapping[rune]
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
) -> tuple[float, float, float, float]:
    """
    Returns the mean and stdev of distinct isomorphs and mean and stdev of total isomorphs
    """
    distincts: Dict[int, list[int]] = {}
    totals: Dict[int, list[int]] = {}

    for _ in range(0, samples):
        # create random samples
        rand: list[int] = [random.randrange(0, 29) for _ in range(sequencelength)]
        isos = all_isomorphs(rand, isomorphlength)
        distinct: int = len(isos.keys())
        total: int = sum([len(x) for x in isos.values()])

        if isomorphlength in distincts:
            distincts[isomorphlength].append(distinct)
            totals[isomorphlength].append(total)
        else:
            distincts[isomorphlength] = [distinct]
            totals[isomorphlength] = [total]

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
        # print(isos.keys())
        distinct: int = len(isos.keys())
        totals: int = sum([len(x) for x in isos.values()])

        (avgdistinct, stdevdistinct, avgtotal, stdevtotal) = random_isomorph_statistics(
            sequencelength=len(seq), isomorphlength=length
        )

        if distinct == totals:
            print(f"no duplicate isomorphs found of length {length}")
            break

        print(f"isomorphs length {length:2d}: distinct isomorphs:", end=" ")
        try:
            print(
                f"{distinct:3d} (avg: {avgdistinct:6.2f}, S={abs(avgdistinct-distinct)/stdevdistinct:4.2f}σ)",
                end=" ",
            )
        except ZeroDivisionError:
            print(
                f"{distinct:3d} (avg: {avgdistinct:6.2f}",
                end=" ",
            )
        try:
            print(
                f"total: {totals:4d} (avg: {avgtotal:7.2f} S={abs(avgtotal-totals)/stdevtotal:4.2f}σ) "
            )
        except ZeroDivisionError:
            print(f"total: {totals:4d} (avg: {avgtotal:7.2f})")
