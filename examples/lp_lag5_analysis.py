#!/usr/bin/env python3
"""Liber Primus lag-5 repeat analysis.

Investigates the suspicion of a lag-5 repeat structure in the unsolved
Liber Primus pages (data/page0-58.txt).

The corpus layout (pages separated by '%', lines by '/', words by '-'/'.'):
  * pages 0-55:  unsolved ciphertext (~13k runes)
  * page 56:     "AN END" -- decrypts with shift = prime(i) - 1 (no
                 interruptors; the transcription has one extra rune around
                 index 60, after which the key stream needs a -1 resync)
  * page 57:     "PARABLE" -- plain runeglish, no encryption

Statistics computed on the unsolved body (all page-wise, so no
comparison ever crosses a page boundary):
  * monographic / digraphic / trigraphic kappa by lag
  * lag-1 delta histogram (the famous doublet deficit)
  * coset IOC for assumed periods 2-10, in both the rune domain and the
    lag-1 delta domain
  * autokey signature streams c[i+s] +/- c[i]
  * cross-page coincidence counting at shifts 0-10
  * corpus-wide repeated n-grams (length >= 5) and their distances mod 5
  * the lag-5 digraph repeats themselves, with a doublet-adjusted
    significance estimate
"""

from __future__ import annotations

import itertools
import math
import os
from collections import Counter, defaultdict

from scipy.stats import poisson

from aldegonde import c3301
from aldegonde.maths.primes import primes
from aldegonde.stats.kappa import doublets

ENG = c3301.CICADA_ENGLISH_ALPHABET
ABC = set(c3301.CICADA_ALPHABET)


