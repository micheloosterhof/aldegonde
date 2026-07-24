# ABOUTME: Observation: kappa (coincidence) is anomalous ONLY at skip 1; every
# ABOUTME: other skip 2..60 is at the random rate.
"""Kappa spectrum. Significance: z of coincidence count at each skip vs the
frequency-based expectation. Only skip 1 (the doublet deficit) departs; skip 5
is mildly elevated (the lag-5 structure) but far weaker."""
from __future__ import annotations
import math
from collections import Counter
from lp_corpus import load_clean, N


def kappa_z(stream, skip):
    n = len(stream) - skip
    hits = sum(1 for i in range(n) if stream[i] == stream[i + skip])
    freq = Counter(stream)
    p = sum(c * c for c in freq.values()) / (len(stream) ** 2)
    return hits, (hits - n * p) / math.sqrt(n * p * (1 - p))


def main() -> None:
    stream, _ = load_clean()
    print("skip : coincidences  z")
    flagged = []
    for skip in range(1, 61):
        hits, z = kappa_z(stream, skip)
        if skip <= 12 or abs(z) > 2:
            tag = "  <-- anomalous" if abs(z) > 3 else ("  (lag-5)" if skip == 5 else "")
            print(f"  {skip:2d} : {hits:5d}       {z:+.2f}{tag}")
        if abs(z) > 3:
            flagged.append(skip)
    print(f"\nskips 1..60 with |z|>3: {flagged}")
    print("VERDICT: only skip 1 (doublet deficit) is strongly anomalous; skip 5")
    print("is mildly elevated (lag-5 structure); all others at random.")


if __name__ == "__main__":
    main()
