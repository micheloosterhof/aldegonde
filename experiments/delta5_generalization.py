# ABOUTME: Stream-level value-literal test: repeated NONzero lag-5 deltas at separations
# ABOUTME: 1/4 vs the elevated zero (equality) value, against doublet-suppressed nulls.
"""Generalize the lag-5 pairing from matches to arbitrary repeated deltas.

The confirmed anomaly (hypotheses/lag5-digraph-structure.md) is about
lag-5 *matches*: positions i with C[i] == C[i+5] pair up at separations
1 and 4. Define the lag-5 delta stream

    delta5[i] = (C[i+5] - C[i]) mod 29        (a match is delta5[i] == 0)

and ask the strictly more general question: does delta5 repeat at short
separations, i.e. how often is delta5[i] == delta5[i+d], and is any excess
carried by the zero value only, or by all values?

Why this discriminates mechanisms:

- ADDITIVE KEY DRIFT / local key stationarity: if the keystream is locally
  5-periodic up to an additive offset (K[i+5] = K[i] + t for a stretch),
  then delta5 = P[i+5] - P[i] + t is *constant on the stretch* whatever t
  is. Repeated NONZERO deltas at separations 1 and 4 should be elevated
  just like the zero deltas (the t=0 case) are.
- COPY / BACK-REFERENCE semantics ("emit the glyph from 5 back"):
  produces literal equalities only. delta5 pairing exists at value 0 and
  nowhere else.

Note the identities:
  delta5[i] == delta5[i+1]  <=>  C[i+1]-C[i]   == C[i+6]-C[i+5]
                                 (the step stream repeats at lag 5)
  delta5[i] == delta5[i+4]  <=>  C[i+4]-C[i]   == C[i+9]-C[i+5]
                                 (the 4-step span repeats at lag 5)

so this is exactly the difference-domain analogue of the d1/d4 pairing.

Null: uniform random runes with the observed doublet rate (the corpus's
only 2nd-order structure), generated as a cumsum of steps that are 0 with
probability r and uniform on 1..28 otherwise -- identical in law to
gen_doublet_suppressed in lag5_digraph_chase.py, vectorized.

Usage: python experiments/delta5_generalization.py [n_surrogates]
"""

from __future__ import annotations

import sys

import numpy as np

ALPHABET = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
DATA = "data/page0-56.txt"
LAG = 5
SEPARATIONS = range(1, 9)


def load_clean() -> np.ndarray:
    """Clean unsolved corpus (12,956 runes): all pages minus the two solved."""
    r2i = {r: i for i, r in enumerate(ALPHABET)}
    with open(DATA) as f:
        raw = f.read()
    pages = [[r2i[ch] for ch in page if ch in r2i] for page in raw.split("%")]
    pages = [p for p in pages if p][:-2]
    return np.array([x for p in pages for x in p], dtype=np.int64)


def delta_stream(c: np.ndarray, lag: int) -> np.ndarray:
    return (c[lag:] - c[:-lag]) % MOD


def repeat_counts(delta: np.ndarray, d: int) -> tuple[int, int]:
    """(# delta5[i]==delta5[i+d] with value 0, # with value != 0)."""
    eq = delta[:-d] == delta[d:]
    zero = eq & (delta[:-d] == 0)
    return int(zero.sum()), int((eq & ~zero).sum())


def surrogates(
    n_sur: int, length: int, rate: float, rng: np.random.Generator
) -> np.ndarray:
    """n_sur doublet-suppressed uniform streams, shape (n_sur, length)."""
    steps = rng.integers(1, MOD, size=(n_sur, length))
    steps[rng.random(size=(n_sur, length)) < rate] = 0
    steps[:, 0] = rng.integers(0, MOD, size=n_sur)  # random start
    return np.cumsum(steps, axis=1) % MOD


def main() -> None:
    n_sur = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    c = load_clean()
    n = len(c)
    doublets = int((c[1:] == c[:-1]).sum())
    rate = doublets / (n - 1)
    print(f"corpus: {n} runes, {doublets} doublets (rate {rate:.4%})")

    delta = delta_stream(c, LAG)
    obs = {d: repeat_counts(delta, d) for d in SEPARATIONS}

    rng = np.random.default_rng(20260707)
    # accumulate null statistics in blocks to bound memory
    zeros = {d: [] for d in SEPARATIONS}
    nonzeros = {d: [] for d in SEPARATIONS}
    block = 250
    done = 0
    while done < n_sur:
        b = min(block, n_sur - done)
        streams = surrogates(b, n, rate, rng)
        dl = (streams[:, LAG:] - streams[:, :-LAG]) % MOD
        for d in SEPARATIONS:
            eq = dl[:, :-d] == dl[:, d:]
            zero = eq & (dl[:, :-d] == 0)
            zeros[d].append(zero.sum(axis=1))
            nonzeros[d].append((eq & ~zero).sum(axis=1))
        done += b
    print(f"null: {n_sur} doublet-suppressed surrogates\n")

    header = (
        f"{'sep':>3} | {'zero obs':>8} {'null':>8} {'z':>6} {'p':>8} | "
        f"{'nonzero obs':>11} {'null':>10} {'z':>6} {'p':>8}"
    )
    print(header)
    print("-" * len(header))
    for d in SEPARATIONS:
        z0 = np.concatenate(zeros[d])
        nz = np.concatenate(nonzeros[d])
        oz, onz = obs[d]
        zz = (oz - z0.mean()) / z0.std()
        znz = (onz - nz.mean()) / nz.std()
        pz = (np.sum(z0 >= oz) + 1) / (n_sur + 1)
        pnz = (np.sum(nz >= onz) + 1) / (n_sur + 1)
        print(
            f"{d:>3} | {oz:>8} {z0.mean():>8.1f} {zz:>+6.2f} {pz:>8.4f} | "
            f"{onz:>11} {nz.mean():>10.1f} {znz:>+6.2f} {pnz:>8.4f}"
        )

    # per-value breakdown at the two anomalous separations
    for d in (1, 4):
        eq = delta[:-d] == delta[d:]
        vals, counts = np.unique(delta[:-d][eq], return_counts=True)
        per_val = dict(zip(vals.tolist(), counts.tolist()))
        expect = (len(delta) - d) / MOD**2  # rough per-value null
        print(
            f"\nsep {d}: repeated-delta counts per value "
            f"(rough null ~{expect:.1f} each):"
        )
        row = [f"{v}:{per_val.get(v, 0)}" for v in range(MOD)]
        print("  " + "  ".join(row))


if __name__ == "__main__":
    main()
