# ABOUTME: Reads the d5 leak deficit as a clock-perturbation rate and compares it with the
# ABOUTME: rate the doublet suppression independently implies.
"""Two anomalies, one possible cause, and whether the numbers agree.

Under a letter step of order 5, positions five apart inside a block share an alphabet
EXACTLY, so `c[j] == c[j+5]` should reproduce the plaintext's own d5 coincidence in full.
It does not: the body reads 1.427 against a plaintext reference near 1.6.

That deficit has a natural reading. If the clock is perturbed at rate q -- a dodge, a
preventer, any rule that skips or repeats a step -- a d5 pair survives intact only when no
perturbation falls between its members, with probability (1-q)^5. So

    phi5 = (observed d5 excess) / (plaintext d5 excess) = (1 - q)^5

and the deficit becomes a measurement of q.

The doublet suppression measures q independently. `quagmire-dodge.md` has the dodge
failing exactly when the schedule offset is zero, one time in five, so the emitted doublet
rate is one fifth of the would-be rate and the dodge fires on the other four fifths.

If both anomalies come from one mechanism the two q's must agree. This checks.

    python d5_deficit_as_perturbation.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

M = 29
PROSE_D5 = 1.595  # d5-partial-alphabet-leak.md, runeglish prose, validated at z = +0.18


def within(stream: list[int], wid: list[int], lag: int) -> tuple[float, int]:
    hits = pairs = 0
    for i in range(len(stream) - lag):
        if wid[i] == wid[i + lag]:
            pairs += 1
            hits += stream[i] == stream[i + lag]
    return hits / pairs * M, pairs


def plain(lag: int) -> tuple[float, int]:
    hits = pairs = 0
    for w in corpus():
        for i in range(len(w) - lag):
            pairs += 1
            hits += w[i] == w[i + lag]
    return hits / pairs * M, pairs


def se(rate: float, pairs: int) -> float:
    p = rate / M
    return math.sqrt(p * (1 - p) / pairs) * M


def main() -> None:
    stream, wid = load_clean()
    d1, _n1 = within(stream, wid, 1)
    d5, n5 = within(stream, wid, 5)
    pd5, pn5 = plain(5)
    s5, sp5 = se(d5, n5), se(pd5, pn5)
    print(f"body    within-block d1 {d1:.4f}, d5 {d5:.4f} +- {s5:.4f} on {n5:,} pairs")
    print(
        f"plaintext references for d5: LP's own {pd5:.4f} +- {sp5:.4f} ({pn5} pairs),"
        f" prose {PROSE_D5:.4f}\n"
    )

    print(f"{'reference':<16}{'phi5':>18}{'implied q':>20}")
    for label, ref, ref_se in (("LP plaintext", pd5, sp5), ("prose", PROSE_D5, 0.0)):
        phi = (d5 - 1) / (ref - 1)
        rel = math.sqrt(
            (s5 / (d5 - 1)) ** 2 + ((ref_se / (ref - 1)) ** 2 if ref_se else 0)
        )
        lo, hi = max(1e-6, phi * (1 - rel)), min(1.0, phi * (1 + rel))
        print(
            f"{label:<16}{phi:>8.3f} +-{phi * rel:<7.3f}"
            f"{1 - hi**0.2:>9.4f} to {1 - lo**0.2:<8.4f}"
        )

    fires = d1 / M * 5 * 0.8
    print(f"\nthe dodge's own rate, from the doublet suppression: q = {fires:.4f}")
    print(
        "  (emitted doublet rate is 1/5 of the would-be rate; the dodge fires on 4/5)\n"
    )

    print(
        "what each q predicts for the body's d5, against the observed"
        f" {d5:.4f} +- {s5:.4f}:"
    )
    for label, q in (
        ("no perturbation", 0.0),
        ("the dodge's rate", fires),
        ("the d5 point estimate", 1 - ((d5 - 1) / (pd5 - 1)) ** 0.2),
    ):
        for rlabel, ref in (("LP", pd5), ("prose", PROSE_D5)):
            pred = 1 + (1 - q) ** 5 * (ref - 1)
            print(
                f"  {label:<22} vs {rlabel:<6} predicts {pred:.4f},"
                f" z = {(d5 - pred) / s5:+.2f}"
            )
    print(
        "\nThe d5 deficit disfavours NO perturbation at 1.2 to 1.7 sigma and is"
        "\nconsistent with the dodge's 0.025. It cannot separate 0.025 from 0.085: the"
        "\nplaintext reference rests on 261 pairs and the body's d5 on 2,073, so phi5"
        "\ncarries a 30-55% relative error and q inherits it fivefold amplified."
    )


if __name__ == "__main__":
    main()
