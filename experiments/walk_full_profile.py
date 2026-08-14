# ABOUTME: Runs the jointly-fitted (g, sigma) walk through full corpus-sized
# ABOUTME: simulation and compares every profile cell against the LP, with bands.
"""Does the joint-fit key survive an actual corpus-sized simulation?

d4_d6_prediction.py showed a single order-5 g reaches the LP's full d1..d6
within-word profile -- but at pair-table level (rate arithmetic on the
distance-d tables), never dropped into encipher() for a full run. This
experiment closes that gap and produces the reference artifact the attack
machinery has been missing.

Design, per the review of 2026-08-14:
- g is fitted to the LP's OBSERVED d1..d6 rates on pair tables built from
  the same plaintext register that is enciphered, inverse-variance
  weighted. The register is CONSECUTIVE PROSE carried into runeglish
  (period5_confirmation.prose_words): a Markov-2 trigram generator lacks
  the distance-4..6 skip-gram structure the d4/d6 cells depend on
  (mechanism_discriminator.py records this; the trigram fit below
  quantifies it), and independently-drawn dictionary words lack the
  word-ORDER structure the seam depends on (their cross table is a
  product of marginals, sigma floor ~0.015 > the 0.0079 target). Only
  running text supplies both. d5 is not a fit target: g^5 = id makes that
  cell the plaintext's own lag-5 rate -- the known register residual,
  reported but not tuned.
- sigma is tuned on the CROSS-word (last-rune, first-rune) table, where the
  seam condition p_last = sigma(p_first) actually lives.
- Each replicate corpus is a random contiguous window of 2,928 prose words
  (natural lengths; windows may overlap, so replicate spread slightly
  understates plaintext variance -- key, base0 and stepkey are fresh each
  time).
- The reference replicate is self-validating: round-trip decipher, and the
  within/seam match conditions checked against their plaintext-side
  algebra exactly (the planted-key verification, repeated here).

Output: cell-by-cell LP vs simulated mean +- sd over replicates, with the
LP binomial error carried into each z. Artifact: walk_reference.json
(key, lengths, plaintext, ciphertext) for crib-propagation validation.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from lp_corpus import load_clean
from period5_confirmation import prose_words
from stay_slot_cipher import (
    M,
    battery,
    diag_rate,
    gen_plaintext,
    load_trigram,
    pair_matrices,
    perm_from_cycles,
    ppow,
    tune,
)

SEED = 3301
REPLICATES = 100
FIT_COPIES = 10
ARTIFACT = Path(__file__).resolve().parent / "walk_reference.json"


def lp_lengths_and_cells() -> tuple[list[int], dict[str, tuple[float, int, int]]]:
    """LP word lengths plus observed (rate, matches, pairs) per profile cell."""
    stream, wid = load_clean()
    lengths: list[int] = []
    for i, w in enumerate(wid):
        if i == 0 or w != wid[i - 1]:
            lengths.append(0)
        lengths[-1] += 1
    cells: dict[str, tuple[float, int, int]] = {}
    for d in range(1, 7):
        for same in (True, False):
            if not same and d not in (1, 5):
                continue
            m = e = 0
            for i in range(len(stream) - d):
                if (wid[i] == wid[i + d]) == same:
                    e += 1
                    m += stream[i] == stream[i + d]
            key = f"d{d}{'w' if same else 'x'}"
            cells[key] = (m / e, m, e)
    return lengths, cells


def cut_to_lengths(stream: list[int], lengths: list[int]) -> list[list[int]]:
    words, i = [], 0
    for length in lengths:
        words.append(stream[i : i + length])
        i += length
    return words


def cross_matrix(words: list[list[int]]) -> list[list[float]]:
    """P[last][first] over adjacent word pairs."""
    mat = [[0.0] * M for _ in range(M)]
    tot = 0
    for k in range(len(words) - 1):
        mat[words[k][-1]][words[k + 1][0]] += 1
        tot += 1
    return [[c / tot for c in row] for row in mat]


def encipher(words, g, base0, sigmas, stepkey):
    gp = [ppow(g, k) for k in range(5)]
    base = base0[:]
    out = []
    for wi, w in enumerate(words):
        out.append([base[gp[j % 5][p]] for j, p in enumerate(w)])
        a = (len(w) - 1) % 5
        sig = sigmas[stepkey[wi]]
        step = [gp[a][sig[x]] for x in range(M)]
        base = [base[step[x]] for x in range(M)]
    return out


def decipher(ct_words, g, base0, sigmas, stepkey):
    inv = lambda p: [p.index(x) for x in range(M)]  # noqa: E731
    gp = [ppow(g, k) for k in range(5)]
    gpi = [inv(q) for q in gp]
    base = base0[:]
    out = []
    for wi, cw in enumerate(ct_words):
        binv = inv(base)
        out.append([gpi[j % 5][binv[c]] for j, c in enumerate(cw)])
        a = (len(cw) - 1) % 5
        sig = sigmas[stepkey[wi]]
        step = [gp[a][sig[x]] for x in range(M)]
        base = [base[step[x]] for x in range(M)]
    return out


def measure(ct_words) -> dict[str, tuple[int, int]]:
    stream = [x for w in ct_words for x in w]
    wid = []
    for i, w in enumerate(ct_words):
        wid += [i] * len(w)
    cells = {}
    for d in range(1, 7):
        for same in (True, False):
            if not same and d not in (1, 5):
                continue
            m = e = 0
            for i in range(len(stream) - d):
                if (wid[i] == wid[i + d]) == same:
                    e += 1
                    m += stream[i] == stream[i + d]
            cells[f"d{d}{'w' if same else 'x'}"] = (m, e)
    return cells


def main() -> None:
    rng = random.Random(SEED)
    lengths, lp = lp_lengths_and_cells()
    nrunes = sum(lengths)
    print(f"LP: {nrunes} runes, {len(lengths)} words")
    print("cell   LP rate  (m/e)")
    for k, (r, m, e) in lp.items():
        print(f"  {k}  {r:.4f}  ({m}/{e})")

    # two registers: consecutive prose (primary) and Markov-2 trigram
    # (comparison -- documents that its tables cannot reach d4/d6)
    prose = prose_words()

    trigram = load_trigram()
    tri_words = []
    for _ in range(FIT_COPIES):
        tri_words += cut_to_lengths(gen_plaintext(trigram, nrunes, rng), lengths)

    # inverse-variance weights from the LP cell errors
    def w(cell):
        r, _, e = lp[cell]
        return 1.0 / (r * (1 - r) / e)

    fit_cells = ["d1w", "d2w", "d3w", "d4w", "d6w"]

    def fit_g(mats):
        def g_obj(g):
            v = 0.0
            acc = g
            for d in range(1, 7):
                if d > 1:
                    acc = [g[x] for x in acc]
                cell = f"d{d}w"
                if cell in fit_cells:
                    v += w(cell) * (diag_rate(mats[d][0], acc) - lp[cell][0]) ** 2
            return v

        return min(
            (
                tune(perm_from_cycles([5] * 5 + [1] * 4, rng), g_obj, rng, iters=30000)
                for _ in range(6)
            ),
            key=g_obj,
        )

    def report_fit(label, mats, g):
        acc = g
        print(f"fitted g on {label} tables (target = LP):")
        for d in range(1, 7):
            if d > 1:
                acc = [g[x] for x in acc]
            tag = "" if f"d{d}w" in fit_cells else "  [not a fit target]"
            print(
                f"  d{d}w  {diag_rate(mats[d][0], acc):.4f}"
                f"  (LP {lp[f'd{d}w'][0]:.4f}){tag}"
            )

    tri_mats = pair_matrices(tri_words, dmax=6)
    report_fit("trigram-register", tri_mats, fit_g(tri_mats))

    mats = pair_matrices(prose, dmax=6)
    xmat = cross_matrix(prose)
    g = fit_g(mats)
    report_fit("prose-register", mats, g)

    seam_target = lp["d1x"][0]

    def s_obj(s):
        return (diag_rate(xmat, s) - seam_target) ** 2

    # ONE sigma: the standing model's key is small and fixed (g, sigma, base0)
    # with the schedule clocked by the public word lengths -- no per-word
    # key freedom. sigmas/stepkey retain their plural shape for the
    # artifact format, but stepkey is constant zero.
    sigmas = [
        min(
            (
                tune(perm_from_cycles([9, 7, 7, 3, 3], rng), s_obj, rng, iters=15000)
                for _ in range(3)
            ),
            key=s_obj,
        )
    ]
    print(
        f"sigma diagonal on cross table: "
        f"{diag_rate(xmat, sigmas[0]):.4f} (LP {seam_target:.4f})"
    )

    # replicate corpora: key fixed, plaintext / base0 / stepkey resampled
    sums: dict[str, list[float]] = {k: [] for k in lp}
    reference = None
    for rep in range(REPLICATES):
        start = rng.randrange(len(prose) - len(lengths))
        words = prose[start : start + len(lengths)]
        base0 = list(range(M))
        rng.shuffle(base0)
        stepkey = [0] * len(words)
        ct = encipher(words, g, base0, sigmas, stepkey)
        for k, (m, e) in measure(ct).items():
            sums[k].append(m / e)
        if rep == 0:
            reference = (words, base0, stepkey, ct)

    # self-validation on the reference replicate
    words, base0, stepkey, ct = reference
    assert decipher(ct, g, base0, sigmas, stepkey) == words, "round-trip failed"
    # seam condition: ciphertext seam doublet <=> p_last == sigma(p_first)
    seam_ok = all(
        (ct[k][-1] == ct[k + 1][0])
        == (words[k][-1] == sigmas[stepkey[k]][words[k + 1][0]])
        for k in range(len(words) - 1)
    )
    # within condition at d: match <=> p_i == g^d(p_{i+d})
    gpow = {d: ppow(g, d) for d in range(1, 7)}
    within_ok = all(
        (cw[i] == cw[i + d]) == (pw[i] == gpow[d][pw[i + d]])
        for d in range(1, 7)
        for pw, cw in zip(words, ct)
        for i in range(len(pw) - d)
    )
    # halt before writing the artifact if the algebra the crib validation
    # relies on does not hold -- these must be exact, not advisory
    assert seam_ok, "seam algebra violated"
    assert within_ok, "within-word algebra violated"
    print("reference replicate: round-trip OK, seam + within algebra exact")

    print("cell   LP        sim mean +- sd     z(combined)")
    for k, (r, _m, e) in lp.items():
        vals = sums[k]
        mu = sum(vals) / len(vals)
        sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / len(vals))
        lp_sd = math.sqrt(r * (1 - r) / e)
        z = (r - mu) / math.sqrt(sd * sd + lp_sd * lp_sd)
        note = "" if f"{k}" != "d5w" else "  [register residual, untuned]"
        print(f"  {k}  {r:.4f}   {mu:.4f} +- {sd:.4f}   {z:+.2f}{note}")

    battery("REFERENCE REPLICATE", ct)

    ARTIFACT.write_text(
        json.dumps(
            {
                "g": g,
                "sigmas": sigmas,
                "base0": base0,
                "stepkey": stepkey,
                "plaintext_words": words,
                "ciphertext_words": ct,
            }
        )
    )
    print(f"reference key + corpus saved to {ARTIFACT.name}")


if __name__ == "__main__":
    main()
