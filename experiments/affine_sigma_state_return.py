# ABOUTME: Tests sigma = affine map (a*x + b mod 29) against the DJU-BEI 6-point
# ABOUTME: state return, over the magic-square g survivor pool (Michel's proposal).
"""Can the space step sigma be affine?

`length-clocked-walk.md` leaves sigma a free mixed permutation with no
construction, which blocks the evaluation of every g construction
(`magic-square-grid-key.md`). Michel's proposal: sigma(x) = a*x + b mod 29 on
the rune index -- 812 candidates, Cicada's own arithmetic idiom. Note the same
family cannot supply g (no affine map has order 5 since 5 divides neither 28
nor 29), so the design would be grid-g + arithmetic-sigma.

Prior strike, register-dependent: `sigma_algebraic_floor.py` floors the affine
family's seam diagonal at 0.0122 on the reference cross-word table vs the
observed 23/2927 = 0.0079 -- the BEST affine member sits ~2 sigma high, the
bulk far higher. This test is independent of that table: the DJU-BEI return is
register-free.

**Filter.** Same ciphertext at word 1477 and 2926 forces base_1477 and
base_2926 to agree on the 6 plaintext-image points of the phrase, i.e. the
interval product Q = prod_{w in [1477,2926)} g^((L_w-1)%5) o sigma must fix
at least 6 points. (Full identity is the retracted too-strict reading -- see
`repeated-phrase-dju-bei.md`.) For an unrelated permutation the fixed-point
count is ~Poisson(1), so P(>=6) ~ 5.9e-4; the empirical null is measured here
over random order-5 g x the same 812 sigmas.

Convention matches walk_verifier.py / phase_absorbing_walk.py:
  base_{w+1} = base_w o g^((L-1)%5) o sigma, permutations as arrays,
  (f o h)[x] = f[h[x]].

Self-test cross-validates the vectorized interval product against
walk_verifier.step_products and calibrates the null.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from magic_square_sweep import survivor_pool  # noqa: E402
from walk_verifier import (  # noqa: E402
    BEI,
    DJU,
    M,
    dewalk_perms,
    inverse,
    load_quadgrams,
    load_words,
    order,
    perm_from_cycles,
    ppow,
    step_products,
)

POOL_SIGMA = 3.5  # retains a true family g with probability 1.00 (sweep table)
MIN_FIX = 6  # points DJU-BEI forces the interval product to fix
NULL_G = 300  # random order-5 g's for the empirical null


def affine_sigmas() -> tuple[np.ndarray, list[tuple[int, int]]]:
    """All 812 affine permutations of Z/29, as a (812, 29) array plus (a, b)."""
    x = np.arange(M)
    perms = []
    ab = []
    for a in range(1, M):
        for b in range(M):
            perms.append((a * x + b) % M)
            ab.append((a, b))
    return np.array(perms), ab


def interval_fixed_counts(
    g: np.ndarray, sigmas: np.ndarray, lengths: list[int]
) -> np.ndarray:
    """Fixed-point count of the [DJU, BEI) interval product for each sigma.

    Q is folded exactly as walk_verifier.step_products folds M_w:
    cur = cur o step, step = g^((L-1)%5) o sigma."""
    gpow = [ppow(g, k) for k in range(5)]
    steps = np.array([gp[sigmas] for gp in gpow])  # (5, Nsig, M)
    cur = np.broadcast_to(np.arange(M), sigmas.shape).copy()
    for length in lengths[DJU:BEI]:
        cur = np.take_along_axis(cur, steps[(length - 1) % 5], axis=1)
    return (cur == np.arange(M)).sum(axis=1)


def quad_table() -> np.ndarray:
    """walk_verifier's quadgram log-probs as a dense (29,29,29,29) array; every
    absent quadgram holds the same floor, so values match the dict exactly."""
    logp, floor = load_quadgrams()
    t = np.full((M, M, M, M), floor)
    for k, v in logp.items():
        t[k] = v
    return t


def quad_fitness(p: np.ndarray, qt: np.ndarray) -> float:
    """Mean log10 quadgram probability of a decrypted rune stream."""
    return float(qt[p[:-3], p[1:-2], p[2:-1], p[3:]].mean())


def solve_base0_fast(
    cipher: np.ndarray,
    D: np.ndarray,
    qt: np.ndarray,
    rng: random.Random,
    restarts: int = 8,
    iters: int = 20000,
) -> tuple[float, np.ndarray]:
    """walk_verifier.solve_base0 with the vectorized fitness: hill-climb the
    outer monoalphabetic base0inv on quadgram fitness of the full decryption."""
    n = len(cipher)
    pos = np.arange(n)

    def fitness(b: np.ndarray) -> float:
        return quad_fitness(D[pos, b[cipher]], qt)

    best_fit, best_b = -1e9, np.arange(M)
    for _ in range(restarts):
        b = np.array(rng.sample(range(M), M))
        f = fitness(b)
        for _ in range(iters):
            x, y = rng.randrange(M), rng.randrange(M)
            if x == y:
                continue
            b[[x, y]] = b[[y, x]]
            nf = fitness(b)
            if nf >= f:
                f = nf
            else:
                b[[x, y]] = b[[y, x]]
        if f > best_fit:
            best_fit, best_b = f, b.copy()
    return best_fit, best_b


def selftest() -> None:
    rng = random.Random(20260817)
    lengths = [len(w) for w in load_words()]
    sigmas, _ab = affine_sigmas()

    ok = True
    for _ in range(5):
        g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
        pick = rng.randrange(len(sigmas))
        counts = interval_fixed_counts(g, sigmas[pick : pick + 1], lengths)
        Ms = step_products(g, sigmas[pick], lengths)
        ref = int((Ms[DJU] == Ms[BEI]).sum())
        ok &= int(counts[0]) == ref
    print(f"self-test: vectorized fold matches step_products agreement? {ok}")

    logp, floor = load_quadgrams()
    qt = quad_table()
    fit_ok = True
    for _ in range(5):
        p = np.array([rng.randrange(M) for _ in range(500)])
        ref_fit = sum(
            logp.get((int(p[i]), int(p[i + 1]), int(p[i + 2]), int(p[i + 3])), floor)
            for i in range(len(p) - 3)
        ) / (len(p) - 3)
        fit_ok &= abs(quad_fitness(p, qt) - ref_fit) < 1e-12
    print(f"self-test: dense quadgram fitness matches walk_verifier's dict? {fit_ok}")
    if not (ok and fit_ok):
        msg = "self-test FAILED"
        raise SystemExit(msg)


def empirical_null(lengths: list[int], sigmas: np.ndarray) -> tuple[float, list[int]]:
    """P(fix >= MIN_FIX) for random order-5 g against the same affine sigmas."""
    rng = random.Random(4242)
    hist = [0] * (M + 1)
    hits = 0
    for _ in range(NULL_G):
        g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
        counts = interval_fixed_counts(g, sigmas, lengths)
        for c in counts:
            hist[c] += 1
        hits += int((counts >= MIN_FIX).sum())
    return hits / (NULL_G * len(sigmas)), hist


def main() -> None:
    lengths = [len(w) for w in load_words()]
    sigmas, ab = affine_sigmas()

    print(f"magic-square g pool at {POOL_SIGMA} sigma ...")
    pool = survivor_pool(POOL_SIGMA)
    print(f"  {len(pool)} g candidates x {len(sigmas)} affine sigmas")

    rate, hist = empirical_null(lengths, sigmas)
    poisson6 = 1 - math.exp(-1) * sum(1 / math.factorial(k) for k in range(MIN_FIX))
    print(
        f"null: P(fix >= {MIN_FIX}) = {rate:.2e} over {NULL_G} random order-5 g "
        f"(Poisson(1) reference {poisson6:.2e})"
    )
    tail = {k: hist[k] for k in range(len(hist)) if hist[k] and k >= MIN_FIX - 2}
    print(f"null fixed-point tail: {tail}")

    expected = rate * len(pool) * len(sigmas)
    survivors = []
    best = (-1, None)
    for g, fixed, rot, by_col in pool:
        assert order(g) == 5
        counts = interval_fixed_counts(g, sigmas, lengths)
        top = int(counts.max())
        if top > best[0]:
            best = (top, (fixed, rot, by_col, ab[int(counts.argmax())]))
        for i in np.flatnonzero(counts >= MIN_FIX):
            survivors.append((fixed, rot, by_col, ab[int(i)], int(counts[i])))

    print(
        f"\n{len(pool) * len(sigmas):,} (g, sigma) pairs -> "
        f"{len(survivors)} with fix >= {MIN_FIX} (chance expects {expected:.1f})"
    )
    for fixed, rot, by_col, (a, b), c in survivors:
        full = " FULL RETURN" if c == M else ""
        print(
            f"  fix={c}{full}  sigma=({a}x+{b})  "
            f"g: fixed={fixed} rot={rot} {'col' if by_col else 'row'}"
        )
    if not survivors:
        top, info = best
        print(f"  best pair reached fix={top}: g={info[:3]} sigma=(ax+b)={info[3]}")


def preview(p: np.ndarray, n: int = 90) -> str:
    from aldegonde import c3301

    return "".join(c3301.CICADA_ENGLISH_ALPHABET[i] for i in p[:n])


def solve_pair(
    g: np.ndarray,
    sigma: np.ndarray,
    words: list[list[int]],
    qt: np.ndarray,
    rng: random.Random,
) -> tuple[float, np.ndarray]:
    lengths = [len(w) for w in words]
    Ms = step_products(g, sigma, lengths)
    cipher = np.array([r for w in words for r in w])
    D = dewalk_perms(g, Ms, words)
    fit, b = solve_base0_fast(cipher, D, qt, rng)
    p = D[np.arange(len(cipher)), b[cipher]]
    return fit, p


def verify() -> None:
    import json

    rng = random.Random(20260817)
    qt = quad_table()

    # positive + negative control on the known-key reference corpus
    ref = json.loads((Path(__file__).parent / "walk_reference.json").read_text())
    ref_words = ref["ciphertext_words"]
    ref_plain = np.array([r for w in ref["plaintext_words"] for r in w])
    g_true = np.array(ref["g"])
    sigma_true = np.array(ref["sigmas"][0])
    base0inv_true = inverse(np.array(ref["base0"]))

    lengths = [len(w) for w in ref_words]
    Ms = step_products(g_true, sigma_true, lengths)
    cipher = np.array([r for w in ref_words for r in w])
    D = dewalk_perms(g_true, Ms, ref_words)
    decrypt_true = D[np.arange(len(cipher)), base0inv_true[cipher]]
    print(
        f"reference round-trip with true key exact? "
        f"{np.array_equal(decrypt_true, ref_plain)}"
    )
    true_fit = quad_fitness(decrypt_true, qt)
    solved_fit, _p = solve_pair(g_true, sigma_true, ref_words, qt, rng)
    sigmas, _ab = affine_sigmas()
    wrong_fit, _p = solve_pair(
        g_true, sigmas[rng.randrange(len(sigmas))], ref_words, qt, rng
    )
    print(
        f"reference: true-base0 fitness {true_fit:.3f}, "
        f"solved-with-true-(g,sigma) {solved_fit:.3f}, "
        f"solved-with-wrong-sigma {wrong_fit:.3f}"
    )

    # the LP survivors
    words = load_words()
    lp_lengths = [len(w) for w in words]
    print(f"\nmagic-square g pool at {POOL_SIGMA} sigma ...")
    pool = survivor_pool(POOL_SIGMA)
    survivors = []
    for g, fixed, rot, by_col in pool:
        counts = interval_fixed_counts(g, sigmas, lp_lengths)
        for i in np.flatnonzero(counts >= MIN_FIX):
            survivors.append((g, sigmas[int(i)], fixed, rot, by_col, _ab[int(i)]))
    print(f"{len(survivors)} survivors to solve; null band from 6 random controls")

    null_fits = []
    for _ in range(6):
        g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
        f, _p = solve_pair(g, sigmas[rng.randrange(len(sigmas))], words, qt, rng)
        null_fits.append(f)
    print(
        f"LP null band: {min(null_fits):.3f} .. {max(null_fits):.3f} "
        f"(mean {sum(null_fits) / len(null_fits):.3f})"
    )

    results = []
    for g, sigma, fixed, rot, by_col, (a, b) in survivors:
        f, p = solve_pair(g, sigma, words, qt, rng)
        results.append((f, fixed, rot, by_col, a, b, p))
    results.sort(reverse=True, key=lambda r: r[0])
    print("\nsurvivors by solved base0 fitness:")
    for f, fixed, rot, by_col, a, b, _p in results:
        print(
            f"  {f:.3f}  sigma=({a}x+{b})  g: fixed={fixed} rot={rot} "
            f"{'col' if by_col else 'row'}"
        )
    print("\ntop-3 decryption previews (transliterated):")
    for f, _fixed, _rot, _by_col, a, b, p in results[:3]:
        print(f"  [{f:.3f} ({a}x+{b})] {preview(p)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    elif args.verify:
        verify()
    else:
        main()
