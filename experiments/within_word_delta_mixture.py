#!/usr/bin/env python3
# ABOUTME: Discriminates copy vs additive key-sharing for the within-word d5 excess
# ABOUTME: via a 1-parameter delta-mixture model, projection test, and power analysis.
"""Discriminate key-sharing vs copy semantics for the within-word d=5 excess.

The within-word distance-5 match excess (4.92% vs 3.45%,
hypotheses/within-word-d5-coincidence.md) has two live interpretations:

- KEY-SHARING: within a word, positions k and k+5 see the same key
  element (per-word key state with a 5-cycle). Then
  (C[k+5]-C[k]) mod 29 = (P[k+5]-P[k]) mod 29 for the affected pairs, so
  the within-word delta histogram is the mixture  f*Q + (1-f)*U  where Q
  is the *plaintext* lag-5 within-word difference distribution and U is
  uniform. Real runeglish gives Q(0) ~ 1.8x uniform, so the observed
  0-bin excess implies f ~ 0.55 -- and Q's NONZERO structure (measured
  from two independent controls in plaintext_control_corpus.py) must
  leak into the nonzero bins at f ~ 0.55 too.
- COPY SEMANTICS: some pairs are literal glyph copies (back-references /
  nulls / stutters). Only the 0 bin is inflated:
  p_0 = e + (1-e)/29, p_b = (1-e)/29 -- nonzero bins stay flat.

This script fits both one-parameter models to the LP within-word delta
histogram by maximum likelihood, compares them (LR / AIC), runs the
optimal one-number test (projection of the nonzero-bin deviations onto
the Q-predicted direction, with a word-length permutation null that
preserves the rune stream byte-for-byte), and reports the power of that
test at the implied f (parametric bootstrap), so a null result is
interpretable.

Prerequisite: run experiments/plaintext_control_corpus.py first (writes
experiments/plaintext_control_stats.json).

Usage: python experiments/within_word_delta_mixture.py [n_perms]
"""

from __future__ import annotations

import json
import random
import sys

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
CONTROLS = "experiments/plaintext_control_stats.json"
WORD_BOUNDARIES = set("-.&%")
D = 5


def parse_clean_sections(path: str = DATA) -> list[list[list[int]]]:
    """Words per $-section, clean corpus (sections 0-9), as in
    experiments/within_word_d5.py."""
    with open(path) as f:
        text = f.read()
    sec_words: list[list[list[int]]] = [[]]
    cur: list[int] = []
    for ch in text:
        if ch in R2I:
            cur.append(R2I[ch])
        elif ch == "$":
            if cur:
                sec_words[-1].append(cur)
                cur = []
            sec_words.append([])
        elif ch in WORD_BOUNDARIES and cur:
            sec_words[-1].append(cur)
            cur = []
    if cur:
        sec_words[-1].append(cur)
    return [s for s in sec_words if s][:10]


def delta_hist(words: list[list[int]]) -> np.ndarray:
    h = np.zeros(MOD, dtype=np.int64)
    for w in words:
        for k in range(len(w) - D):
            h[(w[k + D] - w[k]) % MOD] += 1
    return h


def loglik(h: np.ndarray, p: np.ndarray) -> float:
    return float((h * np.log(p)).sum())


def fit_copy(h: np.ndarray) -> tuple[float, np.ndarray, float]:
    """ML fit of p0 = e + (1-e)/29, pb = (1-e)/29 (closed form)."""
    n = h.sum()
    p0_hat = h[0] / n
    e = max(0.0, (p0_hat - 1 / MOD) / (1 - 1 / MOD))
    p = np.full(MOD, (1 - e) / MOD)
    p[0] = e + (1 - e) / MOD
    return e, p, loglik(h, p)


def fit_mixture(h: np.ndarray, q: np.ndarray) -> tuple[float, np.ndarray, float]:
    """ML fit of p = f*q + (1-f)/29 by grid+refine on f."""
    best = (0.0, None, -np.inf)
    for f in np.linspace(0, 1, 2001):
        p = f * q + (1 - f) / MOD
        if (p <= 0).any():
            continue
        ll = loglik(h, p)
        if ll > best[2]:
            best = (float(f), p, ll)
    return best


def projection_stat(h: np.ndarray, q: np.ndarray) -> float:
    """Projection of nonzero-bin deviations onto the Q-predicted direction.

    Conditions on the nonzero total (so it is orthogonal to the 0-bin
    excess that both models explain): compares the observed nonzero
    histogram, normalized, against uniform along direction
    v = q_nonzero_normalized - uniform.
    """
    nz = h[1:].astype(float)
    n = nz.sum()
    obs = nz / n
    qq = q[1:] / q[1:].sum()
    u = 1 / (MOD - 1)
    v = qq - u
    return float(n * (v * (obs - u)).sum())


