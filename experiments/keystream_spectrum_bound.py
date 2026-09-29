# ABOUTME: Bounds the Fourier spectrum of any additive keystream from the body's flat unigrams,
# ABOUTME: excluding a language-text running key without needing depth, phase or alignment.
"""A running key made of language cannot produce the body's flat unigrams.

`no-running-key-depth.md` excludes every REPEATING key by searching the difference
stream for depth, and states its own gap: a non-repeating key at least as long as the
text leaves no depth to find. It closes that gap only for keys that are
"statistically uniform". A book used once is not statistically uniform, and this
measurement closes that case.

Write the ciphertext as c = p + k mod 29 with k independent of p. In Fourier
coordinates, with P^(j) = sum_x P(x) w^(jx) and w = exp(2 pi i / 29),

    C^(j) = P^(j) K^(j)          and        IoC_c = 1 + sum_(j != 0) |P^(j)|^2 |K^(j)|^2

normalising IoC so that uniform = 1. Every term is a product, so a keystream can only
flatten the ciphertext at a frequency where the plaintext has mass by being flat there
itself. The body's unigrams are flat (`flat-ioc.md`, chi2 26.4 on 28 df), so each
frequency yields a separate cap on |K^(j)|^2.

The test needs no alignment and no phase, so `preventer-blinds-absolute-tests.md` does
not apply: an interrupter moves key letters around but does not change which letters
the keystream is made of. A pass-through interrupt would add plaintext non-uniformity,
which only sharpens the conclusion.

Scope. This bounds ADDITIVE keystreams. A per-position permutation drawn from a
2-transitive family is covered by the orbit theorem instead, not here.

    python keystream_spectrum_bound.py
"""

from __future__ import annotations

import cmath
import collections
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

from aldegonde.maths import primes  # noqa: E402

M = 29


def dist(seq: list[int]) -> list[float]:
    counts = collections.Counter(seq)
    n = len(seq)
    return [counts[i] / n for i in range(M)]


def spectrum(p: list[float]) -> list[float]:
    """|P^(j)|^2 for j = 0..28; P^(0) = 1 and the rest measure non-uniformity."""
    return [
        abs(sum(p[x] * cmath.exp(2j * math.pi * j * x / M) for x in range(M))) ** 2
        for j in range(M)
    ]


def chi2(seq: list[int]) -> float:
    """Unigram chi2 against uniform, which equals n * (normalised IoC - 1)."""
    return len(seq) * (M * sum(q * q for q in dist(seq)) - 1)


def main() -> None:
    rng = random.Random(3301)
    plain = [r for w in corpus() for r in w]
    body, _wid = load_clean()
    n = len(body)
    sp = spectrum(dist(plain))
    sb = spectrum(dist(body))

    print(f"LP plaintext {len(plain):,} runes, chi2 {chi2(plain):,.0f} on 28 df")
    print(
        f"unsolved body {n:,} runes, chi2 {chi2(body):.1f} on 28 df (null 28 +- 7.5)\n"
    )

    print("a language-text running key, spectrum taken from the LP's own plaintext:")
    pred = sum(sp[j] * sp[j] for j in range(1, M))
    print(f"  predicted ciphertext chi2 = n * sum|P^|^4 = {n * pred:,.0f}")
    print(f"  observed                                  = {chi2(body):.1f}")
    print(f"  excluded by a factor of {n * pred / chi2(body):,.0f}\n")

    print("controls, all at the body's length:")
    pt = [plain[i % len(plain)] for i in range(n)]
    text_key = [plain[(i + 977) % len(plain)] for i in range(n)]
    flat_key = [rng.randrange(M) for _ in range(n)]
    print(
        f"  text plaintext + text key    chi2 {chi2([(a + b) % M for a, b in zip(pt, text_key)]):>8,.0f}"
    )
    print(
        f"  text plaintext + uniform key chi2 {chi2([(a + b) % M for a, b in zip(pt, flat_key)]):>8.1f}"
    )

    print("\nper-frequency cap on any additive keystream (95% one-sided):")
    sims = [spectrum(dist([rng.randrange(M) for _ in range(n)])) for _ in range(300)]
    print(f"{'j':>3}{'|P^(j)|^2':>12}{'|C^(j)|^2':>12}{'cap':>10}{'|K^(j)|^2 <=':>14}")
    caps: dict[int, float] = {}
    for j in sorted(range(1, M), key=lambda j: -sp[j])[:8]:
        mu = sum(s[j] for s in sims) / len(sims)
        sd = (sum((s[j] - mu) ** 2 for s in sims) / len(sims)) ** 0.5
        cap = max(sb[j], mu + 1.645 * sd)
        caps[j] = cap / sp[j]
        print(f"{j:>3}{sp[j]:>12.4f}{sb[j]:>12.5f}{cap:>10.5f}{caps[j]:>14.4f}")

    print("\nthe author's own arithmetic keystream, prime(n) - 1 mod 29:")
    pk = [(p - 1) % M for p in primes(300000)[:n]]
    sk = spectrum(dist(pk))
    worst = max(caps, key=lambda j: sk[j] / caps[j])
    print(
        f"  key chi2 {chi2(pk):.0f}; tightest frequency j={worst}: "
        f"|K^|^2 = {sk[worst]:.5f} against a cap of {caps[worst]:.5f}"
    )
    print(
        f"  enciphering LP plaintext with it gives chi2 "
        f"{chi2([(a + b) % M for a, b in zip(pt, pk)]):.1f}, "
        f"against the body's {chi2(body):.1f}"
    )
    print(
        "\nSo arithmetic keystreams pass this bound and language ones do not. The body"
        "\nis flatter than even the prime keystream would leave it."
    )


if __name__ == "__main__":
    main()
