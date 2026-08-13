# ABOUTME: Puts an honest interval on the d5 leak fraction phi5, carrying both the
# ABOUTME: LP's binomial error and the spread across plaintext references.
"""Is phi5 < 1 -- i.e. does the base alphabet really drift WITHIN a word?

`d5-partial-alphabet-leak.md` reads the within-word d5 cell as a partial
same-alphabet leak and concludes the base is not constant across a word. That
conclusion would break the length-clocked walk, which assumes one base per word,
so it is worth knowing how firm the number is.

The leak fraction comes from a two-component mixture: a within-word 5-gap either
shares the alphabet (rate = the plaintext repeat rate r_p) or does not (rate =
1/29, flat).

    observed = phi5 * r_p + (1 - phi5) / 29
    phi5     = (observed - 1/29) / (r_p - 1/29)

Both inputs carry error. `observed` is 102 events -- a binomial error of ~10% on
the rate, which becomes ~33% on phi5 because the denominator is a small
difference of two similar numbers. And `r_p` is not measured but CHOSEN: three
scripts in this repo build the runeglish plaintext reference differently and
disagree by 11%, which moves phi5 by 30%.

This script reports phi5 under every reference available, including the solved LP
pages -- real plaintext in the book's own convention and the only reference with
the right register, at the cost of a small sample. The question is not what phi5
is but whether the interval excludes 1.0.
"""

from __future__ import annotations

import random
from collections import Counter

from experiments.d5_unit_model import (
    LP_COUNTS,
    dict_words,
    profile,
    prose_words,
)
from experiments.doublet_position_profile import solved_plain_words
from experiments.mechanism_discriminator import real_words
from experiments.walk_verifier import load_words

M = 29
FLAT = 1.0 / M
SEED = 3301
SCALE = 30


def weighted_d5(words: list[list[int]], target: Counter) -> tuple[float, int]:
    """Within-word d5 rate, each length weighted to the target histogram.

    Weighting rather than resampling: table noise from a drawn sample swings with
    the seed (`key-local-channel-is-empty.md`), so every word of a given length
    contributes with the same weight and the whole pool is used.
    """
    by_len: dict[int, list[list[int]]] = {}
    for w in words:
        by_len.setdefault(len(w), []).append(w)
    num = den = 0.0
    events = 0
    for length, count in target.items():
        pool = by_len.get(length)
        if not pool or length < 6:
            continue
        hits = tot = 0
        for w in pool:
            for i in range(len(w) - 5):
                tot += 1
                hits += w[i] == w[i + 5]
        if tot:
            wt = count / len(pool)
            num += wt * hits
            den += wt * tot
            events += hits
    return (num / den if den else 0.0), events


def phi(observed: float, r_p: float) -> float:
    return (observed - FLAT) / (r_p - FLAT)


def main() -> None:
    lp = load_words()
    lp_hist = Counter(len(w) for w in lp)
    k, n = LP_COUNTS[5]
    obs = k / n
    se = (obs * (1 - obs) / n) ** 0.5

    print(f"LP within-word d5: {k}/{n} = {obs:.4f} +- {se:.4f}   (flat = {FLAT:.4f})")
    print(f"excess over flat:  {obs - FLAT:.4f} +- {se:.4f}\n")

    rng = random.Random(SEED)
    solved = solved_plain_words()
    prose = prose_words()
    dict_pool = [w for ws in dict_words().values() for w in ws]

    refs: dict[str, tuple[float, str]] = {}

    r, ev = weighted_d5(solved, lp_hist)
    refs["solved LP pages"] = (r, f"{ev} events, right register, small n")

    r, ev = weighted_d5(dict_pool, lp_hist)
    refs["dictionary, weighted"] = (r, f"{ev} events, this file's converter")

    r, ev = weighted_d5(prose, lp_hist)
    refs["running prose, weighted"] = (r, f"{ev} events, P&P register")

    refs["mechanism_discriminator"] = (
        profile(real_words(rng))[5],
        "as used by d4_d6_prediction.py",
    )

    print(f"{'reference':>26}{'r_p':>9}{'phi5':>8}{'+- (binom)':>12}   note")
    lo_all, hi_all = [], []
    for name, (r_p, note) in refs.items():
        if r_p <= FLAT:
            print(f"{name:>26}{r_p:>9.4f}      --  reference at or below flat")
            continue
        p = phi(obs, r_p)
        pe = se / (r_p - FLAT)
        lo_all.append(p - pe)
        hi_all.append(p + pe)
        print(f"{name:>26}{r_p:>9.4f}{p:>8.2f}{pe:>12.2f}   {note}")

    print("\nphi5 across every reference:")
    print(f"   1 sigma: {min(lo_all):.2f} to {max(hi_all):.2f}")
    lo2 = min(lo - (hi - lo) / 2 for lo, hi in zip(lo_all, hi_all))
    hi2 = max(hi + (hi - lo) / 2 for lo, hi in zip(lo_all, hi_all))
    print(f"   2 sigma: {lo2:.2f} to {hi2:.2f}")
    print(
        f"   phi5 = 1.0 (one base per word) is {'OUTSIDE' if hi2 < 1.0 else 'INSIDE'}"
        " the 2-sigma interval"
    )
    print("   A 1-sigma bound short of 1.0 is not an exclusion; only the 2-sigma")
    print("   statement is, and it does not exclude.")

    print("\nWhat it would take to settle it: the denominator is r_p - 1/29, about")
    print("0.02, so phi5 inherits a ~50x magnification of every error in r_p. The")
    print("LP's 102 events alone give +-0.25. No amount of reference work fixes")
    print("that; only more ciphertext would, and there is no more ciphertext.")


if __name__ == "__main__":
    main()
