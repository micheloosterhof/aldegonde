#!/usr/bin/env python3
# ABOUTME: Counts, per keyword Quagmire alphabet, the 5-offset schedules whose
# ABOUTME: predicted d1 doublet rate is in the observed band, and scores each
# ABOUTME: surviving schedule on its exactly-computable d6/d4 predictions.
"""How big is the Quagmire key space really — and does d6 cut it?

The keyword exhaustion (`keyword_exhaustion.py`) selected alphabets by
their FLOOR — the cheapest single conjugated turn. A real schedule picks
five offsets d[0..4] with sum = 0 (mod 29), one per within-word phase, so
the object to count is (alphabet, schedule) pairs whose phase-weighted
predicted doublet rate lands inside the observed within-word band. That
count — not the 12,064 floor-passing alphabets — is the g-side size of
the enumerable key space (`mixed-alphabet-vigenere.md`).

Three predictions are exact per candidate, because under a period-5
schedule the relation at any within-word distance collapses to schedule
sums (5 consecutive offsets cancel):

  d1 pair (j-1, j):  doublet  iff  u[j] - u[j-1] = -d[j mod 5]
  d6 pair (j, j+6):  match    iff  u[j+6] - u[j] = -d[(j+1) mod 5]
  d4 pair (j, j+4):  match    iff  u[j+4] - u[j] = +d[j mod 5]

(u = K^-1(p); within one word the base cancels.) So the same offsets the
schedule spends dodging adjacent doublets are re-spent, on other tables,
at distances 6 and 4 — the d6 depth (0.0245, the corpus's one solid
below-background cell) and the d4 lean (0.0410) become FREE additional
filters on the enumeration, and this script measures how hard they bite.
Note d4 elevation is the schedule-zero signature: the 4-sum vanishes iff
the excluded offset is 0, i.e. one letter step is the identity.

Self-test: the analytic rates are validated against a direct simulation
of the Quagmire walk on the identical word sample (exact match expected,
same sums in different order).
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, prose_words  # noqa: E402
from keyword_exhaustion import DICT, alphabets, kw_runes  # noqa: E402
from lp_corpus import load_clean  # noqa: E402

M = 29
RNG = random.Random(3301)
SAMPLES = 30


def wilson(k: int, n: int) -> tuple[float, float]:
    """95% Wilson interval for a binomial proportion."""
    z = 1.959964
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def lp_words() -> list[list[int]]:
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    return [d[k] for k in sorted(d)]


def observed_rates(words: list[list[int]]) -> dict[int, tuple[int, int]]:
    """Within-word (matches, pairs) at distances 1, 4, 6."""
    out = {}
    for dist in (1, 4, 6):
        hits = pairs = 0
        for w in words:
            for j in range(len(w) - dist):
                pairs += 1
                hits += w[j] == w[j + dist]
        out[dist] = (hits, pairs)
    return out


def sample_register(
    lp_lens: list[int], pools: dict[int, list[list[int]]]
) -> list[list[int]]:
    """Register words matched to the LP length sequence (as in tables())."""
    words = []
    for L in lp_lens:
        LL = L
        while LL not in pools and max(pools) > LL:
            LL += 1
        words.append(RNG.choice(pools[LL])[:L])
    return words


def phase_tables(words: list[list[int]]):
    """Per-phase joint tables for the three distances, plus the seam table.

    T1[f][a][b]: pairs (j-1, j) with f = j mod 5 (f is the offset index
    the pair's doublet condition selects).  T6[f]: pairs (j, j+6) with
    f = (j+1) mod 5.  T4[f]: pairs (j, j+4) with f = j mod 5.  Each is
    normalized by its own total pair count.  cross[a][b]: word-final x
    word-initial pairs (the seam table for sigma).
    """
    T1 = np.zeros((5, M, M))
    T4 = np.zeros((5, M, M))
    T6 = np.zeros((5, M, M))
    cross = np.zeros((M, M))
    for i, w in enumerate(words):
        for j in range(1, len(w)):
            T1[j % 5][w[j - 1]][w[j]] += 1
        for j in range(len(w) - 4):
            T4[j % 5][w[j]][w[j + 4]] += 1
        for j in range(len(w) - 6):
            T6[(j + 1) % 5][w[j]][w[j + 6]] += 1
        if i + 1 < len(words):
            cross[w[-1]][words[i + 1][0]] += 1
    return T1 / T1.sum(), T4 / T4.sum(), T6 / T6.sum(), cross / cross.sum()


def constrained_floor(v: np.ndarray) -> float:
    """Exact minimum of sum_f v[f][d_f] subject to sum d_f = 0 (mod 29).

    DP over the running offset sum; replaces the optimistic unconstrained
    per-phase floor as the grid prefilter.
    """
    idx = (np.arange(M)[:, None] - np.arange(M)[None, :]) % M
    best = v[1].copy()
    for f in (2, 3, 4):
        best = np.min(best[idx] + v[f][None, :], axis=1)
    return float((best[(-np.arange(M)) % M] + v[0]).min())


def delta_vectors(K: list[int], T: np.ndarray, sign: int) -> np.ndarray:
    """v[f][d] = predicted rate contribution of choosing offset d at phase f.

    For each phase table T[f], bins the mass by the K-transformed delta
    pos(b) - pos(a), then maps offset d to the delta the condition selects
    (-d for the d1/d6 conditions, +d for d4).
    """
    pos = np.empty(M, dtype=np.int64)
    pos[np.array(K)] = np.arange(M)
    D = (pos[None, :] - pos[:, None]) % M  # delta of pair (a, b)
    v = np.empty((5, M))
    for f in range(5):
        q = np.bincount(D.ravel(), weights=T[f].ravel(), minlength=M)
        v[f] = q[(sign * np.arange(M)) % M]
    return v


def simulate(
    K: list[int], sched: list[int], words: list[list[int]]
) -> dict[int, float]:
    """Direct Quagmire-walk within-word coincidence rates (base cancels)."""
    pos = {r: i for i, r in enumerate(K)}
    out = {}
    cts = {1: [0, 0], 4: [0, 0], 6: [0, 0]}
    nmax = max(len(w) for w in words)
    s = np.cumsum([0] + [sched[j % 5] for j in range(1, nmax + 1)])
    for w in words:
        c = [K[(pos[r] + s[j]) % M] for j, r in enumerate(w)]
        for dist in (1, 4, 6):
            for j in range(len(c) - dist):
                cts[dist][1] += 1
                cts[dist][0] += c[j] == c[j + dist]
    for dist in (1, 4, 6):
        out[dist] = cts[dist][0] / cts[dist][1]
    return out


def self_test(T1, T4, T6, words) -> None:
    K = list(range(M))
    RNG.shuffle(K)
    sched = [RNG.randrange(M) for _ in range(4)]
    sched.append((-sum(sched)) % M)
    v1 = delta_vectors(K, T1, -1)
    v4 = delta_vectors(K, T4, +1)
    v6 = delta_vectors(K, T6, -1)
    pred = {
        1: sum(v1[f][sched[f]] for f in range(5)),
        4: sum(v4[f][sched[f]] for f in range(5)),
        6: sum(v6[f][sched[f]] for f in range(5)),
    }
    sim = simulate(K, sched, words)
    for dist in (1, 4, 6):
        if abs(pred[dist] - sim[dist]) > 1e-9:
            msg = (
                f"self-test failed at d{dist}: analytic {pred[dist]:.6f} "
                f"vs simulated {sim[dist]:.6f}"
            )
            raise AssertionError(msg)
    r = np.arange(M, dtype=np.int64)
    idx0 = (
        -(
            r[:, None, None, None]
            + r[None, :, None, None]
            + r[None, None, :, None]
            + r[None, None, None, :]
        )
    ) % M
    g4 = (
        v1[1][:, None, None, None]
        + v1[2][None, :, None, None]
        + v1[3][None, None, :, None]
        + v1[4][None, None, None, :]
    )
    grid_min = float((g4 + v1[0][idx0]).min())
    if abs(grid_min - constrained_floor(v1)) > 1e-12:
        msg = "DP floor != brute-force grid minimum"
        raise AssertionError(msg)
    print(
        f"self-test OK: analytic == simulated at d1/d4/d6 "
        f"({pred[1]:.4f}/{pred[4]:.4f}/{pred[6]:.4f}); "
        f"DP floor == grid minimum"
    )


def main() -> None:
    words = lp_words()
    obs = observed_rates(words)
    lo1, hi1 = wilson(*obs[1])
    lo6, hi6 = wilson(*obs[6])
    lo4, hi4 = wilson(*obs[4])
    print("observed within-word rates (clean corpus):")
    for dist in (1, 4, 6):
        k, n = obs[dist]
        lo, hi = wilson(k, n)
        print(f"  d{dist}: {k}/{n} = {k / n:.4f}  95% CI [{lo:.4f}, {hi:.4f}]")

    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if r:
            pools.setdefault(len(r), []).append(r)
    lp_lens = [len(w) for w in words]
    reg = []
    for _ in range(SAMPLES):
        reg.extend(sample_register(lp_lens, pools))
    T1, T4, T6, cross = phase_tables(reg)
    self_test(T1, T4, T6, reg)

    # seam (sigma) side: in-CI turns per alphabet, on the cross-word table
    lo_s, hi_s = 0.0050, 0.0118  # 23/2,927 seam doublets, 95% CI

    vocab = []
    with open(DICT) as fh:
        for line in fh:
            x = line.strip()
            if 4 <= len(x) <= 12 and x.isalpha() and x.isascii():
                vocab.append(x)
    if len(sys.argv) > 2:  # smoke-test limit
        vocab = vocab[: int(sys.argv[2])]

    # offset-grid index of the forced fifth offset, and the no-zero-offset
    # mask: a zero offset is an identity letter step, whose doublets are
    # plaintext doubles concentrated at one phase — excluded by the
    # measured mod-5 uniformity of doublet positions and by the flat
    # position profile that killed stay-slot-hold.
    r = np.arange(M, dtype=np.int64)
    IDX0 = (
        -(
            r[:, None, None, None]
            + r[None, :, None, None]
            + r[None, None, :, None]
            + r[None, None, None, :]
        )
    ) % M
    nz = r != 0
    NZ = (
        nz[:, None, None, None]
        & nz[None, :, None, None]
        & nz[None, None, :, None]
        & nz[None, None, None, :]
        & (IDX0 != 0)
    )

    n_alpha = 0
    uniq: set[bytes] = set()
    pre_pass = 0
    tot_sched = 0
    tot_sched_d6 = 0
    n_alpha_sched = 0
    n_alpha_d6 = 0
    best_rows = []  # (min predicted d6 among in-band-d1, word, rule)
    zero_off_frac_num = 0  # in-band-d1 schedules containing a zero offset
    d4_elev = 0  # in-band-d1 & in-CI-d6 schedules with pred d4 > background
    sig_turns_tot = 0
    sig_alpha = 0
    min_d6_global = 9.0

    np.empty(M, dtype=np.int64)
    for word in vocab:
        seq = kw_runes(word)
        if not seq:
            continue
        for rname, K in alphabets(seq):
            n_alpha += 1
            uniq.add(bytes(K))
            v1 = delta_vectors(K, T1, -1)
            if constrained_floor(v1) > hi1:
                continue  # no schedule can reach the band
            pre_pass += 1
            g4 = (
                v1[1][:, None, None, None]
                + v1[2][None, :, None, None]
                + v1[3][None, None, :, None]
                + v1[4][None, None, None, :]
            )
            rate1 = g4 + v1[0][IDX0]
            band = (rate1 >= lo1) & (rate1 <= hi1)
            zero_off_frac_num += int((band & ~NZ).sum())
            mask = band & NZ
            cnt = int(mask.sum())
            if cnt == 0:
                continue
            n_alpha_sched += 1
            tot_sched += cnt
            i1, i2, i3, i4 = np.nonzero(mask)
            i0 = IDX0[i1, i2, i3, i4]
            v6a = delta_vectors(K, T6, -1)
            rate6 = v6a[0][i0] + v6a[1][i1] + v6a[2][i2] + v6a[3][i3] + v6a[4][i4]
            m6 = float(rate6.min())
            min_d6_global = min(min_d6_global, m6)
            best_rows.append((m6, word, rname))
            sel = (rate6 >= lo6) & (rate6 <= hi6)
            c6 = int(sel.sum())
            if c6:
                n_alpha_d6 += 1
                tot_sched_d6 += c6
                v4a = delta_vectors(K, T4, +1)
                rate4 = (
                    v4a[0][i0[sel]]
                    + v4a[1][i1[sel]]
                    + v4a[2][i2[sel]]
                    + v4a[3][i3[sel]]
                    + v4a[4][i4[sel]]
                )
                d4_elev += int((rate4 > 1 / M).sum())

    # sigma: single turn per disk, cross-word table, phase-blind
    posv = np.empty(M, dtype=np.int64)
    for word in vocab:
        seq = kw_runes(word)
        if not seq:
            continue
        for _rname, K in alphabets(seq):
            posv[np.array(K)] = np.arange(M)
            D = (posv[None, :] - posv[:, None]) % M
            q = np.bincount(D.ravel(), weights=cross.ravel(), minlength=M)
            v = q[(-np.arange(M)) % M]
            n = int(((v[1:] >= lo_s) & (v[1:] <= hi_s)).sum())
            if n:
                sig_alpha += 1
                sig_turns_tot += n

    print(
        f"\nkeyword alphabets scanned: {n_alpha:,} ({len(uniq):,} unique permutations)"
    )
    print(f"d1 prefilter (phase-decomposed floor <= {hi1:.4f}): {pre_pass:,} alphabets")
    print(
        f"\n=== g side: schedules with predicted d1 in "
        f"[{lo1:.4f}, {hi1:.4f}], no zero offset ==="
    )
    print(f"  alphabets with >=1 in-band schedule: {n_alpha_sched:,}")
    print(f"  TOTAL in-band (alphabet, schedule) pairs: {tot_sched:,}")
    print(
        f"  in-band schedules REJECTED for a zero offset (identity "
        f"step, mod-5 doublet comb): {zero_off_frac_num:,}"
    )
    print(
        f"\n=== d6 filter: predicted d6 in [{lo6:.4f}, {hi6:.4f}] "
        f"(observed {obs[6][0]}/{obs[6][1]} = "
        f"{obs[6][0] / obs[6][1]:.4f}) ==="
    )
    print(
        f"  minimum predicted d6 over ALL in-band-d1 schedules: "
        f"{min_d6_global:.4f}  (background 1/29 = {1 / M:.4f})"
    )
    print(f"  alphabets surviving d1 AND d6: {n_alpha_d6:,}")
    print(
        f"  surviving (alphabet, schedule) pairs: {tot_sched_d6:,} "
        f"(cut factor vs d1-only: "
        f"{tot_sched / max(tot_sched_d6, 1):.0f}x)"
    )
    print(
        f"  of those, schedules predicting d4 above background: "
        f"{d4_elev:,} ({d4_elev / max(tot_sched_d6, 1):.1%}; observed d4 "
        f"leans high, {obs[4][0] / obs[4][1]:.4f})"
    )
    best_rows.sort()
    print("  deepest predicted d6 (alphabet minima):")
    for m6, word, rname in best_rows[:8]:
        print(f"     {m6:.4f}  {word:<14} [{rname}]")
    print(f"\n=== sigma side: turns with seam rate in [{lo_s:.4f}, {hi_s:.4f}] ===")
    print(
        f"  alphabets with >=1 in-CI turn: {sig_alpha:,}; "
        f"total (disk, turn) pairs: {sig_turns_tot:,}"
    )
    if tot_sched_d6 and sig_turns_tot:
        print(
            f"\njoint full-key space (g-side x sigma-side): "
            f"{tot_sched_d6:,} x {sig_turns_tot:,} = "
            f"{tot_sched_d6 * sig_turns_tot:.2e}"
        )


if __name__ == "__main__":
    main()
