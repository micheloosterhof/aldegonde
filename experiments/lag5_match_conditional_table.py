# ABOUTME: Given a lag-5 match c_i = c_(i+5), tests the table of the next pair (c_(i+1), c_(i+6))
# ABOUTME: for any relation beyond equality, the off-diagonal face of the d1 pairing.
"""What follows a lag-5 match?

The d1 pairing of `lag5-digraph-structure.md` is the diagonal of this table: after a
match at (i, i+5), the next pair (i+1, i+6) matches again 29 times whole-stream and 9
times within words, both above chance. The off-diagonal has never been looked at. A copy
or echo mechanism predicts equality only; any rule that continued a match with a
different fixed relation would show here.

Thin by construction -- 479 events whole-stream, about 100 within words -- so the
readings are the off-diagonal chi-square and the best fixed-point-free relation against
the pairing-shuffle null of `lag_full_table.py`, and nothing finer.

    python experiments/lag5_match_conditional_table.py [--trials 4000]
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lag_full_table import SEED, load_sections, report  # noqa: E402

LAG = 5


def following_pairs(sections) -> tuple[np.ndarray, np.ndarray]:
    """(within-word, whole-stream) pairs (c_(i+1), c_(i+6)) at every i with c_i = c_(i+5)."""
    within, whole = [], []
    for words in sections:
        stream = [r for w in words for r in w]
        owner = [k for k, w in enumerate(words) for _ in w]
        for i in range(len(stream) - LAG - 1):
            if stream[i] != stream[i + LAG]:
                continue
            pair = (stream[i + 1], stream[i + LAG + 1])
            whole.append(pair)
            if owner[i] == owner[i + LAG + 1]:
                within.append(pair)
    return np.array(within), np.array(whole)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=4000)
    args = ap.parse_args()
    rng = random.Random(SEED)
    within, whole = following_pairs(load_sections())
    for name, pairs in (
        ("within-word, after a match", within),
        ("whole stream, after a match", whole),
    ):
        report(name, pairs, rng, args.trials)


if __name__ == "__main__":
    main()
