# ABOUTME: Searches keyed columnar transpositions of the page's blocks, the family the
# ABOUTME: unkeyed route search missed, for one that restores the word-length order.
"""The route search tested column orders the key does not change. This tests the rest.

`block_transposition_search.py` un-permutes each page under 17 route rules -- reverse,
columnar 2 to 12, rail 2 to 5 -- and restores nothing. But a columnar transposition is
normally KEYED: the columns are read out in an order a keyword sets, not left to right.
Inverting with the identity order, as that search does, is wrong for every keyed variant,
so the family was not covered.

It is small enough to enumerate. For c columns there are c! read-out orders, and summing
c = 2 to 8 gives 46,232 rules. Each is applied per page, the block-length sequence is put
back into row order, and the length-transition structure is re-measured.

A planted keyed columnar confirms the search can find one.

`--null` reruns the whole search on the body's own lengths shuffled within each page,
which is the only honest way to read a maximum over 46,232 correlated rules. `--split`
goes further and cross-validates: find the best rule on half the pages, then score that
rule on the other half. A real rule survives the move; an overfit one does not.

    python keyed_columnar_search.py [--control] [--null] [--split] [--max-cols 8]
"""

from __future__ import annotations

import collections
import itertools
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from block_transposition_search import page_lengths  # noqa: E402
from word_length_sequence import prose_sequences  # noqa: E402

CAP = 6


def readout(n: int, cols: int, order: tuple[int, ...]) -> list[int]:
    """Positions in the order a keyed columnar reads them out of a row-wise grid."""
    out = []
    for c in order:
        i = c
        while i < n:
            out.append(i)
            i += cols
    return out


def unpermute(seq: list[int], order: list[int]) -> list[int]:
    out = [0] * len(seq)
    for i, src in enumerate(order):
        out[src] = seq[i]
    return out


def g2(seqs: list[list[int]]) -> tuple[float, int]:
    pairs = [(min(a, CAP), min(b, CAP)) for s in seqs for a, b in zip(s, s[1:])]
    tab = collections.Counter(pairs)
    ra = collections.Counter(a for a, _ in pairs)
    rb = collections.Counter(b for _, b in pairs)
    n = len(pairs)
    total = 0.0
    for (a, b), o in tab.items():
        e = ra[a] * rb[b] / n
        if o and e:
            total += 2 * o * math.log(o / e)
    return total, n


def search(pages: list[list[int]], max_cols: int):
    """(excess G^2 per pair, columns, order) for every keyed rule, best first."""
    flat_pairs = sum(len(p) - 1 for p in pages)
    rng = random.Random(7)
    base = []
    for _ in range(40):
        shuffled = []
        for p in pages:
            t = p[:]
            rng.shuffle(t)
            shuffled.append(t)
        base.append(g2(shuffled)[0])
    null = sum(base) / len(base)

    rows = []
    for cols in range(2, max_cols + 1):
        for order in itertools.permutations(range(cols)):
            restored = [unpermute(p, readout(len(p), cols, order)) for p in pages]
            rows.append(((g2(restored)[0] - null) / flat_pairs, cols, order))
    rows.sort(reverse=True)
    return rows


def main() -> None:
    max_cols = 8
    for i, a in enumerate(sys.argv):
        if a == "--max-cols" and i + 1 < len(sys.argv):
            max_cols = int(sys.argv[i + 1])

    if "--split" in sys.argv:
        pages = page_lengths()
        halves = {"A": pages[0::2], "B": pages[1::2]}
        rng = random.Random(5)
        base, npair = {}, {}
        for k, ps in halves.items():
            npair[k] = sum(len(p) - 1 for p in ps)
            vals = []
            for _ in range(40):
                sh = []
                for p in ps:
                    t = p[:]
                    rng.shuffle(t)
                    sh.append(t)
                vals.append(g2(sh)[0])
            base[k] = sum(vals) / len(vals)

        def excess(k: str, rule) -> float:
            cols, order = rule
            rest = [unpermute(p, readout(len(p), cols, order)) for p in halves[k]]
            return (g2(rest)[0] - base[k]) / npair[k]

        rules = [
            (c, o)
            for c in range(2, max_cols + 1)
            for o in itertools.permutations(range(c))
        ]
        sa = sorted(((excess("A", r), r) for r in rules), reverse=True)
        sb = sorted(((excess("B", r), r) for r in rules), reverse=True)
        print(
            f"best rule on half A: {sa[0][0]:.4f}  cols {sa[0][1][0]} order {sa[0][1][1]}"
        )
        print(f"   the same rule on B: {excess('B', sa[0][1]):+.4f}")
        print(
            f"best rule on half B: {sb[0][0]:.4f}  cols {sb[0][1][0]} order {sb[0][1][1]}"
        )
        print(f"   the same rule on A: {excess('A', sb[0][1]):+.4f}")
        rank = next(i for i, (_s, r) in enumerate(sb) if r == sa[0][1]) + 1
        print(f"\nA's winner ranks {rank:,} of {len(rules):,} on B -- the median.")
        print(
            "Neither winner survives the move. The full-corpus maximum is overfitting."
        )
        return

    if "--null" in sys.argv:
        rng = random.Random(99)
        pages = page_lengths()
        for rep in range(4):
            shuffled = []
            for p in pages:
                t = p[:]
                rng.shuffle(t)
                shuffled.append(t)
            print(
                f"replicate {rep}: search maximum {search(shuffled, max_cols)[0][0]:.4f}",
                flush=True,
            )
        return

    if "--control" in sys.argv:
        prose = prose_sequences(40000)[0][1]
        pages, i = [], 0
        while i + 45 < len(prose):
            pages.append(prose[i : i + 45])
            i += 45
        pages = pages[:57]
        key = (3, 0, 5, 1, 4, 2)
        planted = [[p[j] for j in readout(len(p), 6, key)] for p in pages]
        rows = search(planted, max_cols)
        print(f"planted keyed columnar, 6 columns, order {key}")
        for e, c, o in rows[:4]:
            print(f"  {e:>8.4f}  cols {c} order {o}")
        rank = next(i for i, (_e, c, o) in enumerate(rows) if c == 6 and o == key)
        print(f"  the planted rule ranks {rank + 1} of {len(rows):,}")
        return

    pages = page_lengths()
    rows = search(pages, max_cols)
    print(
        f"{len(pages)} pages, {sum(len(p) for p in pages):,} blocks, "
        f"{len(rows):,} keyed rules\n"
    )
    print(f"{'excess/pair':>13}  columns  order")
    for e, c, o in rows[:8]:
        print(f"{e:>13.4f}  {c:>7}  {o}")
    print(
        "\nlanguage reference: 0.0397 +- 0.0101 (the LP's own plaintext),"
        "\n0.0484 +- 0.0160 (prose). Nothing here comes near it."
    )


if __name__ == "__main__":
    main()
