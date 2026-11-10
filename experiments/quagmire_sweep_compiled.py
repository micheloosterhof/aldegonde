# ABOUTME: Carries the Quagmire odometer enumeration of quagmire_runner.py to full
# ABOUTME: coverage with a compiled gate and base fit, and writes the outcome to JSON.
"""The gated Quagmire enumeration, re-run with compiled inner loops.

`quagmire_runner.py` defines the candidate set (keyword letter wheels with a 5-offset
schedule in the d1 band, times keyword space wheels in the seam band) and a three-stage
check: the base-free DJU-BEI gate, a base_0 fit on the 2-rune words, and a full decrypt.
Its gate runs at about 1,400 keys a second in pure Python, about 37 core-hours for the
set. The July 2026 run is recorded in `mixed-alphabet-vigenere.md` (313,972,400 keys,
none above -4000) and not in `quagmire-odometer.md` or `docs/new-directions.md`, which
is how it came to be listed as an open computation. This is an independent replication
of that run in about half an hour.

What the gate is worth is settled elsewhere: `dju-bei-gate-validity.md` shows a true key
passes it only at the chance rate unless DJU-BEI is a genuine state return, and
`quagmire_ungated_sweep.py` scores every key with no gate. A negative here is therefore
a negative for "keyword Quagmire walk, no zero offset, inside the one-register bands,
AND DJU-BEI is a state return".

This script streams the same candidates from `quagmire_runner.g_candidates` and
`quagmire_runner.sigma_candidates` and replaces the two inner loops with compiled ones:

  gate   the product of the per-word steps over the DJU-BEI interval, and its fixed
         points. A key passes with 6 or more: the repeat is two three-rune blocks with
         six distinct runes, so the two bases agree on six points.
  fit    a swap hill-climb of base_0 on the 2-rune log-likelihood, as `fit_base0`.

Before the sweep it checks itself against the original code and against planted keys:

  1. the compiled gate equals `interval_product` + `fixed_points` on random keys;
  2. the compiled score equals `_fast_score` on random keys and bases;
  3. keys of the family are planted on a plaintext with the body's block lengths, and
     the fit must lift them above the candidate threshold while wrong keys stay below.

The gate's positive path (a key that does return) is exercised by
`quagmire_runner.py --verify`, which is not repeated here. A planted key of the family
does not return at the DJU-BEI interval, so check 3 covers the fit stage only.

    python experiments/quagmire_sweep_compiled.py --check          # checks only
    python experiments/quagmire_sweep_compiled.py --sweep 4        # full sweep, 4 workers
    python experiments/quagmire_sweep_compiled.py --sweep 4 --every 50   # 1/50 slice

The outcome is written to `experiments/quagmire_sweep_outcome.json`.
"""

from __future__ import annotations

import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from numba import njit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import quagmire_runner as qr  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from keyword_exhaustion import DICT  # noqa: E402
from lp_corpus import load_words  # noqa: E402

from aldegonde.maths import permutation  # noqa: E402

M = qr.M
SEED = 3301
MIN_FP = 6
THRESH = -4000.0  # the runner's candidate threshold on the 2-rune log-likelihood
RESTARTS = 4
OUT = ROOT / "experiments" / "quagmire_sweep_outcome.json"


@njit(cache=True)
def gate_fixed_points(g_by_phase, sigmas, phases):
    """Fixed points of the interval product for one letter wheel and every space wheel.

    step_p = g_p . sigma and prod <- prod . step_p, as `qr.interval_product`."""
    n = sigmas.shape[0]
    out = np.empty(n, dtype=np.int64)
    step = np.empty((5, M), dtype=np.int64)
    prod = np.empty(M, dtype=np.int64)
    nxt = np.empty(M, dtype=np.int64)
    for s in range(n):
        for p in range(5):
            for x in range(M):
                step[p, x] = g_by_phase[p, sigmas[s, x]]
        for x in range(M):
            prod[x] = x
        for i in range(phases.shape[0]):
            p = phases[i]
            for x in range(M):
                nxt[x] = prod[step[p, x]]
            prod, nxt = nxt, prod
        fp = 0
        for x in range(M):
            if prod[x] == x:
                fp += 1
        out[s] = fp
    return out


