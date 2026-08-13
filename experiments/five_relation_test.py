# ABOUTME: Shows the five adjacent-alphabet relations must be IDENTICAL, which pins
# ABOUTME: the mechanism to a single designed order-5 g rather than any schedule.
"""Phase-flat doublets force ONE relation, not five.

Any cipher with five alphabets in rotation, A_0..A_4, has five adjacent relations

    R_j = A_j^-1 A_{j+1}        and closure forces R_0 R_1 R_2 R_3 R_4 = identity

A ciphertext doublet at within-word phase j requires p_j = R_j(p_{j+1}), so each
phase carries its OWN doublet rate, set by that relation's diagonal. Two readings
differ sharply:

  SINGLE g   A_j = base o g^j, so every R_j = g. All five rates are equal.
  SCHEDULE   five free relations. Closure leaves four tunable and forces the fifth
             as the inverse of the others' product, with an UNTUNED diagonal ~1/29.
             That phase must then show a ~5x higher doublet rate.

Measured (within-word pairs, phase = position mod 5):

    phase   pairs   doublets    rate
      0      3408       18     0.528%
      1      2711       22     0.812%
      2      1822        9     0.494%
      3      1228        8     0.651%
      4       859        6     0.698%

The five rates are equal: chi2 = 2.59 on 4 df, p ~ 0.63. And every placement of an
untuned step is excluded, because it would predict 30-118 doublets in that phase
against 6-22 observed:

    untuned phase    predicted    observed      z
        0               118          18      -9.2
        1                93          22      -7.4
        2                63           9      -6.8
        3                42           8      -5.3
        4                30           6      -4.3

So the flatness is not a mild preference. It REQUIRES all five adjacent relations
to share one low diagonal, which is exactly what a single order-5 g provides and
what no multi-step schedule can, since closure always leaves one step untuned.

This generalises the repo's existing use of mod-5 uniformity, which excluded
zero-offset schedules specifically (`stay-slot-hold.md`, the 2.28M rejected in
`quagmire_schedule_census.py`): the argument applies to ANY schedule whose five
relations differ, not only to those containing an identity step.

Combined with two facts already established, the mechanism class is pinned hard:

  - order 5 on 29 points forces cycle type 5^5 1^4, and all such permutations are
    CONJUGATE, so there is no algebraic subfamily to enumerate -- every
    "construction" is just a parameterisation of the conjugating permutation. That
    is why keyword grids and the magic square buy nothing.
  - no affine map on 29 symbols has order 5, since 5 does not divide
    |AGL(1,29)| = 812. Five does divide |GF(29^2)*| = 840 (a DIGRAPH unit, which
    flat parity at periods 2-6 disfavours), |Z/31*| = 30 (needs 31 symbols), and
    |Z/11*| = 10 (many-to-one, so not invertible).

What remains is a single designed order-5 permutation applied per letter -- and
"designed" is the operative word: the diagonal must be built against a digraph
table, though not minimised (0.0063 against an order-5 floor near 0.0027, so
~2.3x above it, mildly rare rather than optimal).
"""

from __future__ import annotations

import sys
from collections import Counter
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import load_words  # noqa: E402

M = 29
CHANCE = 1 / M


def phase_counts(words: list[list[int]]) -> tuple[Counter[int], Counter[int]]:
    """Within-word adjacent pairs and doublets, by position mod 5."""
    pairs: Counter[int] = Counter()
    hits: Counter[int] = Counter()
    for w in words:
        for k in range(len(w) - 1):
            pairs[k % 5] += 1
            if w[k] == w[k + 1]:
                hits[k % 5] += 1
    return pairs, hits


def main() -> None:
    words = load_words()
    pairs, hits = phase_counts(words)
    total_p = sum(pairs.values())
    total_h = sum(hits.values())
    rate = total_h / total_p

    print("Five alphabets in rotation give five adjacent relations R_j, and")
    print("closure forces R_0..R_4 to compose to the identity. A doublet at phase j")
    print("needs p_j = R_j(p_j+1), so each phase carries its own rate.\n")
    print(f"{'phase':>6}{'pairs':>8}{'doublets':>10}{'rate':>9}")
    for j in range(5):
        print(f"{j:>6}{pairs[j]:>8}{hits[j]:>10}{100 * hits[j] / pairs[j]:>8.3f}%")
    chi = sum((hits[j] - pairs[j] * rate) ** 2 / (pairs[j] * rate) for j in range(5))
    print(f"\nequal-rate fit: chi2 = {chi:.2f} on 4 df -- the five rates ARE equal")

    print("\nA schedule's closure constraint forces one relation untuned (~1/29).")
    print(f"{'untuned phase':>14}{'predicted':>11}{'observed':>10}{'z':>8}")
    worst = 0.0
    for j in range(5):
        pred = pairs[j] * CHANCE
        z = (hits[j] - pred) / sqrt(pred)
        worst = min(worst, z)
        print(f"{j:>14}{pred:>11.0f}{hits[j]:>10}{z:>+8.1f}")
    print(
        f"\nEvery placement excluded, worst {worst:+.1f} sigma. So all five relations"
    )
    print("share ONE low diagonal: a single order-5 g, not a schedule.")


if __name__ == "__main__":
    main()
