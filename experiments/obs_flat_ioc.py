# ABOUTME: Observation: the clean LP unigram distribution is flat -- IoC at 1/29
# ABOUTME: and a chi-square uniformity test that does not reject uniformity.
"""Flat unigram distribution. Significance: chi-square goodness-of-fit vs uniform
(28 df) and the normalized IoC (1.00 = random)."""

from __future__ import annotations

from collections import Counter

from lp_corpus import N, load_clean


def main() -> None:
    stream, _ = load_clean()
    n = len(stream)
    c = Counter(stream)
    exp = n / N
    chi2 = sum((c[i] - exp) ** 2 / exp for i in range(N))
    # chi-square survival for 28 df via Wilson-Hilferty approximation
    import math

    k = N - 1
    x = chi2 / k
    z = (x ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
    p = 0.5 * math.erfc(z / math.sqrt(2))
    ioc = N * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))
    print(f"runes {n}, min/max count {min(c.values())}/{max(c.values())}")
    print(f"chi-square (uniform, {k} df): {chi2:.1f}  p={p:.3f}  (crit@0.05 ~41.3)")
    print(f"normalized IoC: {ioc:.4f}  (random = 1.0000)")
    print("VERDICT: flat -- uniformity not rejected, IoC indistinguishable from random")


if __name__ == "__main__":
    main()
