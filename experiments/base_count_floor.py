# ABOUTME: Sharper base-count floor from the zero-background long-word cells,
# ABOUTME: to test whether a commuting (normalising) sigma is finally excluded.
"""How many distinct bases does the walk visit? A tighter floor than the census.

`sigma-power-step.md` bounds the base count at N >~ 600 (2 sigma) from the
identity-pair census, which leaves the COMMUTING normaliser sigma (sigma g
sigma^-1 = g, base = base_0 g^e sigma^w, at most 5*ord(sigma) <= 500 bases)
only marginally disfavoured, and excludes the twisted normalisers (<= 300).

This sharpens the floor using the cells the census dilutes. A repeated plaintext
WORD forces a repeated ciphertext word only when its two occurrences land on the
same base. Under any base schedule that visits N bases about-uniformly over the
2,928 words (the commuting case does: (e mod 5, w mod ord sigma) equidistributes,
and plaintext-repeat gaps are independent of the cipher period, so two equal
words share a base with probability ~1/N), the expected forced ciphertext
word-repeats at length L is C(m_L, 2) * kappa_L / N, where m_L is the corpus
count of length-L words and kappa_L the plaintext collision rate for length-L
words. At L >= 4 the chance background is ~0 (word_repeat_census.py: 0 observed,
null ~0), so 0 observed bounds the forced mean at ~3 (2 sigma), giving

    forced(L, N) = C(m_L, 2) * kappa_L / N,   N <= 500 (commuting), <= 300 (twisted),

so 0 observed at L >= 4 gives a Poisson p = exp(-sum_{L>=4} forced) for each cap.

kappa_L is measured on two independent registers: a large generic-English one
(Project Gutenberg #1342, ~120k tokens) and the same-author LP one (the recovered
position-preserving solved segments). Generic prose is LESS repetitive than the
LP's header-heavy register, so the generic number is the conservative bound; the
same-author number is stronger. kappa is a rate, not a scaled count, so the small
same-author sample is unbiased rather than inflated.
"""

from __future__ import annotations

import sys
import tempfile
import urllib.request
from collections import Counter, defaultdict
from math import comb, exp
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402, I001
from ea_direction_test import PROSE_URL, prose_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from word_base_plaintext_closure import (  # noqa: E402
    observed_by_len,
    register_segments_with_words,
)

PROSE_CACHE = Path(tempfile.gettempdir()) / "pg1342.txt"

# Normaliser base-count caps from sigma-power-step.md's enumeration.
COMMUTING_MAX = 500  # r = 1 (sigma commutes with g)
TWISTED_MAX = 300  # r = 2, 3, 4


def kappa_from(by_len: dict[int, Counter]) -> dict[int, float]:
    """kappa_L = P(two random length-L words are equal), unbiased, per length."""
    kappa: dict[int, float] = {}
    for L, counts in by_len.items():
        n = sum(counts.values())
        if n >= 2:
            kappa[L] = sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))
    return kappa


def generic_english_kappa() -> dict[int, float]:
    """Large, stable register: Project Gutenberg #1342 (~120k word tokens)."""
    if not PROSE_CACHE.exists():
        print(f"downloading {PROSE_URL} -> {PROSE_CACHE}")
        urllib.request.urlretrieve(PROSE_URL, PROSE_CACHE)
    by_len: dict[int, Counter[tuple[str, ...]]] = {}
    for w in prose_words(PROSE_CACHE):
        rg = tuple(to_runeglish(w))
        by_len.setdefault(len(rg), Counter())[rg] += 1
    return kappa_from(by_len)


def same_author_kappa() -> dict[int, float]:
    """LP register: the recovered position-preserving solved segments (486 words).

    kappa is a RATE (ratio), so it is not inflated by the small sample the way a
    quadratically-scaled pair count would be.
    """
    by_len: dict[int, Counter[tuple[int, ...]]] = {}
    for words in register_segments_with_words():
        for w in words:
            by_len.setdefault(len(w), Counter())[w] += 1
    return kappa_from(by_len)


def corpus_length_histogram() -> Counter[int]:
    _, wid = load_clean()
    d: dict[int, int] = defaultdict(int)
    for w in wid:
        d[w] += 1
    out: Counter[int] = Counter()
    for L in d.values():
        out[L] += 1
    return out


def pressure_len4(kappa: dict[int, float], lens: Counter[int]) -> float:
    """Expected plaintext repeat pairs summed over the zero-background L >= 4 cells."""
    return sum(comb(lens.get(L, 0), 2) * kappa.get(L, 0.0) for L in range(4, 15))


def report(name: str, kappa: dict[int, float], lens: Counter[int], obs_hi: int) -> None:
    pressure = pressure_len4(kappa, lens)
    print(
        f"\n{name}: len>=4 plaintext repeat pressure {pressure:.0f} pairs; observed {obs_hi}"
    )
    print(f"  {'variant':>22}{'max bases':>11}{'exp forced':>12}{'P(0 obs)':>12}")
    for label, cap in (
        ("commuting (r=1)", COMMUTING_MAX),
        ("twisted (r=2,3,4)", TWISTED_MAX),
    ):
        mu = pressure / cap  # forced repeats if the walk visited only `cap` bases
        p = exp(-mu) if obs_hi == 0 else float("nan")
        print(f"  {label:>22}{cap:>11}{mu:>12.1f}{p:>12.2g}")


def main() -> None:
    obs, corp_words = observed_by_len()
    obs_hi = sum(obs.get(L, 0) for L in range(4, 15))
    lens = corpus_length_histogram()

    print(
        f"corpus: {corp_words} words; observed ciphertext word-repeats at len>=4: "
        f"{obs_hi} (null ~0, word_repeat_census.py)"
    )
    print(
        "\nA normaliser sigma visits <= 5*ord(sigma) bases (commuting <=500, twisted"
        " <=300)\nabout-uniformly, so two equal plaintext words share a base with prob"
        " ~1/N and\nforce a ciphertext word-repeat. Two independent registers:"
    )
    gen = generic_english_kappa()
    report("generic English (conservative)", gen, lens, obs_hi)
    report("same-author LP register", same_author_kappa(), lens, obs_hi)
    print(
        "\nBoth registers disfavour every normaliser sigma (commuting ~2.9sigma on the"
        "\nconservative register, stronger on the same-author one) -- a likelihood, not"
        "\na proof, and contingent on the plaintext repeat-rate estimate."
    )

    # Adjacent corroboration: a strictly periodic base (period P words) makes two
    # words at a gap divisible by P share a base, so equal-word pairs there force
    # repeats at rate ~pressure/P. 0 observed at len>=4 excludes small P. This only
    # RE-confirms running-key-text.md / running-key-math-sequence.md (both already
    # disproved); a non-repeating running key has no period and is out separately.
    if obs_hi == 0:
        p0 = pressure_len4(gen, lens) / 3.0  # p<0.05 <=> forced>3
        print(
            f"\nadjacent (corroboration, not a new result): a strictly PERIODIC base is"
            f"\nexcluded for every period below ~{p0:.0f} words (conservative register)."
        )


if __name__ == "__main__":
    main()
