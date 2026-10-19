# ABOUTME: Reads the 176 number-grid bytes as rune permutations by every natural
# ABOUTME: derivation and asks whether any yields an order-5 step like the walk's g.
"""Do the number grids carry the walk's permutations?

`number-grids-are-bytes.md` shows pages 50-51 hold 176 uniform bytes and rules out an
additive keystream, a digest of the book, packed runes and a repeating XOR. It never
reads them as PERMUTATIONS, which is what the walk's key is made of: g of order 5 with
five 5-cycles, sigma, and base_0, about 283 bits against the grids' 1,408.

g is the sharp target. A uniformly random permutation of 29 runes has order exactly 5
with probability about 1.1e-7, so a natural derivation that lands on one is not chance.

Byte streams: each grid alone and both concatenation orders, read row-major and
column-major (8 columns), forwards and reversed. Derivations of a permutation from a
stream, at every start:

  rank       the ranks of 29 consecutive bytes (ties broken by position), and inverse
  mixed      bytes mod 29 in order, repeats dropped, missing runes appended in order
  shuffle    Fisher-Yates driven by the bytes, j = b mod (i + 1)
  literal    29 consecutive bytes that are distinct mod 29, taken as the permutation
  lehmer     each big-integer reading of `number_grid_bytes.as_integers`, mod 29!, and
             its successive base-29! digits, decoded as a Lehmer code

**Result (2026-10-19): negative.** 7,422 candidates give one permutation of order 5,
with two 5-cycles, from the top base-29! digit of one big-integer reading. A top digit
is small (23 bits here), so its permutation moves only the last 11 runes, and order 5
is then common. Random bytes through the same pipeline give 2.13 such hits per trial,
so P = 0.82 for the grids' one. None of the 7,422 has the four or five 5-cycles g
needs.

Run with no arguments for the self-test, `--run` for the census.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from number_grid_bytes import as_integers, grid_bytes  # noqa: E402

from aldegonde.maths import permutation  # noqa: E402

M = 29
COLUMNS = 8


def column_major(values: list[int]) -> list[int]:
    rows = [values[i : i + COLUMNS] for i in range(0, len(values), COLUMNS)]
    return [row[c] for c in range(COLUMNS) for row in rows if c < len(row)]


def streams(g: dict[int, list[int]]) -> dict[str, list[int]]:
    out = {}
    for name, parts in (
        ("65", [65]),
        ("66", [66]),
        ("65+66", [65, 66]),
        ("66+65", [66, 65]),
    ):
        for reading, f in (("rows", lambda v: v), ("cols", column_major)):
            seq = [b for p in parts for b in f(g[p])]
            out[f"{name} {reading} fwd"] = seq
            out[f"{name} {reading} rev"] = seq[::-1]
    return out


def rank(window: list[int]) -> list[int]:
    order = sorted(range(M), key=lambda i: (window[i], i))
    out = [0] * M
    for r, i in enumerate(order):
        out[i] = r
    return out


def mixed(stream: list[int], start: int) -> list[int]:
    seen: list[int] = []
    for b in stream[start:]:
        if b % M not in seen:
            seen.append(b % M)
    return seen + [x for x in range(M) if x not in seen]


def shuffle(stream: list[int], start: int) -> list[int] | None:
    if start + M - 1 > len(stream):
        return None
    perm = list(range(M))
    for k, i in enumerate(range(M - 1, 0, -1)):
        j = stream[start + k] % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def literal(window: list[int]) -> list[int] | None:
    values = [b % M for b in window]
    return values if len(set(values)) == M else None


def lehmer(n: int) -> list[int]:
    """The permutation with Lehmer code n, 0 <= n < 29!."""
    pool = list(range(M))
    out = []
    for i in range(M - 1, -1, -1):
        f = math.factorial(i)
        out.append(pool.pop(n // f))
        n %= f
    return out


def candidates(grids: dict[int, list[int]]):
    for name, s in streams(grids).items():
        for start in range(len(s) - M + 1):
            window = s[start : start + M]
            r = rank(window)
            yield f"rank {name} @{start}", r
            yield f"rank-inverse {name} @{start}", permutation.inverse(r)
            lit = literal(window)
            if lit is not None:
                yield f"literal {name} @{start}", lit
        for start in range(len(s)):
            yield f"mixed {name} @{start}", mixed(s, start)
            sh = shuffle(s, start)
            if sh is not None:
                yield f"shuffle {name} @{start}", sh
    fact = math.factorial(M)
    for name, n in as_integers(grids).items():
        digit = 0
        while n:
            yield f"lehmer {name} digit {digit}", lehmer(n % fact)
            n //= fact
            digit += 1


def p_order_five() -> float:
    """P(order exactly 5) for a uniform permutation of 29: cycle lengths in {1, 5}."""
    return sum(
        1 / (5**k * math.factorial(k) * math.factorial(M - 5 * k)) for k in range(1, 6)
    )


def self_test() -> None:
    assert lehmer(0) == list(range(M))
    assert lehmer(math.factorial(M) - 1) == list(range(M))[::-1]
    w = [5, 3, 9] + list(range(100, 126))
    assert rank(w)[:3] == [1, 0, 2]
    assert sorted(mixed([30, 1, 59], 0)) == list(range(M))
    # 30, 1 and 59 are all 1 mod 29, so 1 leads and the rest follow in order
    assert mixed([30, 1, 59], 0)[:3] == [1, 0, 2]
    sh = shuffle(list(range(200)), 0)
    assert sorted(sh) == list(range(M))
    assert abs(p_order_five() - 1.11e-7) < 0.02e-7
    print("self-test passed")


def census(grids: dict[int, list[int]]) -> tuple[int, list[tuple[str, list[int]]]]:
    """(candidates scored, those of order exactly 5 with their cycle types)."""
    total = 0
    hits = []
    for label, perm in candidates(grids):
        assert sorted(perm) == list(range(M)), label
        total += 1
        if permutation.order(perm) == 5:
            hits.append((label, permutation.cycle_type(perm)))
    return total, hits


def five_cycles(cycle_type: list[int]) -> int:
    return sum(1 for c in cycle_type if c == 5)


def run(trials: int = 2000) -> None:
    total, hits = census(grid_bytes())
    print(f"{total:,} candidate permutations from the grids")
    print(
        f"order exactly 5: {len(hits)}   (uniform permutations: {total * p_order_five():.1e})"
    )
    for label, ct in hits:
        print(f"   {label}: {five_cycles(ct)} five-cycles")

    # the uniform-permutation rate is the wrong null: a big integer's top base-29!
    # digit is small, and its permutation moves only the last few runes. Random bytes
    # of the same sizes, through the same pipeline, price every derivation as it is.
    rng = random.Random(3301)
    sizes = {k: len(v) for k, v in grid_bytes().items()}
    null_hits, null_rich = [], []
    for _ in range(trials):
        fake = {k: [rng.randrange(256) for _ in range(n)] for k, n in sizes.items()}
        _, h = census(fake)
        null_hits.append(len(h))
        null_rich.append(sum(1 for _, ct in h if five_cycles(ct) >= 4))
    rich = sum(1 for _, ct in hits if five_cycles(ct) >= 4)
    p_any = sum(1 for x in null_hits if x >= len(hits)) / trials
    p_rich = sum(1 for x in null_rich if x >= rich) / trials
    print(
        f"\nrandom bytes, {trials} trials: order-5 hits {sum(null_hits) / trials:.3f} per trial"
    )
    print(f"  P(at least {len(hits)} order-5 hits) = {p_any:.3f}")
    print(f"  with four or five 5-cycles, as g has: grids {rich}, P = {p_rich:.3f}")


if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    else:
        self_test()
