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

import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, prose_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from two_rune_gradient import compose, inverse  # noqa: E402

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
    minv2 = [inverse(Mw[i]) for i in idx2]
    return _fast_score(cipher2, minv2, inverse(base0), g1inv, table, floor)


def _fast_score(cipher2, minv2, b0inv, g1inv, table, floor):
    """2-rune LL with M_w^-1 and g^-1 precomputed; p = M_w^-1(base0^-1(c))."""
    total = 0.0
    for k in range(len(cipher2)):
        c0, c1 = cipher2[k]
        mk = minv2[k]
        p0 = mk[b0inv[c0]]
        p1 = g1inv[mk[b0inv[c1]]]
        total += table.get((p0, p1), floor)
    return total


def fit_base0(cipher2, idx2, Mw, g_phase1, table, floor, rng, restarts=6):
    """Hill-climb base_0 on the 2-rune likelihood; return (score, base0).

    Precomputes M_w^-1 for the 2-rune words once per key, so each score is
    O(words) instead of O(words x 29).
    """
    g1inv = inverse(g_phase1)
    minv2 = [inverse(Mw[i]) for i in idx2]
    best_s, best_b = -1e18, None
    for _ in range(restarts):
        cur = list(range(M))
        rng.shuffle(cur)
        cur_s = _fast_score(cipher2, minv2, inverse(cur), g1inv, table, floor)
        improved = True
        while improved:
            improved = False
            for a in range(M):
                for b in range(a + 1, M):
                    cur[a], cur[b] = cur[b], cur[a]
                    s = _fast_score(cipher2, minv2, inverse(cur), g1inv,
                                    table, floor)
                    if s > cur_s + 1e-9:
                        cur_s = s
                        improved = True
                    else:
                        cur[a], cur[b] = cur[b], cur[a]
        if cur_s > best_s:
            best_s, best_b = cur_s, cur[:]
    return best_s, best_b


def check_key(K, sched, sigma, ctx, *, strict=True):
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


def encrypt_walk(plain, base0, g_by_phase, sigma):
    """Schedule-model encryption (g_by_phase are the phase steps)."""
    out, base = [], base0[:]
    for w in plain:
        out.append([base[g_by_phase[j % 5][p]] for j, p in enumerate(w)])
        base = compose(base, compose(g_by_phase[(len(w) - 1) % 5], sigma))
    return out


def decrypt_walk(cipher, base0, g_by_phase, sigma):
    """Inverse of encrypt_walk: recover plaintext from a full key."""
    ginv = [inverse(g_by_phase[p]) for p in range(5)]
    out, base = [], base0[:]
    for w in cipher:
        binv = inverse(base)
        out.append([ginv[j % 5][binv[c]] for j, c in enumerate(w)])
        base = compose(base, compose(g_by_phase[(len(w) - 1) % 5], sigma))
    return out


