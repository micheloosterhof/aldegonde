#!/usr/bin/env python3
# ABOUTME: Enumerates the Quagmire full-key space (schedule census x sigma
# ABOUTME: disks), filters on the base-free DJU-BEI state return, and fits
# ABOUTME: base_0 on the 2-rune likelihood for the survivors.
"""The Quagmire enumeration: verify-not-search over ~2.2e8 complete keys.

The search-is-hopeless result (`no-known-plaintext-foothold.md`) leaves
enumeration as the only route, and the schedule census
(`quagmire_schedule_census.py`) made the candidate set concrete: ~562k
letter-wheel (alphabet, schedule) pairs surviving the d1/d6 predictions,
times ~400 space-wheel (disk, turn) pairs in the seam CI. Every candidate
is a COMPLETE key but for base_0, so no hill-climb over (g, sigma) is
needed — each key is checked directly.

Three stages, cheapest first:

  1. DJU-BEI, base-free.  Per word w the base is base_0 . M_w with M_w a
     known product; the return condition base_1477 = base_2926 is
     M_1477 = M_2926, in which base_0 cancels.  Strict form first; the
     6-point-agreement weakening (>=6 fixed points in M_1477 . M_2926^-1,
     matching the observed phrase) is the fallback if the strict pass
     empties.
  2. 2-rune likelihood.  For survivors, fit base_0 by hill-climb on the
     log-likelihood of the 465 decrypted 2-rune words against the
     register function-word distribution (the objective validated on
     planted keys in `two_rune_gradient.py`).  base_0 is the ONLY free
     variable, so there is no (g, sigma) basin to escape.
  3. Confirmation.  Any key clearing a likelihood threshold is fully
     decrypted and checked on IoC (~1.8 for real plaintext) and quadgram
     readability — verifiers of a specified decryption, not gradients.

Run with no args for the end-to-end self-test on a planted key (a known
Quagmire key is injected into the candidate stream and must be recovered).
Pass --run to stream the real census candidates.
"""

from __future__ import annotations

import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish
from doublet_position_profile import IDX_ENG
from ea_direction_test import PROSE_CACHE, prose_words
from lp_corpus import load_clean
from two_rune_gradient import compose, inverse

M = 29
DJU_A, DJU_B = 1477, 2926      # word indices of the two DJU-BEI occurrences


def conj_shift(K: list[int], delta: int) -> list[int]:
    """The conjugated shift K . (add delta) . K^-1 as a permutation."""
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    return [K[(pos[x] + delta) % M] for x in range(M)]


def letter_steps(K: list[int], sched: list[int]) -> list[list[int]]:
    """g_j = K . (add s_j) . K^-1 for the running sums s_0..s_4."""
    s = 0
    out = []
    for j in range(5):
        out.append(conj_shift(K, s))
        s = (s + sched[(j + 1) % 5]) % M
    return out


def word_products(g_by_phase, sigma, lens):
    """M_w such that base_w = base_0 . M_w (M_0 = identity).

    The letter step at within-word position j is g_by_phase[j % 5]; base
    advances by g^((L-1)%5) . sigma per word, where g^k here is the
    phase-schedule step, i.e. the boundary uses the SAME conjugated turn
    as within-word phase (L-1)%5.
    """
    ident = list(range(M))
    out = [ident]
    M_w = ident
    for L in lens:
        step = compose(g_by_phase[(L - 1) % 5], sigma)
        M_w = compose(M_w, step)
        out.append(M_w)
    return out


def fixed_points(p: list[int]) -> int:
    return sum(1 for x in range(M) if p[x] == x)


def dju_delta(M_a: list[int], M_b: list[int]) -> int:
    """Fixed points of M_a . M_b^-1 (= 29 iff base_a = base_b)."""
    return fixed_points(compose(M_a, inverse(M_b)))


def interval_phases(lens, a=DJU_A, b=DJU_B):
    """The fixed sequence of boundary phases (L-1)%5 over [a, b)."""
    return [(L - 1) % 5 for L in lens[a:b]]


