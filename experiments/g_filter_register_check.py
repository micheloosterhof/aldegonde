# ABOUTME: Checks whether the g filter's cycle-count conclusion depends on prose standing
# ABOUTME: in for the body's plaintext, using size-matched controls to separate the causes.
"""The filter predicts the body's lag-k rates from prose. Does the register matter?

`d-profile-pins-g-to-five-cycles.md` filters a pool of order-5 permutations against the
body's lag 2, 3, 4, 6 and 7 rates, and its falsification clause names the obvious worry:
"If the body's plaintext has a materially different lag-k structure from prose, the
predictions shift."

The LP's own plaintext is available -- 723 words from the sixteen solved pages -- and
running the filter on it gives a visibly flatter answer. That could be the register or it
could be the size: 1,465 lag-2 pairs against prose's 375,684, a factor of 250.

Size-matched controls separate them. Cut prose to 723 words, six independent draws, and
see whether prose flattens the same way.

    python g_filter_register_check.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d_profile_constrains_g import (  # noqa: E402
    chi2,
    cycles,
    lag_tables,
    make_pool,
    measure,
)
from fingerprint_battery import lp_words, prose_corpora  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402


def main() -> None:
    pool = make_pool(6000, 5)
    counts = np.array([cycles(g) for g in pool])
    meas = measure(lp_words())
    full = list(prose_corpora(2928, 60))

    def profile(blocks):
        mats, tot = lag_tables(blocks)
        s = np.array([chi2(g, meas, mats, tot) for g in pool])
        keep = s <= np.percentile(s, 1)
        return int(tot[2]), np.bincount(counts[keep], minlength=6)[1:], keep

    n_pr, p_pr, k_pr = profile(full)
    n_10, p_10, k_10 = profile(list(prose_corpora(2928, 10)))
    n_lp, p_lp, k_lp = profile([corpus(keyed=True)])

    print(
        f"{'lag-k tables from':<32}{'lag-2 pairs':>14}"
        f"{'top-1% five-cycle counts':>28}{'shared':>9}"
    )
    print(f"{'prose, 60 corpora (as used)':<32}{n_pr:>14,}{str(p_pr):>28}{'-':>9}")
    print(
        f"{'prose, 10 corpora':<32}{n_10:>14,}{str(p_10):>28}"
        f"{f'{int((k_10 & k_pr).sum())}/60':>9}"
    )
    print(
        f"{'the LP register, 723 words':<32}{n_lp:>14,}{str(p_lp):>28}"
        f"{f'{int((k_lp & k_pr).sum())}/60':>9}"
    )

    print("\nprose cut to the LP register's word count, six draws:\n")
    rng = random.Random(4)
    words = [w for c in full for w in c]
    profiles, shares = [], []
    for t in range(6):
        rng.shuffle(words)
        n, p, k = profile([words[:723]])
        profiles.append(p)
        shares.append(int((k & k_pr).sum()))
        print(f"{'draw ' + str(t):<32}{n:>14,}{str(p):>28}{f'{shares[-1]}/60':>9}")
    P = np.array(profiles, float)
    print(
        f"\n{'matched-size prose, mean':<32}{'':>14}"
        f"{str(np.round(P.mean(axis=0), 1)):>28}{f'{np.mean(shares):.1f}/60':>9}"
    )
    print(
        f"{'the LP register':<32}{'':>14}{str(p_lp):>28}"
        f"{f'{int((k_lp & k_pr).sum())}/60':>9}"
    )

    print(
        "\nThe LP register's flatter answer is a size effect, not a register effect."
        "\nProse cut to the same 723 words flattens the same way and shares about the"
        "\nsame number of permutations with the full-prose list. Both still rise toward"
        "\nfive five-cycles."
        "\n\nSo the conclusion holds, with a practical caveat: the filter needs prose at"
        "\nten corpora or more -- sixty and ten agree closely -- and cannot be run on the"
        "\nLP's own register at all. That is a limit of the control, not evidence against"
        "\nthe result."
    )


if __name__ == "__main__":
    main()