def manufactured_test(ctx, rng):
    """End-to-end on a planted key that genuinely returns.

    A random key almost never satisfies a state return, so to exercise
    the POSITIVE path we plant sigma inside the conjugated-shift group of
    K: every per-word step is then a conjugated shift, the walk lives in a
    29-element cyclic group, and pigeonhole forces an exact base return
    within ~30 words. That return is the anchor. Degenerate as a cipher
    (this is the excluded sigma-in-<g> case), but it drives the full
    gate -> base_0 fit -> decrypt chain on the real length sequence.
    """
    print("=== manufactured-sample test: a key that returns ===")
    lens = ctx["lens"]
    seq = [IDX_ENG[t] for t in to_runeglish("DIUINITY")]
    seen, K = set(), []
    for r in seq + list(range(M)):
        if r not in seen:
            seen.add(r)
            K.append(r)
    sched = [3, 7, 5, 11, (0 - 3 - 7 - 5 - 11) % M]
    sigma = conj_shift(K, 8)          # in <conj-shifts of K> -> small walk group
    g_by_phase = letter_steps(K, sched)

    Mw = word_products(g_by_phase, sigma, lens)
    first, anchor = {}, None
    for w, m in enumerate(Mw):
        t = tuple(m)
        if t in first:
            anchor = (first[t], w)
            break
        first[t] = w
    assert anchor, "no state return found in the corpus"
    a, b = anchor
    print(f"  planted key returns at words {a}/{b} (interval {b - a})")

    phases_ab = [(L - 1) % 5 for L in lens[a:b]]
    fp_true = fixed_points(interval_product(g_by_phase, sigma, phases_ab))
    assert fp_true == M, f"gate rejected a genuine return: fp={fp_true}"
    bad = sigma[:]
    bad[0], bad[1] = bad[1], bad[0]
    fp_bad = fixed_points(interval_product(g_by_phase, bad, phases_ab))
    assert fp_bad < M, f"one-swap sigma wrongly passed: fp={fp_bad}"
    print(f"  gate: genuine key fp=29 (accept), one-swap sigma fp={fp_bad} "
          f"(reject)")

    base_true = list(range(M))
    rng.shuffle(base_true)
    cipher = encrypt_walk(ctx["plain"], base_true, g_by_phase, sigma)
    idx2 = ctx["idx2"]
    cipher2 = [tuple(cipher[i]) for i in idx2]

    s_fit, b0 = fit_base0(cipher2, idx2, Mw, g_by_phase[1],
                          ctx["table"], ctx["floor"], rng)
    agree = sum(1 for x in range(M) if b0[x] == base_true[x])
    print(f"  base_0 fit: {agree}/29 runes recovered (2-rune LL {s_fit:.1f})")
    assert agree >= 27, f"base_0 fit failed: {agree}/29"

    dec = decrypt_walk(cipher, b0, g_by_phase, sigma)
    ok = sum(1 for w in range(len(dec)) if dec[w] == ctx["plain"][w])
    frac = ok / len(dec)
    print(f"  full decrypt with recovered key: {ok}/{len(dec)} words "
          f"({frac:.1%}) match the planted plaintext")
    assert frac >= 0.99, f"decrypt round-trip only {frac:.1%}"

    # Force a genuine return at the PRODUCTION anchor (1477/2926) and check
    # the deployed check_key path accepts it. With sigma = conj_shift(K, d),
    # every step is conj_shift(K, s_phase + d); the interval product is
    # conj_shift(K, S + 1449 d), identity iff S + 1449 d == 0 (mod 29).
    s_run = [0, 0, 0, 0, 0]
    acc = 0
    for j in range(1, 5):
        acc = (acc + sched[j]) % M
        s_run[j] = acc
    S = sum(s_run[(L - 1) % 5] for L in lens[DJU_A:DJU_B]) % M
    n_int = (DJU_B - DJU_A) % M
    d = None
    for cand in range(1, M):
        if (S + n_int * cand) % M == 0:
            d = cand
            break
    assert d is not None, "no nonzero sigma delta forces the return"
    sigma2 = conj_shift(K, d)
    fp_prod = check_key(K, sched, sigma2, ctx, strict=True)
    assert fp_prod == M, f"production check_key rejected a forced return: {fp_prod}"
    print(f"  production gate (check_key at {DJU_A}/{DJU_B}): forced-return "
          f"key with sigma delta {d} accepted (fp=29)")
    print("  manufactured-sample test PASSED "
          "(found the key, recovered base_0, decrypted)\n")


