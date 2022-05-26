def bigram_diagram(runes: list[int]) -> None:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is the bigram frequency diagram printed to stdout
    """
    count = Counter(runes)
    ioc: float = 0.0
    res = Counter(
        "{:02d}-{:02d}".format(runes[idx], runes[idx + 1])
        for idx in range(len(runes) - 1)
    )

    bigram = defaultdict(dict)
    for k in res.keys():
        x, y = k.split("-")
        bigram[int(x)][int(y)] = res[k]

    print("   | ", end="")
    for i in range(0, MAX):
        print(f"{i:02d} ", end="")
    print("| IOC")
    print("---+-", end="")
    for i in range(0, MAX):
        print(f"---", end="")
    print("+------")

    # for i in sorted(bigram.keys()):
    for i in range(0, MAX):
        print(f"{i:02} | ", end="")
        for j in range(0, MAX):
            # for j in sorted(bigram[i]):
            try:
                v = bigram[i][j]
            except:
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
        print("| {0:.3f}".format(pioc))

    print("---+-", end="")
    for i in range(0, MAX):
        print(f"---", end="")
    print("+------")

    print("   | ", end="")
    for i in range(0, MAX):
        print(f"   ", end="")
    print(f"| {ioc:0.3f}")


def bigram_diagram_skip(runes: list[int], skip: int = 1) -> None:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is the bigram frequency diagram printed to stdout
    """
    count = Counter(runes)
    ioc = 0.0
    res = Counter(
        "{:02d}-{:02d}".format(runes[idx], runes[idx + skip])
        for idx in range(len(runes) - skip)
    )
    bigram = defaultdict(dict)

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
            except:
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
        print("| {0:.3f}".format(pioc))

    print(
        "--------------------------------------------------------------------------------------------+----"
    )
    print(
        "                                                                                            | {0:.3f}".format(
            ioc
        )
    )
    print("\n")
