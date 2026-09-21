# ABOUTME: Accounts for the corpus's 17 repeated words and 1 repeated phrase, subtracting
# ABOUTME: the chance floor and inverting each count into a base-pool size under two models.
"""Eleven of the seventeen repeated words are chance. The one repeated phrase is not.

`base_pool_thermometer.py` inverted the two word-repeat counts into a pool size and got
357 from `identical` against 2,928 from the two-rune depth floor, which went into the
specification as an unexplained tension. The inversion was wrong: it never subtracted
the rate at which a random rune stream produces repeated words of three runes, and at
three runes that rate is most of the count.

This redoes the accounting properly.

  1. The chance floor, from shuffling the corpus's own runes inside its own word shapes.
     Nothing about the cipher survives that; word lengths and rune frequencies do.

  2. The plaintext repeat supply, measured on the LP's own plaintext rather than on
     prose, and scaled to 2,928 words by the empirically measured growth exponent
     rather than by assuming a square.

  3. The inversion, under two models that differ in what a repeated PHRASE costs:

       chain   base_w = base_v makes base_(w+1) = base_(v+1) whenever the clock phases
               agree, so a phrase repeat costs one pool draw and one phase in five
       free    the second alphabet has to coincide on its own, so a phrase repeat costs
               two independent pool draws

     Each model must give the same pool from both counts. One of them does.

  4. A key-free check that needs no register at all: shuffle the ORDER of the corpus's
     own ciphertext words. Every word survives intact, so all seventeen repeats are
     held fixed and only adjacency is destroyed.

    python word_repeat_accounting.py [--draws 400]
"""

from __future__ import annotations

import collections
import importlib.util
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import recurrence_counts  # noqa: E402
from fingerprint_battery import lp_words, prose_corpora  # noqa: E402

BLOCKS = 2928


