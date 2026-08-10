#!/usr/bin/env python3
# ABOUTME: Extends the plaintext-autokey repeat-rate kill from depth 1 to
# ABOUTME: depths 2-10: predicted forced ciphertext repeats vs the observed
# ABOUTME: at-chance census, TR-independent, for C[i] = TR[P[i-L]][P[i]].
"""Plaintext autokey at depth L: the repeat-rate kill, quantified.

`plaintext_autokey_closure.py` closed depth 1. The lag-5 anomaly makes
the tapped variant C[i] = TR[P[i-L]][P[i]] (especially L = 5) the obvious
remaining member, and no file covered it: split tests cannot see
plaintext-side feedback at any depth.

The same closure extends exactly. The cipher rune at i is a function of
the pair (P[i-L], P[i]) alone, so the ciphertext n-gram at i is a
function of the augmented n-gram A[i..i+n-1], A[i] = (P[i-L], P[i]).
Every repeated n-gram of the A-stream forces a repeated ciphertext
n-gram, position-free and for ANY tabula recta whose rows are
permutations. At L = 1 this is the (n+1)-gram bound of the depth-1
script (n consecutive A symbols cover n+1 consecutive P symbols).

Scope: the stream-running form (the tap crosses word boundaries and
never resets). Word-boundary-reset variants are a different mechanism,
closed in `word-boundary-reset-autokey.md`.

The bound is validated by direct simulation: encrypting the register
plaintext with a random-permutation TR must produce at least the forced
count (plus chance collisions on top).
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from solved_plaintext_running_key import (  # noqa: E402
    recover_plaintext,
    solved_segments,
)

M = 29


def repeated_pairs(stream, n: int) -> int:
    c = Counter(tuple(stream[i : i + n]) for i in range(len(stream) - n + 1))
    return sum(v * (v - 1) // 2 for v in c.values())


def forced_pairs(pt: list[int], L: int, n: int) -> int:
    aug = list(zip(pt[:-L], pt[L:]))
    return repeated_pairs(aug, n)


def validate(pt: list[int], L: int, n: int) -> None:
    """Simulated lag-L autokey repeats must be >= the forced count."""
    rng = random.Random(3301)
    tr = []
    for _ in range(M):
        row = list(range(M))
        rng.shuffle(row)
        tr.append(row)
    ct = [tr[pt[i - L]][pt[i]] for i in range(L, len(pt))]
    sim = repeated_pairs(ct, n)
    forced = forced_pairs(pt, L, n)
    if sim < forced:
        msg = f"validation failed at L={L}, n={n}: simulated {sim} < forced {forced}"
        raise AssertionError(msg)
    print(
        f"validation OK (L={L}, n={n}): simulated ciphertext repeats "
        f"{sim} >= forced {forced}"
    )


def main() -> None:
    pt = recover_plaintext(solved_segments())
    clean, _ = load_clean()
    scale = (len(clean) / len(pt)) ** 2
    print(
        f"plaintext register: {len(pt)} runes; clean corpus "
        f"{len(clean)} runes; pair-count scale x{scale:.1f}"
    )
    for L in range(1, 11):
        validate(pt, L, 4)

    obs = {n: repeated_pairs(clean, n) for n in (4, 5, 6)}
    print(
        f"\nobserved clean-corpus repeated n-grams: "
        f"4: {obs[4]}, 5: {obs[5]}, 6: {obs[6]} "
        f"(doublet-corrected chance: 124 +- 10 / 4 +- 2 / ~0)"
    )
    # forced repeats add ON TOP of chance, so the binding comparison is
    # against the allowed excess over the null, not the raw observed count
    excess_bar = obs[4] - 124 + 3 * 10
    print(f"allowed forced excess over chance (3 sigma): ~{excess_bar}")
    print(
        f"\n{'L':>3} {'forced 4-gram pairs':>20} {'predicted (scaled)':>19} "
        f"{'vs excess bar':>14}"
    )
    for L in range(1, 11):
        f4 = forced_pairs(pt, L, 4)
        pred = f4 * scale
        margin = pred / excess_bar
        print(f"{L:>3} {f4:>20} {pred:>19.0f} {margin:>13.0f}x")


if __name__ == "__main__":
    main()