@njit(cache=True)
def inverse_products(g_by_phase, sigma, lens, idx2):
    """M_w^-1 for the 2-rune words, with M_w as `qr.word_products`."""
    out = np.empty((idx2.shape[0], M), dtype=np.int64)
    cur = np.arange(M)
    nxt = np.empty(M, dtype=np.int64)
    k = 0
    for w in range(lens.shape[0]):
        if k < idx2.shape[0] and idx2[k] == w:
            for x in range(M):
                out[k, cur[x]] = x
            k += 1
        p = (lens[w] - 1) % 5
        for x in range(M):
            nxt[x] = cur[g_by_phase[p, sigma[x]]]
        cur, nxt = nxt, cur
    return out


@njit(cache=True)
def score(cipher2, minv2, b0inv, g1inv, table):
    """2-rune log-likelihood, as `qr._fast_score`."""
    total = 0.0
    for k in range(cipher2.shape[0]):
        p0 = minv2[k, b0inv[cipher2[k, 0]]]
        p1 = g1inv[minv2[k, b0inv[cipher2[k, 1]]]]
        total += table[p0, p1]
    return total


@njit(cache=True)
def fit(cipher2, minv2, g1inv, table, restarts, seed):
    """Swap hill-climb of base_0 on the 2-rune log-likelihood, as `qr.fit_base0`."""
    np.random.seed(seed)
    best_s = -1e18
    best_b = np.arange(M)
    inv = np.empty(M, dtype=np.int64)
    for _ in range(restarts):
        cur = np.random.permutation(M)
        for x in range(M):
            inv[cur[x]] = x
        cur_s = score(cipher2, minv2, inv, g1inv, table)
        improved = True
        while improved:
            improved = False
            for a in range(M):
                for b in range(a + 1, M):
                    cur[a], cur[b] = cur[b], cur[a]
                    inv[cur[a]] = a
                    inv[cur[b]] = b
                    s = score(cipher2, minv2, inv, g1inv, table)
                    if s > cur_s + 1e-9:
                        cur_s = s
                        improved = True
                    else:
                        cur[a], cur[b] = cur[b], cur[a]
                        inv[cur[a]] = a
                        inv[cur[b]] = b
        if cur_s > best_s:
            best_s = cur_s
            best_b = cur.copy()
    return best_s, best_b


def table_array(table: dict, floor: float) -> np.ndarray:
    arr = np.full((M, M), floor)
    for (a, b), v in table.items():
        arr[a, b] = v
    return arr


def vocabulary() -> list[str]:
    """The runner's keyword list: dictionary words of 4-12 ASCII letters."""
    out = []
    with open(DICT) as fh:
        for line in fh:
            x = line.strip()
            if 4 <= len(x) <= 12 and x.isalpha() and x.isascii():
                out.append(x)
    return out


def corpus():
    words = load_words()
    lens = np.array([len(w) for w in words], dtype=np.int64)
    idx2 = np.array([i for i, w in enumerate(words) if len(w) == 2], dtype=np.int64)
    cipher2 = np.array([words[i] for i in idx2], dtype=np.int64)
    phases = np.array(qr.interval_phases([int(x) for x in lens]), dtype=np.int64)
    return words, lens, idx2, cipher2, phases


# --------------------------------------------------------------------------- checks


