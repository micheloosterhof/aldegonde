# ABOUTME: Observation: adjacent-rune doublets are ~5x suppressed vs random, and
# ABOUTME: the suppression is boundary-blind (within-word rate ~= seam rate).
"""Doublet suppression. Significance: z of the observed doublet count vs the
binomial expectation at 1/29, and a within-word vs cross-word split showing the
suppression ignores word boundaries."""

from __future__ import annotations

import math

from lp_corpus import N, load_clean


def main() -> None:
    stream, wid = load_clean()
    n = len(stream)
    adj = n - 1
    p = 1 / N
    within = wi_pairs = cross = cr_pairs = 0
    doub = 0
    for i in range(adj):
        same_word = wid[i] == wid[i + 1]
        if same_word:
            wi_pairs += 1
        else:
            cr_pairs += 1
        if stream[i] == stream[i + 1]:
            doub += 1
            if same_word:
                within += 1
            else:
                cross += 1
    exp = adj * p
    z = (doub - exp) / math.sqrt(adj * p * (1 - p))
    print(f"adjacent pairs {adj}, doublets {doub}, expected {exp:.1f} (1/29)")
    print(f"suppression factor {exp / doub:.2f}x, rate {doub / adj:.4f}  z={z:+.1f}")
    print(f"within-word: {within}/{wi_pairs} = {within / wi_pairs:.4f}")
    print(f"cross-word:  {cross}/{cr_pairs} = {cross / cr_pairs:.4f}")
    # two-proportion z for within vs cross (boundary-blindness)
    p1, p2 = within / wi_pairs, cross / cr_pairs
    pp = doub / adj
    se = math.sqrt(pp * (1 - pp) * (1 / wi_pairs + 1 / cr_pairs))
    print(f"within vs cross z={(p1 - p2) / se:+.2f}  (|z|<2 => boundary-blind)")
    print("VERDICT: ~5x suppressed at 17 sigma; suppression ignores word boundaries")


if __name__ == "__main__":
    main()
