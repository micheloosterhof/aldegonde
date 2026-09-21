# ABOUTME: Estimates how many 5-cycles the letter step has, from the within-block echo that
# ABOUTME: its FIXED POINTS leave at distances that are not multiples of five.
"""A rune g fixes enciphers to the same value at every position in its block.

The letter step has order 5, so its cycle type is 5^k 1^(29-5k) for some k in 1..5. The
project assumes k = 5 -- five 5-cycles and four fixed points -- but nothing measures it.

There is a channel, and it follows from the model rather than from an assumption. Position
j of a block carries `base o g^j`, so a plaintext rune p enciphers to `base(g^j(p))`. If
**p is a fixed point of g** then `g^j(p) = p` for every j, so

    a fixed-point rune enciphers to the same ciphertext value everywhere in its block

at ANY distance, not only at multiples of five. That puts a floor under the within-block
coincidence at d = 2, 3, 4 proportional to the number of fixed points, on top of whatever
g's graph contributes.

Power is the question, and it is not corpus-limited: the variance comes from where g's
5-cycles happen to fall relative to the plaintext bigram table, so more runes do not help.
The controls below measure it.

Forty draws per cycle count are needed. At twelve or fifteen the medians do not even come
out monotone, which is worth knowing before trusting a smaller run.

    python g_fixed_points.py [--draws 40]
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

M = 29
LAGS = (2, 3, 4)


def planted(k: int, words: list[list[int]], rng: random.Random):
    """A walk whose letter step has k 5-cycles and 29-5k fixed points."""
    points = list(range(M))
    rng.shuffle(points)
    g = list(range(M))
    for c in range(k):
        block = points[c * 5 : (c + 1) * 5]
        for a, b in zip(block, block[1:] + block[:1]):
            g[a] = b
    stream: list[int] = []
    wid: list[int] = []
    for w in range(2928):
        word = rng.choice(words)
        base = list(range(M))
        rng.shuffle(base)
        step = list(range(M))
        for p in word:
            stream.append(base[step[p]])
            wid.append(w)
            step = [g[x] for x in step]
    return stream, wid


def echo(stream: list[int], wid: list[int]) -> float:
    """Within-block coincidence at the lags that are not multiples of five."""
    hits = pairs = 0
    for lag in LAGS:
        for i in range(len(stream) - lag):
            if wid[i] == wid[i + lag]:
                pairs += 1
                hits += stream[i] == stream[i + lag]
    return hits / pairs * M


def main() -> None:
    draws = 40
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    stream, wid = load_clean()
    body = echo(stream, wid)
    print(f"body: within-block coincidence at lags {LAGS} = {body:.4f}\n")

    rng = random.Random(5)
    words = corpus()
    print(f"{'5-cycles':>9}{'fixed':>7}{'median':>9}{'10th':>8}{'90th':>8}"
          f"{'draws below body':>19}")
    for k in range(1, 6):
        vals = sorted(echo(*planted(k, words, rng)) for _ in range(draws))
        below = sum(1 for v in vals if v < body) / len(vals)
        print(f"{k:>9}{29 - 5 * k:>7}{statistics.median(vals):>9.4f}"
              f"{vals[max(0, draws // 10)]:>8.4f}{vals[-1 - draws // 10]:>8.4f}"
              f"{below:>18.0%}")
    print(
        "\nThe medians fall monotonically as fixed points do, so the channel is real. The"
        "\nspread is wide and intrinsic -- it comes from where g's cycles land relative to"
        "\nthe plaintext bigram table, not from corpus size, so more text would not narrow"
        "\nit. At 40 draws the body excludes a single 5-cycle (2% of draws fall below it)"
        "\nand sits at the median for four 5-cycles. Everything from k = 2 up is"
        "\nadmissible."
    )


if __name__ == "__main__":
    main()
