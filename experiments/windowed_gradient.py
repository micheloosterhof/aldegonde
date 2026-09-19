# ABOUTME: Measures whether a walk-key objective summed over short windows, each with
# ABOUTME: its own free base, gives partial credit to near-miss keys (a search gradient).
"""Does cutting the chain into short windows turn the delta function into a slope?

`no-known-plaintext-foothold.md` found the landscape over (g, sigma) is a delta
function: one wrong image in sigma is applied ~2,900 times down the base chain, so
a one-swap neighbour scores like a random key. That was measured with ONE base_0
for the whole corpus. A short PREFIX keeps the signal but cannot pin the key.

This measures the third option: cut the corpus into many disjoint windows of k
words, give each window its own free base (the base_0-free assignment of
`base_free_verifier.py`), and average the window scores. A wrong image in sigma
then damages a window only as far as the chain runs inside it, while the evidence
still comes from the whole corpus.

Reported on the planted-key corpus for each k: the score of the true key, of keys
1, 2, 4 and 8 transpositions away in sigma, of g conjugated by 1, 2 and 4
transpositions, and of random sigma -- each as mean and spread over 20 draws. A
usable gradient needs the near misses to sit clearly between random and true, in
order of distance.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import (  # noqa: E402
    REFERENCE,
    conjugate_swap,
    log_frequencies,
    powers,
    swap_two,
)
from walk_score_kernel import Windows, score_sigmas  # noqa: E402

M = 29
DRAWS = 20


def disjoint_windows(words: list[list[int]], k: int) -> Windows:
    return Windows([words[a : a + k] for a in range(0, len(words) - k + 1, k)])


def repeated(step, key: list[int], times: int, rng: random.Random) -> list[int]:
    for _ in range(times):
        key = step(key, rng)
    return key


def main() -> None:
    with REFERENCE.open() as fh:
        ref = json.load(fh)
    g, sigma, ct = ref["g"], ref["sigmas"][0], ref["ciphertext_words"]
    logf = log_frequencies()
    rng = random.Random(3301)

    def cell(scores) -> str:
        return f"{np.mean(scores):.3f}±{np.std(scores):.3f}"

    print(
        "planted corpus; mean window score in nats/rune, each window with a free base\n"
    )
    header = [
        "k",
        "true",
        "sig 1sw",
        "sig 2sw",
        "sig 4sw",
        "sig 8sw",
        "g 1cj",
        "g 2cj",
        "g 4cj",
        "random",
    ]
    print("".join(f"{h:>13}" for h in header))
    for k in (8, 16, 24, 40, 80, 160, 400, 2928):
        windows = disjoint_windows(ct, k)
        row = [f"{k}"]
        true = score_sigmas(
            powers(g), np.array([sigma]), windows, logf, sum_windows=True
        )[0]
        row.append(f"{true:.3f}")
        for swaps in (1, 2, 4, 8):
            keys = np.array(
                [repeated(swap_two, sigma, swaps, rng) for _ in range(DRAWS)]
            )
            row.append(
                cell(score_sigmas(powers(g), keys, windows, logf, sum_windows=True))
            )
        for conj in (1, 2, 4):
            scores = [
                score_sigmas(
                    powers(repeated(conjugate_swap, g, conj, rng)),
                    np.array([sigma]),
                    windows,
                    logf,
                    sum_windows=True,
                )[0]
                for _ in range(DRAWS)
            ]
            row.append(cell(scores))
        keys = np.array([rng.sample(range(M), M) for _ in range(DRAWS)])
        row.append(cell(score_sigmas(powers(g), keys, windows, logf, sum_windows=True)))
        print("".join(f"{c:>13}" for c in row), flush=True)


if __name__ == "__main__":
    main()