def main() -> None:
    n_perms = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    rng = random.Random(20260707)

    with open(CONTROLS) as f:
        controls = json.load(f)
    q_dom = np.array(controls["in_domain"]["Q"], dtype=float)
    q_dom /= q_dom.sum()
    if controls.get("lexicon") is None:
        print("(lexicon control absent -- using in-domain Q for the projection "
              "direction; install wordfreq and rerun plaintext_control_corpus.py "
              "for the frequency-weighted lexicon Q.)")
        q_lex = q_dom
    else:
        q_lex = np.array(controls["lexicon"]["Q"], dtype=float)
        q_lex /= q_lex.sum()

    sections = parse_clean_sections()
    words = [w for s in sections for w in s]
    h = delta_hist(words)
    n = int(h.sum())
    print(f"corpus: {len(words)} words, {n} within-word (k,k+{D}) pairs, "
          f"{h[0]} matches ({h[0]/n:.4f})")
    print("delta histogram (x29/uniform): "
          + " ".join(f"{MOD*v/n:.2f}" for v in h))

    # ---------------------------------------------------------- model fits
    u = np.full(MOD, 1 / MOD)
    ll_u = loglik(h, u)
    e, p_copy, ll_copy = fit_copy(h)
    f_lex, p_mix, ll_mix = fit_mixture(h, q_lex)
    f_dom, p_mixd, ll_mixd = fit_mixture(h, q_dom)
    print("\nlog-likelihoods (1-param models, same df):")
    print(f"  uniform            : {ll_u:.2f}")
    print(f"  copy    e={e:.4f}   : {ll_copy:.2f}  "
          f"(vs uniform +{ll_copy-ll_u:.2f})")
    print(f"  mixture f={f_lex:.3f} (lexicon Q) : {ll_mix:.2f}  "
          f"(vs copy {ll_mix-ll_copy:+.2f})")
    print(f"  mixture f={f_dom:.3f} (in-domain Q): {ll_mixd:.2f}  "
          f"(vs copy {ll_mixd-ll_copy:+.2f})")

    # --------------------------------------- projection test on nonzero bins
    t_obs = projection_stat(h, q_lex)

    # permutation null: shuffle each section's word lengths, keep stream
    streams = [[c for w in s for c in w] for s in sections]
    lens = [[len(w) for w in s] for s in sections]
    t_null = np.empty(n_perms)
    h0_null = np.empty(n_perms)
    for it in range(n_perms):
        hh = np.zeros(MOD, dtype=np.int64)
        for stream, ls in zip(streams, lens):
            ls2 = ls[:]
            rng.shuffle(ls2)
            pos = 0
            for L in ls2:
                w = stream[pos:pos + L]
                pos += L
                for k in range(L - D):
                    hh[(w[k + D] - w[k]) % MOD] += 1
        t_null[it] = projection_stat(hh, q_lex)
        h0_null[it] = hh[0]
    z = (t_obs - t_null.mean()) / t_null.std()
    p_hi = (np.sum(t_null >= t_obs) + 1) / (n_perms + 1)
    p_lo = (np.sum(t_null <= t_obs) + 1) / (n_perms + 1)
    print("\nprojection test (nonzero bins vs lexicon-Q direction):")
    print(f"  observed T = {t_obs:+.3f}; permutation null "
          f"{t_null.mean():+.3f} ± {t_null.std():.3f}; z = {z:+.2f}; "
          f"P(>=) = {p_hi:.4f}, P(<=) = {p_lo:.4f}")

    # ------------------------------------------- constrained key-sharing test
    # Key-sharing must explain the WHOLE 0-bin excess, which pins f:
    f_pin = float((h[0] / n - 1 / MOD) / (q_lex[0] - 1 / MOD))
    p_pin = f_pin * q_lex + (1 - f_pin) / MOD
    ll_pin = loglik(h, p_pin)
    # predicted projection statistic at f_pin (linear in f), bootstrap sd
    rng_pin = np.random.default_rng(11)
    t_pin = np.array([projection_stat(rng_pin.multinomial(n, p_pin), q_lex)
                      for _ in range(4000)])
    z_rej = (t_pin.mean() - t_obs) / t_pin.std()
    print(f"\nconstrained key-sharing (f pinned by the 0-bin = {f_pin:.3f}):")
    print(f"  log-likelihood {ll_pin:.2f} (vs copy {ll_pin-ll_copy:+.2f})")
    print(f"  predicted T = {t_pin.mean():+.3f} ± {t_pin.std():.3f}; "
          f"observed {t_obs:+.3f}; rejection z = {z_rej:+.2f}")

    # ----------------------------------------------------------- power
    f_implied = f_lex if f_lex > 0 else 0.55
    boots = 4000
    rng_np = np.random.default_rng(7)
    p_true = f_implied * q_lex + (1 - f_implied) / MOD
    t_boot = np.empty(boots)
    for i in range(boots):
        hb = rng_np.multinomial(n, p_true)
        t_boot[i] = projection_stat(hb, q_lex)
    thresh = np.quantile(t_null, 0.95)
    power = float((t_boot >= thresh).mean())
    print(f"\npower: if key-sharing at the implied f = {f_implied:.3f} were "
          f"true, P(T >= 95% null quantile) = {power:.2f}")
    print(f"  (bootstrapped T under mixture: {t_boot.mean():+.3f} "
          f"± {t_boot.std():.3f}; null 95% threshold {thresh:+.3f})")

    # --------------------------------------------------- secondary readouts
    d10_pairs = sum(max(0, len(w) - 10) for w in words)
    d10_match = sum(1 for w in words for k in range(len(w) - 10)
                    if w[k] == w[k + 10])
    print(f"\nd=10 within-word tail: {d10_match}/{d10_pairs} = "
          f"{d10_match/max(d10_pairs,1):.4f} "
          f"(uniform 0.0345, plaintext-leak ~0.061; low power)")

    opps = sum(max(0, len(w) - 6) for w in words)
    reps = sum(1 for w in words for k in range(len(w) - 6)
               if w[k] == w[k + 5] and w[k + 1] == w[k + 6])
    ctrl = controls["lexicon"] if controls.get("lexicon") else controls["in_domain"]
    lex_rate = ctrl["digraph_reps"] / ctrl["digraph_opps"]
    print(f"XY..XY: observed {reps}/{opps} opportunities; "
          f"uniform {opps/MOD**2:.1f}; full-plaintext-leak "
          f"{opps*lex_rate:.1f}; f-mixture "
          f"{f_implied*opps*lex_rate + (1-f_implied)*opps/MOD**2:.1f}")


if __name__ == "__main__":
    main()
