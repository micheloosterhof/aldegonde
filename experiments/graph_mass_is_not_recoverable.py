# ABOUTME: Shows g's bigram graph mass cannot be recovered from any available channel,
# ABOUTME: because it is entangled with the preventer's strength and nothing else sees it.
"""C-1's quantity is the one the preventer hides.

Constraint C-1 records that g's graph carries about 0.026 of the plaintext bigram mass.
It was read off the seam-to-within-word ratio, which
`one-parameter-fits-both-suppressions.md` dissolved, so the number is unsupported and the
question is whether anything else can supply it.

The quantity is

    m_1(g) = P(p_i = g(p_(i+1)))

the plaintext BIGRAM mass on g's graph -- how often the cipher would emit a repeat if it
had no preventer. The body's within-block d1 is that rate after suppression, so

    observed d1  =  f(m_1, phi)

which is one equation in two unknowns. Anything that pins either one frees the other.

Two candidates are tested and both fail.

The d-profile filter (`d-profile-pins-g-to-five-cycles.md`) constrains g through lags 2,
3, 4, 6 and 7. Lag 6 uses the SAME power of g as lag 1, so it looks like the obvious
route. It is not: the lag-1 and lag-6 plaintext tables are different objects -- English has
strong bigram structure and almost none at distance six -- so the two masses are functions
of g that barely correlate.

    python graph_mass_is_not_recoverable.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_constrains_g import (  # noqa: E402
    chi2,
    inverse,
    lag_tables,
    make_pool,
    measure,
)
from fingerprint_battery import M, lp_words, ppow, prose_corpora  # noqa: E402

LAGS = (1, 2, 3, 4, 6, 7)


def main() -> None:
    prose = list(prose_corpora(2928, 60))
    tables = {k: np.zeros((M, M)) for k in LAGS}
    for c in prose:
        for w in c:
            for k in LAGS:
                for i in range(len(w) - k):
                    tables[k][w[i], w[i + k]] += 1
    for k in LAGS:
        tables[k] /= tables[k].sum()

    pool = make_pool(4000, 5)

    def mass(g, k):
        back = inverse(ppow(g, k % 5))
        return sum(tables[k][x, back[x]] for x in range(M))

    values = {k: np.array([mass(g, k) for g in pool]) for k in LAGS}

    print("mass of the plaintext lag-k table on the graph of g^(k mod 5), "
          "over 4,000 g\n")
    print(f"{'lag':>4}{'g power':>9}{'mean':>10}{'sd':>9}{'corr with lag 1':>18}")
    for k in LAGS:
        r = float(np.corrcoef(values[1], values[k])[0, 1])
        print(f"{k:>4}{k % 5:>9}{values[k].mean():>10.4f}{values[k].std():>9.4f}"
              f"{r:>18.3f}")
    print(
        "\nLag 6 uses the same power of g as lag 1 and correlates with it at -0.13."
        "\nEnglish has strong bigram structure and almost none at distance six, so the"
        "\ntwo masses are near-independent functions of the same permutation."
    )

    mats, tot = lag_tables(prose)
    meas = measure(lp_words())
    scores = np.array([chi2(g, meas, mats, tot) for g in pool])
    hits = pairs = 0
    for w in lp_words():
        for i in range(len(w) - 1):
            pairs += 1
            hits += w[i] == w[i + 1]
    d1 = hits / pairs

    print(f"\n\nthe body's within-block d1 = {d1:.4f}\n")
    print(f"{'g population':<28}{'m_1 over that population':>28}")
    for label, keep in (
        ("all 4,000", np.ones(len(pool), bool)),
        ("top 5% by the d-profile", scores <= np.percentile(scores, 5)),
        ("top 1% by the d-profile", scores <= np.percentile(scores, 1)),
    ):
        v = values[1][keep]
        print(f"{label:<28}{f'{v.mean():.4f} +- {v.std():.4f}':>28}")
    print(
        "\nThe filter does not move it. The g it keeps have the same bigram graph mass"
        "\nas the ones it throws away, so C-1 cannot be recovered that way."
        "\n\nThat leaves one equation, observed d1 = f(m_1, phi), in two unknowns. The"
        "\nseam adds a second equation and a third unknown -- the cross-word mass on"
        "\ng^u o sigma o g^v -- so it does not close the system either."
        "\n\nC-1's 0.026 is withdrawn with no replacement. The one route left is the left"
        "\naction: if the base steps on the left the seam's un-suppressed rate averages"
        "\nover conjugates of a single step, which is nearly a constant rather than a free"
        "\nparameter, and the system would close. That depends on"
        "\n`the-base-step-may-act-on-the-left.md`, which is a lean at about two sigma."
    )


if __name__ == "__main__":
    main()
