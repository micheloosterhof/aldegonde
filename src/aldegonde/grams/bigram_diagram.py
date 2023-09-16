"""Bigram diagrams."""

from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import TypeVar

from aldegonde.stats import ngrams

from .color import Colors

T = TypeVar("T")


def print_separator(width: int) -> None:
    """print separator"""
    print("---+-", end="")
    for _i in range(width):
        print("---", end="")
    print("+-------+------")


def print_colored_value(v: int) -> None:
    """print colored value"""
    if v == 0:
        print(Colors.bgRed, end="")
    elif v < 5:
        print(Colors.bgYellow, end="")
    elif v < 10:
        print(Colors.bgGreen, end="")
    elif v > 25:
        print(Colors.bgBlue, end="")
    print(f"{v:02}", end="")
    print(Colors.reset, end=" ")


def print_bigram_diagram(
    runes: Sequence[T], alphabet: Sequence[T], skip: int = 1, cut: int = 0
) -> None:
    """Input is a sequence of items
    Output is the bigram frequency diagram printed to stdout.
    """
    if len(runes) + skip < 2:
        return
    MAX = len(alphabet)
    count = Counter(runes)
    ioc: float = 0.0

    bigram = bigram_diagram(runes, skip=skip, cut=cut)

    print("   | ", end="")
    for i in range(MAX):
        print(f"{i:02d} ", end="")
    print("| IOC   | nIOC")

    print_separator(MAX)

    for i in range(MAX):
        print(f"{i:02} | ", end="")
        for j in range(MAX):
            try:
                v = bigram[alphabet[i]][alphabet[j]]
            except KeyError:
                v = 0
            print_colored_value(v)

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[alphabet[i]] * (count[alphabet[i]] - 1))
            / (len(runes) * (len(runes) - 1))
            * MAX
        )
        ioc += pioc
        print(f"| {pioc:.3f} | {MAX*pioc:.3f}")

    print_separator(MAX)

    print("   | ", end="")
    for _i in range(MAX):
        print("   ", end="")
    print(f"| {ioc:0.3f}")


def bigram_diagram(
    runes: Sequence[T], skip: int = 1, cut: int = 0
) -> dict[T, dict[T, int]]:
    """Input is a sequence of symbols
    Output is bigram frequency diagram as dictionary of dictionaries
    skip is the gap between first and second rune.

    Specify `cut=0` and it operates on sliding blocks of 2 runes: AB, BC, CD, DE (all symbols)
    Specify `cut=1` and it operates on non-overlapping blocks of 2 runes: AB, CD, EF (odd only)
    Specify `cut=2` and it operates on non-overlapping blocks of 2 runes: BC, DE, FG (even only)
    """
    if len(runes) < 2:
        return {}

    if cut == 0:
        r = range(len(runes) - skip)
    elif cut == 1:
        r = range(0, len(runes) - skip, 2)
    elif cut == 2:
        r = range(1, len(runes) - skip, 2)
    else:
        raise ValueError("`cut` variable can be 0, 1 or 2 only")
    res = Counter((runes[idx], runes[idx + skip]) for idx in r)
    bigram: dict[T, dict[T, int]] = defaultdict(dict)
    for k, v in res.items():
        bigram[k[0]][k[1]] = v

    return bigram


def digraph_diagram(
    rows: Sequence[T],
    columns: Sequence[T],
    skip: int = 0,
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
            ngrams.iterngrams(rows, cut=cut, length=length),
            ngrams.iterngrams(columns, cut=cut, length=length),
        )
    )

    # if cut == 0:
    #    r = range(0, len(runes) - skip)
    # elif cut > 0:
    #    r = range(cut-1, len(runes) - skip, length)
    #
    # print(r)
    # res = Counter((runes[idx], runes[idx + skip]) for idx in r)
    digraph: dict[T, dict[T, int]] = defaultdict(dict)
    for k, v in res.items():
        digraph[k[0]][k[1]] = v

    return digraph


def print_digraph_diagram(
    rows: Sequence[T],
    columns: Sequence[T],
    alphabet: Sequence[T],
    skip: int = 0,
    length: int = 1,
    cut: int = 0,
) -> None:
    """Input is a sequence of items
    Output is the bigram frequency diagram printed to stdout.
    """
    symbolcount = len(alphabet)
    count = Counter(rows)
    ioc: float = 0.0

    digraph = digraph_diagram(rows, columns, skip=skip, length=length, cut=cut)

    print("   | ", end="")
    for i in range(symbolcount):
        print(f"{i:02d} ", end="")
    print("| IOC   | nIOC")

    print_separator(symbolcount)

    for i in range(symbolcount):
        print(f"{i:02} | ", end="")
        for j in range(symbolcount):
            try:
                v = digraph[alphabet[i]][alphabet[j]]
            except KeyError:
                v = 0
            print_colored_value(v)

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[alphabet[i]] * (count[alphabet[i]] - 1))
            / (len(rows) * (len(rows) - 1))
            * symbolcount
        )
        ioc += pioc
        print(f"| {pioc:.3f} | {symbolcount*pioc:.3f}")

    print_separator(symbolcount)

    print("   | ", end="")
    for _i in range(symbolcount):
        print("   ", end="")
    print(f"| {ioc:0.3f}")
