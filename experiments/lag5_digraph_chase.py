#!/usr/bin/env python3
# ABOUTME: Characterizes the lag-5 digraph anomaly: paired lag-5 matches at
# ABOUTME: separations 1 and 4, with Monte Carlo global significance testing.
"""Full chase of the lag-5 digraph anomaly in the LP unsolved corpus.

Pipeline (see hypotheses/lag5-digraph-structure.md for conclusions):

1. Digraphic kappa lag spectrum 2..150: lag 5 is +3.5 sigma but a plain max
   over this many lags is not globally significant on its own.
2. Decomposition: the monographic lag-5 excess lives entirely inside paired
   events. The autocorrelation of the lag-5 match indicator M[i] spikes at
   separations d=1 and d=4 only (flat at 2, 3, and 5..25). Translation
   invariant: no mod-5 phase preference, so not a fixed-grid seriation.
3. Depth-L preceding-rune split test for L=1..8: all flat (~1.0), extending
   the ciphertext-autokey disproof to feedback depth up to 8 with any TR.
4. Joint statistic T(L) = (# pairs of lag-L matches at separation 1) +
   (# pairs at separation L-1), the canonical form of the observed pattern.
   T(5)=57 vs null 30.7 +/- 6.5 (local z=+4.1); max-over-lags global Monte
   Carlo: p ~= 0.01. Split-half stable (28/29).
5. Pocket scan: sliding-window M-count locates two dense pockets inside
   section 4 (positions ~3715-3975 and ~5324-5495, pages 15-16 and 21-22),
   but matches inside pockets are scattered, not contiguous, ruling out
   locally period-5 keystream patches.
"""

import random
import statistics
from collections import Counter
from math import sqrt

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
MOD = 29
DATA = "data/page0-58.txt"


def runes_only(text: str) -> str:
    """Strip everything that is not a rune of the Cicada alphabet."""
    return "".join(x for x in text if x in ALPHABET)


def load() -> tuple[str, list[str]]:
    """Return the unsolved corpus and its `$`-sections."""
    with open(DATA) as f:
        raw = f.read()
    pages = [p for p in (runes_only(s) for s in raw.split("%")) if p][:-2]
    sections = [s for s in (runes_only(x) for x in raw.split("$")[:10]) if s]
    return "".join(pages), sections


def match_indicator(text: str, lag: int) -> list[bool]:
    """M[i] = (text[i] == text[i+lag])."""
    return [text[i] == text[i + lag] for i in range(len(text) - lag)]


def joint_t(text: str, lag: int) -> int:
    """Pairs of lag-L matches at separations 1 and L-1 (the observed pattern)."""
    mv = match_indicator(text, lag)
    mlen = len(mv)
    t = sum(1 for i in range(mlen - 1) if mv[i] and mv[i + 1])
    if lag > 2:
        t += sum(1 for i in range(mlen - lag + 1) if mv[i] and mv[i + lag - 1])
    return t


def nioc(text: str) -> float:
    """Normalized index of coincidence."""
    if len(text) < 2:
        return 0.0
    counts = Counter(text)
    return (
        sum(v * (v - 1) for v in counts.values())
        / (len(text) * (len(text) - 1))
        * MOD
    )


def split_test(text: str, depth: int) -> float:
    """Mean group nIoC splitting C[i] by C[i-depth].

    Under ciphertext autokey C[i] = f(P[i], C[i-depth]) with any tabula
    recta, each group is a substitution image of the plaintext, so the mean
    group nIoC should approach plaintext nIoC (~1.7). Random text gives ~1.0.
    """
    groups: dict[str, list[str]] = {}
    for i in range(depth, len(text)):
        groups.setdefault(text[i - depth], []).append(text[i])
    iocs = [nioc("".join(g)) for g in groups.values() if len(g) > 20]
    return sum(iocs) / len(iocs)


def gen_doublet_suppressed(length: int, rate: float) -> str:
    """Uniform random runes with only the observed doublet rate as structure."""
    out = [random.randrange(MOD)]
    for _ in range(length - 1):
        if random.random() < rate:
            out.append(out[-1])
        else:
            c = random.randrange(MOD - 1)
            if c >= out[-1]:
                c += 1
            out.append(c)
    return "".join(ALPHABET[c] for c in out)


def main() -> None:
    """Run the full chase."""
    text, sections = load()
    n = len(text)
    print(f"corpus: {n} runes, {len(sections)} sections")

    # --- M autocorrelation
    mv = match_indicator(text, 5)
    mlen = len(mv)
    p1 = sum(mv) / mlen
    print(f"\nlag-5 match rate: {p1:.4f} (random 1/29 = {1 / MOD:.4f})")
    print("M autocorrelation (z vs independence):")
    for d in range(1, 11):
        cnt = sum(1 for i in range(mlen - d) if mv[i] and mv[i + d])
        exp = (mlen - d) * p1 * p1
        print(f"  d={d:2d}: {cnt:3d} vs {exp:5.1f}  z={(cnt - exp) / sqrt(exp):+5.2f}")

    # --- depth-L autokey split
    print("\ndepth-L split test (autokey predicts ~1.7, random ~1.0):")
    print("  " + " ".join(f"L{d}={split_test(text, d):.3f}" for d in range(1, 9)))

    # --- per-section lag-5 digraph kappa
    print("\nper-section lag-5 digraph kappa:")
    for si, s in enumerate(sections):
        ls = len(s)
        hits = sum(
            1 for i in range(ls - 6) if s[i] == s[i + 5] and s[i + 1] == s[i + 6]
        )
        exp = (ls - 6) / (MOD * MOD)
        z = (hits - exp) / sqrt(exp) if exp > 0 else 0.0
        print(f"  section {si}: len={ls:5d} hits={hits:2d} z={z:+.2f}")

    # --- joint statistic with global Monte Carlo
    lags = range(2, 51)
    obs = {lag: joint_t(text, lag) for lag in lags}
    top = sorted(((v, k) for k, v in obs.items()), reverse=True)[:5]
    print(f"\njoint T(L) top 5: {[(lag, v) for v, lag in top]}")
    half = n // 2
    print(f"T(5) split-half: {joint_t(text[:half], 5)} + {joint_t(text[half:], 5)}"
          f" = {obs[5]}")

    rate = sum(1 for i in range(n - 1) if text[i] == text[i + 1]) / (n - 1)
    trials = 200
    t5 = obs[5]
    null_max = []
    null_t5 = []
    for _ in range(trials):
        sim = gen_doublet_suppressed(n, rate)
        vals = [joint_t(sim, lag) for lag in lags]
        null_max.append(max(vals))
        null_t5.append(vals[3])
    mean5 = statistics.mean(null_t5)
    sd5 = statistics.stdev(null_t5)
    p_local = sum(1 for v in null_t5 if v >= t5) / trials
    p_global = sum(1 for v in null_max if v >= t5) / trials
    print(f"null T(5) = {mean5:.1f} +/- {sd5:.1f}; "
          f"local z = {(t5 - mean5) / sd5:+.2f}, p_local = {p_local:.3f}")
    print(f"global (max over lags 2..50): p = {p_global:.3f}")


if __name__ == "__main__":
    main()