def check(rng: random.Random) -> dict:
    """The compiled paths against the original code, and planted keys through the fit."""
    words, lens, idx2, cipher2, phases = corpus()
    lens_l = [int(x) for x in lens]
    pools, table, floor = qr.load_register(PROSE_CACHE)
    tab = table_array(table, floor)

    def random_key():
        K = permutation.random_permutation(M, rng)
        sched = [rng.randrange(1, M) for _ in range(4)]
        sched.insert(0, (-sum(sched)) % M)
        sigma = qr.conj_shift(
            permutation.random_permutation(M, rng), rng.randrange(1, M)
        )
        return qr.letter_steps(K, sched), sigma

    # 1. gate
    bad = 0
    for _ in range(300):
        g, sigma = random_key()
        want = qr.fixed_points(qr.interval_product(g, sigma, [int(p) for p in phases]))
        got = gate_fixed_points(np.array(g), np.array([sigma]), phases)[0]
        bad += want != got
    print(f"check 1, gate against interval_product: {300 - bad}/300 agree")
    assert bad == 0

    # 2. score
    bad = 0
    c2 = [tuple(int(v) for v in row) for row in cipher2]
    for _ in range(40):
        g, sigma = random_key()
        Mw = qr.word_products(g, sigma, lens_l)
        base0 = permutation.random_permutation(M, rng)
        want = qr.score_2rune(c2, [int(i) for i in idx2], base0, Mw, g[1], table, floor)
        minv2 = inverse_products(np.array(g), np.array(sigma), lens, idx2)
        got = score(
            cipher2,
            minv2,
            np.array(qr.inverse(base0)),
            np.array(qr.inverse(g[1])),
            tab,
        )
        bad += abs(want - got) > 1e-6
    print(f"check 2, score against _fast_score: {40 - bad}/40 agree")
    assert bad == 0

    # 3. planted keys of the family through the fit, on the body's block lengths
    plain = []
    for L in lens_l:
        LL = L
        while LL not in pools and max(pools) > LL:
            LL += 1
        plain.append(rng.choice(pools[LL])[:L])
    vocab = vocabulary()
    from keyword_exhaustion import alphabets, kw_runes

    def keyword_alphabet():
        while True:
            seq = kw_runes(rng.choice(vocab))
            if seq:
                return rng.choice(list(alphabets(seq)))[1]

    true_ll, wrong_ll, recovered = [], [], []
    for trial in range(20):
        K = keyword_alphabet()
        sched = [rng.randrange(1, M) for _ in range(4)]
        sched.insert(0, (-sum(sched)) % M)
        if sched[0] == 0:
            continue
        g = qr.letter_steps(K, sched)
        sigma = qr.conj_shift(keyword_alphabet(), rng.randrange(1, M))
        base0 = permutation.random_permutation(M, rng)
        cipher = qr.encrypt_walk(plain, base0, g, sigma)
        planted2 = np.array([cipher[i] for i in idx2], dtype=np.int64)
        minv2 = inverse_products(np.array(g), np.array(sigma), lens, idx2)
        ll, b0 = fit(
            planted2, minv2, np.array(qr.inverse(g[1])), tab, RESTARTS, SEED + trial
        )
        true_ll.append(ll)
        recovered.append(int((b0 == np.array(base0)).sum()))
        # the same ciphertext under a wrong space wheel
        wrong = qr.conj_shift(keyword_alphabet(), rng.randrange(1, M))
        minv2 = inverse_products(np.array(g), np.array(wrong), lens, idx2)
        ll, _ = fit(
            planted2, minv2, np.array(qr.inverse(g[1])), tab, RESTARTS, SEED + trial
        )
        wrong_ll.append(ll)
    true_ll, wrong_ll = np.array(true_ll), np.array(wrong_ll)
    found = int((true_ll > THRESH).sum())
    print(
        f"check 3, planted keys: {found}/{len(true_ll)} above the threshold {THRESH:.0f}; "
        f"true key LL {true_ll.mean():.0f} +- {true_ll.std(ddof=1):.0f} "
        f"(worst {true_ll.min():.0f}), base_0 runes recovered "
        f"{np.mean(recovered):.1f}/29 (worst {min(recovered)})"
    )
    print(
        f"         wrong space wheel on the same ciphertext: LL {wrong_ll.mean():.0f} "
        f"+- {wrong_ll.std(ddof=1):.0f} (best {wrong_ll.max():.0f})"
    )
    assert found == len(true_ll), "the fit lost a planted key"
    assert wrong_ll.max() < THRESH, "a wrong key cleared the threshold"
    return {
        "planted_keys": len(true_ll),
        "planted_found": found,
        "planted_ll_mean": float(true_ll.mean()),
        "planted_ll_worst": float(true_ll.min()),
        "wrong_ll_mean": float(wrong_ll.mean()),
        "wrong_ll_best": float(wrong_ll.max()),
    }


