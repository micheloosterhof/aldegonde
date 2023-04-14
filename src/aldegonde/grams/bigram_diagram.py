"""Bigram diagrams."""

from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import TypeVar

from .color import Colors

T = TypeVar("T")


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

    bigram = bigram_diagram(runes, skip=skip, cut=0)

    print("   | ", end="")
    for i in range(0, MAX):
        print(f"{i:02d} ", end="")
    print("| IOC   | nIOC")

    print("---+-", end="")
    for _i in range(0, MAX):
        print("---", end="")
    print("+-------+------")

    # for i in sorted(bigram.keys()):
    for i in range(0, MAX):
        print(f"{i:02} | ", end="")
        for j in range(0, MAX):
            try:
                v = bigram[alphabet[i]][alphabet[j]]
            except KeyError:
                v = 0
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

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[alphabet[i]] * (count[alphabet[i]] - 1))
            / (len(runes) * (len(runes) - 1))
            * MAX
        )
        ioc += pioc
        print(f"| {pioc:.3f} | {MAX*pioc:.3f}")

    print("---+-", end="")
    for _i in range(0, MAX):
        print("---", end="")
    print("+--------------")

    print("   | ", end="")
    for _i in range(0, MAX):
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
        r = range(0, len(runes) - skip)
    elif cut == 1:
        r = range(0, len(runes) - skip, 2)
    elif cut == 2:
        r = range(1, len(runes) - skip, 2)
    else:
        raise Exception("`cut` variable can be 0, 1 or 2 only")
    res = Counter((runes[idx], runes[idx + skip]) for idx in r)
    bigram: dict[T, dict[T, int]] = defaultdict(dict)
    for k, v in res.items():
        bigram[k[0]][k[1]] = v

    return bigram
