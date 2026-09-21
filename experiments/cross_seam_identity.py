# ABOUTME: Derives and verifies the cross-seam analogue of the lag-k identity, giving the
# ABOUTME: first key-free handle on sigma, and shows the preventer is strictly adjacent.
"""The base cancels across a block boundary too, and what survives is sigma.

Inside a block `d-profile-pins-g-to-five-cycles.md` uses `c_i = c_(i+k)` iff
`p_i = g^k(p_(i+k))`. Across a boundary the base changes -- `base_(w+1) = base_w o g^a o
sigma` with `a` the clock at the last rune of block w -- and it still cancels:

    c(i) = c'(j)   <=>   p_i = g^(a - c_i) o sigma o g^(c'_j) (p'_j)

Write `u = (a - c_i) mod 5`, which is just the distance from the end of block w, and
`v = c'_j mod 5`. Then each cross-seam pair tests the permutation

    h(u,v) = g^u o sigma o g^v

So the cross-seam coincidence rate, split by (u, v), is a key-free measurement of sigma.
Every other statement about sigma in this directory is conditional on the chain model;
this one is not.

The identity is checked exactly against a synthetic walk before anything is read off it.

The same table answers a second question for free. The adjacent cross-seam pair is the
one the preventer acts on. Does it act on any other?

    python cross_seam_identity.py
"""

from __future__ import annotations

import collections
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, compose, lp_words, ppow, prose_corpora  # noqa: E402

CHANCE = 1 / M


def walk_with_clock(g, sigma, plain, rng):
    gp = [ppow(g, i) for i in range(5)]
    base = rng.sample(range(M), M)
    out, clocks, clock = [], [], 0
    for word in plain:
        cw, cl = [], []
        for p in word:
            cw.append(base[gp[clock % 5][p]])
            cl.append(clock)
            clock += 1
        out.append(cw)
        clocks.append(cl)
        base = compose(base, compose(gp[(clock - 1) % 5], sigma))
    return out, clocks


def verify_identity() -> None:
    rng = random.Random(3)
    g = order5_fixing(rng.sample(range(M), 4), rng)
    sigma = rng.sample(range(M), M)
    plain = next(iter(prose_corpora(2928, 1)))
    cipher, clocks = walk_with_clock(g, sigma, plain, random.Random(1))
    agree = disagree = 0
    for w in range(min(400, len(cipher) - 1)):
        a_cipher, b_cipher = cipher[w], cipher[w + 1]
        if not a_cipher or not b_cipher:
            continue
        a = clocks[w][-1] % 5
        for i in range(len(a_cipher)):
            for j in range(len(b_cipher)):
                u = (a - clocks[w][i]) % 5
                v = clocks[w + 1][j] % 5
                h = compose(compose(ppow(g, u), sigma), ppow(g, v))
                same = plain[w][i] == h[plain[w + 1][j]]
                if same == (a_cipher[i] == b_cipher[j]):
                    agree += 1
                else:
                    disagree += 1
    print(f"identity check against a synthetic walk: {agree:,} agree, "
          f"{disagree:,} disagree")
    print("  c(i) = c'(j)  <=>  p_i = g^(a - c_i) o sigma o g^(c'_j) (p'_j),  "
          "a = clock at the last rune of block w")
    if disagree:
        print("  THE DERIVATION IS WRONG -- nothing below is usable")


def adjacency_table(words) -> None:
    cnt, hits = collections.Counter(), collections.Counter()
    for w in range(len(words) - 1):
        a, b = words[w], words[w + 1]
        if not a or not b:
            continue
        for di in range(min(4, len(a))):
            for j in range(min(4, len(b))):
                cnt[(di, j)] += 1
                hits[(di, j)] += a[len(a) - 1 - di] == b[j]
    print(f"\n\ncross-seam coincidence by distance from the end of block w (di) and "
          f"offset into block w+1 (j).\nchance is {CHANCE:.4f}; z in brackets.\n")
    print("{:>10}".format("") + "".join("{:>16}".format(f"j={j}") for j in range(4)))
    for di in range(4):
        row = ""
        for j in range(4):
            n = cnt[(di, j)]
            r = hits[(di, j)] / n
            se = math.sqrt(r * (1 - r) / n)
            row += "{:>16}".format(f"{r:.4f} ({(r - CHANCE) / se:+.1f})")
        print("{:>10}".format(f"di={di}") + row)
    hit = pair = 0
    for w in words:
        for i in range(len(w) - 1):
            pair += 1
            hit += w[i] == w[i + 1]
    print(f"\nwithin-block adjacent, for comparison: {hit / pair:.4f} on {pair:,} pairs")
    print(
        "\nExactly one cell of the sixteen is suppressed, the adjacent one, and every"
        "\nother sits at chance with |z| at most 1.6. The preventer is STRICTLY"
        "\nadjacent: it inspects the immediately preceding emission and nothing else."
        "\nA rule refusing to repeat within a window of two or more is excluded, and so"
        "\nis any rule with memory beyond one rune."
    )


def sigma_channel(words) -> None:
    """How much does the cross-seam table actually say about sigma?"""
    table = np.zeros((M, M))
    for c in prose_corpora(2928, 40):
        for a, b in zip(c, c[1:]):
            for i in range(max(0, len(a) - 3), len(a)):
                for j in range(min(3, len(b))):
                    if len(a) - 1 - i == 0 and j == 0:
                        continue
                    table[a[i], b[j]] += 1
    table /= table.sum()
    rng = random.Random(5)
    mass = np.array([
        sum(table[x, h[x]] for x in range(M))
        for h in (rng.sample(range(M), M) for _ in range(2000))
    ])

    clock, clocks = 0, []
    for w in words:
        clocks.append(list(range(clock, clock + len(w))))
        clock += len(w)
    cnt = collections.Counter()
    for w in range(len(words) - 1):
        a_w, b_w = words[w], words[w + 1]
        if not a_w or not b_w:
            continue
        a = clocks[w][-1] % 5
        for i in range(max(0, len(a_w) - 3), len(a_w)):
            for j in range(min(3, len(b_w))):
                if i == len(a_w) - 1 and j == 0:
                    continue
                cnt[((a - clocks[w][i]) % 5, clocks[w + 1][j] % 5)] += 1

    counts = np.array(list(cnt.values()))
    se = math.sqrt(CHANCE * (1 - CHANCE) / np.median(counts))
    print(f"\n\nthe sigma channel: {counts.sum():,} usable pairs in {len(cnt)} (u, v) "
          f"cells")
    print(f"  median {int(np.median(counts)):,} pairs per cell, error {se:.4f}")
    print(f"  graph mass of a random permutation on the cross-word table: "
          f"{mass.mean():.4f} +- {mass.std():.4f}")
    print(f"  signal to noise per cell: {mass.std() / se:.2f}")
    print(
        "\nThat is real but small. Fifteen cells at a signal-to-noise of 1.2 carry"
        "\nroughly as much as the within-block profile does about g -- under ten bits --"
        "\nand sigma lives in a space of about a hundred bits, so a pool filter is"
        "\nmeaningless here in a way it was not for g's conjugacy class."
        "\n\nWhat the channel IS good for is verification: given a proposed (g, sigma) it"
        "\npredicts fifteen numbers, and the prediction costs nothing. That is the first"
        "\ncheck on sigma in this directory that does not assume the chain."
    )


def main() -> None:
    verify_identity()
    body = lp_words()
    adjacency_table(body)
    sigma_channel(body)


if __name__ == "__main__":
    main()
