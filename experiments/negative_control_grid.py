# ABOUTME: Family-blind sweep of within-word distances and lag-pair separations
# ABOUTME: against a structure-free surrogate, with a max-statistic scan correction.
"""Every cell, not just the interesting ones.

`negative_control_battery.py` ran the surrogate against the measurements this
repo already treats as findings: within-word d1, d4, d5, d6 and lag-5 pairs at
separations 1 and 4. That is the selection bias the audit exists to catch. A
control applied only to pre-selected cells cannot say whether those cells are
special, and cannot see a cell nobody thought to look at.

So this sweeps the whole grid:

  * within-word coincidence at d = 1..12
  * lag-L match pairs at separation s, for L = 2..15 and s = 1..8

against the same surrogate: real word boundaries, marks, line wraps and page
breaks held exactly, runes redrawn at the observed doublet rate
(`c3301.low_doublet_null`).

Because the grid is scanned, per-cell z is not enough. The family-wise test
compares the real corpus's LARGEST |z| over the grid against the distribution
of the largest |z| the surrogate itself produces over the same grid. A cell
only counts if it beats what a structureless corpus throws up somewhere.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import numpy as np

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
BOUNDARY = "①-.%&$"
WITHIN_D = range(1, 13)
LAGS = range(2, 16)
SEPS = range(1, 9)
DRAWS = 300
SEED = 3301


def load() -> tuple[np.ndarray, list[list[int]]]:
    text = "$".join(CORPUS.read_text().split("$")[:10])
    idx = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
    stream: list[int] = []
    words: list[list[int]] = []
    cur: list[int] = []
    for ch in text:
        if RUNE.match(ch):
            stream.append(idx[ch])
            cur.append(idx[ch])
        elif ch in BOUNDARY and cur:
            words.append(cur)
            cur = []
    if cur:
        words.append(cur)
    return np.array(stream, dtype=np.int8), words


def within_pairs(words: list[list[int]]) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """Index pairs (i, i+d) that lie inside one word, per distance."""
    out: dict[int, tuple[list[int], list[int]]] = {d: ([], []) for d in WITHIN_D}
    pos = 0
    for w in words:
        for d in WITHIN_D:
            for i in range(len(w) - d):
                out[d][0].append(pos + i)
                out[d][1].append(pos + i + d)
        pos += len(w)
    return {d: (np.array(a), np.array(b)) for d, (a, b) in out.items() if a}


def grid(stream: np.ndarray, pairs: dict) -> dict[str, float]:
    cells: dict[str, float] = {}
    for d, (a, b) in pairs.items():
        cells[f"within d{d}"] = float(np.mean(stream[a] == stream[b]))
    for lag in LAGS:
        m = stream[:-lag] == stream[lag:]
        for s in SEPS:
            cells[f"lag{lag} sep{s}"] = float(np.count_nonzero(m[:-s] & m[s:]))
    return cells


def main() -> None:
    rng = random.Random(SEED)
    stream, words = load()
    pairs = within_pairs(words)
    print(f"clean corpus: {len(stream)} runes, {len(words)} words")
    print(f"grid: {len(WITHIN_D)} within-word distances + "
          f"{len(LAGS)}x{len(SEPS)} lag-pair cells = "
          f"{len(WITHIN_D) + len(LAGS) * len(SEPS)} cells")
    print(f"surrogate: boundaries held, runes redrawn at the observed doublet "
          f"rate ({DRAWS} draws)\n")

    real = grid(stream, pairs)
    keys = list(real)
    model = c3301.low_doublet_null()
    draws = np.empty((DRAWS, len(keys)))
    for t in range(DRAWS):
        surr = np.array(model(stream.tolist(), random.Random(rng.randrange(2**32))),
                        dtype=np.int8)
        cells = grid(surr, pairs)
        draws[t] = [cells[k] for k in keys]

    mu, sd = draws.mean(axis=0), draws.std(axis=0)
    sd[sd == 0] = np.inf
    z_real = (np.array([real[k] for k in keys]) - mu) / sd
    z_draws = (draws - mu) / sd

    order = np.argsort(-np.abs(z_real))
    print("strongest ten cells on the real corpus")
    print(f"{'cell':>14}{'real':>12}{'surrogate':>12}{'sd':>9}{'z':>8}")
    for i in order[:10]:
        print(f"{keys[i]:>14}{real[keys[i]]:>12.4f}{mu[i]:>12.4f}{sd[i]:>9.4f}"
              f"{z_real[i]:>+8.2f}")

    real_max = float(np.max(np.abs(z_real)))
    surr_max = np.max(np.abs(z_draws), axis=1)
    beat = int(np.count_nonzero(surr_max >= real_max))
    print(f"\nfamily-wise scan correction over {len(keys)} cells")
    print(f"   real corpus largest |z| : {real_max:.2f}  ({keys[order[0]]})")
    print(f"   surrogate largest |z|   : {surr_max.mean():.2f} +- "
          f"{surr_max.std():.2f}, 95th pct {np.percentile(surr_max, 95):.2f}")
    print(f"   p = {(beat + 1) / (DRAWS + 1):.4f}")

    threshold = float(np.percentile(surr_max, 95))
    survivors = [(keys[i], z_real[i]) for i in order if abs(z_real[i]) >= threshold]
    print(f"\ncells clearing the scan threshold |z| >= {threshold:.2f}: "
          f"{len(survivors)}")
    for name, z in survivors:
        print(f"   {name:>14}  z = {z:+.2f}")
    if not survivors:
        print("   none — no cell beats what the surrogate throws up somewhere")

    # Pooling all 124 is too blunt: the two families are different questions,
    # and 112 of the cells are lag-pair statistics nobody proposed. Correct
    # within each family instead.
    print("\nper-family correction (the families ask different questions)")
    fam = {
        "within-word d1..d12": [i for i, k in enumerate(keys) if k.startswith("within")],
        "lag-pair grid": [i for i, k in enumerate(keys) if k.startswith("lag")],
    }
    for name, ids in fam.items():
        rm = float(np.max(np.abs(z_real[ids])))
        sm = np.max(np.abs(z_draws[:, ids]), axis=1)
        p = (int(np.count_nonzero(sm >= rm)) + 1) / (DRAWS + 1)
        top = keys[ids[int(np.argmax(np.abs(z_real[ids])))]]
        print(f"   {name:>22}  {len(ids):>3} cells  real max |z| {rm:.2f} ({top}) "
              f" surrogate {sm.mean():.2f}+-{sm.std():.2f}  p = {p:.4f}")

    # The max statistic also throws away the structure: the top cells are all
    # lag 5. Ask instead whether any LAG is special, aggregating its separations.
    print("\nis any lag special? aggregate z^2 over its eight separations")
    agg_real, agg_draw = {}, {}
    for lag in LAGS:
        ids = [i for i, k in enumerate(keys) if k.startswith(f"lag{lag} ")]
        agg_real[lag] = float(np.sum(z_real[ids] ** 2))
        agg_draw[lag] = np.sum(z_draws[:, ids] ** 2, axis=1)
    best = max(agg_real, key=agg_real.get)
    real_best = agg_real[best]
    surr_best = np.max(np.stack([agg_draw[lag] for lag in LAGS]), axis=0)
    p = (int(np.count_nonzero(surr_best >= real_best)) + 1) / (DRAWS + 1)
    for lag in sorted(LAGS, key=lambda x: -agg_real[x])[:5]:
        print(f"   lag {lag:>2}: sum z^2 = {agg_real[lag]:6.1f}")
    print(f"   best lag is {best}; against the surrogate's best lag "
          f"({surr_best.mean():.1f} +- {surr_best.std():.1f})  p = {p:.4f}")


if __name__ == "__main__":
    main()
