#!/usr/bin/env python3
"""Unified census: word-anchored, boundary-consistent repeated runs.

Statistic: number of pairs of maximal repeated rune runs (length >= 5) whose
internal word-boundary patterns are identical in both occurrences AND which
contain at least one aligned internal word boundary.

Null: Markov runes (doublet-suppressed), real word-length structure.
"""

from collections import defaultdict

import numpy as np

from anomaly_scan import parse
from aldegonde import c3301

N = 29
MINLEN = 5


def boundary_flags(lens):
    """bound[i] = True if a word boundary follows rune i."""
    n = sum(lens)
    b = np.zeros(n, dtype=bool)
    k = 0
    for L in lens:
        k += L
        if k < n:
            b[k - 1] = True
    return b


def census(arr, bound):
    n = len(arr)
    grams = defaultdict(list)
    for i in range(n - MINLEN + 1):
        grams[tuple(arr[i : i + MINLEN])].append(i)
    found = set()
    count = 0
    examples = []
    for v in grams.values():
        if len(v) < 2:
            continue
        for a in range(len(v)):
            for b in range(a + 1, len(v)):
                i, j = v[a], v[b]
                # extend to maximal run
                s = 0
                while i - s - 1 >= 0 and j - s - 1 >= 0 and arr[i - s - 1] == arr[j - s - 1]:
                    s += 1
                e = MINLEN
                while i + e < n and j + e < n and arr[i + e] == arr[j + e]:
                    e += 1
                key = (i - s, j - s, s + e)
                if key in found:
                    continue
                found.add(key)
                i0, j0, L = key
                # boundary patterns inside the run (after runes 0..L-2)
                pat1 = tuple(bool(bound[i0 + t]) for t in range(L - 1))
                pat2 = tuple(bool(bound[j0 + t]) for t in range(L - 1))
                if pat1 == pat2 and any(pat1):
                    count += 1
                    examples.append((i0, j0, L, pat1))
    return count, examples


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= len(stream) - nplain:
            cw.append(w)
        total += len(w)
    lens = [len(w) for w in cw]
    n = sum(lens)
    arr = np.array([r for w in cw for r in w])
    bound = boundary_flags(lens)
    obs, examples = census(arr, bound)
    print(f"observed anchored boundary-consistent repeats (len>={MINLEN}): {obs}")
    for i0, j0, L, pat in examples:
        s1 = "".join(c3301.CICADA_ALPHABET[x] for x in arr[i0 : i0 + L])
        print(f"  pos {i0} & {j0}, len {L}, dist {j0-i0}: {s1} boundaries {pat}")

    rng = np.random.default_rng(11)
    SAMPLES = 400
    p_dd = 0.00675
    mc = []
    for _ in range(SAMPLES):
        out = np.empty(n, dtype=np.int64)
        out[0] = rng.integers(0, N)
        same = rng.random(n) < p_dd
        jump = rng.integers(0, N - 1, n)
        for i in range(1, n):
            if same[i]:
                out[i] = out[i - 1]
            else:
                j = jump[i]
                out[i] = j if j < out[i - 1] else j + 1
        c, _ = census(out, bound)
        mc.append(c)
    mc = np.array(mc)
    print(f"\nMC null ({SAMPLES} samples): mean={mc.mean():.3f} sd={mc.std():.3f} "
          f"max={mc.max()}")
    print(f"P(>= {obs}) = {(mc >= obs).mean():.5f}")
    print(f"distribution: {np.bincount(mc).tolist()}")


if __name__ == "__main__":
    main()
