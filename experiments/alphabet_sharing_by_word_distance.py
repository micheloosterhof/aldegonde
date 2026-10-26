# ABOUTME: Tests whether consecutive blocks share one alphabet set, by the coincidence of blocks
# ABOUTME: at matched positions as a function of the distance between them in blocks.
"""Do blocks k apart share their alphabets?

The model on record changes the alphabet set at every block. If instead a set served two
or three consecutive blocks, or persisted until some trigger, then two blocks inside one
run would be enciphered identically position by position (under a clock that restarts
at each block) and would coincide at matched positions at the plaintext's own
word-aligned rate, about 0.079, instead of chance 0.0345. Blocks at distance D share a
set with probability (k - D)/k under runs of fixed length k, or (1 - q)^D under a
switch fired with probability q per block. The record's word-aligned test pooled every
pair of blocks in the body, which dilutes a short run a thousandfold; this one reads the
rate block distance by block distance.

Left-aligned (shared position 0) is the reset-clock reading. Right-aligned (shared last
position) is included in case the set is anchored to the block's end. Under a continuous
clock the sharing would surface instead as lag-k coincidence across one boundary, which
the seam-reach census already measures at chance (`key-local-channel-is-empty.md`).

    python experiments/alphabet_sharing_by_word_distance.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from aldegonde import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from within_word_d5 import M, parse_clean_sections  # noqa: E402

DISTANCES = tuple(range(1, 13)) + (15, 20, 30, 50)
PLAINTEXT_ALIGNED = (
    0.0794  # English word-aligned coincidence, lag5-digraph-is-inside-the-word.md
)
CHANCE = 1 / M


def aligned_rate(words: list[list[int]], distance: int, align: str) -> tuple[int, int]:
    hits = pairs = 0
    for a, b in zip(words, words[distance:]):
        n = min(len(a), len(b))
        if align == "right":
            a, b = a[-n:], b[-n:]
        hits += sum(x == y for x, y in zip(a[:n], b[:n]))
        pairs += n
    return hits, pairs


def main() -> None:
    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    print(f"chance {CHANCE:.4f}; plaintext word-aligned rate {PLAINTEXT_ALIGNED:.4f}")
    print(
        "a run of k blocks sharing one alphabet set predicts, at block distance D < k,"
    )
    print("  rate = chance + (plaintext - chance) * (k - D) / k\n")
    for align in ("left", "right"):
        print(f"{align}-aligned")
        print(
            f"{'D':>4}{'pairs':>8}{'hits':>7}{'rate':>9}{'z vs chance':>13}{'k=2 predicts':>14}{'k=3 predicts':>14}"
        )
        for d in DISTANCES:
            hits = pairs = 0
            for s in sections:
                h, p = aligned_rate(s, d, align)
                hits += h
                pairs += p
            z = stats.binomial_z(hits, pairs, CHANCE)
            k2 = CHANCE + (PLAINTEXT_ALIGNED - CHANCE) * max(0, 2 - d) / 2
            k3 = CHANCE + (PLAINTEXT_ALIGNED - CHANCE) * max(0, 3 - d) / 3
            print(
                f"{d:>4}{pairs:>8}{hits:>7}{hits / pairs:>9.4f}{z:>+13.2f}{k2:>14.4f}{k3:>14.4f}"
            )
        print()

    # the continuous-clock reading: lag-k pairs that cross exactly one boundary
    print(
        "continuous-clock reading: lag-k pairs spanning exactly one boundary, hits / pairs"
    )
    print(f"{'k':>4}{'pairs':>8}{'hits':>7}{'rate':>9}{'z vs chance':>13}")
    for k in range(1, 8):
        hits = pairs = 0
        for s in sections:
            stream = [r for w in s for r in w]
            owner = [i for i, w in enumerate(s) for _ in w]
            for i in range(len(stream) - k):
                if owner[i + k] - owner[i] == 1:
                    pairs += 1
                    hits += stream[i] == stream[i + k]
        print(
            f"{k:>4}{pairs:>8}{hits:>7}{hits / pairs:>9.4f}{stats.binomial_z(hits, pairs, CHANCE):>+13.2f}"
        )
    print("  a run of k blocks under a continuous clock puts (k-1)/k of these at the")
    print("  plaintext lag-k rate (0.06-0.07 at lag 5), the rest at chance")


if __name__ == "__main__":
    main()
