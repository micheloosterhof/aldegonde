# ABOUTME: Disproof of ciphertext autokey (any TR) by splitting on preceding rune.
# ABOUTME: If autokey, each split should have English-like IOC, not random IOC.

"""Disproof of ciphertext autokey with any tabula recta.

Under ciphertext autokey C[i] = TR[C[i-1]][P[i]], the plaintext at position i
is determined by a fixed permutation (row C[i-1] of TR_inv) applied to C[i].

If we group all C[i] values by their preceding rune C[i-1], each group is a
permuted version of the plaintext letter distribution. A permutation preserves
the Index of Coincidence. So each group's IOC should match English/runeglish
IOC (significantly above 1/29 = 0.0345).

If instead each group's IOC is close to 1/29, the autokey model is wrong for
ANY choice of TR.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict

sys.path.insert(0, "src")

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
N_RUNES = len(ALPHABET)  # 29


def load_runes(filepath: str) -> list[int]:
    with open(filepath) as f:
        text = f.read()
    return [c3301.r2i(c) for c in text if c in ALPHABET]


def ioc(values: list[int]) -> float:
    """Index of Coincidence for a list of integer values."""
    n = len(values)
    if n < 2:
        return 0.0
    counts = Counter(values)
    numerator = sum(c * (c - 1) for c in counts.values())
    denominator = n * (n - 1)
    return numerator / denominator


def chi_sq_uniform(values: list[int], n_symbols: int) -> float:
    """Chi-square statistic against uniform distribution."""
    n = len(values)
    expected = n / n_symbols
    counts = Counter(values)
    return sum((counts.get(i, 0) - expected) ** 2 / expected
               for i in range(n_symbols))


def main() -> None:
    runes = load_runes("data/page0-58.txt")
    n = len(runes)

    print(f"Total runes: {n}")
    print(f"Random IOC (1/{N_RUNES}): {1/N_RUNES:.6f}")
    print(f"Overall ciphertext IOC: {ioc(runes):.6f}")

    # Split by preceding rune
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(1, n):
        groups[runes[i - 1]].append(runes[i])

    print(f"\n{'C[i-1]':>8} {'rune':>5} {'size':>6} {'IOC':>10} "
          f"{'chi-sq':>8} {'vs random'}")
    print("-" * 65)

    iocs = []
    for k in range(N_RUNES):
        g = groups[k]
        g_ioc = ioc(g)
        g_chi = chi_sq_uniform(g, N_RUNES)
        iocs.append(g_ioc)
        # Compare to random IOC
        ratio = g_ioc / (1 / N_RUNES)
        label = f"{ratio:.2f}x random"
        print(f"{k:>8} {c3301.i2r(k):>5} {len(g):>6} {g_ioc:>10.6f} "
              f"{g_chi:>8.1f} {label}")

    mean_ioc = sum(iocs) / len(iocs)
    print("-" * 65)
    print(f"{'mean':>20} {mean_ioc:>10.6f}")
    print(f"{'random (1/29)':>20} {1/N_RUNES:>10.6f}")

    # For reference: what English IOC would look like
    # English IOC for 26 letters is ~0.0667
    # Runeglish with 29 symbols would be somewhat lower but still well above 1/29
    # A rough estimate: if the most common runeglish runes have freq 5-8% and
    # least common 1-2%, the IOC would be around 0.04-0.05
    print(f"\n{'INTERPRETATION':=^65}")
    print(f"If autokey (any TR): each group's IOC should match English/runeglish")
    print(f"  IOC, which is well above 1/29 = {1/N_RUNES:.4f}")
    if mean_ioc < 1.1 / N_RUNES:
        print(f"Mean IOC ({mean_ioc:.6f}) is indistinguishable from random.")
        print(f"DISPROOF: Ciphertext autokey with any TR is ruled out.")
    else:
        ratio = mean_ioc / (1 / N_RUNES)
        print(f"Mean IOC ({mean_ioc:.6f}) is {ratio:.2f}x random.")
        print(f"Check whether this matches expected runeglish IOC.")

    # Also split by preceding bigram (C[i-2], C[i-1]) to check for 2-deep
    # autokey or other correlations
    print(f"\n{'BIGRAM SPLIT (sample)':=^65}")
    print("Splitting by (C[i-2], C[i-1]) — checking if 2-deep dependencies exist")
    bigram_groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for i in range(2, n):
        bigram_groups[(runes[i - 2], runes[i - 1])].append(runes[i])

    # There are 29*29 = 841 bigram groups. Most will be small (~15 runes each).
    # Just report summary statistics.
    sizes = [len(g) for g in bigram_groups.values()]
    bigram_iocs = [ioc(g) for g in bigram_groups.values() if len(g) >= 5]
    if bigram_iocs:
        mean_bi_ioc = sum(bigram_iocs) / len(bigram_iocs)
        print(f"Bigram groups with >=5 elements: {len(bigram_iocs)} / {len(bigram_groups)}")
        print(f"Mean IOC of these groups: {mean_bi_ioc:.6f}")
        print(f"Random IOC: {1/N_RUNES:.6f}")


if __name__ == "__main__":
    main()