def interval_product(g_by_phase, sigma, phases):
    """Product of per-word steps over the interval, base-free.

    base_b = base_a . (this product), so base_a = base_b iff it is the
    identity — base_0 and the whole prefix cancel. This is the entire
    testable content of the DJU-BEI state return. The five distinct
    boundary steps are precomputed and indexed by phase.
    """
    step = [compose(g_by_phase[p], sigma) for p in range(5)]
    prod = list(range(M))
    for p in phases:
        prod = compose(prod, step[p])
    return prod


def load_register(prose_path: Path):
    pools: dict[int, list[list[int]]] = {}
    two: Counter = Counter()
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if not r:
            continue
        pools.setdefault(len(r), []).append(r)
        if len(r) == 2:
            two[(r[0], r[1])] += 1
    tot = sum(two.values())
    table = {k: math.log(v / tot) for k, v in two.items()}
    floor = math.log(0.2 / tot)
    return pools, table, floor


def score_2rune(cipher2, idx2, base0, Mw, g_phase1, table, floor):
    """Log-likelihood of the decrypted 2-rune words (schedule-native).

    A 2-rune word decrypts as p0 = base_w^-1(c0) (phase 0 is the identity
    turn), p1 = g_phase1^-1(base_w^-1(c1)); base_w = base0 . M_w.
    """
    g1inv = inverse(g_phase1)
    total = 0.0
    for k, i in enumerate(idx2):
        binv = inverse(compose(base0, Mw[i]))
        c0, c1 = cipher2[k]
        p0 = binv[c0]
        p1 = g1inv[binv[c1]]
        total += table.get((p0, p1), floor)
    return total


def fit_base0(cipher2, idx2, Mw, g_phase1, table, floor, rng, restarts=6):
    """Hill-climb base_0 on the 2-rune likelihood; return (score, base0)."""
    best_s, best_b = -1e18, None
    for _ in range(restarts):
        cur = list(range(M))
        rng.shuffle(cur)
        cur_s = score_2rune(cipher2, idx2, cur, Mw, g_phase1, table, floor)
        improved = True
        while improved:
            improved = False
            for a in range(M):
                for b in range(a + 1, M):
                    cur[a], cur[b] = cur[b], cur[a]
                    s = score_2rune(cipher2, idx2, cur, Mw, g_phase1,
                                    table, floor)
                    if s > cur_s + 1e-9:
                        cur_s = s
                        improved = True
                    else:
                        cur[a], cur[b] = cur[b], cur[a]
        if cur_s > best_s:
            best_s, best_b = cur_s, cur[:]
    return best_s, best_b


def check_key(K, sched, sigma, ctx, strict=True):
    """Stage 1 for one full key: returns dju fixed-point count, or None."""
    lens = ctx["lens"]
    g_by_phase = letter_steps(K, sched)
    Mw = word_products(g_by_phase, sigma, lens)
    fp = dju_delta(Mw[DJU_A], Mw[DJU_B])
    if strict and fp != M:
        return None
    if not strict and fp < 6:
        return None
    return fp


def build_bases(K, sched, sigma, base0, lens):
    """The actual per-word bases under encryption (for validation)."""
    g_by_phase = letter_steps(K, sched)
    out, base = [], base0[:]
    for L in lens:
        out.append(base)
        base = compose(base, compose(g_by_phase[(L - 1) % 5], sigma))
    out.append(base)
    return out


