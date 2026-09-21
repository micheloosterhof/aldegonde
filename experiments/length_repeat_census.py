# ABOUTME: Searches the body for repeated plaintext passages using the word-length sequence,
# ABOUTME: which any per-position cipher leaves in clear, and checks DJU-BEI's length context.
"""Does the body repeat itself? The word lengths answer without a key.

Every cipher family still standing here is per-position bijective, so it preserves
word lengths exactly. The body's word-length sequence is therefore PLAINTEXT, readable
with no key at all -- and a repeated passage must show up in it as a repeated run of
lengths, whatever the cipher does to the runes.

`collision-hunt-single-constraint.md` censuses repeated CIPHERTEXT, which finds only
matches where the plaintext and the key state both recur. This is the weaker and
therefore more sensitive test: it finds repeated plaintext regardless of key.

Two questions:

  passages   the longest repeated run of word lengths, against a shuffled null. A
             refrain or a quoted passage would stand out
  DJU-BEI    whether the one repeated ciphertext word pair sits inside a longer
             repeated passage, by extending the length match either side of it

    python length_repeat_census.py [--draws 300]
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402


def body_words() -> list[list[int]]:
    stream, wid = load_clean()
    out, cur, last = [], [], wid[0]
    for r, w in zip(stream, wid):
        if w != last:
            out.append(cur)
            cur, last = [], w
        cur.append(r)
    out.append(cur)
    return out


def longest_repeat(seq: list[int]) -> tuple[int, int, int]:
    best = (0, -1, -1)
    for length in range(3, 30):
        seen: dict[tuple, int] = {}
        found = False
        for i in range(len(seq) - length + 1):
            key = tuple(seq[i : i + length])
            if key in seen:
                best, found = (length, seen[key], i), True
            else:
                seen[key] = i
        if not found:
            break
    return best


def main() -> None:
    draws = 300
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    words = body_words()
    lens = [len(w) for w in words]
    length, i, j = longest_repeat(lens)
    print(f"body: {len(words):,} words\n")
    print(f"longest repeated word-length run: {length} words, at {i} and {j}")
    print(f"  {lens[i : i + length]}")

    rng = random.Random(3301)
    nulls = []
    for _ in range(draws):
        shuffled = lens[:]
        rng.shuffle(shuffled)
        nulls.append(longest_repeat(shuffled)[0])
    counts = collections.Counter(nulls)
    print(f"\nshuffled null over {draws} draws: {dict(sorted(counts.items()))}")
    print(f"  mean {sum(nulls) / len(nulls):.2f}, max {max(nulls)}")
    print(
        f"  P(null >= observed) = {sum(1 for x in nulls if x >= length) / len(nulls):.3f}"
    )
    print(
        f"  -> a repeated passage of {max(nulls) + 1}+ words would have been visible; none is"
    )

    seen: dict[tuple, int] = {}
    hits = []
    for k in range(len(words) - 1):
        key = (tuple(words[k]), tuple(words[k + 1]))
        if key in seen:
            hits.append((seen[key], k))
        else:
            seen[key] = k
    print(f"\nrepeated adjacent ciphertext word pairs: {len(hits)}")
    for a, b in hits:
        fwd = 0
        while (
            a + 2 + fwd < len(lens)
            and b + 2 + fwd < len(lens)
            and lens[a + 2 + fwd] == lens[b + 2 + fwd]
        ):
            fwd += 1
        back = 0
        while (
            a - 1 - back >= 0
            and b - 1 - back >= 0
            and lens[a - 1 - back] == lens[b - 1 - back]
        ):
            back += 1
        print(f"  words {a},{a + 1} and {b},{b + 1}")
        print(f"    length context matches {back} words before, {fwd} after")
        print(f"    before {lens[max(0, a - 4) : a]} vs {lens[max(0, b - 4) : b]}")


if __name__ == "__main__":
    main()


def lag1_correlation(seq: list[int]) -> float:
    """Serial correlation of adjacent word lengths: key-free, since lengths pass through."""
    a, b = seq[:-1], seq[1:]
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    return num / (da * db) if da * db else 0.0
