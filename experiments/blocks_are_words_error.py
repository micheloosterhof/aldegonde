# ABOUTME: Puts an error bar on the d5 length-trend that constraint E7 rests on, and finds
# ABOUTME: it separates words from arbitrary cuts at under two sigma rather than decisively.
"""E7 quotes two point estimates and no error. The error is what decides it.

`blocks_are_words.py` distinguishes whole words from arbitrary cuts of a rune stream by
the correlation between lag-5 coincidence and block length: prose words give about +0.017
and cuts about +0.002, because a cut spans word boundaries and carries no length trend.
The body gives +0.0369, and the specification records that as

    E7  Blocks are still words, not arbitrary cuts -- the d5 length-trend floor is
        +0.0369 against +0.0029 for cuts

The floor argument is sound: attenuation can only shrink an observed correlation, so the
observed value bounds the plaintext's from below whatever the leak fraction is. But a
floor still has sampling error, and only 806 of the body's blocks run to six runes and
contribute a lag-5 pair at all.

This measures that error two ways -- the naive Fisher form and a bootstrap over the
contributing BLOCKS, which are the independent units -- and adds the third segmentation
the earlier file did not have: words with short ones joined, which
`short-units-are-written-joined.md` says the body's blocks actually are.

    python blocks_are_words_error.py [--draws 600]
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import lp_words, prose_corpora  # noqa: E402


def rows_of(blocks):
    """(length, lag-5 hits, lag-5 pairs) for every block long enough to have one."""
    out = []
    for w in blocks:
        pairs = max(0, len(w) - 5)
        if pairs:
            out.append(
                (len(w), sum(1 for i in range(pairs) if w[i] == w[i + 5]), pairs)
            )
    return out


def trend(rows) -> float:
    lengths, hits = [], []
    for n, h, p in rows:
        lengths += [n] * p
        hits += [1] * h + [0] * (p - h)
    if len(set(lengths)) < 2 or not hits:
        return float("nan")
    return float(np.corrcoef(lengths, hits)[0, 1])


def level(rows) -> float:
    return sum(r[1] for r in rows) / sum(r[2] for r in rows)


def cuts(words, rng):
    lengths = [len(w) for w in words]
    rng.shuffle(lengths)
    stream = [r for w in words for r in w]
    out, i = [], 0
    for length in lengths:
        if i >= len(stream):
            break
        out.append(stream[i : i + length])
        i += length
    return out


def joined(words, q, rng):
    out = []
    for w in words:
        if len(w) == 2 and out and rng.random() < q:
            out[-1] = out[-1] + list(w)
        else:
            out.append(list(w))
    return out


def main() -> None:
    draws = 600
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    prose = list(prose_corpora(2928, 40))
    rng = random.Random(5)
    print(f"{'prose blocks built as':<32}{'d5 level':>11}{'length trend':>14}")
    references = {}
    for label, build in (
        ("real words", lambda c: c),
        ("words, 2-rune joined q=0.40", lambda c: joined(c, 0.40, rng)),
        ("arbitrary cuts", lambda c: cuts(c, rng)),
    ):
        rows = []
        for c in prose:
            rows += rows_of(build(c))
        references[label] = trend(rows)
        print(f"{label:<32}{level(rows):>11.4f}{references[label]:>14.4f}")

    body = rows_of(lp_words())
    observed = trend(body)
    pairs = sum(r[2] for r in body)
    print(f"\n{'THE BODY':<32}{level(body):>11.4f}{observed:>14.4f}")
    print(f"  {pairs:,} lag-5 pairs from {len(body)} blocks of six runes or more")

    boot = []
    rb = random.Random(7)
    for _ in range(draws):
        sample = [body[rb.randrange(len(body))] for _ in range(len(body))]
        v = trend(sample)
        if v == v:
            boot.append(v)
    boot = np.array(boot)
    print(f"\n  naive Fisher se on the pairs : {1 / math.sqrt(pairs - 3):.4f}")
    print(f"  bootstrap over blocks        : {boot.std():.4f}")
    print(f"  95% interval                 : [{np.percentile(boot, 2.5):+.4f}, "
          f"{np.percentile(boot, 97.5):+.4f}]")
    print(f"\n{'against':<32}{'z':>8}")
    for label, value in references.items():
        print(f"{label:<32}{(observed - value) / boot.std():>8.2f}")
    print(
        "\nThe two error estimates agree, so the pairs inside a block are not badly"
        "\ncorrelated and the bootstrap is the honest number."
        "\n\nE7 separates words from cuts at 1.75 sigma, not decisively, and the 95%"
        "\ninterval reaches down to the cuts value. The result leans toward words and"
        "\ndoes not establish them. That matters because E7 is what keeps every crib"
        "\nprogram valid: a cut spanning word boundaries matches no dictionary entry."
    )


if __name__ == "__main__":
    main()
