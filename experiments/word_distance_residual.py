# ABOUTME: Breaks down the position-aligned coincidence between words 1,449 apart, the
# ABOUTME: DJU-BEI word distance, with the repeated phrase itself removed.
"""What is left at the DJU-BEI word distance once the phrase is taken out?

`new_directions_probes.py period` found that position-aligned coincidence between word w
and word w + 1449 reads +3.19 sigma, +2.73 without the phrase, and filed it as "no
period: the signal is the phrase". The distance was chosen by the phrase, so the phrase's
two words must be dropped before the figure means anything; once they are, the distance
is a single pre-stated cell and its tail is not a scan's.

This script takes the residual apart, to see whether it has the shape of anything:

  - by whether the two words have the same length, and for different lengths whether
    aligning from the word's start or its end matters;
  - by position in the word;
  - along the body, in bins of words;
  - against its neighbours 1,448 and 1,450 and the divisors of 1,449;
  - against the same statistic at every other distance (the scan's own spread).

The reference rate is 1/29: the rune counts are flat (chi-square 26.4 on 28 df) and the
statistic never compares adjacent runes, so the doublet deficit does not enter.

    python experiments/word_distance_residual.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402

from aldegonde.stats import binomial_z  # noqa: E402

CHANCE = 1 / 29
PLAINTEXT_RATE = (
    1.78 / 29
)  # the author's plaintext coincidence rate, as new_directions_probes
BIN = 150
MIN_PAIRS = 200  # word pairs a distance must have to enter the scan


def repeated_phrase(words: list[list[int]]) -> tuple[int, int]:
    """Word indices of the two occurrences of the repeated pair of blocks."""
    seen: dict[tuple, int] = {}
    for i in range(len(words) - 1):
        key = (tuple(words[i]), tuple(words[i + 1]))
        if len(key[0]) + len(key[1]) >= 6 and key in seen:
            return seen[key], i
        seen.setdefault(key, i)
    msg = "no repeated pair of blocks"
    raise RuntimeError(msg)


def aligned(words, d, skip=frozenset(), *, which="all", end=False) -> tuple[int, int]:
    """Position-aligned coincidences and pairs between words d apart."""
    h = p = 0
    for w in range(len(words) - d):
        if w in skip:
            continue
        a, b = words[w], words[w + d]
        same = len(a) == len(b)
        if (which == "same" and not same) or (which == "different" and same):
            continue
        m = min(len(a), len(b))
        p += m
        if end:
            h += sum(a[-1 - j] == b[-1 - j] for j in range(m))
        else:
            h += sum(a[j] == b[j] for j in range(m))
    return h, p


def main() -> None:
    words = lp_corpus.load_words()
    first, second = repeated_phrase(words)
    d = second - first
    skip = frozenset({first, first + 1})
    print(
        f"repeated pair of blocks at words {first} and {second}; word distance {d}; "
        f"{len(words)} words\n"
    )

    def line(label, h, p):
        print(
            f"  {label:<46}{h:>5} of {p:>5}   rate {h / p:.4f}   z {binomial_z(h, p, CHANCE):+.2f}"
        )

    print("the residual")
    line("all pairs, phrase included", *aligned(words, d))
    h0, p0 = aligned(words, d, skip)
    line("all pairs, phrase removed", h0, p0)
    line("same length, phrase removed", *aligned(words, d, skip, which="same"))
    line(
        "different length, aligned from the start",
        *aligned(words, d, skip, which="different"),
    )
    line(
        "different length, aligned from the end",
        *aligned(words, d, skip, which="different", end=True),
    )
    z0 = binomial_z(h0, p0, CHANCE)
    full = (PLAINTEXT_RATE - CHANCE) * p0
    share = (h0 - CHANCE * p0) / full
    print(
        f"  a full word-period would add {full:.0f} coincidences; the residual is "
        f"{h0 - CHANCE * p0:.0f}, {share:.2f} of that\n"
    )

    print("by position in the word, from the start (phrase removed)")
    hits, pairs = Counter(), Counter()
    for w in range(len(words) - d):
        if w in skip:
            continue
        a, b = words[w], words[w + d]
        for j in range(min(len(a), len(b))):
            pairs[j] += 1
            hits[j] += a[j] == b[j]
    print(
        "  "
        + "  ".join(
            f"{j}: {binomial_z(hits[j], pairs[j], CHANCE):+.1f}"
            for j in range(6)
            if pairs[j]
        )
    )

    print(f"\nalong the body, bins of {BIN} words (phrase removed)")
    hits, pairs = Counter(), Counter()
    for w in range(len(words) - d):
        if w in skip:
            continue
        a, b = words[w], words[w + d]
        m = min(len(a), len(b))
        pairs[w // BIN] += m
        hits[w // BIN] += sum(a[j] == b[j] for j in range(m))
    zs = [binomial_z(hits[k], pairs[k], CHANCE) for k in sorted(pairs)]
    print("  " + "  ".join(f"{z:+.1f}" for z in zs))
    positive = sum(z > 0 for z in zs)
    print(f"  {positive} of {len(zs)} bins positive")

    print("\nneighbours and divisors (phrase words removed where they enter)")
    divisors = [k for k in range(2, d) if d % k == 0]
    for dd in (d - 1, d + 1, *sorted(divisors, reverse=True)[:6]):
        h, p = aligned(words, dd)
        print(f"  D = {dd:<6} z {binomial_z(h, p, CHANCE):+.2f}")

    scan = []
    for dd in range(1, len(words) - MIN_PAIRS):
        if dd == d:
            continue
        h, p = aligned(words, dd)
        scan.append(binomial_z(h, p, CHANCE))
    scan_arr = np.array(scan)
    above = int((scan_arr >= z0).sum())
    print(
        f"\nevery other distance: mean {scan_arr.mean():+.3f}, sd {scan_arr.std():.3f}; "
        f"{above} of {len(scan_arr)} read at least {z0:+.2f}"
    )
    p_single = (above + 1) / (len(scan_arr) + 1)
    if p_single < 0.01:
        shape = "spread evenly" if positive >= 0.8 * len(zs) else "concentrated"
        print(
            f"VERDICT: a residual of {z0:+.2f} at one pre-stated distance, empirical "
            f"P {p_single:.4f}, {shape} along the body and {share:.2f} of a full "
            f"word-period. Too small to be a period, too large to ignore; no model here "
            f"predicts it."
        )
    else:
        print(
            f"VERDICT: with the phrase removed the distance is unremarkable "
            f"(empirical P {p_single:.3f})."
        )


if __name__ == "__main__":
    main()
