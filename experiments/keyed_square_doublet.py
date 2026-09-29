# ABOUTME: Tests the "keyed 5x5 square + row/column rotation" reading of g against
# ABOUTME: the doublet rate: plain GP square, random grids, and keyword-filled squares.
"""Could g be a keyed 5x5 square stepped by a row/column rotation?

An order-5 permutation on 29 runes with the minimum 4 fixed points is exactly a
5x5 grid of 25 runes (each row or column a 5-cycle) with 4 leftovers fixed. The
ciphertext doublet rate is then sum_x f(x, g^-1 x) = the plaintext frequency of
each grid rune paired with its row/column neighbour, plus the leftovers' self-
frequency. This script scores that rate (against the runeglish lexicon bigram
table) for:

- the plain Gematria-Primus-order square (leftovers AE Y IA EA),
- random grids (can grid+rotation reach the observed 0.0063 at all?),
- keyword-filled squares (does any real keyword land on it?).

Result on the lexicon proxy: the plain square is excluded (~0.036-0.061);
grid+rotation can reach 0.0063 but only ~0.03% of grids do; and no common or
Cicada-thematic keyword reaches it (closest ~0.0065). Proxy caveat: the real LP
plaintext bigram table differs, so the exact winner is indicative, not final.

Usage: python experiments/keyed_square_doublet.py
"""

from __future__ import annotations

import random

import numpy as np

from aldegonde import c3301

MOD = 29
OBSERVED = 0.0063
ROTATIONS = ("row+", "row-", "col+", "col-")
THEMATIC = [
    "PRIME", "PRIMES", "PRIMALITY", "TOTIENT", "DIVINITY", "CIRCUMFERENCE",
    "INSTAR", "PARABLE", "KOAN", "WISDOM", "SACRED", "WELCOME", "TRUTH",
    "WITHIN", "MOBIUS", "CICADA", "LIBER", "PRIMUS", "CONSUME", "PRESERVE",
]



def transliterate(word: str) -> list[int] | None:
    if not (word.isascii() and word.isalpha()):
        return None
    return c3301.encode_english(word)


def bigram_table() -> np.ndarray:
    from wordfreq import top_n_list, word_frequency

    counts = np.zeros((MOD, MOD))
    for word in top_n_list("en", 40000):
        runes = transliterate(word)
        if not runes:
            continue
        weight = word_frequency(word, "en")
        for i in range(len(runes) - 1):
            counts[runes[i]][runes[i + 1]] += weight
    return counts / counts.sum()


def grid_rate(f: np.ndarray, order: list[int], mode: str) -> float:
    """Doublet rate for a 25-rune row-major grid stepped by `mode`; 4 leftovers fixed."""
    grid = [order[r * 5 : r * 5 + 5] for r in range(5)]
    ginv: dict[int, int] = {}
    for r in range(5):
        for c in range(5):
            if mode == "row+":
                ginv[grid[r][c]] = grid[r][(c - 1) % 5]
            elif mode == "row-":
                ginv[grid[r][c]] = grid[r][(c + 1) % 5]
            elif mode == "col+":
                ginv[grid[r][c]] = grid[(r - 1) % 5][c]
            else:
                ginv[grid[r][c]] = grid[(r + 1) % 5][c]
    leftovers = [x for x in range(MOD) if x not in ginv]
    return sum(f[x][ginv[x]] for x in ginv) + sum(f[x][x] for x in leftovers)


def keyed_order(keyword: str) -> list[int] | None:
    """Mixed alphabet: keyword runes (deduped) then remaining GP order; grid = first 25."""
    runes = transliterate(keyword)
    if not runes:
        return None
    order: list[int] = []
    for x in runes + list(range(MOD)):
        if x not in order:
            order.append(x)
    return order


def best_rate(f: np.ndarray, order: list[int]) -> float:
    return min(grid_rate(f, order, m) for m in ROTATIONS)


def main() -> None:
    from wordfreq import top_n_list

    f = bigram_table()

    print(f"plain GP-order 5x5 square (target {OBSERVED}):")
    for m in ROTATIONS:
        rate = grid_rate(f, list(range(25)), m)
        print(f"  {m}: {rate:.4f}  ({rate / (1 / MOD):.2f}x chance)")

    rng = random.Random(3)
    mins = np.array([
        best_rate(f, rng.sample(range(MOD), 25)) for _ in range(4000)
    ])
    print(f"\nrandom grid best-of-4: mean={mins.mean():.4f} min={mins.min():.4f} "
          f"frac<=obs={(mins <= OBSERVED).mean():.4f}")

    scored: list[tuple[float, str]] = []
    for kw in THEMATIC + [w for w in top_n_list("en", 6000) if w.isalpha() and len(w) >= 3]:
        order = keyed_order(kw)
        if order:
            scored.append((best_rate(f, order), kw))
    scored.sort()
    print(f"\nkeyword squares: {len(scored)} tested, "
          f"{sum(1 for r, _ in scored if r <= OBSERVED)} reach <= {OBSERVED}")
    print("  lowest:", ", ".join(f"{kw}={r:.4f}" for r, kw in scored[:6]))
    thematic = sorted((r, kw) for r, kw in scored if kw in THEMATIC)
    print("  thematic:", ", ".join(f"{kw}={r:.4f}" for r, kw in thematic[:6]))


if __name__ == "__main__":
    main()
