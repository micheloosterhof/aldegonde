# ABOUTME: Shows that the walk's sigma chain can trap a ciphertext rune on one plaintext
# ABOUTME: letter when sigma fixes a fixed point of g, and how often random keys do it.
"""The walk's base chain is deterministic, and that leaves a unigram trace.

Under base_(w+1) = base_w ∘ g^(L_w - 1) ∘ σ the preimage of a ciphertext rune r follows
x_(w+1) = σ⁻¹ g^-(L_w-1) (x_w), a deterministic orbit on 29 points. If σ fixes a point
that g also fixes, the orbit can stop there, and from then on rune r is the image of one
plaintext letter: its count is that letter's count, 8 for a letter the author never
writes or 1,000 for E. The body's counts run 399 to 492, so under the walk such keys are
excluded. This script draws random keys, sorts them by how many fixed points g and σ
share, and prints the unigram damage, with independent per-word bases as the control.

    python experiments/walk_chain_traps.py [--keys 300]
"""

from __future__ import annotations

import argparse
import collections
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from cipher_zoo_fingerprint import compose, plaintext  # noqa: E402
from lp_corpus import load_tokenized  # noqa: E402

from aldegonde.maths import permutation as pm  # noqa: E402

M = 29


def walk(
    g: list[int], sigma: list[int], base: list[int], words: list[list[int]]
) -> list[list[int]]:
    powers = [list(range(M))]
    for _ in range(4):
        powers.append(compose(powers[-1], g))
    out = []
    for w in words:
        out.append([compose(powers[j % 5], base)[p] for j, p in enumerate(w)])
        base = compose(powers[(len(w) - 1) % 5], sigma, base)
    return out


def nioc_and_range(words: list[list[int]]) -> tuple[float, int, int]:
    stream = [r for w in words for r in w]
    c = collections.Counter(stream)
    n = len(stream)
    return (
        M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1)),
        min(c.values()),
        max(c.values()),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", type=int, default=300)
    args = ap.parse_args()
    rng = random.Random(5)
    words = plaintext(rng, 2928)
    body = collections.Counter(load_tokenized().stream)
    print(
        f"body rune counts run {min(body.values())} to {max(body.values())}; 447 expected, sd 20"
    )
    by: dict[int, list[tuple[float, int, int]]] = collections.defaultdict(list)
    for _ in range(args.keys):
        g = pm.random_with_cycle_type(M, [5, 5, 5, 5, 5], rng)
        sigma = rng.sample(range(M), M)
        shared = sum(1 for x in range(M) if g[x] == x and sigma[x] == x)
        by[shared].append(
            nioc_and_range(walk(g, sigma, rng.sample(range(M), M), words))
        )
    print(
        f"{'fixed points shared by g and σ':<32}{'keys':>6}{'nIoC':>8}{'worst min':>10}{'worst max':>10}"
    )
    for shared in sorted(by):
        v = by[shared]
        print(
            f"{shared:<32}{len(v):>6}{sum(x[0] for x in v) / len(v):>8.4f}{min(x[1] for x in v):>10}{max(x[2] for x in v):>10}"
        )
    control = []
    for _ in range(60):
        g = pm.random_with_cycle_type(M, [5, 5, 5, 5, 5], rng)
        powers = [list(range(M))]
        for _ in range(4):
            powers.append(compose(powers[-1], g))
        ct = [
            [
                compose(powers[j % 5], rng.sample(range(M), M))[p]
                for j, p in enumerate(w)
            ]
            for w in words
        ]
        control.append(nioc_and_range(ct)[0])
    mean = sum(control) / len(control)
    print(f"independent bases per word, 60 keys: nIoC {mean:.4f}")
    trapped = sum(1 for v in by.values() for x in v if x[1] < 300 or x[2] > 600)
    print(
        f"keys whose counts fall outside 300..600: {trapped} of {args.keys}; the body's walk key, if any, is not one of them"
    )


if __name__ == "__main__":
    main()
