#!/usr/bin/env python3
# ABOUTME: Tests whether any inverse-transposition geometry converts the
# ABOUTME: lag-5 anomaly and doublet suppression into a simpler pre-stream.
"""Can a transposition geometry make the lag-5 anomaly natural?

Theory first: a transposition is a permutation of positions, so it can
NEITHER create NOR destroy equal-symbol coincidences - it only relocates
them. Therefore transposition could at most explain why the copy distance
is 5; the 57 verified copy events must exist in any pre-stream too. The
testable question: does some inverse geometry make the anomalies look
NATURAL - e.g., the lag-5 copy events become adjacent stutters (AABB or
AAA patterns), and the doublet suppression moves to a sensible place?

Under a 5-row column-read block transposition (blocks 5 x W), visible
lag-5 maps exactly to pre-stream adjacency, visible d1 events map to two
pre-doublets W apart, d4 events to two pre-doublets W-1 apart, and the
visible (suppressed) doublets map to pre-lag-W pairs.

Scan: inverse transpositions for 5 x W (W = 2..30), whole-text 5-row, and
R x 5 column variants. For each pre-stream: doublet rate, triplets, AABB
counts, and the strongest pair-cell over (L <= 6, d <= 4).

Result - NEGATIVE on every geometry:
- Pre-doublet rates land at ~3.3-3.8% (the visible lag-5 rate, as algebra
  demands): normal, no stutter excess.
- Triplets and AABB counts sit at uniform expectations (~15) everywhere;
  the copy events never become adjacent duplications. (The 5x2 triplet
  deficit, 5 vs 15, is the visible doublet suppression relocated: visible
  lag-1 maps to pre-lag-2 there, and a pre-triplet needs a lag-2 pair.)
- Top pair-cells across all geometries max out at |z| = 3.2 over ~840
  looks - noise. The visible (5,1)+(5,4) joint structure never reassembles
  into anything stronger or simpler; it only smears.
- Already-established results bound the rest: no mod-5 phase in the events
  (a fixed block grid would impose one), and 2nd-order tables flat at lags
  1-60 plus kappa flat to 6400 exclude substitution+transposition with any
  geometry lag up to half the corpus (pre-stream language structure would
  surface at the geometry lags).

Conclusion: the lag-5 anomaly cannot be linked to transposition in any
generative sense. Transposition relabels distances but cannot produce the
copies, and no tested geometry yields a more natural pre-stream. The
mystery is geometry-invariant: whatever produced the stream, it contained
deterministic short-range copies and a 5x coincidence suppression."""

import random
from math import sqrt

import numpy as np

from aldegonde import c3301

AB = c3301.CICADA_ALPHABET
N = 29

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
keep = [i for i, p in enumerate(parts) if any(c in AB for c in p)][:-2]
text = "".join(x for i in keep for x in parts[i] if x in AB)
n = len(text)
a = np.array([c3301.r2i(c) for c in text])

def profile(s: np.ndarray) -> dict:
    out = {}
    out["dbl%"] = 100 * float(np.mean(s[:-1] == s[1:]))
    out["tripl"] = int(np.sum((s[:-2] == s[1:-1]) & (s[1:-1] == s[2:])))
    # AABB: adjacent doublets back-to-back with different values
    dd = (s[:-1] == s[1:])
    aabb = int(np.sum(dd[:-2] & dd[2:] & (s[:-3] != s[2:-1])))
    out["AABB"] = aabb
    # pair structure of lag-1..6 matches at separations 1..4 (top cell)
    best = (0.0, 0, 0)
    for L in range(1, 7):
        M = s[:-L] == s[L:]
        for d in range(1, 5):
            pairs = int(np.sum(M[:-d] & M[d:]))
            e = (len(M) - d) * float(np.mean(M)) ** 2
            if e > 3:
                z = (pairs - e) / sqrt(e)
                if abs(z) > abs(best[0]):
                    best = (z, L, d)
    out["top-pair"] = f"z={best[0]:+.1f}@(L{best[1]},d{best[2]})"
    return out

def untranspose_block(s: np.ndarray, rows: int, width: int) -> np.ndarray:
    """Assume visible was produced by writing pre row-major into rows x width
    blocks and reading column-major. Invert per block; remainder unchanged."""
    blk = rows * width
    nb = len(s) // blk
    out = s.copy()
    for b in range(nb):
        seg = s[b * blk:(b + 1) * blk]
        grid = seg.reshape(width, rows).T  # visible was grid.T.flatten()
        out[b * blk:(b + 1) * blk] = grid.flatten()
    return out

print("visible:", profile(a))
print()
print(f"{'geometry':22s} {'dbl%':>5s} {'tripl':>5s} {'AABB':>4s}  top-pair")
rows = 5
results = []
for width in list(range(2, 31)) + [n // 5]:
    pre = untranspose_block(a, rows, width)
    p = profile(pre)
    tag = f"5 rows x {width}" if width != n // 5 else "5 rows whole text"
    print(f"{tag:22s} {p['dbl%']:5.2f} {p['tripl']:5d} {p['AABB']:4d}  {p['top-pair']}")
    results.append((tag, p))
# also 5-column geometries (visible lag-R <-> pre adjacency)
for width in (2, 3, 4, 6, 10):
    pre = untranspose_block(a, width, 5)
    p = profile(pre)
    print(f"{f'{width} rows x 5':22s} {p['dbl%']:5.2f} {p['tripl']:5d} {p['AABB']:4d}  {p['top-pair']}")

# baseline for AABB/triplets in doublet-suppressed random (visible-like)

rate = 86 / (n - 1)
sims = []
for _ in range(6):
    out = [random.randrange(N)]
    for _ in range(n - 1):
        if random.random() < rate:
            out.append(out[-1])
        else:
            c = random.randrange(N - 1)
            if c >= out[-1]:
                c += 1
            out.append(c)
    sims.append(profile(np.array(out)))
print(f"\nnull visible-like:  dbl {np.mean([s['dbl%'] for s in sims]):.2f}  "
      f"tripl {np.mean([s['tripl'] for s in sims]):.1f}  "
      f"AABB {np.mean([s['AABB'] for s in sims]):.1f}")
# expected AABB / triplets for UNIFORM pre-stream with normal doublets:
print(f"uniform-stream expectation: dbl 3.45%, tripl ~{(n-2)/841:.0f}, "
      f"AABB ~{(n-3)/841*(28/29):.0f}")
