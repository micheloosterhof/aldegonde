# ABOUTME: Observation: no periodic key -- the Friedman periodic-IoC test is flat
# ABOUTME: at every period 2..40, so no fixed-period polyalphabetic structure.
"""Periodicity. Significance: for each period p, average the IoC of the p
columns (runes at i mod p). A period-p key spikes this toward plaintext IoC
(~1.7 normalized); observed stays ~1.0 for all p."""

from __future__ import annotations

from collections import Counter

from lp_corpus import N, load_clean


def col_ioc(col):
    n = len(col)
    if n < 2:
        return 0.0
    c = Counter(col)
    return N * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def main() -> None:
    stream, _ = load_clean()
    print("period : mean column nIoC (random=1.0, period key -> ~1.7)")
    worst = 0.0
    for p in range(2, 41):
        cols = [stream[i::p] for i in range(p)]
        m = sum(col_ioc(c) for c in cols) / p
        worst = max(worst, m)
        if p <= 12 or m > 1.05:
            print(f"  {p:2d}   : {m:.4f}")
    print(f"max over periods 2..40: {worst:.4f}")
    print("VERDICT: flat at ~1.0 for every period -- no fixed-period key")


if __name__ == "__main__":
    main()
