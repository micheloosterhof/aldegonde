#!/usr/bin/env python3
# ABOUTME: Can sigma be arithmetic? Minimum achievable seam-doublet rate for
# ABOUTME: additive / multiplicative / affine / Beaufort / inverse families on
# ABOUTME: the CROSS-word plaintext bigram table, vs the observed 0.0079.
"""Is the space step sigma an arithmetic map?

At a seam the walk gives c_last = psi(p_last) and c_first =
psi(sigma(p_first)) with a common psi, so a cross-word doublet occurs iff
    p_last = sigma(p_first)
and the observed seam rate 23/2927 = 0.0079 IS sigma's diagonal measured
on the cross-word plaintext table T[p_last][p_first] — a different table
from g's within-word adjacent bigrams (word-final and word-initial
letter distributions are very unlike each other in English, so the known
"affine cannot beat 1.25%" result for g does not carry over).

For each arithmetic family this computes the minimum achievable
    D(sigma) = sum_x T[sigma(x)][x]
and compares it with the observed 0.0079. A family whose floor lies
above the observation cannot supply sigma. Reference points: the
unconstrained permutation floor (Hungarian assignment) and the mean over
random permutations.

Same computation is run for g on the within-word table, reproducing the
documented affine floor as a cross-check.
"""

from __future__ import annotations

import itertools
import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402

M = 29
INV = {a: pow(a, M - 2, M) for a in range(1, M)}


def tables(lp_lens, pools, rng, samples=30):
    """Cross-word (last, first) and within-word adjacent bigram tables."""
    cross = np.zeros((M, M))
    within = np.zeros((M, M))
    for _ in range(samples):
        words = []
        for L in lp_lens:
            LL = L
            while LL not in pools and max(pools) > LL:
                LL += 1
            words.append(rng.choice(pools[LL])[:L])
        for i, w in enumerate(words):
            for j in range(len(w) - 1):
                within[w[j]][w[j + 1]] += 1
            if i + 1 < len(words):
                cross[w[-1]][words[i + 1][0]] += 1
    return cross / cross.sum(), within / within.sum()


def diag(T, perm):
    return sum(T[perm[x]][x] for x in range(M))


def families():
    """(name, iterable of permutations) for each arithmetic family."""
    yield ("additive  x+b", [[(x + b) % M for x in range(M)] for b in range(M)])
    yield ("multiplicative a*x", [[(a * x) % M for x in range(M)] for a in range(1, M)])
    yield ("beaufort   b-x", [[(b - x) % M for x in range(M)] for b in range(M)])
    aff = [[(a * x + b) % M for x in range(M)] for a in range(1, M) for b in range(M)]
    yield ("affine   a*x+b", aff)
    invs = []
    for a in range(1, M):
        for b in range(M):
            p = [(a * INV[x] + b) % M if x else b for x in range(M)]
            if len(set(p)) == M:
                invs.append(p)
    yield ("inverse a/x+b", invs)


def report(name, T, observed):
    print(f"\n{name} (observed diagonal {observed:.4f}):")
    print(f"  {'family':<20} {'min':>8} {'max':>8} {'verdict':>28}")
    for fname, fam in families():
        vals = [diag(T, p) for p in fam]
        lo, hi = min(vals), max(vals)
        verdict = "CANNOT reach observed" if lo > observed else "can reach observed"
        print(f"  {fname:<20} {lo:>8.4f} {hi:>8.4f} {verdict:>28}")
    row, col = linear_sum_assignment(T.T)
    perm = [0] * M
    for x, y in zip(row, col):
        perm[x] = y
    floor = sum(T[perm[x]][x] for x in range(M))
    rng2 = random.Random(7)
    rnd = []
    for _ in range(2000):
        p = list(range(M))
        rng2.shuffle(p)
        rnd.append(diag(T, p))
    print(
        f"  {'unconstrained perm':<20} {floor:>8.4f} {'':>8} "
        f"{'(assignment-problem floor)':>28}"
    )
    print(
        f"  {'random permutation':<20} {np.mean(rnd):>8.4f} "
        f"{'':>8} {'(mean; sd ' + f'{np.std(rnd):.4f})':>28}"
    )


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    words = [d[k] for k in sorted(d)]
    lens = [len(w) for w in words]

    seam_d = sum(1 for i in range(len(words) - 1) if words[i][-1] == words[i + 1][0])
    within_d = sum(1 for w in words for i in range(len(w) - 1) if w[i] == w[i + 1])
    within_n = sum(len(w) - 1 for w in words)
    print(
        f"LP: seam doublets {seam_d}/{len(words) - 1} = "
        f"{seam_d / (len(words) - 1):.4f}; within-word {within_d}/{within_n}"
        f" = {within_d / within_n:.4f}"
    )

    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    if not prose_path.exists():
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if r:
            pools.setdefault(len(r), []).append(r)
    cross, within = tables(lens, pools, rng)

    print(
        "\ncross-word table shape: word-final vs word-initial marginals "
        "differ strongly in English"
    )
    fin = cross.sum(1)
    ini = cross.sum(0)

    def top(v):
        return ", ".join(f"{i}:{v[i]:.3f}" for i in np.argsort(v)[::-1][:5])

    print(f"  most common finals (index:freq):  {top(fin)}")
    print(f"  most common initials(index:freq): {top(ini)}")

    report("SIGMA on the cross-word table", cross, seam_d / (len(words) - 1))
    report("G on the within-word table", within, within_d / within_n)

    # Could the period-5 step be a 5-letter VIGENERE (shift schedule)
    # rather than a mixed permutation? Then a ciphertext doublet occurs
    # exactly when the plaintext adjacent delta equals one phase-specific
    # value, so the doublet rate is bounded below by the rarest delta.
    print("\n5-LETTER VIGENERE step (shift schedule) on the within-word table:")
    delta = np.zeros(M)
    for a in range(M):
        for b in range(M):
            delta[(b - a) % M] += within[a][b]
    ph: Counter = Counter()
    for x in words:
        for j in range(1, len(x)):
            ph[j % 5] += 1
    tot = sum(ph.values())
    wgt = [ph[p] / tot for p in range(5)]
    rarest = float(delta.min())  # ty: ignore[invalid-argument-type]  # numpy stub overload; ndarray.min is fine here
    best = (9.0, None)
    for combo in itertools.product(range(M), repeat=4):
        ds = combo + ((-sum(combo)) % M,)
        rate = sum(wgt[p] * delta[(-ds[p]) % M] for p in range(5))
        if rate < best[0]:
            best = (rate, ds)
    obs = within_d / within_n
    print(f"  rarest plaintext adjacent delta:      {rarest:.4f}")
    print(f"  best 5-shift schedule (sum=0 mod 29): {best[0]:.4f} shifts {best[1]}")
    print(f"  observed within-word doublet rate:    {obs:.4f}")
    print(
        f"  => shift schedules are {best[0] / obs:.1f}x too high; even "
        f"ignoring the\n     period-5 closure the floor is "
        f"{rarest:.4f} ({rarest / obs:.1f}x). A Vigenere step cannot\n"
        f"     supply the suppression — English has no delta rare enough."
    )


if __name__ == "__main__":
    main()
