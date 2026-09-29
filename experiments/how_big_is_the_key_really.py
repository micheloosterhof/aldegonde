# ABOUTME: Shows the 283-bit budget assumes free permutations, and costs the search under
# ABOUTME: the reading that the author built his key the way he built the solved pages'.
"""283 bits is the model's parameter space, not necessarily the key.

`the-bit-budget.md` totals the key at 283 bits -- g 79.7, sigma 101.8, base_0 101.8 --
and concludes no statistical route can close it. Every one of those three numbers is the
size of a FREE permutation space. A real key is rarely a free permutation, and this
author's demonstrably is not: the solved pages use DIVINITY and FIRFUMFERENFE, keywords
turned into mixed alphabets.

So the budget depends entirely on how the key was built, and the difference is enormous.

Three readings are costed. The middle one uses a structured `g` -- fix four runes and
step the other twenty-five by five in alphabet order, which is the obvious way to build
an order-5 permutation of 29 points by hand -- and the test below checks that such a `g`
is consistent with the body's coincidence profile.

    python how_big_is_the_key_really.py
"""

from __future__ import annotations

import collections
import itertools
import random
import sys
from math import comb, factorial, log2
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_constrains_g import chi2, lag_tables, measure  # noqa: E402
from fingerprint_battery import M, lp_words, prose_corpora  # noqa: E402


def structured_g(fixed) -> list[int]:
    """Fix these four runes; step the other twenty-five by five in alphabet order."""
    rest = [x for x in range(M) if x not in fixed]
    g = list(range(M))
    for i, x in enumerate(rest):
        g[x] = rest[(i + 5) % 25]
    return g


def main() -> None:
    prose = list(prose_corpora(2928, 60))
    mats, tot = lag_tables(prose)
    meas = measure(lp_words())

    combos = list(itertools.combinations(range(M), 4))
    structured = np.array([chi2(structured_g(f), meas, mats, tot) for f in combos])
    rng = random.Random(5)
    free = []
    for _ in range(len(combos)):
        pts = rng.sample(range(M), 25)
        g = list(range(M))
        for c in range(5):
            cycle = pts[5 * c : 5 * c + 5]
            for i in range(5):
                g[cycle[i]] = cycle[(i + 1) % 5]
        free.append(chi2(g, meas, mats, tot))
    free = np.array(free)

    print("is a structured g consistent with the body's coincidence profile?\n")
    print(f"{'pool':<36}{'n':>9}{'best':>9}{'1st pct':>10}{'median':>9}")
    for label, v in (
        ("structured: fix 4, step 25 by five", structured),
        ("free five-cycle permutations", free),
    ):
        print(
            f"{label:<36}{len(v):>9,}{v.min():>9.2f}"
            f"{np.percentile(v, 1):>10.2f}{np.median(v):>9.1f}"
        )
    print(
        "\nThe tails match, so the profile does not prefer either family. A structured"
        "\ng is consistent; it is not evidence FOR one, and the filter is worth 6.2"
        "\nbits on individuals rather than on populations."
    )

    vocab = collections.Counter()
    for c in prose:
        for w in c:
            vocab[tuple(w)] += 1
    keywords = sum(1 for w in vocab if len(set(w)) == len(w) and 3 <= len(w) <= 12)
    free_perm = log2(factorial(M) // 2)
    free_g = log2(
        sum(
            comb(M, 5 * k) * factorial(5 * k) // (5**k * factorial(k))
            for k in range(1, 6)
        )
    )
    struct = log2(comb(M, 4))
    kw = log2(keywords)

    print(
        f"\n\nkeyword supply: {len(vocab):,} prose word types, {keywords:,} with "
        f"all-distinct runes and 3-12 of them = {kw:.1f} bits\n"
    )
    print(
        f"{'how the key was built':<34}{'g':>8}{'sigma':>8}{'base':>8}"
        f"{'bits':>7}{'keys':>10}"
    )
    for label, a, b, c in (
        ("every part a free permutation", free_g, free_perm, free_perm),
        ("g structured, the rest free", struct, free_perm, free_perm),
        ("every part naturally built", struct, kw, kw),
    ):
        t = a + b + c
        print(
            f"{label:<34}{a:>8.1f}{b:>8.1f}{c:>8.1f}{t:>7.1f}{f'1e{t * 0.301:.0f}':>10}"
        )

    total = struct + kw + kw
    keys = 2**total
    pruned = 2 ** (total - 6.2)
    print(
        f"\nUnder the third reading the search is {total:.0f} bits, about "
        f"{keys:.1e} keys."
        f"\nThe d-profile filter is worth 6.2 bits on g and the cross-seam identity"
        f"\nverifies a (g, sigma) pair at no cost, which brings it to about {pruned:.1e}"
        "\nbefore any decryption is attempted. At the compiled scorer's 5,000 keys per"
        f"\nsecond that is roughly {pruned / 5000 / 3600:,.0f} core-hours -- the same order"
        "\nas the sweep already costed and parked."
        "\n\nFour things make that optimistic and are worth saying plainly. The structured"
        "\nfamily above is one invention and others exist. The keyword list is prose"
        "\nvocabulary; a dictionary is larger. The filter's pruning is unreliable -- three"
        "\nof six planted trials put the true g outside the top 2%. And the whole reading"
        "\nis a hypothesis, supported by the author's habits on the solved pages and by"
        "\nnothing in the body itself."
    )


if __name__ == "__main__":
    main()
