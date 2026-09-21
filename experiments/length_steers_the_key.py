# ABOUTME: Tests whether the block lengths were chosen to steer the key's g-exponents,
# ABOUTME: which would unify the two unexplained facts. They were not.
"""The two unexplained facts have an attractive common cause. It does not survive.

`what-any-solution-must-satisfy.md` now names two facts a solution has to explain rather
than merely satisfy:

    E1/E2   the block lengths are detached from everything
    D6      one state return, at the end of the body

One hypothesis covers both. Under the walk the base steps by `g^(a_w) o sigma` where the
exponent a_w = (cumulative runes - 1) mod 5 is fixed by the BLOCK LENGTHS. So an author
who chooses where the blocks break chooses the exponent sequence -- and an author who
chooses the exponent sequence can force the product back to the identity after 1,449
blocks. The lengths would be detached from the plaintext because they are attached to the
key, and the return would be what they were arranged for.

It predicts structure in the exponent sequence. There is none.

**The null matters more than the statistic here.** Exponents are a deterministic transform
of the lengths -- cumulative sums mod 5 -- so a null that shuffles the EXPONENTS destroys
the modular arithmetic along with the hypothesis, and reports the arithmetic as a finding:
the lag-1 autocorrelation is -0.164 against +0.019 for shuffled exponents, an apparent
-8.9 sigma. Shuffling the LENGTHS and recomputing gives -0.145 +- 0.014, and the same
observation is -1.4 sigma.

    python length_steers_the_key.py [--draws 200]
"""

from __future__ import annotations

import collections
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

GAP = (1477, 2926)  # block indices of the two DJU-BEI occurrences


def block_lengths() -> list[int]:
    stream, wid = load_clean()
    out, cur = [], 0
    for i in range(len(stream)):
        cur += 1
        if i + 1 >= len(stream) or wid[i + 1] != wid[i]:
            out.append(cur)
            cur = 0
    return out


def exponents(lengths: list[int]) -> list[int]:
    """The walk's g-exponent at each step: (cumulative runes - 1) mod 5."""
    cum, out = 0, []
    for x in lengths:
        cum += x
        out.append((cum - 1) % 5)
    return out


def acf(s: list[int], lag: int) -> float:
    m = statistics.mean(s)
    v = sum((x - m) ** 2 for x in s)
    return sum((s[i] - m) * (s[i + lag] - m) for i in range(len(s) - lag)) / v


def main() -> None:
    draws = 200
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lengths = block_lengths()
    exps = exponents(lengths)
    rng = random.Random(3)

    counts = collections.Counter(exps)
    expected = len(exps) / 5
    chi = sum((counts[k] - expected) ** 2 / expected for k in range(5))
    print(f"{len(lengths):,} blocks")
    print(f"exponent distribution {[counts[k] for k in range(5)]}, "
          f"chi2 {chi:.1f} on 4 df (5% crit 9.5)\n")

    print(f"{'lag':>4}{'observed':>11}{'null from shuffled LENGTHS':>30}{'z':>8}")
    for lag in (1, 2, 3, 5):
        null = []
        for _ in range(draws):
            t = lengths[:]
            rng.shuffle(t)
            null.append(acf(exponents(t), lag))
        mu, sd = statistics.mean(null), statistics.pstdev(null)
        print(f"{lag:>4}{acf(exps, lag):>+11.4f}{mu:>+18.4f} +-{sd:.4f}"
              f"{(acf(exps, lag) - mu) / sd:>+8.2f}")

    a, b = GAP
    obs = sum(exps[a:b]) % 5
    hits = 0
    for _ in range(2000):
        t = lengths[:]
        rng.shuffle(t)
        hits += sum(exponents(t)[a:b]) % 5 == 0
    print(f"\nsum of exponents over the {b - a} blocks between the occurrences: "
          f"mod 5 = {obs}")
    print(f"  shuffled-length corpora giving 0: {hits / 2000:.3f} (chance 0.200)")
    print(
        "\nNothing. The exponent marginal is uniform, the autocorrelation is the modular"
        "\narithmetic and not the text, and the sum over the gap lands on its chance rate."
        "\nThe block lengths were not chosen to steer the key, and the two unexplained"
        "\nfacts stay unconnected."
    )


if __name__ == "__main__":
    main()
