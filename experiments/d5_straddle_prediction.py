# ABOUTME: Tests whether missing separators alone explain the d5 partial leak,
# ABOUTME: by predicting phi5 from the straddle fraction of the merge model.
"""Does the 2-rune deficit explain the d5 partial leak?

Two open problems in this repo have been treated separately:

  `two-rune-deficit.md`        visible units hold far fewer 2-rune words than any
                               reference (z = -10); merging is one candidate cause
  `d5-partial-alphabet-leak.md`  the within-word d5 cell delivers only ~60-70% of
                               the plaintext repeat rate, read there as the base
                               alphabet drifting WITHIN a word

They may be one problem. Under the walk `c_j = base_w(g^(j mod 5)(p_j))`, so for a
distance-5 pair

    c_j = c_{j+5}  <=>  p_j = p_{j+5}       ONLY IF both runes sit in the same
                                            true word, so that base_w cancels

The phase cancels wherever the word starts, so a misplaced boundary does not
matter -- but a MISSING one does. If two true words read as a single visible unit,
a distance-5 pair can straddle the join, and there the two bases differ and the
cell goes flat at 1/29.

That gives an exact prediction with no free parameter beyond the absorption rate
already fixed by the 2-rune share:

    phi5 = 1 - s5      s5 = fraction of within-unit distance-5 pairs that straddle

If s5 lands near the measured 1 - phi5, the partial leak needs no sub-word base
drift, and the walk's one-base-per-word assumption survives intact.

The script reports the full d1..d6 dilution profile too, because the same straddle
fraction dilutes every cell toward 1/29 and that changes what a candidate g is
required to reproduce.
"""

from __future__ import annotations

import random
from collections import Counter

from experiments.d5_unit_model import LP_COUNTS, prose_words, tuned_q
from experiments.walk_verifier import load_words

M = 29
FLAT = 1.0 / M
SEED = 3301
DMAX = 6


def merge_tagged(
    words: list[list[int]], q: float, rng: random.Random
) -> list[list[tuple[int, int]]]:
    """Merge short words into the preceding unit, tagging each rune's true word."""
    out: list[list[tuple[int, int]]] = []
    for wid, w in enumerate(words):
        tagged = [(r, wid) for r in w]
        if out and len(w) <= 2 and rng.random() < q:
            out[-1] = out[-1] + tagged
        else:
            out.append(tagged)
    return out


def straddle_and_rate(
    units: list[list[tuple[int, int]]], d: int
) -> tuple[float, float, int]:
    """Straddle fraction, within-true-word repeat rate, and event count at distance d."""
    straddle = total = 0
    hits = same = 0
    for u in units:
        for i in range(len(u) - d):
            (a, wa), (b, wb) = u[i], u[i + d]
            total += 1
            if wa != wb:
                straddle += 1
            else:
                same += 1
                hits += a == b
    return (
        straddle / total if total else 0.0,
        hits / same if same else 0.0,
        hits,
    )


def main() -> None:
    lp = load_words()
    lp_hist = Counter(len(w) for w in lp)
    lp_share = 100 * lp_hist[2] / len(lp)

    words = prose_words()
    q = tuned_q(words, lp_share, SEED)
    units = merge_tagged(words, q, random.Random(SEED))

    k, n = LP_COUNTS[5]
    obs5 = k / n
    se5 = (obs5 * (1 - obs5) / n) ** 0.5

    print(f"LP 2-rune share {lp_share:.1f}%  ->  absorption rate q = {q:.3f}")
    print("   (q is fixed by the 2-rune deficit alone; nothing here is fitted to d5)\n")

    s5, rp5, ev5 = straddle_and_rate(units, 5)
    pred5 = (1 - s5) * rp5 + s5 * FLAT

    print("the distance-5 cell, predicted with no free parameter:")
    print(f"   straddle fraction s5           {s5:.3f}")
    print(f"   within-true-word repeat r_p    {rp5:.4f}   ({ev5} events)")
    print(f"   predicted  (1-s5)*r_p + s5/29  {pred5:.4f}")
    print(f"   LP observed                    {obs5:.4f} +- {se5:.4f}")
    print(f"   z                              {(obs5 - pred5) / se5:+.2f}\n")

    print("read as a leak fraction, which is how the doc states it:")
    print(f"   merge model predicts phi5 = 1 - s5 = {1 - s5:.2f}")
    phi_obs = (obs5 - FLAT) / (rp5 - FLAT)
    phi_se = se5 / (rp5 - FLAT)
    print(f"   LP implies         phi5          = {phi_obs:.2f} +- {phi_se:.2f}")
    print(
        f"   the two agree to {abs(phi_obs - (1 - s5)) / phi_se:.2f} sigma"
        " of the LP's own binomial error\n"
    )

    print("full dilution profile -- the same straddle fraction hits every cell:")
    print(f"{'d':>3}{'straddle':>11}{'flat pull':>12}{'LP observed':>14}")
    for d in range(1, DMAX + 1):
        s, _, _ = straddle_and_rate(units, d)
        kk, nn = LP_COUNTS[d]
        print(f"{d:>3}{s:>11.3f}{s * FLAT:>12.4f}{kk / nn:>14.4f}")

    print("\nConsequence if this holds: the P_d tables every g-filter is scored")
    print("against are built from unmerged dictionary words, so each observed cell")
    print("is a blend of a g-diagonal and a flat component the filters do not model.")
    print("d1 is least affected (adjacent pairs rarely straddle), d6 most.")

    print("\nsensitivity -- q is pinned by the 2-rune share, but check the range:")
    for qq in (0.0, 0.15, q, 0.5, 0.75, 1.0):
        u = merge_tagged(words, qq, random.Random(SEED))
        s, rp, _ = straddle_and_rate(u, 5)
        pred = (1 - s) * rp + s * FLAT
        tag = "  <- fixed by the 2-rune share" if abs(qq - q) < 1e-9 else ""
        print(
            f"   q = {qq:.3f}  s5 = {s:.3f}  phi5 = {1 - s:.2f}"
            f"  predicts d5 {pred:.4f}  z = {(obs5 - pred) / se5:+.2f}{tag}"
        )


if __name__ == "__main__":
    main()
