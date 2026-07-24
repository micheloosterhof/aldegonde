#!/usr/bin/env python3
# ABOUTME: Uniqueness census for the DJU-BEI state return: other occurrences,
# ABOUTME: near-collisions among adjacent 3+3 word blocks, and the word-initial
# ABOUTME: digraph distribution behind the DJ-prefix curiosity.
"""Is there another DJU, and is the state return isolated?

Three questions:
  A. Do the words DJU / BEI occur anywhere else in the clean corpus, and
     is word repetition generally at chance?
  B. Is the 6-of-6 agreement the tip of a graded family? Compares every
     pair of adjacent 3+3 word blocks by positional agreement against
     the binomial chance expectation — a partial-base-collision model
     predicts an excess at 4 and 5.
  C. The DJ-prefix cluster: six 3-rune words start with the digraph that
     opens DJU. Scored against the whole word-initial-digraph
     distribution (the honest max-statistic), and against all word
     lengths, where the choice of "3-rune words" is not made post hoc.
"""

from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lp_corpus import ALPHABET, load_clean


def main() -> None:
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    words = [tuple(d[k]) for k in sorted(d)]
    txt = lambda t: "".join(ALPHABET[r] for r in t)
    idx = {c: ALPHABET.index(c) for c in "ᛞᛄᚢᛒᛖᛁ"}
    DJU = tuple(idx[c] for c in "ᛞᛄᚢ")
    BEI = tuple(idx[c] for c in "ᛒᛖᛁ")

    print("A. occurrences")
    for name, target in (("DJU", DJU), ("BEI", BEI)):
        at = [i for i, x in enumerate(words) if x == target]
        print(f"   {name} ({txt(target)}): {len(at)} at word indices {at}")
    c = Counter(x for x in words if len(x) >= 3)
    reps = {k: v for k, v in c.items() if v > 1}
    pairs = sum(v * (v - 1) // 2 for v in reps.values())
    n3 = sum(1 for x in words if len(x) == 3)
    exp3 = n3 * (n3 - 1) / 2 / 29 ** 3
    print(f"   repeated words len>=3: {len(reps)} distinct, {pairs} pairs "
          f"(3-rune chance expectation alone: {exp3:.1f})")

    print("\nB. near-collision census (adjacent 3+3 blocks)")
    blocks = [(i, words[i] + words[i + 1]) for i in range(len(words) - 1)
              if len(words[i]) == 3 and len(words[i + 1]) == 3]
    hist: Counter = Counter()
    hits = []
    for a in range(len(blocks)):
        ia, ba = blocks[a]
        for b in range(a + 1, len(blocks)):
            ib, bb = blocks[b]
            k = sum(1 for p, q in zip(ba, bb) if p == q)
            hist[k] += 1
            if k >= 4:
                hits.append((k, ia, ib, txt(ba), txt(bb)))
    total = sum(hist.values())
    print(f"   {total} block pairs; agreement histogram "
          f"{dict(sorted(hist.items()))}")
    print(f"   {'k':>2} {'observed':>9} {'chance':>10}")
    for k in range(3, 7):
        e = total * math.comb(6, k) * (1 / 29) ** k * (28 / 29) ** (6 - k)
        print(f"   {k:>2} {hist[k]:>9} {e:>10.4f}")
    for h in hits:
        print(f"   {h[0]}-of-6: words {h[1]} / {h[2]}  {h[3]}  {h[4]}")

    print("\nD. catalog: 3-rune words grouped by their 2-rune prefix")
    groups: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for i, x in enumerate(words):
        if len(x) == 3:
            groups.setdefault(x[:2], []).append((i, x[2]))
    n3 = sum(len(v) for v in groups.values())
    e3 = n3 / 841
    mult = Counter(len(v) for v in groups.values())
    print(f"   {n3} words in {len(groups)} distinct prefixes "
          f"(chance: {841 * (1 - math.exp(-e3)):.0f})")
    print(f"   {'size':>4} {'prefixes':>9} {'chance':>8}")
    for k in sorted(mult):
        print(f"   {k:>4} {mult[k]:>9} "
              f"{841 * math.exp(-e3) * e3 ** k / math.factorial(k):>8.1f}")
    colliding = sum(v * (v - 1) // 2 for v in mult.elements()) if False else \
        sum(len(v) * (len(v) - 1) // 2 for v in groups.values())
    exp_pairs = n3 * (n3 - 1) / 2 / 841
    print(f"   prefix-sharing pairs: {colliding} vs {exp_pairs:.0f} expected "
          f"(z = {(colliding - exp_pairs) / math.sqrt(exp_pairs):+.2f})")
    print("   groups of 3 or more (third runes with word index):")
    for p, v in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(v) < 3:
            continue
        thirds = " ".join(f"{ALPHABET[t]}({i})" for i, t in sorted(v))
        print(f"     {txt(p)} x{len(v)}: {thirds}")

    print("\nC. word-initial digraph distribution")
    DJ = DJU[:2]
    for label, pool in (("3-rune words", [x for x in words if len(x) == 3]),
                        ("all words len>=2",
                         [x for x in words if len(x) >= 2])):
        pref = Counter(x[:2] for x in pool)
        e = len(pool) / 841
        mx = max(pref.values())
        tail = 841 * sum(math.exp(-e) * e ** k / math.factorial(k)
                         for k in range(mx, 40))
        print(f"   {label}: n={len(pool)}, expected/cell {e:.2f}; "
              f"DJ count {pref[DJ]}")
        print(f"      max cell {mx} "
              f"({', '.join(txt(k) for k, v in pref.items() if v == mx)}); "
              f"cells >= {mx}: {sum(1 for v in pref.values() if v >= mx)} "
              f"vs {tail:.2f} expected")


if __name__ == "__main__":
    main()