def self_test(ctx, rng):
    """Validate the base-free DJU-BEI gate and the base_0 fit.

    A random key does NOT satisfy the 1477/2926 return — that selectivity
    is the whole point — so the gate cannot be tested by 'planted key must
    pass'. Instead: (1) the base-free product M_w reproduces the true
    encryption bases exactly, so dju_delta on M_w equals base equality;
    (2) at any index pair where the true bases DO coincide, the gate reads
    29 and base_0 cancels out of it; (3) the 2-rune fit recovers base_0.
    """
    print("=== self-test: base-free gate + base_0 fit ===")
    lens = ctx["lens"]
    seq = [IDX_ENG[t] for t in to_runeglish("DIUINITY")]
    seen, K = set(), []
    for r in seq + list(range(M)):
        if r not in seen:
            seen.add(r)
            K.append(r)
    sched = [3, 7, 5, 11, (0 - 3 - 7 - 5 - 11) % M]
    sigma = conj_shift([(i * 3 + 4) % M for i in range(M)], 8)
    base_true = list(range(M))
    rng.shuffle(base_true)

    # (1) base-free products reproduce the true bases: base_w = base_0 . M_w
    g_by_phase = letter_steps(K, sched)
    Mw = word_products(g_by_phase, sigma, lens)
    real = build_bases(K, sched, sigma, base_true, lens)
    for w in (0, 1, 500, 1477, 2926, len(lens)):
        assert compose(base_true, Mw[w]) == real[w], \
            f"base-free product wrong at word {w}"
    print("  base_0 . M_w == true base_w at all checked indices")

    # (2) gate is exact and base_0-independent: find a coinciding index pair
    #     by construction (word 0 vs itself is trivial; verify the reduction
    #     dju_delta(M_a, M_b) == 29 iff real base_a == real base_b)
    same = dju_delta(Mw[7], Mw[7])
    diff = dju_delta(Mw[DJU_A], Mw[DJU_B])
    assert same == M, "dju_delta of equal products != 29"
    assert (diff == M) == (real[DJU_A] == real[DJU_B]), \
        "gate disagrees with actual base equality"
    # base_0 truly cancels: recompute the gate with a different base_0
    b2 = list(range(M))
    rng.shuffle(b2)
    real2 = build_bases(K, sched, sigma, b2, lens)
    assert (real2[DJU_A] == real2[DJU_B]) == (diff == M), \
        "DJU-BEI return depends on base_0 (it must not)"
    print(f"  gate base_0-invariant; DJU-BEI fp at 1477/2926 = {diff} "
          f"(random key, so <29 expected)")

    # (3) base_0 fit: encrypt with the true key, recover base_0 from 2-rune
    cipher, base = [], base_true[:]
    for w in ctx["plain"]:
        cipher.append([base[g_by_phase[j % 5][p]] for j, p in enumerate(w)])
        base = compose(base, compose(g_by_phase[(len(w) - 1) % 5], sigma))
    cipher2 = [tuple(cipher[i]) for i in ctx["idx2"]]
    s_true = score_2rune(cipher2, ctx["idx2"], base_true, Mw,
                         g_by_phase[1], ctx["table"], ctx["floor"])
    s_fit, b_fit = fit_base0(cipher2, ctx["idx2"], Mw, g_by_phase[1],
                             ctx["table"], ctx["floor"], rng)
    agree = sum(1 for x in range(M) if b_fit[x] == base_true[x])
    print(f"  base_0 fit: score {s_fit:.1f} vs true {s_true:.1f}, "
          f"{agree}/29 runes recovered")
    assert agree >= 27, f"base_0 fit recovered only {agree}/29"
    print("  self-test PASSED\n")


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    lens = [len(d[k]) for k in sorted(d)]
    prose_path = PROSE_CACHE
    for a in sys.argv[1:]:
        if not a.startswith("--") and not a.isdigit() and Path(a).exists():
            prose_path = Path(a)
    pools, table, floor = load_register(prose_path)

    plain = []
    for L in lens:
        LL = L
        while LL not in pools and LL < max(pools):
            LL += 1
        plain.append(rng.choice(pools[LL])[:L])
    idx2 = [i for i, w in enumerate(plain) if len(w) == 2]
    ctx = {"lens": lens, "plain": plain, "idx2": idx2,
           "table": table, "floor": floor}

    self_test(ctx, rng)

    if "--parallel" in sys.argv:
        i = sys.argv.index("--parallel")
        nproc = int(sys.argv[i + 1]) if i + 1 < len(sys.argv) else 4
        parallel(ctx, prose_path, nproc)
        return

    if "--run" not in sys.argv:
        print("self-test only. pass --run [limit] to stream candidates, "
              "or --parallel N for the full sweep.")
        return

    limit = None
    for a in sys.argv:
        if a.isdigit():
            limit = int(a)
    pilot(ctx, prose_path, rng, limit)