def load_pages(path: str) -> list[list[int]]:
    """Load the LP transcription and return rune indices per page."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return [
        [c3301.r2i(ch) for ch in page if ch in ABC] for page in text.split("%")
    ]


def to_english(runes: list[int]) -> str:
    """Render rune indices as runeglish letters."""
    return "".join(ENG[r] for r in runes)


def primes_minus_one_decrypt(runes: list[int]) -> str:
    """Decrypt with plaintext = cipher - (prime_i - 1) mod 29."""
    plist = primes(200000)
    return "".join(ENG[(r - (plist[i] - 1)) % 29] for i, r in enumerate(runes))


def normalized_ioc(seq: list[int], alphabetsize: int = 29) -> float:
    """Index of coincidence normalized so uniform random text scores 1.0."""
    n = len(seq)
    if n < 2:
        return 0.0
    counts = Counter(seq)
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1)) * alphabetsize


def pagewise_kappa(
    pages: list[list[int]], skip: int, length: int = 1
) -> tuple[int, int]:
    """Count doublets at `skip` over all pages without crossing boundaries."""
    hits = 0
    total = 0
    for page in pages:
        positions, comparisons = doublets(page, skip=skip, length=length)
        hits += len(positions)
        total += comparisons
    return hits, total


def zscore(hits: int, total: int, p0: float) -> float:
    """Binomial z-score of `hits` successes in `total` trials."""
    return (hits - total * p0) / math.sqrt(total * p0 * (1 - p0))


def delta_stream(page: list[int], skip: int = 1) -> list[int]:
    """Differences (c[i+skip] - c[i]) mod 29."""
    return [(page[i + skip] - page[i]) % 29 for i in range(len(page) - skip)]


def confirm_tail(pages: list[list[int]]) -> None:
    """Verify the known tail pages so we can exclude them."""
    print("=== tail confirmation ===")
    print("page 57 (direct runeglish):", to_english(pages[57])[:60])
    print("page 56 (primes-1):       ", primes_minus_one_decrypt(pages[56])[:60])


def kappa_tables(pages: list[list[int]]) -> None:
    """Print mono-/di-/trigraphic kappa tables by lag."""
    print("\n=== monographic kappa by lag (baseline 1/29) ===")
    for lag in range(1, 41):
        hits, total = pagewise_kappa(pages, lag)
        flag = "  <-- lag 5" if lag == 5 else ""
        print(
            f"lag {lag:3d}: {hits:5d}/{total}  k={hits / total:.5f}"
            f"  z={zscore(hits, total, 1 / 29):+6.2f}{flag}",
        )

    print("\n=== digraphic kappa by lag, doublet-adjusted baseline ===")
    print("lag  obs  naive_exp  adj_exp  poisson_p(adj)")
    for lag in range(1, 21):
        obs, total = pagewise_kappa(pages, lag, length=2)
        mono_h, mono_t = pagewise_kappa(pages, lag)
        delta_h = delta_t = 0
        for page in pages:
            deltas = delta_stream(page)
            for i in range(len(deltas) - lag):
                delta_t += 1
                if deltas[i] == deltas[i + lag]:
                    delta_h += 1
        # P(digram at i == digram at i+lag) factored as
        # P(c[i]==c[i+lag]) * P(delta[i]==delta[i+lag]); this accounts for
        # the doublet deficit instead of assuming uniform runes
        adjusted = total * (mono_h / mono_t) * (delta_h / delta_t)
        pval = poisson.sf(obs - 1, adjusted)
        print(
            f"{lag:3d} {obs:4d}   {total / 841:7.1f}  {adjusted:7.1f}   {pval:.4f}",
        )

    print("\n=== trigraphic kappa by lag ===")
    for lag in range(1, 11):
        hits, total = pagewise_kappa(pages, lag, length=3)
        print(f"lag {lag:3d}: hits={hits} expected={total / 29**3:.2f}")


def doublet_deficit(pages: list[list[int]]) -> None:
    """Histogram of lag-1 deltas: only delta=0 is suppressed."""
    print("\n=== lag-1 delta histogram ===")
    counts: Counter[int] = Counter()
    total = 0
    for page in pages:
        for d in delta_stream(page):
            counts[d] += 1
            total += 1
    for d in range(29):
        z = zscore(counts[d], total, 1 / 29)
        print(f"delta {d:2d}: {counts[d]:5d}  z={z:+6.2f}")


def coset_iocs(pages: list[list[int]]) -> None:
    """Coset IOCs for assumed periods, rune domain and delta domain."""
    print("\n=== coset IOC by assumed period (rune / delta domain) ===")
    deltas = [delta_stream(p) for p in pages]
    for period in range(2, 11):
        rune_iocs = []
        delta_iocs = []
        for k in range(period):
            rune_iocs.append(
                normalized_ioc([x for p in pages for x in p[k::period]]),
            )
            delta_iocs.append(
                normalized_ioc([x for d in deltas for x in d[k::period]]),
            )
        print(
            f"period {period:2d}: rune={sum(rune_iocs) / period:.4f}"
            f"  delta={sum(delta_iocs) / period:.4f}",
        )


def autokey_signatures(pages: list[list[int]]) -> None:
    """IOC of c[i+s]-c[i] and c[i+s]+c[i]: flat rules out ct-autokey."""
    print("\n=== autokey signature streams ===")
    for skip in range(1, 11):
        diff = []
        summ = []
        for page in pages:
            for i in range(len(page) - skip):
                diff.append((page[i + skip] - page[i]) % 29)
                summ.append((page[i + skip] + page[i]) % 29)
        print(
            f"skip {skip:2d}: IOC(diff)={normalized_ioc(diff):.4f}"
            f"  IOC(sum)={normalized_ioc(summ):.4f}",
        )


def cross_page_coincidence(pages: list[list[int]]) -> None:
    """Coincidence counting between all page pairs at shifts 0-10."""
    print("\n=== cross-page coincidence (keystream reuse test) ===")
    nonempty = [p for p in pages if p]
    for shift in range(11):
        hits = total = 0
        for a, b in itertools.combinations(range(len(nonempty)), 2):
            pa, pb = nonempty[a], nonempty[b]
            n = min(len(pa) - shift, len(pb))
            for i in range(max(0, n)):
                total += 1
                if pa[i + shift] == pb[i]:
                    hits += 1
        print(
            f"shift {shift:2d}: rate={hits / total:.5f}"
            f"  z={zscore(hits, total, 1 / 29):+6.2f}",
        )


def long_repeats(pages: list[list[int]]) -> None:
    """Corpus-wide repeated n-grams (length >= 5) and distances mod 5."""
    print("\n=== corpus-wide repeated n-grams (length >= 5) ===")
    full: list[int] = []
    page_of: list[int] = []
    for i, page in enumerate(pages):
        full.extend(page)
        page_of.extend([i] * len(page))
    for length in (5, 6, 7):
        seen: dict[tuple[int, ...], list[int]] = defaultdict(list)
        for i in range(len(full) - length + 1):
            seen[tuple(full[i : i + length])].append(i)
        expected = len(full) ** 2 / 2 / 29**length
        repeated = {k: v for k, v in seen.items() if len(v) > 1}
        print(f"length {length}: {len(repeated)} repeats (expected ~{expected:.1f})")
        for gram, positions in repeated.items():
            dists = [positions[j + 1] - positions[j] for j in range(len(positions) - 1)]
            print(
                f"  {to_english(list(gram)):12s} pages"
                f" {[page_of[p] for p in positions]} dist={dists}"
                f" mod5={[d % 5 for d in dists]}",
            )


def lag5_repeats(pages: list[list[int]]) -> None:
    """List every lag-5 digraph repeat with context."""
    print("\n=== lag-5 digraph repeats (pattern XY...XY at distance 5) ===")
    for i, page in enumerate(pages):
        positions, _ = doublets(page, skip=5, length=2)
        for q in positions:
            print(
                f"page {i:2d} pos {q:3d}"
                f"  {to_english(page[q : q + 2]):4s}"
                f"  context {to_english(page[q : q + 7])}",
            )


def main() -> None:
    """Run the full lag-5 analysis."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "..", "data", "page0-58.txt")
    pages = load_pages(data_file)

    confirm_tail(pages)
    unsolved = pages[:56]
    flat = [x for p in unsolved for x in p]
    print(f"\nunsolved body: pages 0-55, {len(flat)} runes")
    print(f"normalized IOC: {normalized_ioc(flat):.4f} (uniform=1.0, runeglish~1.8)")

    kappa_tables(unsolved)
    doublet_deficit(unsolved)
    coset_iocs(unsolved)
    autokey_signatures(unsolved)
    cross_page_coincidence(unsolved)
    long_repeats(unsolved)
    lag5_repeats(unsolved)


if __name__ == "__main__":
    main()
