# ABOUTME: Turns the body's d5 shortfall into a bound on how often the cipher's clock is
# ABOUTME: perturbed, and shows the channel is exhausted at about two sigma.
"""`g` has order 5, so a clean walk puts the body's d5 at the plaintext's d5 exactly.

Within a block the base is fixed and `g^5` is the identity, so two runes five apart are
enciphered by the same alphabet and coincide at the plaintext rate. That makes d5 the one
key-free window onto the plaintext (`period5-is-confirmed`), and it makes any SHORTFALL a
measurement of how often the clock is perturbed.

A rule that advances the clock an extra step on a would-be repeat breaks that alignment.
A lag-5 pair survives only if no perturbation falls in the five positions between, so

    d5_body = A * d5_plain + (1 - A) / 29,     A = (1 - q)^5

with `q` the per-position perturbation rate. Inverting gives `q` from three measured
numbers and nothing else -- no key, no model fit.

The clock-dodge family predicts `q` equal to the would-be doublet rate, about 1/29 =
0.0345, because that is when it fires. So the question is whether the measured `q` is
near 0.035 or far above it.

`register_is_bigger.py` sharpened the plaintext side: d5 is measured on words long enough
to have a lag-5 pair, and the sixteen-page register has 382 of them against the old 261.
Prose supplies a far more precise estimate and the two agree, so both are reported.

    python d5_attenuation_bound.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import lp_words, prose_corpora  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

M = 29
CHANCE = 1 / M


def profile(words, lag: int) -> tuple[float, float, int]:
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - lag):
            pairs += 1
            hits += w[i] == w[i + lag]
    if not pairs:
        return float("nan"), float("nan"), 0
    rate = hits / pairs
    return rate, math.sqrt(rate * (1 - rate) / pairs), pairs


def main() -> None:
    lp = corpus(True)
    body = lp_words()
    prose = list(prose_corpora(2928, 40))

    print(
        "within-word coincidence, three corpora. Only lag 5 should leak under a walk"
        f" with g of order 5; chance is {CHANCE:.4f}.\n"
    )
    print(f"{'lag':>4}{'LP plaintext':>24}{'prose':>20}{'the body':>24}")
    prose_d5 = prose_se = 0.0
    for lag in range(1, 8):
        a, ase, ap = profile(lp, lag)
        hits = pairs = 0
        for c in prose:
            r, _, p = profile(c, lag)
            hits += r * p
            pairs += p
        b = hits / pairs
        bse = math.sqrt(b * (1 - b) / pairs)
        d, dse, dp = profile(body, lag)
        if lag == 5:
            prose_d5, prose_se = b, bse
        print(
            f"{lag:>4}{f'{a:.4f} +- {ase:.4f} ({ap})':>24}"
            f"{f'{b:.4f} +- {bse:.4f}':>20}"
            f"{f'{d:.4f} +- {dse:.4f} ({dp})':>24}"
        )

    lp_d5, lp_se, _ = profile(lp, 5)
    body_d5, body_se, body_pairs = profile(body, 5)
    diff = lp_d5 - prose_d5
    print(
        f"\nThe two plaintext estimates agree: {lp_d5:.4f} +- {lp_se:.4f} against "
        f"{prose_d5:.4f} +- {prose_se:.4f},"
    )
    print(
        f"a difference of {diff:+.4f} +- {math.sqrt(lp_se**2 + prose_se**2):.4f}. "
        f"Prose is used below for its precision."
    )

    print(f"\n{'quantity':<40}{'value':>12}{'error':>10}")
    print(f"{'plaintext d5 (prose)':<40}{prose_d5:>12.4f}{prose_se:>10.4f}")
    print(f"{'body d5':<40}{body_d5:>12.4f}{body_se:>10.4f} ({body_pairs:,} pairs)")
    shortfall = body_d5 - prose_d5
    se = math.sqrt(body_se**2 + prose_se**2)
    print(
        f"{'shortfall':<40}{shortfall:>+12.4f}{se:>10.4f}   z = {shortfall / se:+.2f}"
    )

    a_hat = (body_d5 - CHANCE) / (prose_d5 - CHANCE)
    a_se = math.sqrt(
        (body_se / (prose_d5 - CHANCE)) ** 2
        + (a_hat * prose_se / (prose_d5 - CHANCE)) ** 2
    )
    lo, hi = max(1e-6, a_hat - 1.96 * a_se), min(1.0, a_hat + 1.96 * a_se)
    print(
        f"\nfraction of lag-5 pairs still aligned: A = {a_hat:.3f} +- {a_se:.3f}, "
        f"95% [{lo:.3f}, {hi:.3f}]"
    )
    q = lambda A: 1 - A ** (1 / 5)  # noqa: E731
    print(
        f"perturbation rate q = 1 - A^(1/5):        {q(a_hat):.3f}, "
        f"95% [{q(hi):.3f}, {q(lo):.3f}]"
    )
    print(
        f"\nthe clock-dodge family predicts q = the would-be doublet rate = "
        f"{CHANCE:.3f}"
    )
    print(f"a clean walk with no perturbation predicts q = 0")

    print(
        "\nBoth sit inside the interval. The point estimate is about three times the"
        "\ndodge's rate and the shortfall is about two sigma, so the direction is right"
        "\nand the precision is not there."
        "\n\nThe channel is exhausted. The plaintext side is already at +- 0.0008 from"
        f"\nprose; the body side has {body_pairs:,} lag-5 pairs and cannot be enlarged,"
        "\nsince it is fixed by how many blocks run to six runes or more. Lag 10 leaks"
        "\ntoo -- g^10 is also the identity -- and would measure A directly as the ratio"
        "\nof excesses, but blocks of eleven runes or more supply too few pairs."
    )


if __name__ == "__main__":
    main()