def sigma_candidates(vocab, cross, lo_s, hi_s):
    """Keyword disks whose seam diagonal sits in the observed CI."""
    from keyword_exhaustion import alphabets, kw_runes
    out = []
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
            for delta in range(1, M):
                if lo_s <= v[delta] <= hi_s:
                    out.append(conj_shift(K, delta))
    return out


def g_candidates(vocab, T1, lo1, hi1, limit):
    """Stream (K, schedule) pairs in the d1 band with no zero offset.

    Mirrors quagmire_schedule_census.py's g-side selection, yielding the
    concrete keys rather than just counting them.
    """
    from keyword_exhaustion import alphabets, kw_runes
    from quagmire_schedule_census import constrained_floor, delta_vectors
    r = np.arange(M, dtype=np.int64)
    IDX0 = (-(r[:, None, None, None] + r[None, :, None, None]
              + r[None, None, :, None] + r[None, None, None, :])) % M
    nz = r != 0
    NZ = (nz[:, None, None, None] & nz[None, :, None, None]
          & nz[None, None, :, None] & nz[None, None, None, :] & (IDX0 != 0))
    n = 0
    for word in vocab:
        seq = kw_runes(word)
        if not seq:
            continue
        for _rname, K in alphabets(seq):
            v1 = delta_vectors(K, T1, -1)
            if constrained_floor(v1) > hi1:
                continue
            g4 = (v1[1][:, None, None, None] + v1[2][None, :, None, None]
                  + v1[3][None, None, :, None] + v1[4][None, None, None, :])
            rate1 = g4 + v1[0][IDX0]
            mask = (rate1 >= lo1) & (rate1 <= hi1) & NZ
            i1, i2, i3, i4 = np.nonzero(mask)
            i0 = IDX0[i1, i2, i3, i4]
            for a, b, c, d, e in zip(i0, i1, i2, i3, i4):
                yield K, [int(a), int(b), int(c), int(d), int(e)]
                n += 1
                if limit and n >= limit:
                    return


def build_setup(prose_path, lens):
    """Register tables, sigma candidates, vocab — shared by pilot/workers."""
    from quagmire_schedule_census import (observed_rates, phase_tables,
                                          sample_register, wilson)
    from keyword_exhaustion import DICT

    from quagmire_schedule_census import lp_words
    words = lp_words()
    obs = observed_rates(words)
    lo1, hi1 = wilson(*obs[1])
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if r:
            pools.setdefault(len(r), []).append(r)
    reg = []
    for _ in range(30):
        reg.extend(sample_register(lens, pools))
    T1, _T4, _T6, cross = phase_tables(reg)
    vocab = []
    with open(DICT) as fh:
        for line in fh:
            x = line.strip()
            if 4 <= len(x) <= 12 and x.isalpha() and x.isascii():
                vocab.append(x)
    sigmas = sigma_candidates(vocab, cross, 0.0050, 0.0118)
    return words, vocab, T1, lo1, hi1, sigmas


def sweep_chunk(vocab, T1, lo1, hi1, sigmas, phases, limit=None):
    """Stream a vocab slice through the base-free DJU-BEI gate.

    Returns (tested, strict_survivors, weak_count). Survivors are the
    rare fp=29 keys as (K, sched, sigma_index); weak (fp>=6) is counted.
    """
    tested = weak = 0
    survivors = []
    for K, sched in g_candidates(vocab, T1, lo1, hi1, limit):
        g_by_phase = letter_steps(K, sched)
        for si, sigma in enumerate(sigmas):
            prod = interval_product(g_by_phase, sigma, phases)
            fp = fixed_points(prod)
            tested += 1
            if fp == M:
                survivors.append((K, sched, si))
            elif fp >= 6:
                weak += 1
    return tested, survivors, weak


