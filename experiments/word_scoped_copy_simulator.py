#!/usr/bin/env python3
"""Word-scoped copy model: can one rule reproduce the whole fingerprint?

Model (the surviving explanation family after within-word-key-sharing.md):

    base   : doublet-suppressed uniform stream (the established base
             process), cut into the REAL word-length sequence
    copies : literal glyph copies from 5 back, in three shapes --
             single (1 glyph), digraph (2 adjacent), frame (positions
             i and i+4 of a 5-window) -- fired at independent rates for
             word-internal sites vs boundary-crossing sites

Rates are calibrated by moment-matching FIVE marginal targets (d1 pairs,
d4 pairs, paired-within matches, isolated-within matches, mono total).
Everything else the script reports is EMERGENT and constitutes the test:

    - the full paired/isolated x within/across decomposition
    - pair separations 2, 3, 5..8 (must stay at chance)
    - the within-word delta histogram off zero (must stay flat)
    - the within-word d=6 count (does the model produce the observed
      deficit? prediction: no -- only a ~1-glyph doublet-interaction
      dip, so a real d=6 deficit would be NEW structure the copy model
      does not explain)
    - doublet rate / triplets (must remain intact)

Usage: python experiments/word_scoped_copy_simulator.py [n_sims]
"""

from __future__ import annotations

import sys

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
WORD_BOUNDARIES = set("-.&%")
D = 5


# ------------------------------------------------------------------ corpus
def parse_clean_sections() -> list[list[list[int]]]:
    with open(DATA) as f:
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


# --------------------------------------------------------------- statistics
def fingerprint(c: np.ndarray, widx: np.ndarray) -> dict:
    """All fingerprint statistics for one stream + word structure."""
    m = c[:-D] == c[D:]                          # lag-5 match indicator
    mlen = len(m)
    within = widx[:-D] == widx[D:]               # pair inside one word

    # paired positions: i belongs to a pair event at separation 1 or 4
    in_pair = np.zeros(mlen, dtype=bool)
    for d in (1, 4):
        both = m[:-d] & m[d:]
        idx = np.nonzero(both)[0]
        in_pair[idx] = True
        in_pair[idx + d] = True
    seps = {d: int((m[:-d] & m[d:]).sum()) for d in range(1, 9)}

    stats = {
        "mono": int(m.sum()),
        "d1": seps[1], "d4": seps[4],
        "sep2": seps[2], "sep3": seps[3], "sep5": seps[5],
        "sep6": seps[6], "sep7": seps[7], "sep8": seps[8],
        "paired_within": int((m & in_pair & within).sum()),
        "paired_across": int((m & in_pair & ~within).sum()),
        "isolated_within": int((m & ~in_pair & within).sum()),
        "isolated_across": int((m & ~in_pair & ~within).sum()),
        "doublets": int((c[1:] == c[:-1]).sum()),
        "triplets": int(((c[2:] == c[1:-1]) & (c[1:-1] == c[:-2])).sum()),
    }
    # within-word d=6 count
    w6 = widx[:-6] == widx[6:]
    stats["d6_within"] = int(((c[:-6] == c[6:]) & w6).sum())
    # within-word delta histogram chi2 off zero
    deltas = (c[D:] - c[:-D]) % MOD
    hh = np.bincount(deltas[within], minlength=MOD).astype(float)
    nz = hh[1:]
    exp = nz.sum() / (MOD - 1)
    stats["offzero_chi2"] = float(((nz - exp) ** 2 / exp).sum())
    return stats


# ------------------------------------------------------------------- model
def simulate(lens: list[int], rates: dict, rng: np.random.Generator
             ) -> tuple[np.ndarray, np.ndarray]:
    n = sum(lens)
    steps = rng.integers(1, MOD, size=n)
    steps[rng.random(n) < rates["doublet"]] = 0
    steps[0] = rng.integers(0, MOD)
    c = np.cumsum(steps) % MOD
    widx = np.repeat(np.arange(len(lens)), lens)

    def try_copy(i: int, j: int) -> None:
        """C[j] := C[i], skipped if it would create a doublet."""
        v = c[i]
        if j >= 1 and c[j - 1] == v:
            return
        if j + 1 < n and c[j + 1] == v:
            return
        c[j] = v

    u = rng.random(n)
    u2 = rng.random(n)
    for i in range(n - D - 4):
        j = i + D
        in_word_single = widx[i] == widx[j]
        in_word_digraph = widx[i] == widx[min(j + 1, n - 1)]
        # digraph copy (creates a d1 event)
        r = rates["digraph_in"] if in_word_digraph else rates["digraph_x"]
        if u[i] < r and j + 1 < n:
            try_copy(i, j)
            try_copy(i + 1, j + 1)
            continue
        # frame copy (creates a d4 event): copies at (j, j+4) from (i, i+4)
        if u[i] < r + rates["frame"] and j + 4 < n:
            try_copy(i, j)
            try_copy(i + 4, j + 4)
            continue
        # single copy
        rs = rates["single_in"] if in_word_single else rates["single_x"]
        if u2[i] < rs:
            try_copy(i, j)
    return c, widx


def main() -> None:
    n_sims = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    sections = parse_clean_sections()
    words = [w for s in sections for w in s]
    lens = [len(w) for w in words]
    real_c = np.array([x for w in words for x in w], dtype=np.int64)
    real_w = np.repeat(np.arange(len(words)), lens)
    real = fingerprint(real_c, real_w)
    print("LP observed:", {k: (round(v, 1) if isinstance(v, float) else v)
                           for k, v in real.items()})

    rate = float((real_c[1:] == real_c[:-1]).mean())
    # calibrated by moment matching (see docstring); rates are per-site
    rates = {
        "doublet": rate,
        "digraph_in": 8 / 1267,     # ~8 in-word digraph copies / sites
        "digraph_x": 4 / 11500,     # ~4 cross-word digraph copies
        "frame": 11.5 / 12900,      # ~11.5 frame copies (mostly cross-word)
        "single_in": 15 / 2073,     # ~15 in-word single copies
        "single_x": 0.0,
    }

    rng = np.random.default_rng(20260707)
    keys = list(real.keys())
    acc = {k: [] for k in keys}
    for _ in range(n_sims):
        c, widx = simulate(lens, rates, rng)
        fp = fingerprint(c, widx)
        for k in keys:
            acc[k].append(fp[k])
    print(f"\nmodel ({n_sims} sims) vs LP:")
    print(f"{'stat':>16} {'LP':>7} {'model':>9} {'sd':>6} {'z':>6}")
    for k in keys:
        a = np.array(acc[k], dtype=float)
        z = (real[k] - a.mean()) / a.std() if a.std() else 0.0
        flag = " <-- calibrated" if k in (
            "mono", "d1", "d4", "paired_within", "isolated_within") else ""
        print(f"{k:>16} {real[k]:>7} {a.mean():>9.1f} {a.std():>6.1f} "
              f"{z:>+6.2f}{flag}")


if __name__ == "__main__":
    main()
