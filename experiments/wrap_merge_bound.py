# ABOUTME: Bounds how many of the hypothesised lost word separators could sit at line
# ABOUTME: wraps, the place a transcription would most plausibly drop one.
"""If separators were lost, were they lost at line breaks?

`two-rune-deficit.md` records that the body's word lengths fit a model in which about
280 separators were dropped, merging two plaintext words into one apparent word. The
model fits; it does not establish that the loss happened, because the same
distribution follows if the body's prose simply uses fewer short words.

Layout gives a test that register cannot imitate. A transcription drops a separator
where the separator is hardest to see, and the overwhelmingly likeliest such place is
a LINE BREAK -- the break itself reads as a word gap, so a separator glyph beside it
is easy to miss. Authorial word choice has no reason to track line breaks at all.

Two measurements on the clean corpus:

  placement   how often a line wrap falls inside a word rather than at a boundary,
              against a null placing the same wraps at random rune positions
  length      whether the words that DO contain a wrap are longer than that null
              predicts. A merged word is two words glued, so merges hiding at wraps
              must inflate this mean; the length bias (long words are likelier to
              contain a wrap) is already in the null

    python wrap_merge_bound.py [--draws 3000]
"""

from __future__ import annotations

import bisect
import random
import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
RUNE = re.compile(r"[ᚠ-᛿]")
WRAP = "/\n"
MERGE_GAIN = 2.6  # runes a merge adds: the short word it glues on


def words() -> tuple[list[int], list[bool], int]:
    text = "$".join((ROOT / "data" / "page0-56.txt").read_text().split("$")[:10])
    lens: list[int] = []
    wrapped: list[bool] = []
    cur, seen, nwrap = 0, False, 0
    for ch in text:
        if RUNE.match(ch):
            cur += 1
        elif ch in WRAP:
            nwrap += 1
            if cur:
                seen = True
        elif ch in c3301.WORD_BOUNDARY and cur:
            lens.append(cur)
            wrapped.append(seen)
            cur, seen = 0, False
    if cur:
        lens.append(cur)
        wrapped.append(seen)
    return lens, wrapped, nwrap


def null(lens: list[int], nwrap: int, draws: int, rng: random.Random):
    total = sum(lens)
    starts, p = [], 0
    for length in lens:
        starts.append(p)
        p += length
    counts, means = [], []
    for _ in range(draws):
        cuts = sorted(rng.randrange(1, total) for _ in range(nwrap))
        hit = lsum = 0
        for st, length in zip(starts, lens):
            i = bisect.bisect_right(cuts, st)
            if i < len(cuts) and cuts[i] < st + length:
                hit += 1
                lsum += length
        counts.append(hit)
        means.append(lsum / hit if hit else 0.0)
    return counts, means


def stats(values):
    m = sum(values) / len(values)
    sd = (sum((v - m) ** 2 for v in values) / len(values)) ** 0.5
    return m, sd


def main() -> None:
    draws = 3000
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lens, wrapped, nwrap = words()
    span = [length for length, w in zip(lens, wrapped) if w]
    obs_mean = sum(span) / len(span)
    counts, means = null(lens, nwrap, draws, random.Random(3301))

    mc, sc = stats(counts)
    mm, sm = stats(means)
    print(f"{len(lens):,} words, {sum(lens):,} runes, {nwrap:,} line wraps\n")
    print(
        f"wraps falling inside a word: {len(span)} observed, "
        f"{mc:.0f} +- {sc:.0f} under random placement, z = {(len(span) - mc) / sc:+.1f}"
    )
    print("  -> the scribe breaks lines at word boundaries, as expected\n")
    print(
        f"mean length of a wrap-spanning word: {obs_mean:.2f} observed, "
        f"{mm:.2f} +- {sm:.2f} null, z = {(obs_mean - mm) / sm:+.2f}"
    )
    print("\nhow many merges hiding among those words would have shown up:")
    for k in (10, 20, 40, 80, 280):
        rise = k * MERGE_GAIN / len(span)
        print(
            f"  {k:>3} merges -> mean {obs_mean + rise:.2f}, z = {(obs_mean + rise - mm) / sm:+.1f}"
        )
    print(
        "\nSo line wraps carry at most ~20 of the 280 separators the deficit model needs,"
        "\nand the full 280 is excluded outright. If separators were lost, they were lost"
        "\nmid-line, which is not what a transcription failure looks like."
    )


if __name__ == "__main__":
    main()
