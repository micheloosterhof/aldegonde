# ABOUTME: Scores a generative cipher against every measurable LP property at once,
# ABOUTME: separating the cells a model was tuned on from the ones it actually predicts.
"""Does a candidate algorithm reproduce the corpus, or only the cells it was fitted to?

`walk_full_profile.py` reports that one fitted key lands every hard cell within noise,
and then says the quiet part: most of those cells are "near-tautological
confirmations", because the fitted `g`'s within-word rate at distance d IS the
diagonal it was fitted to. Only two cells there are free, and the one falsifiable cell
misses by 15%.

A crib test, or any key search, is only as good as the model it assumes. So before
either, a model has to be scored on what it PREDICTS. This battery measures the LP and
a generator on the same 18 statistics and tags each cell:

  fitted     the model's parameters were chosen against this number
  free       nothing in the fitting touched it

A model is worth attacking with only if the free cells land.

**Result (2026-09-20): a length-clocked walk CAN pass 12 of its 13 free cells, but
the fitted diagonals do not pin such a key.** Across five independently fitted keys,
all non-degenerate (2,928 distinct bases each), the number of failing free cells runs
from 1 to 6, and only the DJU-BEI repeat fails for every key:

    cell             tail across 5 keys        verdict
    d5w, d5x, triplets, long   0.13 - 0.73     passes for every key
    returns                    0.033           FAILS for every key
    ioc, entropy, bigram_chi2, kappa_max_z,
    doublet_pos, doublet_gap_min, identical, clock
                               0.000 - 0.97    borderline: flips with the key

That is a real constraint rather than a defect. The six fitted diagonals leave `g` and
sigma far from determined, and the free cells move with whatever else the fitting did
not touch -- so they carry additional key information, and a key search could use them
as filters. It also means no single fitted key settles the model: the honest claim is
that the walk FAMILY contains keys reproducing everything except the repeat.

One such key, fitted to d1-d4, d6 and the seam and scored on 60 prose corpora:

    cell              LP      model   two-sided tail
    d5w           0.0492     0.0562   0.367    the one cell g^5 = id forces
    d5x           0.0347     0.0371   0.067
    ioc           0.9999     0.9999   0.967    flat unigrams, not fitted
    entropy       4.8565     4.8564   0.900
    triplets           0        0.60  0.767
    bigram_chi2    841.2      804.3   0.400    off-diagonal uniformity
    kappa_max_z     2.908      4.147  0.233    no periodicity at skips 2-40
    doublet_pos    0.5532     0.4003  0.067    where doublets sit in the word
    doublet_gap_min     6       2.17  0.100
    returns             1       0.00  0.033  <== the only miss
    identical          17       9.82  0.100
    long                0       0.18  0.367
    clock          1.0071     1.0020  0.400

So this key is a validated generator for everything the corpus shows EXCEPT the
DJU-BEI repeat, which it never produces in 60 draws. Another fitted key may miss
several of the borderline cells above; the repeat is the only universal miss. Flat unigrams, maximal entropy,
the absence of triplets, off-diagonal bigram uniformity and the absence of periodicity
all come out free — none of them was fitted.

Four cells sit at p <= 0.1 where 1.3 are expected, and they pair up: doublet_pos with
doublet_gap_min (the fine structure of where doublets fall), identical with returns
(repeat structure). Neither pair is significant on its own and both are watch-items,
not failures. A first version of this table reported doublet_gap_min at z = 4.09; a
minimum is far from normal and its real tail is 0.100, which is why this battery
reports empirical tails.

**Verified 2026-09-20.** The battery accepts the walk (one free cell failing, the
DJU-BEI repeat) and rejects three mutants once each is scored against the set IT was
fitted on: sigma = g^2, seven free cells; a base that never advances, eight; an
independent base per word, which fails the seam at 0.0343 against 0.0079. That last
one passes if scored with the WALK's fitted set, which is the trap the constant above
now documents.

Run with no arguments for the self-test, `--walk` to score the length-clocked walk.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import (  # noqa: E402
    clock_reading,
    lp_words,
    prose_corpora,
    recurrence_counts,
)

M = 29
CHANCE = 1.0 / M

# Which cells a length-clocked walk is fitted on: g is chosen against the within-word
# distances and sigma against the seam. Everything else is a prediction.
#
# The fitted set belongs to the MODEL, not to this file, and the battery is only as
# honest as that declaration. Scoring a model that tunes no sigma with WALK_FITTED
# hides its seam failure: an independent base per word gives a seam of 0.0343 against
# the LP's 0.0079, which is fatal, and invisible if the seam is marked fitted. Always
# pass the set the model being scored was actually fitted on.
WALK_FITTED = {"d1w", "d2w", "d3w", "d4w", "d6w", "seam"}
G_ONLY_FITTED = {"d1w", "d2w", "d3w", "d4w", "d6w"}  # a model with no tuned sigma


def within_word(words, d: int) -> float:
    hits = total = 0
    for w in words:
        for j in range(len(w) - d):
            total += 1
            hits += w[j] == w[j + d]
    return hits / total if total else float("nan")


def cross_word_d5(words) -> float:
    """Distance-5 coincidence for pairs straddling a word boundary."""
    stream, wid = [], []
    for i, w in enumerate(words):
        stream += w
        wid += [i] * len(w)
    hits = total = 0
    for j in range(len(stream) - 5):
        if wid[j] != wid[j + 5]:
            total += 1
            hits += stream[j] == stream[j + 5]
    return hits / total if total else float("nan")


def fingerprint(words) -> dict[str, float]:
    """Every property the corpus fixes, measured the same way on any corpus."""
    stream = [r for w in words for r in w]
    n = len(stream)
    counts = np.bincount(stream, minlength=M)
    out: dict[str, float] = {}

    for d in range(1, 7):
        out[f"d{d}w"] = within_word(words, d)
    out["seam"] = sum(
        1 for a, b in zip(words, words[1:]) if a and b and a[-1] == b[0]
    ) / (len(words) - 1)
    out["d5x"] = cross_word_d5(words)

    out["ioc"] = float((counts * (counts - 1)).sum() / (n * (n - 1)) * M)
    p = counts / n
    out["entropy"] = float(-(p[p > 0] * np.log2(p[p > 0])).sum())
    out["triplets"] = float(
        sum(1 for i in range(n - 2) if stream[i] == stream[i + 1] == stream[i + 2])
    )

    # off-diagonal bigram uniformity: the corpus is flat there, doublets excepted
    big = np.zeros((M, M))
    for a, b in zip(stream, stream[1:]):
        big[a, b] += 1
    off = big[~np.eye(M, dtype=bool)]
    out["bigram_chi2"] = float(((off - off.mean()) ** 2 / off.mean()).sum())

    # periodicity: the largest coincidence departure over skips 2..40
    best = 0.0
    for skip in range(2, 41):
        hits = sum(1 for i in range(n - skip) if stream[i] == stream[i + skip])
        tot = n - skip
        z = (hits - tot * CHANCE) / math.sqrt(tot * CHANCE * (1 - CHANCE))
        best = max(best, abs(z))
    out["kappa_max_z"] = best

    # doublets: how they sit in the word, and how they space out
    positions, gaps, last = [], [], None
    for w in words:
        for j in range(len(w) - 1):
            if w[j] == w[j + 1]:
                positions.append(j / max(1, len(w) - 2) if len(w) > 2 else 0.5)
    for i in range(n - 1):
        if stream[i] == stream[i + 1]:
            if last is not None:
                gaps.append(i - last)
            last = i
    out["doublet_pos"] = float(np.mean(positions)) if positions else float("nan")
    out["doublet_gap_min"] = float(min(gaps)) if gaps else float("nan")

    counts_r = recurrence_counts(words)
    out["returns"] = float(counts_r["returns"])
    out["identical"] = float(counts_r["identical"])
    out["long"] = float(counts_r["long"])
    out["clock"] = clock_reading(words)
    return out


def compare(generator, draws: int, fitted: set[str], label: str) -> None:
    """Score a generator against the LP, cell by cell, tagging fitted versus free."""
    lp = fingerprint(lp_words())
    corpora = prose_corpora(2928, draws)
    rng = random.Random(3301)
    sims = [fingerprint(generator(plain, rng)) for plain in corpora]
    print(f"{label}: {draws} prose corpora\n")
    print(f"{'cell':<16}{'LP':>10}{'model':>11}{'spread':>10}{'z':>7}{'tail':>8}   tag")
    misses = []
    for key in lp:
        values = np.array([s[key] for s in sims])
        mean, sd = float(values.mean()), float(values.std())
        z = (lp[key] - mean) / sd if sd > 1e-12 else float("nan")
        # an empirical two-sided tail, because minima and counts are far from normal
        # and a z on them overstates the departure
        below = float((values <= lp[key]).mean())
        tail = 2 * min(below, 1 - below + 1.0 / len(values))
        tag = "fitted" if key in fitted else "FREE"
        flag = ""
        if tag == "FREE" and tail <= 0.05:
            flag = "  <== miss"
            misses.append((key, tail))
        print(
            f"{key:<16}{lp[key]:>10.4f}{mean:>11.4f}{sd:>10.4f}{z:>7.2f}{tail:>8.3f}"
            f"   {tag}{flag}"
        )
    free = [k for k in lp if k not in fitted]
    print(
        f"\n{len(free)} free cells, {len(sims)} draws (tail resolution "
        f"{2.0 / len(sims):.3f})"
    )
    if misses:
        print(
            "misses: "
            + ", ".join(
                f"{k} (p={t:.3f})" for k, t in sorted(misses, key=lambda x: x[1])
            )
        )
    else:
        print("no free cell departs at p <= 0.05")


def distance_tables(draws: int = 40) -> dict:
    """Within-word plaintext pair tables at distances 1..6, and the cross-word table."""
    tabs = {d: np.zeros((M, M)) for d in range(1, 7)}
    cross = np.zeros((M, M))
    for plain in prose_corpora(2928, draws):
        for w in plain:
            for d in range(1, 7):
                for j in range(len(w) - d):
                    tabs[d][w[j], w[j + d]] += 1
        for a, b in zip(plain, plain[1:]):
            if a and b:
                cross[a[-1], b[0]] += 1
    return {d: t / t.sum() for d, t in tabs.items()} | {"cross": cross / cross.sum()}


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def ppow(g, k):
    out = list(range(M))
    for _ in range(k):
        out = compose(g, out)
    return out


def rich_order5(rng):
    pts = rng.sample(range(M), 25)
    g = list(range(M))
    for c in range(5):
        cyc = pts[5 * c : 5 * c + 5]
        for t in range(5):
            g[cyc[t]] = cyc[(t + 1) % 5]
    return g


def diag(table, perm):
    return float(sum(table[perm[y], y] for y in range(M)))


def fit_walk_key(tabs, targets, rng, rounds=20000):
    """g fitted jointly to the within-word distances, sigma to the seam."""

    def cost(g):
        return sum(
            (diag(tabs[d], ppow(g, d % 5)) - targets[f"d{d}w"]) ** 2
            for d in (1, 2, 3, 4, 6)
        )

    g = rich_order5(rng)
    best = cost(g)
    for _ in range(rounds):
        a, b = rng.sample(range(M), 2)
        t = list(range(M))
        t[a], t[b] = b, a
        cand = [t[g[t[x]]] for x in range(M)]
        c = cost(cand)
        if c < best:
            g, best = cand, c
    sigma = list(range(M))
    rng.shuffle(sigma)
    s_best = abs(diag(tabs["cross"], sigma) - targets["seam"])
    for _ in range(rounds):
        cand = list(sigma)
        a, b = rng.sample(range(M), 2)
        cand[a], cand[b] = cand[b], cand[a]
        s = abs(diag(tabs["cross"], cand) - targets["seam"])
        if s < s_best:
            sigma, s_best = cand, s
    return g, sigma, best, s_best


def walk_generator(g, sigma):
    """base_{w+1} = base_w . g^((L-1) mod 5) . sigma, clocked by the word lengths."""
    gp = [ppow(g, k) for k in range(5)]

    def generate(plain, rng):
        base = list(range(M))
        rng.shuffle(base)
        out = []
        for w in plain:
            out.append([base[gp[j % 5][p]] for j, p in enumerate(w)])
            step = compose(gp[(len(w) - 1) % 5], sigma)
            base = compose(base, step)
        return out

    return generate


def self_test() -> None:
    lp = fingerprint(lp_words())
    print("LP fingerprint:")
    for k, v in lp.items():
        print(f"  {k:<16}{v:>10.4f}")
    assert abs(lp["d1w"] - 0.0063) < 5e-4, "within-word doublet rate off"
    assert abs(lp["seam"] - 0.0079) < 5e-4, "seam rate off"
    assert lp["triplets"] == 0, "the corpus has no triplets"
    assert abs(lp["ioc"] - 1.0) < 0.02, "unigrams should be flat"

    # the battery must call a plainly wrong model wrong: a monoalphabet keeps the
    # plaintext's own statistics, so many free cells should blow up
    def mono(plain, rng):
        key = list(range(M))
        rng.shuffle(key)
        return [[key[p] for p in w] for w in plain]

    corpora = prose_corpora(2928, 4)
    rng = random.Random(1)
    sims = [fingerprint(mono(p, rng)) for p in corpora]
    misses = sum(
        1
        for k in lp
        if np.std([s[k] for s in sims]) > 1e-12
        and abs((lp[k] - np.mean([s[k] for s in sims])) / np.std([s[k] for s in sims]))
        > 3
    )
    print(f"\nmonoalphabetic control: {misses} cells off by more than 3 sigma")
    assert misses >= 5, "the battery does not detect a plainly wrong model"
    print("self-test passed")


if __name__ == "__main__":
    if "--walk" in sys.argv:
        rng = random.Random(3301)
        lp = fingerprint(lp_words())
        tabs = distance_tables()
        g, sigma, gerr, serr = fit_walk_key(tabs, lp, rng)
        print(f"fitted g (residual {gerr:.2e}) and sigma (residual {serr:.2e})\n")
        compare(walk_generator(g, sigma), 60, WALK_FITTED, "length-clocked walk")
    else:
        self_test()
