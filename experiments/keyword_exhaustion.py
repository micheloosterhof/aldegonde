#!/usr/bin/env python3
# ABOUTME: Exhausts the keyword-derived alphabet families for the walk's two
# ABOUTME: steps, testing whether ANY keyword reaches the required diagonals —
# ABOUTME: the family test the earlier 12-keyword samples were mistaken for.
"""Can a keyword-derived alphabet supply g or sigma?

Two earlier tests sampled 12 keywords and found none reaching the
required diagonals. That was a statement about the sample: twelve RANDOM
alphabets floor the same way (`mixed-alphabet-vigenere.md`). This runs
the family test instead — a full dictionary, several keyword→alphabet
construction rules, and a matched random null at every sample size.

Targets: the letter step needs a diagonal near 0.0063 on the within-word
bigram table (`length-clocked-walk.md`); the space step needs 0.0079 on
the cross-word table (`sigma-power-step.md`). For a Quagmire/disk
formulation the achievable relations are the conjugated shifts
K(add d)K^-1, so per alphabet the floor is the cheapest of the 28
non-identity turns, and a schedule's rate can never beat that floor.

Construction rules tested (a single rule was the blind spot last time):
  R1 keyword, remainder in gematria order
  R2 keyword, remainder in reverse gematria order
  R3 keyword, remainder continuing cyclically after the last keyword rune
  R4 keyword into a 5x6 grid, read out by columns

If no keyword under any rule reaches the target, "no small human-memorable
key" is earned by exhaustion rather than assumed. If some do, they are a
small enumerable candidate set for the full battery.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish
from doublet_position_profile import IDX_ENG
from ea_direction_test import PROSE_CACHE, prose_words
from lp_corpus import load_clean
from sigma_algebraic_floor import tables

M = 29
DICT = Path("/usr/share/dict/web2")
TARGET_G = 0.0063
TARGET_S = 0.0079


def kw_runes(word: str) -> list[int]:
    """Keyword letters as runes, de-duplicated, order preserved."""
    out, seen = [], set()
    for t in to_runeglish(word.upper()):
        i = IDX_ENG.get(t)
        if i is not None and i not in seen:
            out.append(i)
            seen.add(i)
    return out


def alphabets(seq: list[int]):
    """The four construction rules, as full 29-rune alphabets."""
    rest = [i for i in range(M) if i not in seq]
    yield "R1 gematria", seq + rest
    yield "R2 reversed", seq + rest[::-1]
    if seq:
        k = seq[-1]
        cyc = [i for i in list(range(k + 1, M)) + list(range(0, k + 1))
               if i not in seq]
        yield "R3 cyclic", seq + cyc
    full = seq + rest
    cols = [full[c::6] for c in range(6)]
    yield "R4 grid-cols", [x for col in cols for x in col]


def floor_of(K, T):
    """Cheapest non-identity conjugated-shift diagonal for alphabet K."""
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    best = 9.0
    for dl in range(1, M):
        v = sum(T[K[(pos[x] + dl) % M]][x] for x in range(M))
        if v < best:
            best = v
    return best


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    words = [d[k] for k in sorted(d)]
    lens = [len(w) for w in words]
    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if r:
            pools.setdefault(len(r), []).append(r)
    cross, within = tables(lens, pools, rng)

    vocab = []
    with open(DICT) as fh:
        for line in fh:
            x = line.strip()
            if 4 <= len(x) <= 12 and x.isalpha() and x.isascii():
                vocab.append(x)
    print(f"dictionary: {len(vocab)} words of length 4-12")

    results = {}
    for tname, T, target in (("g (within-word)", within, TARGET_G),
                             ("sigma (cross-word)", cross, TARGET_S)):
        floors = []
        hits = []
        for word in vocab:
            seq = kw_runes(word)
            if not seq:
                continue
            for rname, K in alphabets(seq):
                f = floor_of(K, T)
                floors.append(f)
                if f <= target:
                    hits.append((f, word, rname))
        floors = np.array(floors)
        hits.sort()
        results[tname] = (floors, hits, target)
        print(f"\n=== {tname}: target {target} ===")
        print(f"  {len(floors):,} keyword-alphabet candidates "
              f"({len(vocab):,} words x 4 rules)")
        print(f"  floor distribution: min {floors.min():.4f}  "
              f"1st pct {np.percentile(floors,1):.4f}  "
              f"median {np.median(floors):.4f}")
        print(f"  reaching the target: {len(hits):,} "
              f"({len(hits)/len(floors)*100:.3f}%)")
        for f, word, rname in hits[:8]:
            print(f"     {f:.4f}  {word:<14} [{rname}]")

        n_rand = min(len(floors), 40000)
        rfl = []
        for _ in range(n_rand):
            K = list(range(M))
            rng.shuffle(K)
            rfl.append(floor_of(K, T))
        rfl = np.array(rfl)
        print(f"  RANDOM alphabets, same count: min {rfl.min():.4f}  "
              f"median {np.median(rfl):.4f}  "
              f"reaching target {(rfl<=target).mean()*100:.3f}%")
        kp = (rfl < np.median(floors)).mean() * 100
        print(f"  keyword median sits at the {kp:.0f}th percentile of random")


if __name__ == "__main__":
    main()
