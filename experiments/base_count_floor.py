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

    N >~ sum_{L>=4} C(m_L, 2) * kappa_L / 3.

kappa_L is estimated on a large generic-English runeglish register (Project
Gutenberg #1342, ~120k word tokens). Generic prose is LESS repetitive than the
LP's header-heavy register, so this UNDER-estimates kappa, hence N -- any
N > 500 here is a conservative exclusion of the commuting sigma.
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
from word_base_plaintext_closure import observed_by_len  # noqa: E402

PROSE_CACHE = Path(tempfile.gettempdir()) / "pg1342.txt"

# Normaliser base-count caps from sigma-power-step.md's enumeration.
COMMUTING_MAX = 500  # r = 1 (sigma commutes with g)
TWISTED_MAX = 300  # r = 2, 3, 4


def register_collision_by_len() -> dict[int, float]:
    """kappa_L = P(two random length-L register words are equal), unbiased."""
    if not PROSE_CACHE.exists():
        print(f"downloading {PROSE_URL} -> {PROSE_CACHE}")
        urllib.request.urlretrieve(PROSE_URL, PROSE_CACHE)
    by_len: dict[int, Counter[tuple[str, ...]]] = {}
    for w in prose_words(PROSE_CACHE):
        rg = tuple(to_runeglish(w))
        by_len.setdefault(len(rg), Counter())[rg] += 1
    kappa: dict[int, float] = {}
    for L, counts in by_len.items():
        n = sum(counts.values())
        if n >= 2:
            kappa[L] = sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))
    return kappa


def main() -> None:
    kappa = register_collision_by_len()
    obs, corp_words = observed_by_len()

    # corpus length histogram
    stream, wid = load_clean()
    lens: Counter[int] = Counter()
    d: dict[int, int] = defaultdict(int)
    for w in wid:
        d[w] += 1
    for L in d.values():
        lens[L] += 1

    print(f"corpus: {corp_words} words; register kappa from Gutenberg #1342\n")
    print(f"  {'len':>4}{'corpus m_L':>11}{'kappa_L':>11}{'pt pairs':>11}{'obs ct':>8}")
    floor_num = 0.0
    for L in range(1, 15):
        m = lens.get(L, 0)
        k = kappa.get(L, 0.0)
        pt_pairs = comb(m, 2) * k
        if L >= 4:
            floor_num += pt_pairs
        mark = "  <- zero bg" if L >= 4 else ""
        print(f"  {L:>4}{m:>11}{k:>11.5f}{pt_pairs:>11.0f}{obs.get(L, 0):>8}{mark}")

    obs_hi = sum(obs.get(L, 0) for L in range(4, 15))
    print(
        f"\nlen>=4 plaintext repeat pressure: {floor_num:.0f} pairs; "
        f"observed ciphertext repeats there: {obs_hi} (null ~0)"
    )
    print("\nexclusion of a normaliser sigma via its base-count cap:")
    print(f"  {'variant':>22}{'max bases':>11}{'exp forced':>12}{'P(0 obs)':>12}")
    for name, cap in (
        ("commuting (r=1)", COMMUTING_MAX),
        ("twisted (r=2,3,4)", TWISTED_MAX),
    ):
        mu = floor_num / cap  # forced repeats if the walk visited only `cap` bases
        p = exp(-mu) if obs_hi == 0 else float("nan")
        print(f"  {name:>22}{cap:>11}{mu:>12.1f}{p:>12.2g}")
    print(
        "\n  A normaliser sigma visits <= 5*ord(sigma) bases; equidistribution + "
        "plaintext-\n  repeat gaps independent of the cipher period give "
        "P(two equal words share a\n  base) ~ 1/N, so fewer bases force MORE repeats. "
        "Generic prose under-estimates\n  the LP register's repetition, so this "
        "exclusion is conservative."
    )


if __name__ == "__main__":
    main()
