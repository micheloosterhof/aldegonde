#!/usr/bin/env python3
# ABOUTME: Tests page/section-aligned kappa (shared keystream reset at boundaries),
# ABOUTME: doublet-suppressed null model, and the lag-5 digraphic kappa anomaly.
"""Aligned-kappa and null-model validation for Liber Primus (page0-58).

Three experiments on the unsolved corpus (excluding the solved AN END and
parable pages at the end of the file):

1. Page-aligned and section-aligned kappa. If the cipher were
   C[i] = f(P[i], K[i]) with ANY positional keystream K that resets at page
   (or section) boundaries and is shared across pages, aligning two pages
   position-by-position cancels the key and the coincidence rate rises to
   the plaintext IOC (~1.7 normalized). Result: page-aligned z = +0.2 sigma,
   section-aligned z = -0.8 sigma. Disproved for any shared boundary-reset
   keystream; see hypotheses/page-reset-keystream.md.

2. Doublet-suppressed null model. Generates uniform text whose only structure
   is the observed doublet rate, and compares bigram IOC and n-gram repeat
   counts. Result: observed bigram nIOC 1.0256 vs null 1.0251 +/- 0.0033, and
   2-/3-gram repeat pair counts match the null exactly. The 8-sigma bigram IOC
   elevation and the apparent 4-sigma trigram repeat deficit reported against
   a plain uniform null are both artifacts of doublet suppression alone.

3. Lag-5 digraphic kappa. 29 repeated digraphs at distance exactly 5 vs 15.4
   expected (+3.5 sigma), present in both halves of the text (+2.6 / +2.3
   sigma) and within pages alone (+3.4 sigma). Characterization: hits are
   diffuse (no phase preference mod 5, chi-sq p ~= 0.2; no page concentration;
   no word-position pattern; all 29 digraph values distinct). Monographic
   kappa at skip 5 is only +1.5 sigma, which rules out a simple period-5
   substitution explanation. Unexplained; after a look-elsewhere correction
   over ~50 tested skips the global significance is roughly p ~= 0.01.
"""

import random
import statistics
from collections import Counter
from math import sqrt

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
MOD = 29
DATA = "data/page0-58.txt"


def runes_only(text: str) -> str:
    """Strip everything that is not a rune of the Cicada alphabet."""
    return "".join(x for x in text if x in ALPHABET)


def load() -> tuple[list[str], list[str], str]:
    """Return unsolved pages, sections, and the joined unsolved corpus."""
    with open(DATA) as f:
        raw = f.read()
    pages = [p for p in (runes_only(s) for s in raw.split("%")) if p]
    pages = pages[:-2]  # drop solved AN END + parable
    sections = [s for s in (runes_only(x) for x in raw.split("$")[:10]) if s]
    return pages, sections, "".join(pages)


def aligned_kappa_battery(units: list[str], name: str) -> None:
    """Pairwise position-aligned coincidence counting over text units."""
    tot_hits = 0
    tot_n = 0
    pair_z: list[tuple[float, int, int]] = []
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            n = min(len(units[i]), len(units[j]))
            hits = sum(1 for k in range(n) if units[i][k] == units[j][k])
            tot_hits += hits
            tot_n += n
            sd = sqrt(n * (1 / MOD) * (1 - 1 / MOD))
            pair_z.append(((hits - n / MOD) / sd, i, j))
    expected = tot_n / MOD
    z = (tot_hits - expected) / sqrt(tot_n * (1 / MOD) * (1 - 1 / MOD))
    pair_z.sort(reverse=True)
    print(f"{name}-aligned kappa: hits={tot_hits} expected={expected:.0f} "
          f"z={z:+.2f} sigma (ratio {tot_hits / expected:.3f})")
    tops = ", ".join(f"({i},{j})={zz:+.1f}" for zz, i, j in pair_z[:5])
    print(f"  top pairs (sigma): {tops}")


def doublet_rate(text: str) -> float:
    """Fraction of adjacent positions holding two identical runes."""
    return sum(1 for i in range(len(text) - 1) if text[i] == text[i + 1]) / (
        len(text) - 1
    )


def gen_doublet_suppressed(n: int, rate: float) -> str:
    """Uniform random runes whose only structure is the given doublet rate."""
    out = [random.randrange(MOD)]
    for _ in range(n - 1):
        if random.random() < rate:
            out.append(out[-1])
        else:
            c = random.randrange(MOD - 1)
            if c >= out[-1]:
                c += 1
            out.append(c)
    return "".join(ALPHABET[c] for c in out)


def bigram_nioc(text: str) -> float:
    """Bigram index of coincidence normalized by 29*29."""
    counts = Counter(text[i : i + 2] for i in range(len(text) - 1))
    n = len(text) - 1
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1)) * MOD * MOD


def repeat_pairs(text: str, length: int) -> int:
    """Number of coinciding n-gram pairs at the given length."""
    counts = Counter(text[i : i + length] for i in range(len(text) - length + 1))
    return sum(v * (v - 1) // 2 for v in counts.values() if v > 1)


def digraphic_kappa(text: str, skip: int) -> tuple[int, float]:
    """Count repeated digraphs at the given distance, with expectation."""
    n = len(text) - skip - 1
    hits = sum(
        1
        for i in range(n)
        if text[i] == text[i + skip] and text[i + 1] == text[i + skip + 1]
    )
    return hits, n / (MOD * MOD)


def main() -> None:
    """Run all three validation experiments."""
    pages, sections, text = load()
    print(f"{len(pages)} unsolved pages, {len(text)} runes, "
          f"{len(sections)} sections\n")

    aligned_kappa_battery(pages, "page")
    aligned_kappa_battery(sections, "section")

    rate = doublet_rate(text)
    sims_b = []
    sims_r2 = []
    sims_r3 = []
    for _ in range(12):
        m = gen_doublet_suppressed(len(text), rate)
        sims_b.append(bigram_nioc(m))
        sims_r2.append(repeat_pairs(m, 2))
        sims_r3.append(repeat_pairs(m, 3))
    print(f"\nbigram nIOC: observed={bigram_nioc(text):.4f} "
          f"doublet-suppressed null={statistics.mean(sims_b):.4f}"
          f"+/-{statistics.stdev(sims_b):.4f} (plain uniform theory: 1.0357)")
    print(f"2-gram repeat pairs: observed={repeat_pairs(text, 2)} "
          f"null={statistics.mean(sims_r2):.0f}+/-{statistics.stdev(sims_r2):.0f}")
    print(f"3-gram repeat pairs: observed={repeat_pairs(text, 3)} "
          f"null={statistics.mean(sims_r3):.0f}+/-{statistics.stdev(sims_r3):.0f}")

    half = len(text) // 2
    for name, seg in [("full", text), ("half1", text[:half]),
                      ("half2", text[half:])]:
        parts = []
        for skip in (2, 3, 4, 5, 6, 7, 10):
            hits, exp = digraphic_kappa(seg, skip)
            z = (hits - exp) / sqrt(exp * (1 - 1 / (MOD * MOD)))
            parts.append(f"skip{skip}={hits}({z:+.1f})")
        print(f"\ndigraphic kappa {name} (sigma): " + " ".join(parts))

    hits5 = 0.0
    exp5 = 0.0
    for p in pages:
        hits, exp = digraphic_kappa(p, 5)
        hits5 += hits
        exp5 += exp
    print(f"\nwithin-page digraphic skip=5: hits={hits5:.0f} "
          f"expected={exp5:.1f} z={(hits5 - exp5) / sqrt(exp5):+.2f} sigma")


if __name__ == "__main__":
    main()
