# ABOUTME: Full 29x29 tables at every seam reach (a, b): the a-th rune from the end of a word
# ABOUTME: against the b-th from the start of the next, tested for any relation beyond equality.
"""The seam reach family, tested off the diagonal.

`key-local-channel-is-empty.md` measures the 25 seam reaches (a, b) with a, b in 0..4 --
the pair (last-a of word w, first+b of word w+1) -- and finds every diagonal but the
doublet seam at chance. That is equality only. `seam-channel-clean.md` tests the full
table only at (0, 0). Here every reach gets the full table, the off-diagonal chi-square
and the best fixed-point-free relation, against the pairing-shuffle null of
`lag_full_table.py`.

Under the walk the two runes go through two different bases, so a non-flat table needs
adjacent bases related by a small family. The whole-stream lag tables already pool these
pairs; this isolates them by reach.

    python experiments/seam_reach_tables.py [--trials 2000]
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lag_full_table import SEED, STATISTICS, compare, load_sections, table  # noqa: E402

REACH = 5


def seam_pairs(sections, a: int, b: int) -> np.ndarray:
    pairs = [
        (w[-1 - a], nxt[b])
        for words in sections
        for w, nxt in zip(words, words[1:])
        if len(w) > a and len(nxt) > b
    ]
    return np.array(pairs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=2000)
    args = ap.parse_args()
    rng = random.Random(SEED)
    sections = load_sections()
    labels = [label for label, _ in STATISTICS]
    print(
        f"{'reach':<8}{'pairs':>6}{'diag':>6}" + "".join(f"{lb:>26}" for lb in labels)
    )
    worst: dict[str, tuple[float, tuple[int, int]]] = dict.fromkeys(
        labels, (0.0, (0, 0))
    )
    for a in range(REACH):
        for b in range(REACH):
            pairs = seam_pairs(sections, a, b)
            results = compare(pairs, rng, args.trials)
            diag = int(np.trace(table(pairs)))
            row = f"({a},{b})   {len(pairs):>6}{diag:>6}"
            for lb in labels:
                r = results[lb]
                row += f"{r.observed:>12.1f} z={r.z:>+6.2f}      "
                if (a, b) != (0, 0) and abs(r.z) > abs(worst[lb][0]):
                    worst[lb] = (r.z, (a, b))
            print(row)
    print("\nlargest |z| over the 24 reaches other than the doublet seam (0,0):")
    for lb, (z, reach) in worst.items():
        print(f"  {lb:<24} z={z:+.2f} at {reach}   (expected max of 24 nulls ~ 2.2)")


if __name__ == "__main__":
    main()
