# ABOUTME: "Test F" for the lag-11 cross-word coincidence deficit: stratify the
# ABOUTME: d=11 pairs by word-position alignment and scan sections 1/8 for
# ABOUTME: word-length periodicity (lag11-cross-word-deficit.md).
"""Test F: does word-length periodicity explain the lag-11 deficit?

The word-length-periodicity interpretation predicts (a) the deficit tracks
word-position alignment — concentrated in specific (pos_i, pos_j) strata,
e.g. word-initial-to-word-initial — and vanishes when stratified; and (b) a
repeating word-length rhythm in the carrying sections (1 and 8).

Part 1 stratifies all cross-word d=11 pairs by position-in-word alignment,
with a per-section word-length-sequence permutation null (rune stream held
fixed, boundaries reshuffled, as in lag5_word_boundary.py).
Part 2 scans each section's word-length sequence for periodicity (max
FFT power over the spectrum, plus autocorrelation at lags 1..20) against a
within-section shuffle null.
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lp_corpus import IDX, RUNE

from aldegonde import c3301

BOUNDARY_CHARS = frozenset(
    c3301.MARK_CHARS + "%&" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS
)

ROOT = Path(__file__).resolve().parent.parent
D = 11
CHANCE = 0.03455  # sum f^2 on the clean corpus


def load_sections() -> list[tuple[list[int], list[int]]]:
    """Per-section word-length sequences AND rune streams for sections 0-9."""
    text = (ROOT / "data" / "page0-58.txt").read_text()
    sections = [s for s in text.split("$") if RUNE.search(s)][:10]
    out = []
    for s in sections:
        stream: list[int] = []
        wlens: list[int] = []
        cur = 0
        for ch in s:
            if RUNE.match(ch):
                stream.append(IDX[ch])
                cur += 1
            elif ch in BOUNDARY_CHARS:
                if cur:
                    wlens.append(cur)
                    cur = 0
        if cur:
            wlens.append(cur)
        out.append((stream, wlens))
    return out


def positions_from_lengths(wlens: list[int]) -> tuple[list[int], list[int], list[int]]:
    """(word_id, pos0, wlen) arrays for a stream segmented by wlens."""
    wid, pos, wl = [], [], []
    for w, L in enumerate(wlens):
        for p in range(L):
            wid.append(w)
            pos.append(p)
            wl.append(L)
    return wid, pos, wl


def poslabel(p: int, L: int) -> str:
    if L == 1:
        return "lone"
    if p == 0:
        return "first"
    if p == L - 1:
        return "last"
    return "mid"


def stratified_counts(match, wid, pos, wl, n):
    """Per-alignment-stratum (matches, pairs) over cross-word d=11 pairs."""
    strata: Counter[tuple[str, str]] = Counter()
    hits: Counter[tuple[str, str]] = Counter()
    same_pos = [0, 0]
    for i in range(n - D):
        j = i + D
        if wid[i] == wid[j]:
            continue
        key = (poslabel(pos[i], wl[i]), poslabel(pos[j], wl[j]))
        strata[key] += 1
        m = match[i]
        hits[key] += m
        same = pos[i] == pos[j]
        same_pos[0] += m if same else 0
        same_pos[1] += 1 if same else 0
    return strata, hits, same_pos


def main() -> None:
    rng = random.Random(11)
    secs = load_sections()
    stream = [r for s, _ in secs for r in s]
    wlens_all = [(k, L) for k, (_, wl) in enumerate(secs) for L in wl]
    n = len(stream)
    match = [1 if i + D < n and stream[i] == stream[i + D] else 0 for i in range(n)]
    wid, pos, wl = positions_from_lengths([L for _, L in wlens_all])
    assert len(wid) == n, (len(wid), n)

    total_m = sum(match[i] for i in range(n - D))
    print(
        f"clean corpus: {n} runes, lag {D}: {total_m} matches "
        f"(chance {CHANCE * (n - D):.1f})"
    )

    strata, hits, same_pos = stratified_counts(match, wid, pos, wl, n)
    cross_pairs = sum(strata.values())
    cross_hits = sum(hits.values())
    print(
        f"cross-word pairs {cross_pairs}, matches {cross_hits} "
        f"(rate {cross_hits / cross_pairs:.4f} vs chance {CHANCE:.4f})"
    )

    print("\nPart 1a: alignment strata (pos of i x pos of i+11), obs rate vs chance z:")
    print(f"{'stratum':>16} {'pairs':>6} {'match':>6} {'rate':>7} {'z':>6}")
    for key in sorted(strata, key=lambda k: -strata[k]):
        e = strata[key] * CHANCE
        sd = (strata[key] * CHANCE * (1 - CHANCE)) ** 0.5
        z = (hits[key] - e) / sd if sd else float("nan")
        print(
            f"{'-'.join(key):>16} {strata[key]:>6} {hits[key]:>6} "
            f"{hits[key] / strata[key]:>7.4f} {z:>+6.2f}"
        )
    e = same_pos[1] * CHANCE
    sd = (same_pos[1] * CHANCE * (1 - CHANCE)) ** 0.5
    print(
        f"{'same-pos-in-word':>16} {same_pos[1]:>6} {same_pos[0]:>6} "
        f"{same_pos[0] / same_pos[1]:>7.4f} {(same_pos[0] - e) / sd:>+6.2f}"
    )

    # Part 1b: is the OBSERVED cross-word deficit bigger than under
    # word-length-sequence permutation? If boundary structure caused it,
    # permuting boundaries (stream fixed) would move the cross-word count.
    print("\nPart 1b: per-section word-length permutation null (2000 shuffles):")
    obs = cross_hits
    null = []
    for _ in range(2000):
        perm_lens: list[int] = []
        for _, (_s, wlseq) in enumerate(secs):
            w = wlseq[:]
            rng.shuffle(w)
            perm_lens.extend(w)
        pwid, ppos, pwl = positions_from_lengths(perm_lens)
        tot = 0
        for i in range(n - D):
            if pwid[i] != pwid[i + D]:
                tot += match[i]
        null.append(tot)
    mu, sd = float(np.mean(null)), float(np.std(null))
    print(
        f"  cross-word matches: obs {obs} vs null {mu:.1f} ± {sd:.1f} "
        f"(z = {(obs - mu) / sd:+.2f})"
    )
    print("  (near-zero z = the deficit is indifferent to where boundaries sit;")
    print("   the boundary structure is not the cause)")

    # Part 2: word-length periodicity per section
    print("\nPart 2: word-length-sequence periodicity per section")
    print(
        f"{'sec':>4} {'words':>6} {'maxpow/mean':>12} {'null95':>7} "
        f"{'max|acf| lag1-20':>17} {'null95':>7}"
    )
    for k, (_, wlseq) in enumerate(secs):
        x = np.array(wlseq, dtype=float)
        if len(x) < 40:
            continue
        x = x - x.mean()

        def stats(v):
            p = np.abs(np.fft.rfft(v)[1:]) ** 2
            ratio = p.max() / p.mean()
            ac = [np.corrcoef(v[:-lag], v[lag:])[0, 1] for lag in range(1, 21)]
            return ratio, max(abs(a) for a in ac)

        r_obs, a_obs = stats(x)
        rs, as_ = [], []
        for _ in range(500):
            y = x.copy()
            rng.shuffle(y)
            r, a = stats(y)
            rs.append(r)
            as_.append(a)
        print(
            f"{k:>4} {len(x):>6} {r_obs:>12.2f} {np.quantile(rs, 0.95):>7.2f} "
            f"{a_obs:>17.3f} {np.quantile(as_, 0.95):>7.3f}"
            + ("   <- carries the d11 deficit" if k in (1, 8) else "")
        )


if __name__ == "__main__":
    main()
