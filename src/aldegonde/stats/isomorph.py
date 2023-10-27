"""Example ATTACK and EFFECT both normalize to ABBACD.

length 1: A (1)
length 2: AA | AB (2)
length 3: AAA | AAB ABA ABB | ABC (5)
length 4: AAAA | AAAB AABA AABB ABAA ABAB ABBA ABBB |
AABC AACB ABAC ABBC ABCA ABCB ABCC ABCA ABCB ABCC | ABCD
"""
import random
import statistics
from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import TypeVar

from aldegonde.stats.ngrams import iterngrams

T = TypeVar("T")


def isomorph(text: Sequence[T]) -> str:
    """Input is a piece of text as a sequence
    Output is this normalized as an isomorph, as a string in alphabet A-Z
    Example ATTACK and EFFECT both normalize to ABBACD
    TODO: raise exception when we go beyond Z.
    """
    output: str = ""
    letter: str = "A"
    mapping: dict[str, str] = {}
    for rune in text:
        if str(rune) not in mapping:
            mapping[str(rune)] = letter
            letter = chr(ord(letter) + 1)
        output = output + mapping[str(rune)]
    return output


def isomorph_distribution(
    ciphertext: Sequence[T],
    length: int,
    cut: int = 0,
) -> dict[str, int]:
    """Return all isomorphs of a particular length from a sequence with their count."""
    return Counter([isomorph(x) for x in iterngrams(ciphertext, length=length)])


def isomorph_positions(
    text: Sequence[T],
    length: int = 1,
    cut: int = 0,
) -> dict[str, list[int]]:
    """Flexible isomorph positions function, returns each ngram and its starting location in the source text."""
    out: dict[str, list[int]] = defaultdict(list)
    for i, e in enumerate(iterngrams(text, length=length, cut=cut)):
        out[isomorph(e)].append(i)
    return out


def isomorph_statistics(dist: dict[str, int]) -> tuple[int, int]:
    """Input is the output of `isomorph_distribution`.
    Returns `distincts` and `duplicates` for the input.
    """
    distinct: int = len(dist.keys())
    duplicate: int = sum(v for v in dist.values() if v > 1)
    return (distinct, duplicate)


def random_isomorph_statistics(
    sequencelength: int,
    isomorphlength: int,
    samples: int = 20,
    alphabetlen: int = 29,
    *,
    trace: bool = False,
) -> tuple[float, float, float, float]:
    """Return the mean and stdev of distinct isomorphs and mean and stdev of duplicate isomorphs."""
    distincts: list[int] = []
    duplicates: list[int] = []

    for _ in range(samples):
        rand: list[int] = [
            random.randrange(0, alphabetlen) for _ in range(sequencelength)
        ]
        isos = isomorph_distribution(rand, isomorphlength)
        (distinct, duplicate) = isomorph_statistics(isos)
        distincts.append(distinct)
        duplicates.append(duplicate)

    meandistinct = statistics.mean(distincts)
    stdevdistinct = statistics.stdev(distincts)
    meanduplicate = statistics.mean(duplicates)
    stdevduplicate = statistics.stdev(duplicates)
    return (meandistinct, stdevdistinct, meanduplicate, stdevduplicate)


def print_isomorph_statistics(seq: Sequence[T], *, trace: bool = False) -> None:
    """Look for isomorphs in the sequence.
    Isomorphs are sequences that have the same number of unique characters:
    CDDE and LKKY are isomorphs, that can be generalized to the pattern ABBC
    This function collects all isomorphs.
    """
    startlength = 4
    endlength = 40
    isos: dict[str, int]  # normalized isomorph as key, count as value

    for length in range(startlength, endlength + 1):
        isos = isomorph_distribution(seq, length)
        (distinct, duplicate) = isomorph_statistics(isos)
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
                f"duplicate: {duplicate:5d} (avg: {avgduplicate:8.2f} S={abs(avgduplicate-duplicate)/stdevduplicate:5.2f}σ) ",
            )
        except ZeroDivisionError:
            print(f"duplicate: {duplicate:5d} (avg: {avgduplicate:8.2f})")