# ---------------------------------------------------------------------------- sweep

_W: dict = {}


def _init(sigmas: np.ndarray) -> None:
    from quagmire_schedule_census import lp_words, observed_rates, wilson

    words, lens, idx2, cipher2, phases = corpus()
    lens_l = [int(x) for x in lens]
    obs = observed_rates(lp_words())
    lo1, hi1 = qr.D1_BAND if qr.D1_BAND else wilson(*obs[1])
    T1, _T4, _T6, _cross = qr.build_register(PROSE_CACHE, lens_l)
    _, table, floor = qr.load_register(PROSE_CACHE)
    _W.update(
        lens=lens,
        idx2=idx2,
        cipher2=cipher2,
        phases=phases,
        T1=T1,
        lo1=lo1,
        hi1=hi1,
        sigmas=sigmas,
        tab=table_array(table, floor),
    )


def _work(args):
    chunk_id, chunk = args
    w = _W
    tested = wheels = 0
    fp_hist = np.zeros(M + 1, dtype=np.int64)
    lls: list[float] = []
    cands = []
    for K, sched in qr.g_candidates(chunk, w["T1"], w["lo1"], w["hi1"], None):
        g = np.array(qr.letter_steps(K, sched), dtype=np.int64)
        fps = gate_fixed_points(g, w["sigmas"], w["phases"])
        wheels += 1
        tested += len(fps)
        fp_hist += np.bincount(fps, minlength=M + 1)
        g1inv = np.array(qr.inverse([int(v) for v in g[1]]), dtype=np.int64)
        for si in np.nonzero(fps >= MIN_FP)[0]:
            sigma = w["sigmas"][si]
            minv2 = inverse_products(g, sigma, w["lens"], w["idx2"])
            ll, b0 = fit(
                w["cipher2"],
                minv2,
                g1inv,
                w["tab"],
                RESTARTS,
                SEED + chunk_id + int(si),
            )
            lls.append(float(ll))
            if ll > THRESH:
                Mw = qr.word_products(
                    [list(map(int, r)) for r in g],
                    [int(v) for v in sigma],
                    [int(x) for x in w["lens"]],
                )
                cands.append(
                    {
                        "K": [int(v) for v in K],
                        "sched": [int(v) for v in sched],
                        "sigma": [int(v) for v in sigma],
                        "fp": int(fps[si]),
                        "bases": len({tuple(m) for m in Mw}),
                        "two_rune_ll": float(ll),
                        "base0": [int(v) for v in b0],
                    }
                )
    return tested, wheels, fp_hist, lls, cands


