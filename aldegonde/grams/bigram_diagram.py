from collections import Counter, defaultdict
from typing import Dict

from ..structures import sequence

from .color import colors


def print_bigram_diagram(runes: sequence.Sequence) -> None:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is the bigram frequency diagram printed to stdout
    """
    if len(runes) < 2:
        return
    MAX = len(runes.alphabet)

    count = Counter(runes)
    ioc: float = 0.0
    res = Counter(
        f"{runes[idx]:02d}-{runes[idx + 1]:02d}" for idx in range(len(runes) - 1)
    )

    bigram: Dict = defaultdict(dict)
    for k in res.keys():
        x, y = k.split("-")
        bigram[int(x)][int(y)] = res[k]

    print("   | ", end="")
    for i in range(0, MAX):
        print(f"{i:02d} ", end="")
    print("| IOC")
    print("---+-", end="")
    for i in range(0, MAX):
        print("---", end="")
    print("+------")

    # for i in sorted(bigram.keys()):
    for i in range(0, MAX):
        print(f"{i:02} | ", end="")
        for j in range(0, MAX):
            # for j in sorted(bigram[i]):
            try:
                v = bigram[i][j]
            except KeyError:
                v = 0
            if v == 0:
                print(colors.bgRed, end="")
            elif v < 5:
                print(colors.bgYellow, end="")
            elif v < 10:
                print(colors.bgGreen, end="")
            elif v > 25:
                print(colors.bgBlue, end="")
            print(f"{v:02}", end="")
            print(colors.reset, end=" ")

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[int(i)] * (count[int(i)] - 1))
            / (len(runes) * (len(runes) - 1))
            * MAX
        )
        ioc += pioc
        print(f"| {pioc:.3f}")

    print("---+-", end="")
    for i in range(0, MAX):
        print("---", end="")
    print("+------")

    print("   | ", end="")
    for i in range(0, MAX):
        print("   ", end="")
    print(f"| {ioc:0.3f}")


def bigram_diagram(runes: sequence.Sequence, cut: int = 0) -> list[list[int]]:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is bigram frequency diagram as matrix

    Specify `cut=0` and it operates on sliding blocks of 2 runes: AB, BC, CD, DE
    Specify `cut=1` and it operates on non-overlapping blocks of 2 runes: AB, CD, EF
    Specify `cut=2` and it operates on non-overlapping blocks of 2 runes: BC, DE, FG
    """
    if len(runes) < 2:
        return []
    MAX = len(runes.alphabet)

    count = Counter(runes)
    ioc: float = 0.0
    if cut == 0:
        res = Counter(
            f"{runes[idx]:02d}-{runes[idx + 1]:02d}" for idx in range(0, len(runes) - 1)
        )
    elif cut == 1:
        res = Counter(
            f"{runes[idx]:02d}-{runes[idx + 1]:02d}" for idx in range(0, len(runes) - 1, 2)
        )
    elif cut == 2:
        res = Counter(
            f"{runes[idx]:02d}-{runes[idx + 1]:02d}" for idx in range(1, len(runes) - 1, 2)
        )
    else:
        raise Exception("`cut` variable can be 0, 1 or 2")

    bigram: Dict = defaultdict(dict)
    for k in res.keys():
        x, y = k.split("-")
        bigram[int(x)][int(y)] = res[k]

    output: list[list[int]] = [([0] * MAX) for i in range(MAX)]
    for x in range(0, MAX):
        for y in range(0, MAX):
            try:
                output[x][y] = bigram[x][y]
            except KeyError:
                pass

    return output


def bigram_diagram_skip(runes: sequence.Sequence, skip: int = 1) -> None:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is the bigram frequency diagram printed to stdout
    """
    if len(runes) < 2:
        return
    MAX = len(runes.alphabet)
    count = Counter(runes)
    ioc = 0.0
    res = Counter(
        f"{runes[idx]:02d}-{runes[idx + skip]:02d}" for idx in range(len(runes) - skip)
    )
    bigram: Dict = defaultdict(dict)

    for k in res.keys():
        x, y = k.split("-")
        bigram[int(x)][int(y)] = res[k]

    print(
        "   | 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 | IOC"
    )
    print(
        "---+----------------------------------------------------------------------------------------+----"
    )

    i: int
    for i in range(0, MAX):
        print(f"{i:02} | ", end="")
        j: int
        for j in range(0, MAX):
            # for j in sorted(bigram[i]):
            try:
                v = bigram[i][j]
            except IndexError:
                v = 0
            if v == 0:
                print(colors.bgRed, end="")
            elif v < 5:
                print(colors.bgBlue, end="")
            print(f"{v:02}", end="")
            print(colors.reset, end=" ")

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[int(i)] * (count[int(i)] - 1))
            / (len(runes) * (len(runes) - 1))
            * MAX
        )
        ioc += pioc
        print(f"| {pioc:.3f}")

    print(
        "--------------------------------------------------------------------------------------------+----"
    )
    print(
        "                                                                                            | {:.3f}".format(
            ioc
        )
    )
    print("\n")
