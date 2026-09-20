# ABOUTME: Counts the keys a zero-offset sweep would have to test, the schedule half
# ABOUTME: every keyword sweep in this project excluded by construction.
"""How big is the search `quagmire-dodge.md` asks for?

`quagmire_runner.g_candidates` masks its schedules with `nz = r != 0`, requiring all
five offsets non-zero, and bands the SUM of the five phase contributions against the
observed distance-1 rate. Under the dodge model both choices are wrong: the schedule
needs exactly one zero offset, and the doublet rate comes from one phase, not five.

Work out what replaces the band. A surviving doublet at clock phase k needs two things:

    the skip fails:            offsets[(k+1) % 5] = 0,  so k = z-1
    the first emission repeated: pos(p_j) - pos(p_(j-1)) = -offsets[k]

The second is a plaintext distance-1 diagonal in K coordinates, and only one phase in
five is at k = z-1, so

    d1 = (1/5) x diagonal(-offsets[(z-1) % 5])

One offset is pinned by the observed rate; the zero is free to sit at any of the five
positions; the other three are unconstrained beyond summing to zero. The old filter
pinned the five jointly. That is the whole difference, and it decides whether the sweep
is affordable.

Run with no arguments; `--vocab N` to census more keyword alphabets.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from quagmire_runner import (  # noqa: E402
    PROSE_CACHE,
    build_register,
    build_setup,
    load_clean,
)
from quagmire_schedule_census import delta_vectors  # noqa: E402

M = 29
VOCAB_SAMPLE = 400


def nonzero_triples(target: int) -> int:
    """Three non-zero residues summing to `target` mod 29."""
    a = np.arange(1, M)
    pair = np.add.outer(a, a) % M
    rest = (target - pair) % M
    return int(np.count_nonzero(rest))


def old_filter(K, T1, lo1, hi1) -> int:
    """Schedules the existing sweep accepts: no zero offset, the five-phase sum in band."""
    v1 = delta_vectors(K, T1, -1)
    r = np.arange(M, dtype=np.int64)
    idx0 = (
        -(
            r[:, None, None, None]
            + r[None, :, None, None]
            + r[None, None, :, None]
            + r[None, None, None, :]
        )
    ) % M
    nz = r != 0
    keep = (
        nz[:, None, None, None]
        & nz[None, :, None, None]
        & nz[None, None, :, None]
        & nz[None, None, None, :]
        & (idx0 != 0)
    )
    rate = (
        v1[1][:, None, None, None]
        + v1[2][None, :, None, None]
        + v1[3][None, None, :, None]
        + v1[4][None, None, None, :]
        + v1[0][idx0]
    )
    return int(np.count_nonzero((rate >= lo1) & (rate <= hi1) & keep))


def dodge_filter(K, T1, lo1, hi1) -> int:
    """Schedules the dodge model admits: exactly one zero, one offset pinned by d1.

    The pinned offset sits at position z-1 for whichever position z holds the zero, and
    only its own phase contributes, so the band applies to a fifth of the pooled
    diagonal rather than to the five-phase sum.
    """
    pooled = delta_vectors(K, T1, -1).sum(axis=0)
    band = [
        d for d in range(1, M) if lo1 <= pooled[d] / 5 <= hi1
    ]  # offsets[z-1], non-zero or the schedule would hold two zeros
    return 5 * sum(nonzero_triples((-d) % M) for d in band)


def diluted_band(lo: float, hi: float, distance: int, skips=(0.02, 0.06)):
    """Widen a band on the corpus into the band the SCHEDULE's own rate must hit.

    Over `distance` clock steps the dodge inserts an extra step with probability q each
    time, and any insertion sends the relation to a different shift, which reads as
    chance. The observed rate is that mixture, so the schedule's own rate is further
    from chance than the corpus is. `skips` brackets q, which is key-dependent.
    """
    out_lo, out_hi = float("inf"), float("-inf")
    for q in skips:
        keep = (1 - q) ** distance
        out_lo = min(out_lo, (lo - (1 - keep) / M) / keep)
        out_hi = max(out_hi, (hi - (1 - keep) / M) / keep)
    return out_lo, out_hi


def dodge_filter_full(K, tables, bands) -> int:
    """The dodge filter with the distance-4 and distance-6 relations added.

    Under a period-5 schedule the five offsets sum to zero, so both distances reduce to
    one term per phase, the shape of constraint the old d1 band used:

        distance 4 at phase k:  shift -(S_(k+4) - S_k) = +offsets[k]
        distance 6 at phase k:  6 = 1 mod 5, so the shift is offsets[k+1]

    They are different functions of the same five offsets, so they constrain
    independently.
    """
    T1, T4, T6 = tables
    (lo1, hi1), (lo4, hi4), (lo6, hi6) = bands
    pooled = delta_vectors(K, T1, -1).sum(axis=0)
    v4 = delta_vectors(K, T4, 1)
    v6 = delta_vectors(K, T6, -1)
    inband = np.zeros(M, dtype=bool)
    for d in range(1, M):  # offsets[z-1], non-zero or the schedule holds two zeros
        inband[d] = lo1 <= pooled[d] / 5 <= hi1
    if not inband.any():
        return 0

    r = np.arange(M, dtype=np.int64)
    a, b, c = r[:, None, None], r[None, :, None], r[None, None, :]
    total = 0
    for z in range(5):
        slots = [(z + 1) % 5, (z + 2) % 5, (z + 3) % 5, (z + 4) % 5]
        pinned = (-(a + b + c)) % M  # the d1-pinned offset sits at (z-1) % 5 = slots[3]
        offs = {z: 0, slots[0]: a, slots[1]: b, slots[2]: c, slots[3]: pinned}
        keep = (a != 0) & (b != 0) & (c != 0) & inband[pinned]
        rate4 = sum(v4[k][offs[k]] for k in range(5))
        rate6 = sum(v6[k][offs[(k + 1) % 5]] for k in range(5))
        keep &= (rate4 >= lo4) & (rate4 <= hi4)
        keep &= (rate6 >= lo6) & (rate6 <= hi6)
        total += int(np.count_nonzero(keep))
    return total


def main() -> None:
    sample = VOCAB_SAMPLE
    for i, a in enumerate(sys.argv):
        if a == "--vocab" and i + 1 < len(sys.argv):
            sample = int(sys.argv[i + 1])

    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]

    from quagmire_schedule_census import lp_words, observed_rates, wilson

    _words, vocab, T1, lo1, hi1, _sigmas = build_setup(PROSE_CACHE, lens, vocab=["the"])
    _T1, T4, T6, _cross = build_register(PROSE_CACHE, lens)
    obs = observed_rates(lp_words())
    raw4, raw6 = wilson(*obs[4]), wilson(*obs[6])
    bands = ((lo1, hi1), diluted_band(*raw4, 4), diluted_band(*raw6, 6))
    print(f"chance is {1 / M:.5f}; bands on the corpus, then on the schedule itself")
    print(f"   d1 {lo1:.5f} - {hi1:.5f}")
    print(f"   d4 {raw4[0]:.5f} - {raw4[1]:.5f}   ->  {bands[1][0]:.5f} - {bands[1][1]:.5f}")
    print(f"   d6 {raw6[0]:.5f} - {raw6[1]:.5f}   ->  {bands[2][0]:.5f} - {bands[2][1]:.5f}")

    from keyword_exhaustion import DICT, alphabets, kw_runes

    if "--priority" in sys.argv:
        from quagmire_ungated_sweep import priority_vocabulary

        full = priority_vocabulary()
        print("\nvocabulary: 3301's own words, not the dictionary")
    else:
        full = []
        with open(DICT) as fh:
            for line in fh:
                x = line.strip()
                if 4 <= len(x) <= 12 and x.isalpha() and x.isascii():
                    full.append(x)
    keys = []
    for word in full:
        seq = kw_runes(word)
        if seq:
            keys.extend(K for _name, K in alphabets(seq))
    print(f"{len(full):,} keywords -> {len(keys):,} keyword alphabets\n")

    step = max(1, len(keys) // sample)
    picked = keys[::step][:sample]
    old = np.array([old_filter(K, T1, lo1, hi1) for K in picked], dtype=float)
    new = np.array([dodge_filter(K, T1, lo1, hi1) for K in picked], dtype=float)
    both = np.array(
        [dodge_filter_full(K, (T1, T4, T6), bands) for K in picked], dtype=float
    )
    rate = 45_000  # walk_score_kernel.c, keys/s/core
    disks = 369  # the seam band's sigma count: the existing sweep's 8.4e5 -> 3.1e8
    print(f"\ncensused {len(picked)} alphabets, {len(keys):,} in the vocabulary\n")
    print(f"{'filter':<40}{'per alphabet':>14}{'pairs':>15}{'keys':>13}{'core-h':>10}")
    for label, accepted in (
        ("existing sweep: no zero, five-phase d1", old),
        ("dodge: one zero, d1 pins one offset", new),
        ("dodge, plus the d4 and d6 sums", both),
    ):
        pairs = accepted.mean() * len(keys)
        full = pairs * disks
        print(
            f"{label:<40}{accepted.mean():>14,.1f}{pairs:>15,.0f}"
            f"{full:>13.2e}{full / rate / 3600:>10,.0f}"
        )
    print(f"\nkeys are pairs x {disks} sigma disks from the seam band, at {rate:,}/s/core.")
    del vocab


if __name__ == "__main__":
    main()
