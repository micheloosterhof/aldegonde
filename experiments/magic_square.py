# ABOUTME: Verifies the 5x5 magic square printed in the Liber Primus and reports
# ABOUTME: what it can and cannot supply as key material for the walk's g.
"""The book prints a 5x5 magic square with constant 3301.

Master transcription lines 179-183 hold a 5x5 grid of numbers whose every row,
every column and both diagonals sum to 3301 -- the project's own number, itself
prime. The grid is 180-degree symmetric and its centre cell, 809, is the only
prime among the thirteen distinct values.

This matters to the cipher because `g-from-5x5-grid.md` builds `g` by laying 25
runes into a 5x5 grid and rotating each column, and its stated obstruction is that
the family is too rich to enumerate: fill order, the four fixed runes and the
rotations are all free. A grid printed in the book could remove the fill-order
freedom, which is the largest of the three.

What the square can and cannot do, measured rather than assumed: it has only 13
distinct values and only 11 distinct residues mod 29, so its cells CANNOT map onto
25 distinct runes. It can therefore supply an ordering at most, and because twelve
of the values appear twice, even that ordering needs a tie-breaking rule. See
`hypotheses/magic-square-grid-key.md` for the attack this sizes and for the gap
that decides it -- sigma has no construction here.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
CONSTANT = 3301
SIZE = 5


def extract() -> list[list[int]]:
    """The 5x5 grid of numbers from the transcription, found by its own shape."""
    rows: list[list[int]] = []
    for line in MASTER.read_text().split("\n"):
        stripped = line.strip().rstrip("/")
        if not re.fullmatch(r"[\d-]+", stripped):
            continue
        cells = [int(v) for v in stripped.split("-") if v]
        if len(cells) == SIZE:
            rows.append(cells)
        elif rows and len(rows) < SIZE:
            rows = []
        if len(rows) == SIZE:
            return rows
    msg = "no 5x5 numeric grid found in the master transcription"
    raise ValueError(msg)


def report(grid: list[list[int]]) -> None:
    flat = [v for row in grid for v in row]
    rows = [sum(r) for r in grid]
    cols = [sum(grid[i][j] for i in range(SIZE)) for j in range(SIZE)]
    diag = sum(grid[i][i] for i in range(SIZE))
    anti = sum(grid[i][SIZE - 1 - i] for i in range(SIZE))
    broken = [sum(grid[i][(i + k) % SIZE] for i in range(SIZE)) for k in range(SIZE)]
    for r in grid:
        print("  " + " ".join(f"{v:>5}" for r_ in [r] for v in r_))
    print()
    print(f"  row sums        {rows}")
    print(f"  column sums     {cols}")
    print(f"  diagonals       {diag}, {anti}")
    print(f"  total           {sum(flat)} = {SIZE} x {sum(flat) // SIZE}")
    print(f"  centre          {grid[2][2]}")
    print(
        f"  180-deg symmetric {
            all(
                grid[i][j] == grid[4 - i][4 - j]
                for i in range(SIZE)
                for j in range(SIZE)
            )
        }"
    )
    magic = all(v == CONSTANT for v in rows + cols + [diag, anti])
    print(f"  fully magic at {CONSTANT}: {magic}")
    print(f"  pandiagonal: {all(v == CONSTANT for v in broken)}  (broken {broken})")

    distinct = sorted(set(flat))
    residues = sorted({v % 29 for v in distinct})
    print(f"\n  distinct values {len(distinct)}: {distinct}")
    print(f"  residues mod 29 {len(residues)}: {residues}")
    print("\nSo the cells cannot carry 25 distinct runes -- the square can supply a")
    print("fill ORDER for the 5x5 rune grid, not the rune content, and twelve values")
    print("appear twice so the order needs a tie-break. Free parameters that remain:")
    print("  four fixed runes  C(29,4) = 23,751")
    print("  rotation          4")
    print("  column or row     2")
    print("  tie-breaks        up to 2^12 = 4,096")
    print("  -> 1.9e5 candidates canonically, 7.8e8 at worst; both enumerable")
    print("     (the Quagmire sweep drove 3.1e8 keys in 12.4h)")


def main() -> None:
    report(extract())


if __name__ == "__main__":
    main()
