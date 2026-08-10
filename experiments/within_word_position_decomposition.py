#!/usr/bin/env python3
# ABOUTME: Decomposes within-word coincidence by phase, absolute position-in-word,
# ABOUTME: and word length -- tests whether phase (d mod 5) captures all structure.
"""Under a pure period-5 letter step modulated only at word boundaries, the
within-word coincidence rate for a pair (i, i+d) should depend ONLY on the phase
d mod 5 -- not on the absolute start position i, nor on the word length L.

Two sharp discriminators:

  * d5 echo vs absolute position: if the base DRIFTS within a word, the d5
    same-alphabet leak should DECAY as the pair starts later in the word
    (more accumulated drift). If the base is word-LOCKED, the echo is flat.
  * d1 doublet vs absolute position: is the doublet suppression uniform, or is
    the word-initial pair (i=0, right after the sigma step) special?

We report rates with Wilson 95% CIs and a chi-square homogeneity test across
position/length buckets. Clean corpus: sections 0-9 of data/page0-58.txt.
"""

from __future__ import annotations

from collections import defaultdict

from scipy.stats import chi2_contingency

from aldegonde import c3301

BOUNDARY_CHARS = frozenset(
    c3301.MARK_CHARS + "&%$" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS
)

ALPH = c3301.CICADA_ALPHABET
RUNES = set(ALPH)
R2I = {r: i for i, r in enumerate(ALPH)}
CLEAN = 12956  # sections 0-9


def load_words() -> list[list[int]]:
    """Words as rune-index lists. Words flow across line wraps; split on
    - . & % (word seps) and $ (section); capped at the clean corpus."""
    with open("data/page0-58.txt") as f:
        text = f.read()
    words: list[list[int]] = []
    cur: list[int] = []
    total = 0
    for ch in text:
        if total >= CLEAN:
            break
        if ch in RUNES:
            cur.append(R2I[ch])
            total += 1
        elif ch in BOUNDARY_CHARS:
            if cur:
                words.append(cur)
                cur = []
        elif ch in "/\n":
            pass
    if cur:
        words.append(cur)
    return words


def wilson(k: int, n: int) -> tuple[float, float, float]:
    """Point rate and Wilson 95% CI."""
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.96
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def collect(words: list[list[int]], d: int) -> list[tuple[int, int, int]]:
    """Every within-word pair at distance d: (abs_start_i, word_len, coincidence)."""
    out = []
    for w in words:
        L = len(w)
        for i in range(L - d):
            out.append((i, L, int(w[i] == w[i + d])))
    return out


def bucketize(pairs, keyfn, labels) -> dict[str, tuple[int, int]]:
    """Group pairs into named buckets -> (n_pairs, n_coinc)."""
    agg: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for i, L, c in pairs:
        b = keyfn(i, L)
        if b is None:
            continue
        agg[b][0] += 1
        agg[b][1] += c
    return {lab: (agg[lab][0], agg[lab][1]) for lab in labels if lab in agg}


def report_buckets(title: str, buckets: dict[str, tuple[int, int]]) -> None:
    print(f"\n{title}")
    print(f"  {'bucket':<10} {'pairs':>6} {'coinc':>6} {'rate':>8}  95% CI")
    table = []
    for lab, (n, k) in buckets.items():
        p, lo, hi = wilson(k, n)
        print(f"  {lab:<10} {n:>6} {k:>6} {p:>8.4f}  [{lo:.4f},{hi:.4f}]")
        table.append([k, n - k])
    if len(table) >= 2 and all(sum(row) > 0 for row in table):
        chi2, pv, dof, _ = chi2_contingency(table)
        print(
            f"  homogeneity chi2={chi2:.2f} dof={dof} p={pv:.3f}"
            f"  ({'FLAT' if pv > 0.05 else 'STRUCTURE'})"
        )


def main() -> None:
    words = load_words()
    print(f"words: {len(words)}, runes: {sum(len(w) for w in words)}")

    # Phase recap d1..d6.
    print("\nphase recap (rate by distance):")
    print(f"  {'d':>2} {'phase':>5} {'pairs':>6} {'coinc':>6} {'rate':>8}  95% CI")
    for d in range(1, 7):
        pairs = collect(words, d)
        n = len(pairs)
        k = sum(c for _, _, c in pairs)
        p, lo, hi = wilson(k, n)
        print(f"  {d:>2} {d % 5:>5} {n:>6} {k:>6} {p:>8.4f}  [{lo:.4f},{hi:.4f}]")

    # --- d1 doublet by absolute position (highest power) ---
    d1 = collect(words, 1)
    report_buckets(
        "d1 doublet suppression by absolute start position:",
        bucketize(
            d1,
            lambda i, L: {0: "i=0", 1: "i=1", 2: "i=2"}.get(i, "i>=3"),
            ["i=0", "i=1", "i=2", "i>=3"],
        ),
    )

    # --- d5 echo by absolute position (drift signature) ---
    d5 = collect(words, 5)
    report_buckets(
        "d5 echo by absolute start position (drift -> decays with i):",
        bucketize(
            d5,
            lambda i, L: {0: "i=0", 1: "i=1", 2: "i=2"}.get(i, "i>=3"),
            ["i=0", "i=1", "i=2", "i>=3"],
        ),
    )

    # --- d5 echo by word length ---
    report_buckets(
        "d5 echo by word length:",
        bucketize(
            d5,
            lambda i, L: {6: "L=6", 7: "L=7", 8: "L=8"}.get(L, "L>=9"),
            ["L=6", "L=7", "L=8", "L>=9"],
        ),
    )

    # --- phase-1 consistency: d1 vs d6 ---
    print("\nphase-1 consistency (pure phase => d1 rate == d6 rate):")
    for d in (1, 6):
        pairs = collect(words, d)
        n, k = len(pairs), sum(c for _, _, c in pairs)
        p, lo, hi = wilson(k, n)
        print(f"  d{d}: {k}/{n} = {p:.4f}  [{lo:.4f},{hi:.4f}]")


if __name__ == "__main__":
    main()