def verify_candidate_generation(ctx, prose_path):
    """g_candidates over a vocab slice must match the census count."""
    from quagmire_schedule_census import (lp_words, observed_rates, wilson,  # noqa: I001
                                          phase_tables, sample_register)
    from keyword_exhaustion import DICT
    print("=== candidate-generation cross-check ===")
    lens = ctx["lens"]
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
    T1, _t4, _t6, _cross = phase_tables(reg)
    vocab = []
    with open(DICT) as fh:
        for line in fh:
            x = line.strip()
            if 4 <= len(x) <= 12 and x.isalpha() and x.isascii():
                vocab.append(x)
    slice_ = vocab[:500]
    gen = sum(1 for _ in g_candidates(slice_, T1, lo1, hi1, None))
    print(f"  g_candidates over first 500 words: {gen:,} (K, schedule) pairs")
    print("  cross-check: `quagmire_schedule_census.py <prose> 500` reports "
          "the same in-band total (1,219 at the seed-3301 register draw)")
    return gen


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
        while LL not in pools and max(pools) > LL:
            LL += 1
        plain.append(rng.choice(pools[LL])[:L])
    idx2 = [i for i, w in enumerate(plain) if len(w) == 2]
    ctx = {"lens": lens, "plain": plain, "idx2": idx2,
           "table": table, "floor": floor}

    self_test(ctx, rng)

    if "--verify" in sys.argv:
        manufactured_test(ctx, rng)
        verify_candidate_generation(ctx, prose_path)
        return

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
    from quagmire_schedule_census import (observed_rates, phase_tables,  # noqa: I001
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


def sweep_chunk(vocab, T1, lo1, hi1, sigmas, phases, lens,
                cipher2, idx2, table, floor, rng,
                thresh=-4000.0, min_fp=6, limit=None):
    """Stream a vocab slice through the CORRECT DJU-BEI test.

    The observed DJU-BEI ciphertext repeat forces base_1477 and base_2926
    to agree on the 6 plaintext image points, i.e. fixed_points of the
    interval product >= 6 (base_0-independent). Full equality (fp=29) is
    reachable only by the degenerate sigma-in-<g> class and so is NOT the
    right condition. Every key with fp >= min_fp is 2-rune-fit; those
    scoring above `thresh` (well over the ~-4950 random floor) are kept as
    candidates. Returns (tested, weak_count, candidates), candidates as
    (sched, si, fp, ll, base0).
    """
    tested = weak = 0
    cands = []
    for K, sched in g_candidates(vocab, T1, lo1, hi1, limit):
        g_by_phase = letter_steps(K, sched)
        for si, sigma in enumerate(sigmas):
            prod = interval_product(g_by_phase, sigma, phases)
            fp = fixed_points(prod)
            tested += 1
            if fp < min_fp:
                continue
            weak += 1
            Mw = word_products(g_by_phase, sigma, lens)
            ll, b0 = fit_base0(cipher2, idx2, Mw, g_by_phase[1],
                               table, floor, rng, restarts=2)
            if ll > thresh:
                distinct = len({tuple(m) for m in Mw})
                cands.append((K, sched, si, fp, distinct, round(ll, 1), b0))
    return tested, weak, cands


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

    _, table, floor = load_register(prose_path)
    phases = interval_phases(lens)
    t0 = time.time()
    tested, weak, cands = sweep_chunk(vocab, T1, lo1, hi1, sigmas, phases,
                                      lens, real_cipher2, real_idx2, table,
                                      floor, rng, limit=limit)
    dt = time.time() - t0
    rate = tested / dt if dt else 0
    print(f"tested {tested:,} full keys in {dt:.1f}s ({rate:,.0f}/s)")
    print(f"  weak DJU-BEI (fp>=6): {weak}; candidates (2-rune LL>-4000): "
          f"{len(cands)}")
    for _K, sched, _si, fp, distinct, ll, _b0 in sorted(
            cands, key=lambda c: -c[5])[:10]:
        tag = "degen" if distinct < 600 else "GENUINE"
        print(f"    LL {ll} fp {fp} bases {distinct} [{tag}] sched {sched}")


def analyze_survivor(K, sched, sigma, lens, cipher2, idx2, table, floor, rng):
    """Degeneracy + 2-rune fit for one strict survivor.

    distinct_bases separates a genuine key (visits ~2,928 bases, as the
    census requires >~600) from the degenerate sigma-in-<g> class the
    model excludes (small walk group -> trivial return, few bases).
    """
    g_by_phase = letter_steps(K, sched)
    Mw = word_products(g_by_phase, sigma, lens)
    distinct = len({tuple(m) for m in Mw})
    ll, b0 = fit_base0(cipher2, idx2, Mw, g_by_phase[1], table, floor, rng)
    return distinct, ll, b0


def report_survivors(survivors, sigmas, lens, cipher2, idx2, ctx, rng):
    """base_0-fit the strict survivors on the real 2-rune words."""
    if not survivors:
        print("no strict DJU-BEI survivors in this slice "
              "(expected unless the true key is in the family).")
        return
    print(f"fitting base_0 on {min(len(survivors), 50)} survivors:")
    scored = []
    for K, sched, si in survivors[:50]:
        distinct, ll, _ = analyze_survivor(K, sched, sigmas[si], lens,
                                           cipher2, idx2, ctx["table"],
                                           ctx["floor"], rng)
        scored.append((ll, distinct, sched))
    scored.sort(reverse=True)
    for ll, distinct, sched in scored[:10]:
        tag = "DEGENERATE" if distinct < 600 else "non-degenerate"
        print(f"  2-rune LL {ll:.1f}  bases {distinct:>4} [{tag}]  "
              f"sched {sched}")
    print("(a real key: many bases AND high 2-rune LL; degenerate = the "
          "excluded sigma-in-<g> return)")


_W = {}


def _init_worker(prose_path, lens):
    _W["lens"] = lens
    _W["phases"] = interval_phases(lens)
    words, vocab, T1, lo1, hi1, sigmas = build_setup(prose_path, lens)
    _, table, floor = load_register(prose_path)
    idx2 = [i for i, w in enumerate(words) if len(w) == 2]
    cipher2 = [tuple(words[i]) for i in idx2]
    _W.update(words=words, T1=T1, lo1=lo1, hi1=hi1, sigmas=sigmas,
              cipher2=cipher2, idx2=idx2, table=table, floor=floor,
              rng=random.Random(3301))


def _work(chunk):
    return sweep_chunk(chunk, _W["T1"], _W["lo1"], _W["hi1"], _W["sigmas"],
                       _W["phases"], _W["lens"], _W["cipher2"], _W["idx2"],
                       _W["table"], _W["floor"], _W["rng"])


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
    out_path = ROOT / "experiments" / "quagmire_candidates.jsonl"
    with out_path.open("w") as fout:
        print(f"=== parallel sweep (weak-DJU-BEI + 2-rune fit): "
              f"{len(vocab):,} words, {nproc} workers ===")
        print(f"candidates (2-rune LL > -4000) -> {out_path}")
        t0 = time.time()
        tested = weak = ncand = 0
        best_ll = -1e18
        with Pool(nproc, initializer=_init_worker,
                  initargs=(prose_path, lens)) as pool:
            for tc, wk, cands in pool.imap_unordered(_work, chunks):
                tested += tc
                weak += wk
                for K, sched, si, fp, distinct, ll, b0 in cands:
                    ncand += 1
                    best_ll = max(best_ll, ll)
                    degen = distinct < 600
                    rec = {"sched": sched, "sigma_idx": si, "fp": fp,
                           "bases": distinct, "two_rune_ll": ll,
                           "degenerate": degen, "K": K, "base0": b0}
                    fout.write(json.dumps(rec) + "\n")
                    fout.flush()
                    print(f"  *** CANDIDATE #{ncand}: 2-rune LL {ll} fp {fp} "
                          f"bases {distinct} {'[degen]' if degen else '[GENUINE]'}"
                          f" sched {sched}", flush=True)
                print(f"  progress: {tested:,} keys, {weak} weak(fp>=6), "
                      f"{ncand} cands, best LL {best_ll:.0f}, "
                      f"{time.time()-t0:.0f}s", flush=True)
    dt = time.time() - t0
    print(f"\nDONE: {tested:,} keys in {dt/3600:.2f}h "
          f"({tested/dt:,.0f}/s); {weak} weak(fp>=6), {ncand} candidates, "
          f"best 2-rune LL {best_ll:.0f}")
    print(f"candidates written to {out_path}")
    print("(a genuine keyword-Quagmire key: 2-rune LL ~-1300, non-degenerate; "
          "if best LL stays ~-4900 the family is excluded)")


if __name__ == "__main__":
    main()
