# ABOUTME: Reframes phi5 as a key-free check on the walk's clock; the length-resolved
# ABOUTME: test intended to separate scribal merging from register has no power.
"""Does the enciphering clock match the visible word boundaries?

Every key search in this repo steps the base alphabet once per visible word:
`base_{w+1} = base_w . g^((L_w - 1) mod 5) . sigma`. If the composer enciphered
using FINER units than we see -- because a scribe wrote two words joined -- then
two steps happened where we model one, and every search has been driving a wrong
clock. Nothing about a verified transcription settles this: the transcription can
faithfully record a join the scribe made.

The distance-5 cell tests it without a key. Under the walk

    c_j = c_{j+5}  <=>  p_j = p_{j+5}     iff both runes are in the same TRUE word

because the phase (j mod 5) is equal at j and j+5 wherever the word starts, so
base_w cancels -- but only one base_w is involved. A pair straddling a join sees
two different bases and goes flat at 1/29. So

    phi5 = (LP - flat) / (plaintext - flat) = fraction of pairs inside one true word

and the three candidate causes of the 2-rune deficit split cleanly:

    register             units ARE words        phi5 = 1     clock right
    compositional merge  joined before cipher   phi5 = 1     clock right
    scribal merge        joined after cipher    phi5 < 1     CLOCK WRONG

This is what phi5 measures. `d5-partial-alphabet-leak.md` frames it as whether the
base drifts within a word, which is a different question and not the load-bearing
one.

Two tests here:

  1. the count, which `d5-partial-alphabet-leak.md` already shows is underpowered
     (102 events); reported for completeness with the merge model's prediction
  2. phi5 RESOLVED BY UNIT LENGTH. The intent was a test with power the count
     lacks: scribal merging should concentrate in long units, so phi5 should
     DECLINE with length while register predicts it flat.

     **That intent fails, and the failure is the result.** A merged unit's own
     straddle fraction FALLS with length -- a 2+k join puts the seam at position
     2, so only 2 of the L-5 distance-5 pairs cross it -- and that cancels the
     rising chance that a long unit contains a join at all. The merge model
     therefore predicts phi5 flat in length too (0.83 to 0.90 across L = 6..12),
     which is what register predicts. Measured slope +0.011 +- 0.137 (z = +0.08):
     consistent with both, discriminating between neither.
"""

from __future__ import annotations

import random
from collections import Counter

from experiments.d5_straddle_prediction import merge_tagged, straddle_and_rate
from experiments.d5_unit_model import dict_words, prose_words, tuned_q
from experiments.walk_verifier import load_words

M = 29
FLAT = 1.0 / M
SEED = 3301


def d5_by_length(units: list[list[int]]) -> dict[int, tuple[int, int]]:
    """Distance-5 matches and pairs, bucketed by unit length."""
    out: dict[int, tuple[int, int]] = {}
    for u in units:
        if len(u) < 6:
            continue
        m = sum(u[i] == u[i + 5] for i in range(len(u) - 5))
        k, n = out.get(len(u), (0, 0))
        out[len(u)] = (k + m, n + len(u) - 5)
    return out


def main() -> None:
    lp = load_words()
    lp_hist = Counter(len(w) for w in lp)
    lp_share = 100 * lp_hist[2] / len(lp)

    ref_pool = [w for ws in dict_words().values() for w in ws]
    lp_d5 = d5_by_length(lp)
    ref_d5 = d5_by_length(ref_pool)

    tot_k = sum(k for k, _ in lp_d5.values())
    tot_n = sum(n for _, n in lp_d5.values())
    print(f"LP within-unit d5: {tot_k}/{tot_n} = {tot_k / tot_n:.4f}")
    print("phi5 = (LP - 1/29) / (plaintext - 1/29), the fraction of distance-5")
    print("pairs that sit inside a single true word.\n")

    words = prose_words()
    q = tuned_q(words, lp_share, SEED)
    merged = merge_tagged(words, q, random.Random(SEED))
    s5, _, _ = straddle_and_rate(merged, 5)
    print(f"scribal-merge model at the 2-rune-fixed rate q = {q:.3f}:")
    print(
        f"   predicts phi5 = 1 - s5 = {1 - s5:.2f}  (uniform over lengths? no -- see below)\n"
    )

    print("phi5 resolved by visible unit length")
    print(
        f"{'len':>5}{'LP k/n':>12}{'LP rate':>10}{'ref rate':>10}{'phi5':>8}{'+-':>7}{'units':>8}"
    )
    rows = []
    for L in sorted(lp_d5):
        k, n = lp_d5[L]
        if L not in ref_d5 or n < 40:
            continue
        rk, rn = ref_d5[L]
        r_ref = rk / rn
        if r_ref <= FLAT:
            continue
        rate = k / n
        se = (max(rate, 1 / n) * (1 - rate) / n) ** 0.5
        p = (rate - FLAT) / (r_ref - FLAT)
        pe = se / (r_ref - FLAT)
        rows.append((L, p, pe, n))
        print(
            f"{L:>5}{f'{k}/{n}':>12}{rate:>10.4f}{r_ref:>10.4f}"
            f"{p:>8.2f}{pe:>7.2f}{lp_hist[L]:>8}"
        )

    print("\nwhat the merge model predicts for this table:")
    mt = merge_tagged(words, q, random.Random(SEED))
    by_len: dict[int, list] = {}
    for u in mt:
        by_len.setdefault(len(u), []).append(u)
    print(f"{'len':>5}{'straddle':>11}{'predicted phi5':>17}")
    for L, _, _, _ in rows:
        pool = by_len.get(L, [])
        if not pool:
            continue
        st = tot = 0
        for u in pool:
            for i in range(len(u) - 5):
                tot += 1
                st += u[i][1] != u[i + 5][1]
        if tot:
            print(f"{L:>5}{st / tot:>11.3f}{1 - st / tot:>17.2f}")

    print("\nThe discriminating question is the SLOPE, not the level:")
    print("  register / compositional merge -> phi5 flat in length")
    print("  scribal merge                  -> phi5 falls as length grows")

    if len(rows) >= 3:
        xs = [r[0] for r in rows]
        ys = [r[1] for r in rows]
        ws = [1 / r[2] ** 2 for r in rows]
        sw = sum(ws)
        mx = sum(w * x for w, x in zip(ws, xs)) / sw
        my = sum(w * y for w, y in zip(ws, ys)) / sw
        sxx = sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
        sxy = sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys))
        slope = sxy / sxx
        slope_se = (1 / sxx) ** 0.5
        print(
            f"\n  weighted slope of phi5 vs unit length: {slope:+.4f} +- {slope_se:.4f}"
            f"  ->  z = {slope / slope_se:+.2f}"
        )
        print("  (negative and significant would mean the clock is wrong)")


if __name__ == "__main__":
    main()