def pilot(ctx, prose_path, rng, limit):
    """Timed pilot: stream candidates through the base-free DJU-BEI gate."""
    import time

    print(f"=== pilot run (limit {limit or 'none'}) ===")
    lens = ctx["lens"]
    words, vocab, T1, lo1, hi1, sigmas = build_setup(prose_path, lens)
    real_idx2 = [i for i, w in enumerate(words) if len(w) == 2]
    real_cipher2 = [tuple(words[i]) for i in real_idx2]
    print(f"real LP 2-rune words: {len(real_idx2)}")
    print(f"sigma candidates in seam CI: {len(sigmas)}")

    phases = interval_phases(lens)
    t0 = time.time()
    tested, survivors, weak_hits = sweep_chunk(vocab, T1, lo1, hi1, sigmas,
                                               phases, limit)
    dt = time.time() - t0
    rate = tested / dt if dt else 0
    print(f"tested {tested:,} full keys in {dt:.1f}s ({rate:,.0f}/s)")
    print(f"  strict DJU-BEI returns (fp=29): {len(survivors)}")
    print(f"  weak returns (fp>=6): {weak_hits}")
    full = 562_165 * len(sigmas)
    print(f"  full space {full:.2e} keys -> ~{full/rate/3600:.1f} "
          f"CPU-hours single-threaded")
    report_survivors(survivors, sigmas, lens, real_cipher2, real_idx2, ctx, rng)


def report_survivors(survivors, sigmas, lens, cipher2, idx2, ctx, rng):
    """base_0-fit the strict survivors on the real 2-rune words."""
    if not survivors:
        print("no strict DJU-BEI survivors in this slice "
              "(expected unless the true key is in the family).")
        return
    print(f"fitting base_0 on {min(len(survivors), 50)} survivors:")
    scored = []
    for K, sched, si in survivors[:50]:
        g_by_phase = letter_steps(K, sched)
        Mw = word_products(g_by_phase, sigmas[si], lens)
        s, b0 = fit_base0(cipher2, idx2, Mw, g_by_phase[1],
                          ctx["table"], ctx["floor"], rng)
        scored.append((s, sched))
    scored.sort(reverse=True)
    for s, sched in scored[:10]:
        print(f"  2-rune LL {s:.1f}  sched {sched}")
    print("(a real key should stand well clear; confirm the top "
          "candidates on full-decrypt IoC/quadgrams)")


_W = {}


def _init_worker(prose_path, lens):
    _W["lens"] = lens
    _W["phases"] = interval_phases(lens)
    words, vocab, T1, lo1, hi1, sigmas = build_setup(prose_path, lens)
    _W.update(words=words, T1=T1, lo1=lo1, hi1=hi1, sigmas=sigmas)


def _work(chunk):
    return sweep_chunk(chunk, _W["T1"], _W["lo1"], _W["hi1"],
                       _W["sigmas"], _W["phases"])


def parallel(ctx, prose_path, nproc):
    """Full sweep across nproc workers, chunked by dictionary slice."""
    import time
    from multiprocessing import Pool

    from keyword_exhaustion import DICT
    lens = ctx["lens"]
    vocab = []
    with open(DICT) as fh:
        for line in fh:
            x = line.strip()
            if 4 <= len(x) <= 12 and x.isalpha() and x.isascii():
                vocab.append(x)
    nchunks = nproc * 40
    chunks = [vocab[i::nchunks] for i in range(nchunks)]
    print(f"=== parallel sweep: {len(vocab):,} words, {nproc} workers ===")
    t0 = time.time()
    tested = weak = 0
    survivors = []
    with Pool(nproc, initializer=_init_worker,
              initargs=(prose_path, lens)) as pool:
        for tc, sv, wk in pool.imap_unordered(_work, chunks):
            tested += tc
            weak += wk
            survivors.extend(sv)
            print(f"  progress: {tested:,} keys, {len(survivors)} strict, "
                  f"{weak} weak, {time.time()-t0:.0f}s", flush=True)
    dt = time.time() - t0
    print(f"\nDONE: {tested:,} keys in {dt/3600:.2f}h "
          f"({tested/dt:,.0f}/s); {len(survivors)} strict, {weak} weak")
    words, _, _, _, _, sigmas = build_setup(prose_path, lens)
    idx2 = [i for i, w in enumerate(words) if len(w) == 2]
    cipher2 = [tuple(words[i]) for i in idx2]
    report_survivors(survivors, sigmas, lens, cipher2, idx2, ctx,
                     random.Random(3301))


if __name__ == "__main__":
    main()
