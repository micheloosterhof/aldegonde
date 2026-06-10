#!/usr/bin/env python3
# ABOUTME: Tests whether rune VALUES drive block-boundary placement: value
# ABOUTME: windows around doublets/lag-5 events and capacity-rule scans.
"""Value-driven blocking tests.

Idea (five-block-boundary refinement): block lengths of 4/5/6 could arise
from packing runes into a fixed capacity — high-value runes overflow a
block earlier. If the rule consumes CIPHERTEXT values it is reconstructible
by a decryptor and by us, and the 86 doublets (which mark boundaries under
the model) give a direct check.

Results — negative for ciphertext-value-driven blocking:

1. Model-free: mean rune values (index and Gematria Primus) in windows of
   1-5 runes before doublets, at doublets, and before lag-5 d1/d4 events
   are all within ~1 sigma of corpus baseline. No "overflow" enrichment.
2. Capacity-rule scan: accumulate ciphertext values (index or GP) to a
   threshold (reset or carry remainder, per page), capacities spanning mean
   block lengths ~3-10, ~600 rules total. Best doublet-boundary enrichment
   is z = +3.0, exactly the expected maximum order statistic of the scan.
   Under a true rule, ALL 86 doublets would sit on boundaries; the best
   rule catches 24 vs 15 expected by chance.

Caveat: a PLAINTEXT-value-driven rule is invisible to these tests (the
ciphertext is flat regardless) yet remains decryptable — the receiver can
update the accumulator progressively while decrypting. That variant stays
open but is untestable from ciphertext statistics alone; doublet-gap
quantization from 4/5/6 blocks also washes out at the observed ~151 mean
gap (CLT over ~30 blocks).
"""

import random
import statistics
from math import sqrt

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
DATA = "data/page0-58.txt"


def load_pages() -> list[str]:
    """Rune-only text per unsolved page."""
    with open(DATA) as f:
        raw = f.read()
    parts = raw.split("%")
    keep = [i for i, p in enumerate(parts) if any(c in ALPHABET for c in p)][:-2]
    return ["".join(x for x in parts[i] if x in ALPHABET) for i in keep]


def window_z(vals: list[int], positions: list[int], w: int) -> tuple[float, float]:
    """Mean of w-windows before positions vs random-position null (z)."""
    obs = [sum(vals[p - w : p]) / w for p in positions if p >= w]
    null = []
    for _ in range(4000):
        p = random.randrange(w, len(vals) - 1)
        null.append(sum(vals[p - w : p]) / w)
    z = (statistics.mean(obs) - statistics.mean(null)) / (
        statistics.stdev(null) / sqrt(len(obs))
    )
    return statistics.mean(obs), z


def boundary_scan(pages_vals: list[list[int]], dpos: list[int], n: int,
                  cmin: int, cmax: int, step: int, *,
                  carry: bool) -> tuple[float, int, int]:
    """Scan capacities; return best (z, capacity, hits) for doublet
    enrichment on reconstructed block boundaries."""
    best = (-99.0, 0, 0)
    nd = len(dpos)
    dset = set(dpos)
    for cap in range(cmin, cmax + 1, step):
        boundaries = set()
        off = 0
        for pv in pages_vals:
            cur = 0
            for j, v in enumerate(pv):
                cur += v
                if cur >= cap:
                    cur = cur - cap if carry else 0
                    if j < len(pv) - 1:
                        boundaries.add(off + j)
            off += len(pv)
        p = len(boundaries) / (n - 1)
        hits = len(dset & boundaries)
        exp = nd * p
        if exp > 0:
            z = (hits - exp) / sqrt(exp * (1 - p))
            if z > best[0]:
                best = (z, cap, hits)
    return best


def main() -> None:
    """Run all value-driven blocking tests."""
    pages = load_pages()
    text = "".join(pages)
    n = len(text)
    idx = [c3301.r2i(c) for c in text]
    gpv = [c3301.r2v(c) for c in text]
    dpos = [i for i in range(n - 1) if text[i] == text[i + 1]]
    print(f"{n} runes, {len(dpos)} doublets; mean index {sum(idx)/n:.2f}, "
          f"mean GP {sum(gpv)/n:.2f}")

    print("\nvalue windows before doublets (z vs random positions):")
    for name, vals in (("index", idx), ("GP", gpv)):
        for w in (1, 2, 3, 5):
            mean, z = window_z(vals, dpos, w)
            print(f"  {name:5s} w={w}: mean={mean:6.2f} z={z:+.2f}")

    mv = [text[i] == text[i + 5] for i in range(n - 5)]
    ev = sorted({i for i in range(len(mv) - 1) if mv[i] and mv[i + 1]}
                | {i for i in range(len(mv) - 4) if mv[i] and mv[i + 4]})
    print("\nvalue windows before lag-5 d1/d4 events:")
    for name, vals in (("index", idx), ("GP", gpv)):
        for w in (3, 5):
            mean, z = window_z(vals, ev, w)
            print(f"  {name:5s} w={w}: mean={mean:6.2f} z={z:+.2f}")

    print("\ncapacity-rule scans (doublet-boundary enrichment):")
    pages_idx = [[c3301.r2i(c) for c in p] for p in pages]
    pages_gpv = [[c3301.r2v(c) for c in p] for p in pages]
    for name, pv, cmin, cmax, step in (
        ("index", pages_idx, 30, 130, 1),
        ("GP", pages_gpv, 120, 450, 2),
    ):
        for carry in (False, True):
            z, cap, hits = boundary_scan(pv, dpos, n, cmin, cmax, step,
                                         carry=carry)
            tag = "carry" if carry else "reset"
            print(f"  {name}-{tag}: best z={z:+.2f} at capacity {cap} "
                  f"(hits {hits}/{len(dpos)})")
    print("(~600 rules scanned; the expected max-z under the null is ~3.1)")


if __name__ == "__main__":
    main()
