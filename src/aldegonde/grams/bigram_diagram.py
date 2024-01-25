"""Bigram diagrams."""

from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import TypeVar

from aldegonde.stats import ngrams

from .color import Colors

T = TypeVar("T")


def print_separator(width: int) -> None:
    """Print separator"""
    print("---+-", end="")
    for _i in range(width):
        print("---", end="")
    print("+-------+------")


def print_colored_value(v: int) -> None:
    """Print colored value"""
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


def print_auto_bigram_diagram(
    runes: Sequence[T],
    alphabet: Sequence[T],
    skip: int = 1,
    cut: int = 0,
) -> None:
    """Input is a sequence of items
    Output is the bigram frequency diagram printed to stdout.
    """
    print_bigram_diagram(runes[0:-skip], runes[skip:], alphabet=alphabet, cut=cut)


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
            ngrams.iterngrams(rows, cut=cut, length=length),
            ngrams.iterngrams(columns, cut=cut, length=length),
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
) -> None:
    """Input is a sequence of items
    Output is the bigram frequency diagram printed to stdout.
    """
    symbolcount = pow(len(alphabet), length)
    count = Counter(rows)
    ioc: float = 0.0

    bigram = bigram_diagram(rows, columns, length=length, cut=cut)

    print("   | ", end="")
    for i in range(symbolcount):
        print(f"{i:02d} ", end="")
    print("| IOC   | nIOC")

    print_separator(symbolcount)

    for i in range(symbolcount):
        print(f"{i:02} | ", end="")
        for j in range(symbolcount):
            try:
                v = bigram[alphabet[i]][alphabet[j]]
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
