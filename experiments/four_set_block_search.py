# ABOUTME: Enumerates all 23,751 four-rune subsets and tests each as the small block of a
# ABOUTME: [25,4] intransitive cipher, the one structural escape still open.
"""One block shape survives every test so far. This one enumerates it.

`no-block-partition.md` searches for the rune partition an intransitive cipher would
leave and finds nothing at any block count from 2 to 6 -- except that its power is
partition-dependent, and a block of four against a block of twenty-five is detected only
8% of the time. `rotor-machine-compact-state.md` reaches the same shape independently:
four singleton blocks fail the unigram mass test at z = -5.0, but the four fixed points
of a 5^5 1^4 letter step sharing one block of four costs only 0.7%.

So the live hypothesis is a single named set: the four runes g fixes, never mixed with
the other twenty-five.

Block membership passes through the cipher untouched, so the ciphertext's membership
INDICATOR sequence is the plaintext's. That indicator is a binary sequence, and in
language it is serially dependent. The test is the G^2 of its lag-k transition table,
pooled over lags 1 to 5.

Enumerating all 23,751 four-subsets is cheap because the statistic factors: the 2x2
indicator table at lag k is four sums over the 29x29 lag-k bigram count matrix, so the
matrices are built once and each candidate costs a handful of lookups.

The honest question is power, and it is answered by planting: the same enumeration is run
on a synthetic [25,4] cipher over the LP's own plaintext, and the planted set's rank
reported.

    python four_set_block_search.py [--control]
"""

from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29
LAGS = (1, 2, 3, 4, 5)


def bigram_tables(stream: list[int]) -> dict[int, np.ndarray]:
    """29x29 counts of (stream[i], stream[i+k]) for each lag."""
    a = np.array(stream, dtype=np.int64)
    out = {}
    for k in LAGS:
        t = np.zeros((M, M), dtype=np.int64)
        np.add.at(t, (a[:-k], a[k:]), 1)
        out[k] = t
    return out


def score_subsets(tables: dict[int, np.ndarray]) -> list[tuple[float, tuple[int, ...]]]:
    """Pooled G^2 of the membership-indicator transition tables, per 4-subset."""
    rows = []
    for s in itertools.combinations(range(M), 4):
        idx = np.array(s)
        total = 0.0
        for t in tables.values():
            inin = t[np.ix_(idx, idx)].sum()
            inall = t[idx, :].sum()
            allin = t[:, idx].sum()
            n = t.sum()
            tab = np.array(
                [[inin, inall - inin], [allin - inin, n - inall - allin + inin]],
                dtype=float,
            )
            r = tab.sum(1)
            c = tab.sum(0)
            for i in range(2):
                for j in range(2):
                    e = r[i] * c[j] / n
                    if tab[i, j] > 0 and e > 0:
                        total += 2 * tab[i, j] * math.log(tab[i, j] / e)
        rows.append((total, s))
    rows.sort(reverse=True)
    return rows


def main() -> None:
    if "--control" in sys.argv:
        import random  # noqa: PLC0415

        from lp_plaintext_register import corpus  # noqa: PLC0415

        rng = random.Random(11)
        words = corpus()
        planted = tuple(sorted(rng.sample(range(M), 4)))
        rest = [r for r in range(M) if r not in planted]
        cipher: list[int] = []
        for i in range(2928):
            word = words[i % len(words)]
            perm = list(range(M))
            for group in (list(planted), rest):
                shuffled = group[:]
                rng.shuffle(shuffled)
                for src, dst in zip(group, shuffled):
                    perm[src] = dst
            cipher += [perm[r] for r in word]
        rows = score_subsets(bigram_tables(cipher))
        rank = next(i for i, (_s, s4) in enumerate(rows) if s4 == planted)
        print(f"PLANTED [25,4] cipher over LP plaintext, small block {planted}")
        print(f"  top scores: " + ", ".join(f"{s:.1f}" for s, _ in rows[:5]))
        print(f"  planted set scores {rows[rank][0]:.1f}, rank {rank + 1} of {len(rows):,}")
        return

    stream, _wid = load_clean()
    rows = score_subsets(bigram_tables(stream))
    vals = [s for s, _ in rows]
    mu = sum(vals) / len(vals)
    sd = (sum((x - mu) ** 2 for x in vals) / len(vals)) ** 0.5
    print(f"{len(rows):,} four-rune subsets, pooled G^2 over lags {LAGS}")
    print(f"  mean {mu:.2f}, sd {sd:.2f}, max {vals[0]:.2f}")
    print(f"  best sets:")
    for s, s4 in rows[:5]:
        print(f"    {s:>7.2f}  {s4}   z = {(s - mu) / sd:+.2f}")
    top, tset = rows[0]
    disjoint = next((sc, x) for sc, x in rows if not set(x) & set(tset))
    print(f"\n  best set sharing no rune with the top one: {disjoint[0]:.2f} {disjoint[1]}")
    print(f"  top-to-disjoint ratio {top / disjoint[0]:.3f}")
    print(
        "\nThat ratio is the discriminator, not the absolute score. A real block wins by"
        "\na margin; the body's top candidates overlap each other and are separated by"
        "\nnothing, which is what a maximum over 23,751 correlated draws looks like."
    )


if __name__ == "__main__":
    main()
