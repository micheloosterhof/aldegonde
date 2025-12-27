#!/usr/bin/env python

import sys


def multable(size: int = 29):
    for row in range(size + 1):
        print(f"{row:02d} | ", end="")
        for col in range(size + 1):
            mul = col * row % size
            if mul == 0:
                mul = size
            print(f"{mul:02d} ", end="")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <size>")
        sys.exit(1)
    multable(int(sys.argv[1]))
