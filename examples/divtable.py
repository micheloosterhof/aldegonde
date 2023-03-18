#!/usr/bin/env python

import sys

from aldegonde.maths.modular import modDivide


def divtable(size: int = 29):
    for row in range(0, size + 1):
        print(f"{row:02d} | ", end="")
        for col in range(0, size + 1):
            div = col * row % size
            try:
                div = modDivide(col, row, size)
            except:
                div = -1
            print(f"{div:02d} ", end="")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <size>")
        sys.exit(1)
    divtable(int(sys.argv[1]))