def supplies(words) -> tuple[int, int]:
    """(repeated word pairs of >=3 runes, repeated two-word phrase pairs of >=6)."""
    c = collections.Counter(tuple(w) for w in words if len(w) >= 3)
    p = collections.Counter(
        (tuple(a), tuple(b)) for a, b in zip(words, words[1:]) if len(a) + len(b) >= 6
    )
    pairs = lambda d: sum(n * (n - 1) // 2 for n in d.values())  # noqa: E731
    return pairs(c), pairs(p)


def lp_plaintext() -> list[list[int]]:
    spec = importlib.util.spec_from_file_location(
        "lp_plaintext_register", ROOT / "experiments" / "lp_plaintext_register.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.corpus()


def growth_exponents(draws: int = 25) -> tuple[float, float]:
    """How each supply grows with corpus size, measured rather than assumed.

    Both are sub-quadratic because a longer corpus also has more distinct types, so
    scaling a 486-word register to 2,928 words by (2928/486)^2 overstates it.
    """
    small = [supplies(p[:486]) for p in prose_corpora(BLOCKS, draws)]
    big = [supplies(p) for p in prose_corpora(BLOCKS, draws)]
    out = []
    for j in range(2):
        a = float(np.mean([s[j] for s in small]))
        b = float(np.mean([s[j] for s in big]))
        out.append(math.log(b / a) / math.log(BLOCKS / 486))
    return out[0], out[1]


def main() -> None:
    draws = 400
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = lp_words()
    obs = recurrence_counts(lp)
    print(f"corpus: identical {obs['identical']}, long {obs['long']}, "
          f"returns {obs['returns']}\n")

    # 1. the chance floor
    stream = [r for w in lp for r in w]
    rng = random.Random(2)
    floors: dict[str, list[float]] = {"identical": [], "long": [], "returns": []}
    for _ in range(draws):
        s = stream[:]
        rng.shuffle(s)
        it = iter(s)
        shuffled = [[next(it) for _ in w] for w in lp]
        got = recurrence_counts(shuffled)
        for k in floors:
            floors[k].append(got[k])
    print(f"chance floor, {draws} rune shuffles inside the corpus's own word shapes:")
    for k in floors:
        v = np.array(floors[k], float)
        print(f"  {k:<11}{v.mean():>8.2f} +- {v.std():>5.2f}   corpus {obs[k]:>3}"
              f"   excess {obs[k] - v.mean():>+7.2f}")
    fl = np.array(floors["identical"], float)
    excess, se = obs["identical"] - fl.mean(), fl.std()
    print(f"\nSo {fl.mean():.0f} of the {obs['identical']} repeated words are chance. The "
          f"excess is {excess:.1f} +- {se:.1f}, z = {excess / se:+.2f}:")
    print("`identical` is a weak pool estimator, and a lower bound on the pool at best.")

    # 2. the supplies, in both registers
    ei, ep = growth_exponents()
    plain = lp_plaintext()
    f = BLOCKS / len(plain)
    lp_i, lp_p = supplies(plain)
    prose = [supplies(p) for p in prose_corpora(BLOCKS, 40)]
    pr_i = float(np.mean([s[0] for s in prose]))
    pr_p = float(np.mean([s[1] for s in prose]))
    print(f"\nplaintext repeat supply per {BLOCKS:,} words "
          f"(growth exponents {ei:.2f} and {ep:.2f}, measured):")
    print(f"  prose            words {pr_i:>9,.0f}   phrases {pr_p:>7,.0f}")
    print(f"  LP own register  words {lp_i * f**ei:>9,.0f}   phrases "
          f"{lp_p * f**ep:>7,.0f}   (from {lp_i} and {lp_p} in {len(plain)} words)")
    print("The LP's own plaintext repeats whole phrases about seven times as often as")
    print("prose does, which is the register effect every earlier estimate missed.")

    # 3. the inversion
    print("\npool size implied by each count, chance floor removed:")
    print(f"{'register':<18}{'from identical':>18}{'returns: chain':>17}"
          f"{'returns: free':>16}")
    for name, si, sp in (
        ("prose", pr_i, pr_p),
        ("LP own register", lp_i * f**ei, lp_p * f**ep),
    ):
        pool_i = si / excess
        pool_chain = sp / 5 / max(obs["returns"], 1)
        pool_free = math.sqrt(sp / max(obs["returns"], 1))
        print(f"{name:<18}{pool_i:>18,.0f}{pool_chain:>17,.0f}{pool_free:>16,.0f}")
        # a single count of 1 has an exact Poisson 95% interval of [0.0253, 3.689]
        lo_n, hi_n = 0.0253, 3.689
        print(f"{'  95% interval':<18}{'':>18}"
              f"{f'[{sp / 5 / hi_n:,.0f}, {sp / 5 / lo_n:,.0f}]':>17}"
              f"{f'[{math.sqrt(sp / hi_n):,.0f}, {math.sqrt(sp / lo_n):,.0f}]':>16}")
    print(
        "\nA model is consistent when both counts give the same pool. On the LP's own"
        "\nregister the chain does, within a factor of four and well inside the interval"
        "\nof a single observed event. The free model is out by more than an order of"
        "\nmagnitude, because it has to buy the phrase repeat twice."
    )

    # 4. the key-free check
    rng = random.Random(5)
    hits = []
    for _ in range(20000):
        s = lp[:]
        rng.shuffle(s)
        hits.append(recurrence_counts(s)["returns"])
    h = np.array(hits, float)
    print(f"\nword-order shuffle, 20,000 draws: every word intact, all "
          f"{obs['identical']} repeats held fixed,")
    print(f"only adjacency destroyed.  returns mean {h.mean():.4f}, "
          f"P(>=1) = {(h >= 1).mean():.5f}")
    print(
        "\nGiven exactly the repeated words the corpus has, two of them landing adjacent"
        "\nin the same order happens once in twenty thousand shuffles. That needs no"
        "\nregister, no simulated cipher and no key."
    )


if __name__ == "__main__":
    main()
