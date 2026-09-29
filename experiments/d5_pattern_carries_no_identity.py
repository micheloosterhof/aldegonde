# ABOUTME: Tests whether a block's lag-5 coincidence pattern identifies its plaintext word
# ABOUTME: or detects repeated words, and measures why it carries almost no information.
"""A repeated ciphertext word needs a base return. A repeated d5 PATTERN needs only a
repeated plaintext word -- which sounds far more sensitive. It is not.

Under the walk, `c[j] == c[j+5]` iff `p[j] == p[j+5]`, so the pattern of which lag-5
pairs coincide inside a block is a function of the plaintext word alone. Two blocks with
the same plaintext therefore share a pattern whatever their bases are. That would be a
key-free detector of repeated plaintext, sensitive where `identical` -- which needs the
bases to coincide too, about once in 2,700 -- is not.

Two things are measured here, and both say no.

  concentration  are blocks of the same length more likely to share a pattern than
                 prose words drawn to the same length profile?
  information    how many bits does a pattern carry, against how many are needed to
                 name a word of that length?

    python d5_pattern_carries_no_identity.py [--draws 300]
"""

from __future__ import annotations

import collections
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import lp_words, prose_corpora  # noqa: E402

MIN_LEN = 8


def pattern(w) -> tuple:
    return tuple(w[i] == w[i + 5] for i in range(len(w) - 5))


def concentration(blocks):
    """(same-length pairs, pairs sharing a pattern, the same among coincident blocks)."""
    by = collections.defaultdict(list)
    for w in blocks:
        if len(w) >= MIN_LEN:
            by[len(w)].append(pattern(w))
    total = same = live = live_same = 0
    for ps in by.values():
        c = collections.Counter(ps)
        total += len(ps) * (len(ps) - 1) // 2
        same += sum(v * (v - 1) // 2 for v in c.values())
        z = [p for p in ps if any(p)]
        cz = collections.Counter(z)
        live += len(z) * (len(z) - 1) // 2
        live_same += sum(v * (v - 1) // 2 for v in cz.values())
    return total, same, live, live_same, {k: len(v) for k, v in by.items()}


def main() -> None:
    draws = 300
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    body = lp_words()
    total, same, live, live_same, shape = concentration(body)
    long_blocks = [w for w in body if len(w) >= MIN_LEN]
    rate = sum(1 for w in long_blocks if any(pattern(w))) / len(long_blocks)

    prose = [w for c in prose_corpora(2928, 40) for w in c]
    by_len = collections.defaultdict(list)
    for w in prose:
        by_len[len(w)].append(w)

    rng = random.Random(7)
    S, LS, R = [], [], []
    for _ in range(draws):
        sample = []
        for length, n in shape.items():
            pool = by_len[length]
            if len(pool) < n:
                continue
            sample += [pool[rng.randrange(len(pool))] for _ in range(n)]
        _, s, _, ls, _ = concentration(sample)
        S.append(s)
        LS.append(ls)
        R.append(sum(1 for w in sample if any(pattern(w))) / len(sample))
    S, LS, R = (np.array(x, float) for x in (S, LS, R))

    print(
        f"blocks of {MIN_LEN}+ runes: {len(long_blocks)} in the body, "
        f"{total:,} same-length pairs\n"
    )
    print(f"{'statistic':<44}{'body':>9}{'prose, matched shape':>24}{'z':>8}")
    print(
        f"{'pairs sharing a pattern':<44}{same:>9,}"
        f"{f'{S.mean():.0f} +- {S.std():.0f}':>24}{(same - S.mean()) / S.std():>8.2f}"
    )
    print(
        f"{'  among blocks carrying a coincidence':<44}{live_same:>9,}"
        f"{f'{LS.mean():.1f} +- {LS.std():.1f}':>24}"
        f"{(live_same - LS.mean()) / LS.std():>8.2f}"
    )
    print(
        f"{'fraction of blocks with a coincidence':<44}{rate:>9.3f}"
        f"{f'{R.mean():.3f} +- {R.std():.3f}':>24}{(rate - R.mean()) / R.std():>8.2f}"
    )
    print(
        "\nThe first two point opposite ways at about two sigma, which is what happens"
        "\nwhen a statistic is driven by the coincidence RATE rather than by word"
        "\nidentity: a lower rate means more all-zero patterns, hence more matches among"
        "\nall blocks and fewer among the ones carrying a coincidence. The rate itself is"
        "\nthe d5 leak, already measured and bounded in D10."
    )

    print("\n\nwhy: how much does a pattern say about which word it is?\n")
    print(
        f"{'length':>7}{'prose words':>13}{'distinct':>11}{'pattern bits':>14}"
        f"{'words per pattern':>19}"
    )
    for length in range(6, 15):
        ws = by_len[length]
        if len(ws) < 200:
            continue
        pats = collections.Counter(pattern(w) for w in ws)
        n = sum(pats.values())
        bits = -sum(v / n * math.log2(v / n) for v in pats.values())
        types = len({tuple(w) for w in ws})
        print(
            f"{length:>7}{len(ws):>13,}{types:>11,}{bits:>14.2f}"
            f"{types / 2**bits:>19,.0f}"
        )
    print(
        "\nNaming a word of length ten takes about ten bits; the pattern supplies 1.6,"
        "\nleaving some 250 candidates. Even at length thirteen it supplies 2.4."
        "\n\nThe reason is that the pattern is nearly always all-zero: only 65 of the"
        f"\nbody's {len(long_blocks)} blocks of eight runes or more carry any coincidence"
        "\nat all. A detector whose output is one bit on a fifth of the data cannot tell"
        "\nwords apart, and the arithmetic says so before any test is run."
    )


if __name__ == "__main__":
    main()
