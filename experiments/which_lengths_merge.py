# ABOUTME: Pins which unit lengths the body's merging acts on, with a parametric null for
# ABOUTME: each rule that carries the 723-word reference's own sampling error.
"""Absorbing short units explains the block lengths. Which units?

`block-lengths-have-a-hole-at-two.md`, after its retraction, leaves one mechanism
standing: about 40% of 2-rune units are joined to the unit before them. That is
consistent with the length marginal at P = 0.79 and with the serial order at 1.2 sigma.

A rule that acts on length 2 and not on length 1 is a strange rule. A rule that acts on
everything short is an ordinary one -- in runeglish, two runes or fewer is almost exactly
the function-word class: THE, TO, OF, IS, BE, WE, HE, A, I, AN, OR, DO. So the question
is where the boundary sits, and it is answerable.

Each candidate is scored against its OWN parametric null: let that rule be true, draw a
723-word reference and a 2,928-block body from it, fit and score. Comparing raw chi2
across rules would not be fair, since the rules differ in how much they move the
distribution.

    python which_lengths_merge.py [--draws 60]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import lp_words  # noqa: E402
from lp_plaintext_register import word_lengths  # noqa: E402
from reference_noise_in_length_tests import CAP, GRID, histogram  # noqa: E402


def absorber(targets: set[int]):
    """Join a unit of one of these lengths to the one before it, with probability q."""

    def rule(lengths, q: float, rng):
        out = []
        for length in lengths:
            if length in targets and out and rng.random() < q:
                out[-1] += length
            else:
                out.append(length)
        return out

    return rule


def fit(reference, rule, target_hist, n_target, reps: int = 25, seed: int = 0):
    best, best_q = float("inf"), None
    for q in GRID:
        h, n = np.zeros(CAP), 0
        for t in range(reps):
            m = rule(reference, float(q), random.Random(seed * 997 + t))
            h += histogram(m)
            n += len(m)
        e = h / n * n_target
        c = float((((target_hist - e) ** 2) / np.maximum(e, 1e-9)).sum())
        if c < best:
            best, best_q = c, float(q)
    return best, best_q


def main() -> None:
    draws = 60
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    author = word_lengths()
    body = histogram([len(w) for w in lp_words()])
    n_body = int(body.sum())
    rng = random.Random(9)

    print(f"{'rule':<26}{'best q':>8}{'chi2':>8}{'null, rule true':>22}{'P':>7}")
    for name, targets in (
        ("absorb length 2", {2}),
        ("absorb length 1 or 2", {1, 2}),
        ("absorb length 1", {1}),
        ("absorb length 3", {3}),
        ("absorb length 3 or less", {1, 2, 3}),
    ):
        rule = absorber(targets)
        obs, q = fit(author, rule, body, n_body)
        nulls = []
        for b in range(draws):
            ref = [author[rng.randrange(len(author))] for _ in range(len(author))]
            pool = [author[rng.randrange(len(author))] for _ in range(6000)]
            synth = histogram(rule(pool, q, random.Random(b))[:n_body])
            c, _ = fit(ref, rule, synth, int(synth.sum()), reps=6, seed=b)
            nulls.append(c)
        n = np.array(nulls)
        print(
            f"{name:<26}{q:>8.2f}{obs:>8.1f}"
            f"{f'{n.mean():.1f} +- {n.std():.1f}':>22}{(n >= obs).mean():>7.2f}"
        )

    print(
        "\nThe boundary sits between 2 and 3. Absorbing units of two runes, or of one or"
        "\ntwo, both fit; absorbing three-rune units is dead, and absorbing only one-rune"
        "\nunits is rejected too. The one- and two-rune versions cannot be separated --"
        "\nthe author's 723 words hold only 29 of length one."
    )

    rule = absorber({2})
    qs = np.linspace(0.05, 1.0, 39)
    scores = []
    for q in qs:
        h, n = np.zeros(CAP), 0
        for t in range(40):
            m = rule(author, float(q), random.Random(991 + t))
            h += histogram(m)
            n += len(m)
        e = h / n * n_body
        scores.append(float((((body - e) ** 2) / np.maximum(e, 1e-9)).sum()))
    scores = np.array(scores)
    band = qs[scores <= scores.min() + 34]  # the null spread, from the table above
    frac2 = sum(1 for x in author if x == 2) / len(author)
    print(
        f"\nbest q {qs[int(scores.argmin())]:.2f}; within the null's own spread the "
        f"rate is indistinguishable over q in [{band.min():.2f}, {band.max():.2f}]\n"
    )
    print(f"{'q':>6}{'plaintext words':>18}{'joined to a neighbour':>24}")
    for q in (band.min(), float(qs[int(scores.argmin())]), band.max()):
        words = n_body / (1 - q * frac2)
        print(f"{q:>6.2f}{words:>18,.0f}{words - n_body:>24,.0f}")
    print(
        "\nSo the body's plaintext held somewhere near 3,100 to 3,300 words, of which"
        "\n170 to 400 were written joined to their neighbour. That is a prediction a"
        "\nsolved body page would test directly."
    )


if __name__ == "__main__":
    main()
