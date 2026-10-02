# ABOUTME: Follows the 361 suppressed doublets into the off-diagonal bigram table, which
# ABOUTME: bounds how many distinct substitutions a substituting preventer could be using.
"""The doublets that did not happen had to become something. What?

`survivors-use-every-rune.md` refutes a preventer with one fixed substitution tau: the
86 survivors use 28 of the 29 runes, which forces |fix(tau)| >= 28, while 81%
suppression forces about 5.6. That argument is about the doublets that SURVIVED.

This one is about the 361 that did not. Whatever the rule emitted instead, it landed
somewhere in the off-diagonal bigram table, and the shape of the landing separates the
families:

  one fixed tau      the mass lands in 29 cells, one per row, each gaining 361/29 = 12.4
                     on a base of 15.8 -- an eighty percent bump
  k substitutions    29k cells, each gaining 12.4/k
  rune-blind         the re-run emits whatever the schedule gives, so the mass spreads
                     over all 812 off-diagonal cells at 0.44 each, invisible

So the table measures k. A planted null does the arithmetic honestly: displace the same
361 from the diagonal into k random one-per-row targets and see what the off-diagonal
chi2 and the largest row maximum become.

    python where_the_doublets_went.py [--draws 500]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

from aldegonde import c3301  # noqa: E402

ENG = c3301.CICADA_ENGLISH_ALPHABET
M = 29


def table(stream) -> np.ndarray:
    big = np.zeros((M, M))
    for a, b in zip(stream, stream[1:]):
        big[a, b] += 1
    return big


def row_max_z(big_off: np.ndarray) -> float:
    """Largest standardised row maximum over the off-diagonal."""
    e = big_off.sum(axis=1) / (M - 1)
    return float(((big_off.max(axis=1) - e) / np.sqrt(e)).max())


def main() -> None:
    draws = 500
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    stream, _ = load_clean()
    n = len(stream)
    big = table(stream)
    off_full = np.array([np.delete(big[r], r) for r in range(M)])
    off = off_full.ravel()
    missing = int(round((n - 1) / M - np.diag(big).sum()))
    obs_chi = float((((off - off.mean()) ** 2) / off.mean()).sum())
    obs_rm = row_max_z(off_full)

    print(
        f"{n - 1:,} bigrams: diagonal {np.diag(big).sum():.0f} against "
        f"{(n - 1) / M:.0f} expected flat, so {missing} were displaced"
    )
    print(
        f"off-diagonal: {off.size} cells, mean {off.mean():.2f}, "
        f"sd {off.std():.2f}, max {off.max():.0f}"
    )
    print(
        f"  chi2 {obs_chi:.1f} on {off.size - 1} df, largest row-max z {obs_rm:.2f}\n"
    )

    strongest = sorted(
        (
            (
                np.delete(big[r], r).max(),
                ENG[r],
                ENG[
                    [c for c in range(M) if c != r][int(np.delete(big[r], r).argmax())]
                ],
            )
            for r in range(M)
        ),
        reverse=True,
    )[:5]
    print(
        "strongest off-diagonal cells: "
        + ", ".join(f"{r}->{c} {int(v)}" for v, r, c in strongest)
    )

    rng = np.random.default_rng(21)
    total = int(off.sum())
    print(f"\nplanting the {missing} displaced doublets into k targets, one per row:\n")
    print(f"{'k':>4}{'off-diagonal chi2':>26}{'largest row-max z':>26}{'verdict':>10}")
    for k in (0, 1, 2, 3, 4, 6, 8, 12):
        chis, rms = [], []
        flat = np.full(M * (M - 1), 1 / (M * (M - 1)))
        for _ in range(draws):
            spread = total - (missing if k else 0)
            base = rng.multinomial(spread, flat).reshape(M, M - 1).astype(float)
            for _t in range(k):
                targets = rng.integers(0, M - 1, size=M)
                base[np.arange(M), targets] += rng.multinomial(
                    missing // k, np.full(M, 1 / M)
                )
            chis.append(float((((base - base.mean()) ** 2) / base.mean()).sum()))
            rms.append(row_max_z(base))
        c, r = np.array(chis), np.array(rms)
        zc = (obs_chi - c.mean()) / c.std()
        zr = (obs_rm - r.mean()) / r.std()
        verdict = "EXCLUDED" if abs(zc) > 2 or abs(zr) > 2 else "open"
        label = "rune-blind" if k == 0 else str(k)
        print(
            f"{label:>4}{f'{c.mean():.0f} +- {c.std():.0f}   z {zc:+.1f}':>26}"
            f"{f'{r.mean():.2f} +- {r.std():.2f}   z {zr:+.1f}':>26}{verdict:>10}"
        )

    print(
        "\nThe corpus sits on the rune-blind row. One substitution is excluded at about"
        "\nz -5 on the chi2 and -3 on the row maximum; two at -2.3. Three or more is"
        "\nindistinguishable from spreading the mass everywhere, because 12.4 split three"
        "\nways is 4.1 on a base of 15.8 and the table is not that precise."
        "\n\nSo a substituting preventer is not refuted outright by this test, but it needs"
        "\nat least three distinct substitutions -- three more permutations of key doing"
        "\nwhat one clock re-run does for nothing. That is a parsimony argument, not a"
        "\nproof, and it should be quoted as one."
    )


if __name__ == "__main__":
    main()
