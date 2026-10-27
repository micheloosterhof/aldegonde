# ABOUTME: Isomorphs: a text's pattern of repeated symbols, with no symbol identity.
# ABOUTME: Counts repeated patterns and compares them against random text.

"""Example ATTACK and EFFECT both normalize to (0, 1, 1, 0, 2, 3).

The patterns per length, written with A for 0, B for 1 and so on:

length 1: A (1)
length 2: AA | AB (2)
length 3: AAA | AAB ABA ABB | ABC (5)
length 4: AAAA | AAAB AABA AABB ABAA ABAB ABBA ABBB |
AABC AACB ABAC ABBC ABCA ABCB ABCC ABCA ABCB ABCC | ABCD
"""

import random
import statistics
from collections import Counter, defaultdict
from collections.abc import Hashable, Sequence
from typing import TypeVar

from aldegonde.exceptions import InvalidInputError
from aldegonde.stats.ngram import iterngrams
from aldegonde.stats.nulls import NullModel
from aldegonde.stats.zscore import z_score

T = TypeVar("T")

#: A text's pattern of repeated symbols: each symbol replaced by the order of
#: its first appearance, counting from 0.
Isomorph = tuple[int, ...]


def isomorph(text: Sequence[Hashable]) -> Isomorph:
    """Normalize a text to its isomorph.

    Example: ATTACK and EFFECT both normalize to (0, 1, 1, 0, 2, 3).

    Args:
        text: Sequence of symbols, compared by equality

    Returns:
        Each symbol replaced by the order of its first appearance
    """
    first_seen: dict[Hashable, int] = {}
    return tuple(first_seen.setdefault(symbol, len(first_seen)) for symbol in text)


def isomorph_distribution(
    ciphertext: Sequence[Hashable],
    length: int,
    cut: int = 0,
) -> dict[Isomorph, int]:
    """Return all isomorphs of a particular length from a sequence with their count."""
    return Counter([isomorph(x) for x in iterngrams(ciphertext, length=length)])


def isomorph_positions(
    text: Sequence[Hashable],
    length: int = 1,
    cut: int = 0,
) -> dict[Isomorph, list[int]]:
    """Flexible isomorph positions function, returns each ngram and its starting location in the source text."""
    out: dict[Isomorph, list[int]] = defaultdict(list)
    for i, e in enumerate(iterngrams(text, length=length, cut=cut)):
        out[isomorph(e)].append(i)
    return out


def isomorph_statistics(dist: dict[Isomorph, int]) -> tuple[int, int]:
    """Input is the output of `isomorph_distribution`.
    Returns `distincts` and `duplicates` for the input.
    """
    distinct: int = len(dist.keys())
    duplicate: int = sum(v for v in dist.values() if v > 1)
    return (distinct, duplicate)


#: Seed for the isomorph null when the caller supplies no source. Fixed so a
#: quoted z-score can be reproduced; pass `rng` to vary the draw deliberately.
DEFAULT_NULL_SEED = 3301


def random_isomorph_statistics(
    sequencelength: int,
    isomorphlength: int,
    samples: int = 20,
    alphabetlen: int = 29,
    *,
    trace: bool = False,
    rng: random.Random | None = None,
    null: NullModel[int] | None = None,
    observed: Sequence[int] | None = None,
) -> tuple[float, float, float, float]:
    """Mean and stdev of distinct and of duplicate isomorphs under a null.

    The default null is uniform random text, which is the wrong null for
    doublet-suppressed text: a missing diagonal alone changes the isomorph
    counts (`hypotheses/bigram-ioc.md`). For such text pass a resampler such
    as `c3301.low_doublet_null()` or `stats.doublet_shuffle(rate)` together
    with the observed sequence it resamples.

    Args:
        sequencelength: Length of each random sequence drawn
        isomorphlength: Length of the isomorphs counted
        samples: How many random sequences to draw
        alphabetlen: Size of the alphabet drawn from
        trace: Unused, kept for call compatibility
        rng: Injected random source. Defaults to one seeded with
            `DEFAULT_NULL_SEED`, so the null is the same on every run.
        null: A resampler `(observed, rng) -> surrogate`. None draws uniform
            text of `sequencelength` from `alphabetlen` symbols.
        observed: The sequence the resampler draws from. Required with `null`.

    Returns:
        (mean distinct, stdev distinct, mean duplicate, stdev duplicate)

    Raises:
        InvalidInputError: If `null` is given without `observed`.
    """
    if null is not None and observed is None:
        msg = "a null resampler needs the observed sequence to resample"
        raise InvalidInputError(msg)
    source = random.Random(DEFAULT_NULL_SEED) if rng is None else rng
    distincts: list[int] = []
    duplicates: list[int] = []

    for _ in range(samples):
        rand: Sequence[int]
        if null is None:
            rand = [source.randrange(0, alphabetlen) for _ in range(sequencelength)]
        else:
            rand = null(observed if observed is not None else [], source)
        isos = isomorph_distribution(rand, isomorphlength)
        (distinct, duplicate) = isomorph_statistics(isos)
        distincts.append(distinct)
        duplicates.append(duplicate)

    meandistinct = statistics.mean(distincts)
    stdevdistinct = statistics.stdev(distincts)
    meanduplicate = statistics.mean(duplicates)
    stdevduplicate = statistics.stdev(duplicates)
    return (meandistinct, stdevdistinct, meanduplicate, stdevduplicate)


def print_isomorph_statistics(seq: Sequence[Hashable], *, trace: bool = False) -> None:
    """Look for isomorphs in the sequence.
    Isomorphs are sequences that have the same number of unique characters:
    CDDE and LKKY are isomorphs, that can be generalized to the pattern ABBC
    This function collects all isomorphs.
    """
    startlength = 4
    endlength = 40
    isos: dict[Isomorph, int]  # normalized isomorph as key, count as value

    print(
        "null hypothesis: uniform random text "
        "(isomorph counts from random data); z = standard deviations from this null"
    )
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
        print(
            f"{distinct:5d} (avg: {avgdistinct:8.2f}, "
            f"z={z_score(distinct, avgdistinct, stdevdistinct):+5.2f})",
            end=" ",
        )
        print(
            f"duplicate: {duplicate:5d} (avg: {avgduplicate:8.2f} "
            f"z={z_score(duplicate, avgduplicate, stdevduplicate):+5.2f}) ",
        )