def sweep(nproc: int, every: int, checks: dict) -> None:
    from quagmire_schedule_census import lp_words

    _words, lens, _idx2, _cipher2, phases = corpus()
    lens_l = [int(x) for x in lens]
    vocab = vocabulary()
    _T1, _T4, _T6, cross = qr.build_register(PROSE_CACHE, lens_l)
    t0 = time.time()
    sigmas = np.array(qr.sigma_candidates(vocab, cross, *qr.SEAM_BAND), dtype=np.int64)
    distinct = len({tuple(s) for s in sigmas.tolist()})
    print(
        f"space wheels in the seam band {qr.SEAM_BAND}: {len(sigmas)} "
        f"({distinct} distinct) from {len(vocab):,} keywords, {time.time() - t0:.0f}s"
    )
    assert len(lp_words()) == len(lens)

    used = vocab[::every]
    nchunks = max(nproc * 60, 1)
    chunks = [(i, used[i::nchunks]) for i in range(nchunks)]
    tested = wheels = 0
    fp_hist = np.zeros(M + 1, dtype=np.int64)
    lls: list[float] = []
    cands: list[dict] = []
    t0 = time.time()
    with Pool(nproc, initializer=_init, initargs=(sigmas,)) as pool:
        for done, (tc, wc, fh, ll, cs) in enumerate(pool.imap_unordered(_work, chunks)):
            tested += tc
            wheels += wc
            fp_hist += fh
            lls.extend(ll)
            cands.extend(cs)
            if (done + 1) % 20 == 0 or done + 1 == nchunks:
                best = max(lls) if lls else float("nan")
                print(
                    f"  {done + 1}/{nchunks} chunks: {tested:,} keys, "
                    f"{len(lls):,} through the gate, {len(cands)} candidates, "
                    f"best LL {best:.0f}, {time.time() - t0:.0f}s",
                    flush=True,
                )
    dt = time.time() - t0
    arr = np.array(lls)
    passed = len(arr)
    # the gate's pass rate against a uniformly random permutation: P(fixed points >= 6)
    poisson_tail = 1 - sum(np.exp(-1) / np.prod(np.arange(1, k + 1)) for k in range(6))
    genuine = [c for c in cands if c["bases"] >= 600]
    outcome = {
        "keywords": len(used),
        "keywords_in_dictionary": len(vocab),
        "slice": f"1/{every}",
        "space_wheels": len(sigmas),
        "space_wheels_distinct": distinct,
        "letter_wheels": wheels,
        "keys_tested": tested,
        "gate_min_fixed_points": MIN_FP,
        "gate_passed": passed,
        "gate_pass_rate": passed / tested if tested else 0.0,
        "gate_pass_rate_random_permutation": float(poisson_tail),
        "fixed_point_histogram": fp_hist.tolist(),
        "two_rune_ll_mean": float(arr.mean()) if passed else None,
        "two_rune_ll_sd": float(arr.std(ddof=1)) if passed > 1 else None,
        "two_rune_ll_best": float(arr.max()) if passed else None,
        "threshold": THRESH,
        "candidates": len(cands),
        "candidates_non_degenerate": len(genuine),
        "candidate_list": sorted(cands, key=lambda c: -c["two_rune_ll"])[:50],
        "hours": dt / 3600,
        "workers": nproc,
        "checks": checks,
    }
    if every == 1:
        OUT.write_text(json.dumps(outcome, indent=1) + "\n")
        print(f"\noutcome written to {OUT.relative_to(ROOT)}")
    print(
        f"\n{tested:,} complete keys ({wheels:,} letter wheels x {len(sigmas)} space "
        f"wheels) in {dt / 3600:.2f} h on {nproc} workers"
    )
    print(
        f"gate (>= {MIN_FP} fixed points): {passed:,} passed, rate "
        f"{outcome['gate_pass_rate']:.2e} against {poisson_tail:.2e} for a random "
        f"permutation; {int(fp_hist[M])} keys return exactly (29 fixed points)"
    )
    if passed:
        print(
            f"2-rune fit of the passers: LL {arr.mean():.0f} +- {arr.std(ddof=1):.0f}, "
            f"best {arr.max():.0f}; planted keys read "
            f"{checks['planted_ll_mean']:.0f} (worst {checks['planted_ll_worst']:.0f})"
        )
    coverage = "the whole candidate set" if every == 1 else f"a 1/{every} slice"
    if genuine:
        print(
            f"VERDICT: {len(genuine)} non-degenerate candidates above {THRESH:.0f} on "
            f"{coverage}; decrypt them before anything else."
        )
    elif cands:
        print(
            f"VERDICT: {len(cands)} candidates above {THRESH:.0f}, all degenerate "
            f"(fewer than 600 bases), on {coverage}. No key of the family survives."
        )
    else:
        print(
            f"VERDICT: no key above {THRESH:.0f} on {coverage}. Negative for the "
            f"keyword Quagmire walk inside these bands, conditional on DJU-BEI being a "
            f"state return (dju-bei-gate-validity.md)."
            if every == 1
            else f"VERDICT: no key above {THRESH:.0f} on {coverage}."
        )


def main() -> None:
    rng = random.Random(SEED)
    if not PROSE_CACHE.exists():
        import urllib.request

        from ea_direction_test import PROSE_URL

        urllib.request.urlretrieve(PROSE_URL, PROSE_CACHE)
    checks = check(rng)
    if "--sweep" not in sys.argv:
        print("checks only. pass --sweep N [--every k] for the enumeration.")
        return
    nproc = int(sys.argv[sys.argv.index("--sweep") + 1])
    every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 1
    sweep(nproc, every, checks)


if __name__ == "__main__":
    main()
