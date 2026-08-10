"""Bigram diagrams."""

import bisect
import statistics
from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import TypeVar

from aldegonde.stats import iterngrams

from . import color

T = TypeVar("T")

# 256-color background ramp from rare (cold) to frequent (hot): dark blue,
# blue, azure, cyan, green, yellow-green, yellow, orange, red. A bigram grid
# clusters around its mean, so a cold-to-hot ramp drives the rare cells and the
# frequent cells to opposite saturated ends, away from the muted middle.
_RAMP: tuple[int, ...] = (17, 21, 39, 44, 46, 154, 226, 208, 202, 196)

# The bigram never occurs: distinct dim gray so an absent cell reads as empty
# rather than merely rare.
_ABSENT = 236

DEFAULT_GROUPS = 8


def print_separator(width: int) -> None:
    """Print separator"""
    print("---+-", end="")
    for _i in range(width):
        print("---", end="")
    print("+-------+------")


def quantile_edges(values: Sequence[int], groups: int) -> list[float]:
    """The groups-1 quantile cut points over the positive cell values.

    Zero cells are absent rather than low, so they are excluded. Returns an
    empty list when there are fewer than two positive cells, too few to split.
    """
    positive = [v for v in values if v > 0]
    if groups < 2 or len(positive) < 2:
        return []
    return statistics.quantiles(positive, n=groups)


def value_color(v: int, edges: Sequence[float]) -> str:
    """Background color for a bigram cell, by quantile of the value spread.

    Zero is absent (dim gray), distinct from a cell that is merely rare.
    Non-zero cells are placed in the quantile group `edges` defines and colored
    along a cold-to-hot ramp: rare cells cold, frequent cells hot, the typical
    bulk muted in the middle. With too few positive cells to form groups, every
    present cell takes the hot end.
    """
    if v == 0:
        return color.bg256(_ABSENT)
    if not edges:
        return color.bg256(_RAMP[-1])
    groups = len(edges) + 1
    bucket = bisect.bisect_left(edges, v)  # ty: ignore[invalid-argument-type]  # mypy accepts this; ty rejects Sequence[float] for bisect
    ramp_index = round(bucket * (len(_RAMP) - 1) / (groups - 1))
    return color.bg256(_RAMP[ramp_index])


def print_colored_value(v: int, edges: Sequence[float]) -> None:
    """Print colored value"""
    print(value_color(v, edges), end="")
    print(f"{v:02}", end="")
    print(color.reset, end=" ")


def print_auto_bigram_diagram(
    runes: Sequence[T],
    alphabet: Sequence[T],
    skip: int = 1,
    cut: int = 0,
    groups: int = DEFAULT_GROUPS,
) -> None:
    """Input is a sequence of items
    Output is the bigram frequency diagram printed to stdout.
    """
    print_bigram_diagram(
        runes[0:-skip], runes[skip:], alphabet=alphabet, cut=cut, groups=groups
    )


def bigram_diagram(
    rows: Sequence[T],
    columns: Sequence[T],
    length: int = 1,
    cut: int = 0,
) -> dict[T, dict[T, int]]:
    """Input is two sequences of symbols
    Output is bigram frequency diagram as dictionary of dictionaries

    length is the length of the segment
    skip is an offset between the two, defaults to 0

    Specify `cut=0` and it operates on sliding blocks of 2 runes: AB, BC, CD, DE (all symbols)
    Specify `cut=1` and it operates on non-overlapping blocks of 2 runes: AB, CD, EF (odd only)
    Specify `cut=2` and it operates on non-overlapping blocks of 2 runes: BC, DE, FG (even only)
    """
    res = Counter(
        zip(
            iterngrams(rows, cut=cut, length=length),
            iterngrams(columns, cut=cut, length=length),
        ),
    )
    bigram: dict[T, dict[T, int]] = defaultdict(dict)
    for k, v in res.items():
        bigram[k[0][0]][k[1][0]] = v

    return bigram


def print_bigram_diagram(
    rows: Sequence[T],
    columns: Sequence[T],
    alphabet: Sequence[T],
    length: int = 1,
    cut: int = 0,
    groups: int = DEFAULT_GROUPS,
) -> None:
    """Input is a sequence of items
    Output is the bigram frequency diagram printed to stdout.
    """
    symbolcount = pow(len(alphabet), length)
    count = Counter(rows)
    ioc: float = 0.0

    bigram = bigram_diagram(rows, columns, length=length, cut=cut)

    values = [
        [bigram.get(alphabet[i], {}).get(alphabet[j], 0) for j in range(symbolcount)]
        for i in range(symbolcount)
    ]
    edges = quantile_edges([v for row in values for v in row], groups)

    print("   | ", end="")
    for i in range(symbolcount):
        print(f"{i:02d} ", end="")
    print("| IOC   | nIOC")

    print_separator(symbolcount)

    for i in range(symbolcount):
        print(f"{i:02} | ", end="")
        for j in range(symbolcount):
            print_colored_value(values[i][j], edges)

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[alphabet[i]] * (count[alphabet[i]] - 1))
            / (len(rows) * (len(rows) - 1))
            * symbolcount
        )
        ioc += pioc
        print(f"| {pioc:.3f} | {symbolcount * pioc:.3f}")

    print_separator(symbolcount)

    print("   | ", end="")
    for _i in range(symbolcount):
        print("   ", end="")
    print(f"| {ioc:0.3f}")
