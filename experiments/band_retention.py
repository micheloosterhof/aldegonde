# ABOUTME: Measures how often the dodge sweep's d1/d4/d6 schedule bands keep a TRUE key,
# ABOUTME: calibrating the bands on each planted key's own ciphertext as well as on the LP.
"""Does the filter the sweep runs in front of its scorer keep the key it is looking for?

`zero_offset_census.dodge_filter_full` bands three predicted rates before any key is
scored. A band that rejects true keys costs the sweep its answer no matter how good the
scorer is, and this project has already been bitten twice by a search that could not
have found what it was looking for -- once by an invalid DJU-BEI gate, once by a scorer
that assumed clock = position.

Two retention numbers, because they answer different questions:

  self-calibrated   the bands are derived from the PLANTED key's own ciphertext, by the
                    same Wilson-plus-dilution pipeline the sweep uses on the LP. This is
                    an invariant: a filter that cannot keep a key when calibrated on
                    that key's own output is broken outright, whatever the LP looks like.
  LP-calibrated     the bands are the ones the sweep actually uses. This is the retention
                    the sweep really gets, and it also asks whether keys of this family
                    reproduce the LP's rates at all.

    python band_retention.py --trials 200
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_phase_test import encipher  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from pure_quagmire_restart import matched_register, schedule  # noqa: E402
from quagmire_runner import build_register, build_setup, load_register  # noqa: E402
from quagmire_schedule_census import (  # noqa: E402
    delta_vectors,
    lp_words,
    observed_rates,
    wilson,
)
from zero_offset_census import PROSE_CACHE, diluted_band  # noqa: E402

M = 29
TRIALS = 200


def predicted(K, offsets, tables) -> tuple[float, float, float]:
    """The three rates the filter compares against its bands, for one schedule.

    Mirrors `dodge_filter_full`: the d1 term is the pooled diagonal at the offset
    sitting one phase before the zero, divided by five; d4 and d6 are the per-phase
    sums the period-5 schedule reduces them to.
    """
    T1, T4, T6 = tables
    z = offsets.index(0)
    pooled = delta_vectors(K, T1, -1).sum(axis=0)
    r1 = pooled[offsets[(z + 4) % 5]] / 5
    v4 = delta_vectors(K, T4, 1)
    v6 = delta_vectors(K, T6, -1)
    r4 = sum(v4[k][offsets[k]] for k in range(5))
    r6 = sum(v6[k][offsets[(k + 1) % 5]] for k in range(5))
    return float(r1), float(r4), float(r6)


def bands_from(words) -> tuple[tuple[float, float], ...]:
    """The sweep's own band pipeline, applied to whatever corpus it is handed."""
    obs = observed_rates(words)
    return (
        wilson(*obs[1]),
        diluted_band(*wilson(*obs[4]), 4),
        diluted_band(*wilson(*obs[6]), 6),
    )


def main() -> None:
    trials = TRIALS
    for i, a in enumerate(sys.argv):
        if a == "--trials" and i + 1 < len(sys.argv):
            trials = int(sys.argv[i + 1])

    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]

    _words, _v, T1, lo1, hi1, _s = build_setup(PROSE_CACHE, lens, vocab=["the"])
    _T1, T4, T6, _cross = build_register(PROSE_CACHE, lens)
    tables = (T1, T4, T6)
    lp_bands = ((lo1, hi1), *bands_from(lp_words())[1:])
    pools, _t, _f = load_register(PROSE_CACHE)

    print(f"{len(lens):,} words, {sum(lens):,} runes; {trials} planted keys\n")
    print("bands the sweep uses, from the LP:")
    for name, (lo, hi) in zip(("d1", "d4", "d6"), lp_bands):
        edge = " (upper edge is chance)" if abs(hi - 1 / M) < 5e-4 else ""
        print(f"   {name}  {lo:.5f} .. {hi:.5f}{edge}")
    print(f"   chance {1 / M:.5f}\n")

    rng = random.Random(3301)
    keep_self = np.zeros((trials, 3), dtype=bool)
    keep_lp = np.zeros((trials, 3), dtype=bool)
    rates = np.zeros((trials, 3))
    for t in range(trials):
        K = rng.sample(range(M), M)
        offsets = schedule(rng)
        dials = (rng.randrange(M), rng.randrange(M))
        cipher = encipher(
            matched_register(rng, lens, pools), K, offsets, dials, 0, "advance"
        )
        r = predicted(K, offsets, tables)
        rates[t] = r
        self_bands = bands_from(cipher)
        for j in range(3):
            keep_self[t, j] = self_bands[j][0] <= r[j] <= self_bands[j][1]
            keep_lp[t, j] = lp_bands[j][0] <= r[j] <= lp_bands[j][1]

    print(f"{'band':<8}{'self-calibrated':>18}{'LP-calibrated':>16}")
    for j, name in enumerate(("d1", "d4", "d6")):
        print(f"{name:<8}{keep_self[:, j].mean():>17.1%}{keep_lp[:, j].mean():>16.1%}")
    for label, sl in (("d1+d4", slice(0, 2)), ("all three", slice(0, 3))):
        print(
            f"{label:<8}{keep_self[:, sl].all(axis=1).mean():>17.1%}"
            f"{keep_lp[:, sl].all(axis=1).mean():>16.1%}"
        )

    print(f"\npredicted rates of the planted schedules (chance {1 / M:.5f}):")
    for j, name in enumerate(("d1", "d4", "d6")):
        col = rates[:, j]
        print(
            f"   {name}  mean {col.mean():.5f}  sd {col.std():.5f}  "
            f"min {col.min():.5f}  max {col.max():.5f}"
        )
    above = (rates[:, 2] > lp_bands[2][1]).mean()
    print(
        f"\nd6: {above:.0%} of true schedules predict a rate ABOVE the LP band's "
        f"upper edge,\nwhich sits at chance -- the band asks a true key to be "
        f"at or below chance at d6."
    )
    cost(tables, lp_bands, keep_lp)


