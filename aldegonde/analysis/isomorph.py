"""
    Example ATTACK and EFFECT both normalize to ABBACD

    length 1: A (1)
    length 2: AA | AB (2)
    length 3: AAA | AAB ABA ABB | ABC (5)
    length 4: AAAA | AAAB AABA AABB ABAA ABAB ABBA ABBB |
              AABC AACB ABAC ABBC ABCA ABCB ABCC ABCA ABCB ABCC | ABCD
"""
from collections import defaultdict
import itertools
import random
import statistics
from typing import Dict

from ..structures import sequence
from ..math import factor


def isomorph(ciphertext: sequence.Sequence) -> str:
    """
    Input is a piece of ciphertext as a list of int
    Output is this normalized as an isomorph, as a string in alphabet A-Z
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
    isos: dict[str, list[int]] = defaultdict(
        list
    )  # normalized isomorph as key, list of positions as value
    for pos in range(0, len(ciphertext) - length):
        iso = isomorph(ciphertext[pos : pos + length])
        isos[iso].append(pos)
    return isos


def isomorph_statistics(isomorphs: dict[str, list[int]]) -> (int, int):
    """
    Input is the output of `all_isomorphs`.
    Returns `distincts` and `duplicates` for the input
    """
    distinct: int = len(isomorphs.keys())
    duplicate: int = sum([len(x) for x in isomorphs.values() if len(x) > 1])
    return (distinct, duplicate)


def random_isomorph_statistics(
    sequencelength: int, isomorphlength: int, samples: int = 20, trace: bool = False
) -> tuple[float, float, float, float]:
    """
    Returns the mean and stdev of distinct isomorphs and mean and stdev of duplicate isomorphs
    """
    distincts: list[int] = []
    duplicates: list[int] = []

    for _ in range(0, samples):
        rand: list[int] = [random.randrange(0, 29) for _ in range(sequencelength)]
        isos = all_isomorphs(rand, isomorphlength)
        (distinct, duplicate) = isomorph_statistics(isos)
        distincts.append(distinct)
        duplicates.append(duplicate)

    meandistinct = statistics.mean(distincts)
    stdevdistinct = statistics.stdev(distincts)
    meanduplicate = statistics.mean(duplicates)
    stdevduplicate = statistics.stdev(duplicates)
    return (meandistinct, stdevdistinct, meanduplicate, stdevduplicate)


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
        (distinct, duplicate) = isomorph_statistics(isos)
        if duplicate < 100 or trace is True:
            for key, values in isos.items():
                for v in itertools.combinations(values, 2):
                    print(
                        f"{key} loc={v[1]}-{v[0]} diff={abs(v[1]-v[0])} factors={factor.prime_factors(abs(v[1]-v[0]))}"
                    )

        (
            avgdistinct,
            stdevdistinct,
            avgduplicate,
            stdevduplicate,
        ) = random_isomorph_statistics(sequencelength=len(seq), isomorphlength=length)

        if duplicate == 0:
            print(f"no duplicate isomorphs found of length {length}")
            break

        print(f"isomorphs length {length:2d}: distinct isomorphs:", end=" ")
        try:
            print(
                f"{distinct:5d} (avg: {avgdistinct:8.2f}, S={abs(avgdistinct-distinct)/stdevdistinct:5.2f}σ)",
                end=" ",
            )
        except ZeroDivisionError:
            print(
                f"{distinct:5d} (avg: {avgdistinct:8.2f}",
                end=" ",
            )
        try:
            print(
                f"duplicate: {duplicate:5d} (avg: {avgduplicate:8.2f} S={abs(avgduplicate-duplicate)/stdevduplicate:5.2f}σ) "
            )
        except ZeroDivisionError:
            print(f"duplicate: {duplicate:5d} (avg: {avgduplicate:8.2f})")
