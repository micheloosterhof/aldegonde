# ABOUTME: Verifies the base-reuse floor that several results take on trust, and finds it
# ABOUTME: conservative by an order of magnitude.
"""The >= 300 base floor is cited but was never calibrated. It is far too modest.

`rotor-machine-compact-state.md` lists the ">= 300-base floor of
two-rune-depth-no-base-reuse.md" under *taken on trust, not verified here* -- and it is
what makes "a single rotor's 29 alphabets is too few" bite. So it is worth pinning.

The statistic is the one that file defines. Two 2-rune blocks agree at BOTH positions
either by coincidence or because they carry the same plaintext AND the same base. Measured
against the baseline that the two positions agree independently, the excess is

    P(same plaintext 2-rune word)  x  P(same base)  x  pairs

and P(same base) is 1/N for a pool of N bases. The plaintext rate is measured on the LP's
own words rather than assumed: 0.1006, from 116 two-rune words of which 20 are distinct.

Planted pools calibrate the conversion, which matters because the baseline uses the
OBSERVED marginals and so partly absorbs the effect it is testing.

One correction worth recording: a pool of N *shifts* is not a pool of N bases. Shifts
collapse mod 29, so a shift schedule has at most 29 effective states however many
nominal ones it has -- the first version of this control varied N up to 3,000 and got the
same answer every time.

    python base_pool_floor.py [--draws 15]
"""

from __future__ import annotations

import collections
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

M = 29


def two_rune_blocks(stream: list[int], wid: list[int]) -> list[tuple[int, int]]:
    blocks, cur = [], []
    for i, v in enumerate(stream):
        if i and wid[i] != wid[i - 1]:
            blocks.append(cur)
            cur = []
        cur.append(v)
    blocks.append(cur)
    return [tuple(b) for b in blocks if len(b) == 2]


def excess(two: list[tuple[int, int]]) -> tuple[float, int, int]:
    """(excess of joint agreement over the independent baseline, joint count, pairs)."""
    n = len(two)
    both = a0 = a1 = total = 0
    for i in range(n):
        for j in range(i + 1, n):
            x = two[i][0] == two[j][0]
            y = two[i][1] == two[j][1]
            total += 1
            a0 += x
            a1 += y
            both += x and y
    baseline = (a0 / total) * (a1 / total) * total
    return both - baseline, both, total


def planted(pool_size: int, words, rng: random.Random, count: int) -> list[tuple[int, int]]:
    pool = []
    for _ in range(pool_size):
        p = list(range(M))
        rng.shuffle(p)
        pool.append(p)
    out = []
    for _ in range(count):
        w = rng.choice(words)
        b = rng.choice(pool)
        out.append((b[w[0]], b[(w[1] + 7) % M]))
    return out


def main() -> None:
    draws = 15
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    stream, wid = load_clean()
    two = two_rune_blocks(stream, wid)
    e, both, total = excess(two)
    se = math.sqrt(both) if both else 1.0
    print(f"body: {len(two)} two-rune blocks, {total:,} pairs")
    print(f"  agreeing at both positions: {both}, baseline {both - e:.1f}")
    print(f"  excess {e:+.1f} +- {se:.1f}, 95% upper bound {e + 1.645 * se:+.1f}\n")

    words = [w for w in corpus() if len(w) == 2]
    c = collections.Counter(tuple(w) for w in words)
    n = len(words)
    rate = sum(v * (v - 1) // 2 for v in c.values()) / (n * (n - 1) // 2)
    print(f"LP plaintext: {n} two-rune words, {len(c)} distinct, "
          f"P(two identical) = {rate:.4f}")
    print(f"so a pool of N bases predicts an excess of {rate * total:.0f}/N\n")

    rng = random.Random(5)
    print(f"{'pool N':>8}{'median':>10}{'10th':>9}{'90th':>9}{'predicted':>12}")
    for pool in (29, 100, 300, 1000, 2928):
        vals = sorted(excess(planted(pool, words, rng, len(two)))[0] for _ in range(draws))
        print(f"{pool:>8}{statistics.median(vals):>10.1f}{vals[max(0, draws // 10)]:>9.1f}"
              f"{vals[-1 - draws // 10]:>9.1f}{rate * total / pool:>12.1f}")
    print(
        "\nThe body sits below the 10th percentile of every pool, including one as large"
        "\nas the block count itself. The measurement is consistent with the base being"
        "\ndistinct for every block, and a pool of 300 -- the floor cited on trust -- is"
        "\nexcluded by an order of magnitude."
    )


if __name__ == "__main__":
    main()