def survivors(K, tables, bands, use) -> int:
    """Schedules kept when only the bands in `use` are applied.

    Same construction as `zero_offset_census.dodge_filter_full`, with each band
    switchable so the sweep's cost can be priced against its retention.
    """
    T1, T4, T6 = tables
    (lo1, hi1), (lo4, hi4), (lo6, hi6) = bands
    pooled = delta_vectors(K, T1, -1).sum(axis=0)
    inband = np.ones(M, dtype=bool)
    inband[0] = False
    if 1 in use:
        for d in range(1, M):
            inband[d] = lo1 <= pooled[d] / 5 <= hi1
    if not inband.any():
        return 0
    v4 = delta_vectors(K, T4, 1)
    v6 = delta_vectors(K, T6, -1)
    r = np.arange(M, dtype=np.int64)
    a, b, c = r[:, None, None], r[None, :, None], r[None, None, :]
    total = 0
    for z in range(5):
        slots = [(z + 1) % 5, (z + 2) % 5, (z + 3) % 5, (z + 4) % 5]
        pinned = (-(a + b + c)) % M
        offs = {z: 0, slots[0]: a, slots[1]: b, slots[2]: c, slots[3]: pinned}
        keep = (a != 0) & (b != 0) & (c != 0) & inband[pinned]
        if 4 in use:
            rate4 = sum(v4[k][offs[k]] for k in range(5))
            keep = keep & (rate4 >= lo4) & (rate4 <= hi4)
        if 6 in use:
            rate6 = sum(v6[k][offs[(k + 1) % 5]] for k in range(5))
            keep = keep & (rate6 >= lo6) & (rate6 <= hi6)
        total += int(np.count_nonzero(keep))
    return total


def cost(tables, bands, keep_lp, sample: int = 40) -> None:
    """Keys to score, and keys to score per true key actually retained.

    A tighter band cuts the first number and the second is what matters: a filter
    that halves the work and thirds the retention has made the sweep worse.
    """
    from keyword_exhaustion import alphabets, kw_runes  # noqa: PLC0415
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415

    keys = []
    for word in priority_vocabulary():
        seq = kw_runes(word)
        if seq:
            keys.extend(K for _name, K in alphabets(seq))
    step = max(1, len(keys) // sample)
    picked = keys[::step][:sample]
    rate = 5001  # dodge_score_kernel.c, keys/s/core

    print(f"\n\ncost, over {len(keys):,} keyed alphabets ({len(picked)} censused)")
    print(
        f"{'filter':<14}{'scheds/alph':>13}{'keys':>11}{'core-h':>9}{'keep':>8}{'core-h/key found':>19}"
    )
    for label, use in (
        ("no bands", set()),
        ("d1 only", {1}),
        ("d1+d4", {1, 4}),
        ("d1+d4+d6", {1, 4, 6}),
    ):
        mean = float(np.mean([survivors(K, tables, bands, use) for K in picked]))
        total = mean * len(keys) * M
        hours = total / rate / 3600
        kept = (
            1.0
            if not use
            else keep_lp[:, 0].mean()
            if use == {1}
            else keep_lp[:, 0:2].all(axis=1).mean()
            if use == {1, 4}
            else keep_lp.all(axis=1).mean()
        )
        print(
            f"{label:<14}{mean:>13,.0f}{total:>11.1e}{hours:>9,.0f}"
            f"{kept:>8.1%}{hours / max(kept, 1e-9):>19,.0f}"
        )


if __name__ == "__main__":
    main()
