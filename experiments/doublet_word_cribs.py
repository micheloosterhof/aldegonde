# ABOUTME: Prunes plaintext candidates for doublet-bearing short words using the
# ABOUTME: diagonal budget, which forces the doublet's plaintext bigram to be rare.
"""Every doublet marks a RARE plaintext bigram, so it prunes the word.

Inside a word `base_w` is one bijection, so a ciphertext doublet at position k
means

    p_k == g(p_{k+1})

and that plaintext bigram `(p_k, p_{k+1})` is one of the 29 terms of g's
diagonal, `sum_b P(g(b), b)`, measured at **0.00628 +- 0.00079** (63 doublets in
10,028 pairs). Every term is non-negative, so each individual term obeys

    P(p_k, p_{k+1}) <= 0.00786          (the point estimate plus 2 sigma)

An earlier version used the point estimate 0.0063 as a hard bound, which is too
tight: the diagonal is a MEASUREMENT, and words sitting between 0.0063 and 0.0079
cannot be excluded. Carrying the error returns IT, HE and AS to the candidate list
and drops the excluded register share from 65% to 51%.

That inverts the usual crib logic. A doublet does not mark a common word; it
marks a place where the plaintext bigram is RARE, because a frequent bigram
would exhaust the whole diagonal budget by itself.

The corpus has exactly one 2-rune doublet word, and it is the sharpest single
constraint available: the whole word is two runes, so the plaintext is one of a
few dozen 2-letter English words, and the budget excludes twelve of them --
including THE, TO, OF and IN -- four of the eight words that make up 69% of the
2-rune class, and 51% of its register share. BE, IT, HE and AS survive.

The bound is rigorous but loose. A tighter one follows from g's four fixed
points, which contribute plaintext-doublet mass P(b, b) apiece and so consume
much of the 0.0063 unless g fixes only rarely-doubling runes -- the
HEAVY_DOUBLERS condition `construction_search.py` already imposes. This script
reports both the rigorous bound and the conditional tighter one, and never
asserts the tighter one as established.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.stats.compare import loadgrams  # noqa: E402

IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ALPHA = c3301.CICADA_ALPHABET
DIAGONAL = 0.00786  # measured 0.00628 + 2 sigma (63 doublets in 10,028)
MAX_LEN = 4  # beyond this the candidate word list stops pruning usefully

# The 2-rune class, register-weighted; share of 2-rune tokens where known.
TWO_RUNE = [
    ("THE", 0.16),
    ("TO", 0.15),
    ("OF", 0.13),
    ("IN", 0.07),
    ("IT", 0.05),
    ("HE", 0.05),
    ("BE", 0.04),
    ("AS", 0.04),
    ("AT", None),
    ("ON", None),
    ("IS", None),
    ("OR", None),
    ("WE", None),
    ("SO", None),
    ("DO", None),
    ("IF", None),
    ("MY", None),
    ("NO", None),
    ("UP", None),
    ("US", None),
    ("AN", None),
    ("BY", None),
    ("ME", None),
    ("GO", None),
    ("AM", None),
    ("OH", None),
    ("AX", None),
    ("OX", None),
]


def bigram_table() -> dict[str, float]:
    grams = loadgrams("aldegonde.data.ngrams.runeglish", "bigrams.txt")
    total = sum(grams.values())
    return {k: v / total for k, v in grams.items()}


def to_runes(word: str) -> str:
    return "".join(c for c in english_to_runeglish(word.upper()) if c in IDX)


def doublet_words(limit: int) -> list[tuple[int, int, int, str]]:
    """(word index, length, doublet position, ciphertext) for short words."""
    out = []
    for wi, w in enumerate(load_words()):
        for k in range(len(w) - 1):
            if w[k] == w[k + 1] and len(w) <= limit:
                out.append((wi, len(w), k, "".join(ALPHA[r] for r in w)))
    return out


def main() -> None:
    P = bigram_table()
    found = doublet_words(MAX_LEN)
    two = [f for f in found if f[1] == 2]

    print(f"short doublet-bearing words (L <= {MAX_LEN}): {len(found)}")
    print(f"of which 2-rune: {len(two)}\n")

    print("=== the 2-rune doublet word: the sharpest constraint in the corpus ===")
    for wi, _L, k, txt in two:
        print(f"word {wi}, ciphertext {txt}, doublet at {k}")
        print("  the whole word is the doublet, so p0 = g(p1) and P(p0,p1) is a")
        print(f"  single term of a diagonal totalling {DIAGONAL}\n")
        print(f"  {'word':>5}{'runes':>7}{'P(p0,p1)':>11}{'share':>8}  verdict")
        rows = []
        for eng, share in TWO_RUNE:
            r = to_runes(eng)
            if len(r) != 2:
                continue
            rows.append((P.get(r, 0.0), eng, r, share))
        excluded_share = 0.0
        for p, eng, r, share in sorted(rows):
            ok = p <= DIAGONAL
            if not ok and share:
                excluded_share += share
            tag = "possible" if ok else f"EXCLUDED {p / DIAGONAL:.1f}x over"
            s = f"{share:.0%}" if share else "-"
            print(f"  {eng:>5}{r:>7}{p:>11.5f}{s:>8}  {tag}")
        survivors = [e for p, e, _r, _s in rows if p <= DIAGONAL]
        print(f"\n  {len(survivors)} of {len(rows)} survive: {', '.join(survivors)}")
        print(f"  register share excluded: {excluded_share:.0%} of the 2-rune class")

    print("\n=== 3- and 4-rune doublet words: same bound, per position ===")
    print("Each needs a word list to enumerate; the bound applies to the bigram at")
    print("the doublet position. Reported here as the constraint, not the solution.")
    print(f"\n{'word':>6}{'L':>3}{'pos':>5}  ciphertext   constraint")
    for wi, L, k, txt in found:
        if L == 2:
            continue
        print(f"{wi:>6}{L:>3}{k:>5}  {txt:<11}  P(p{k},p{k + 1}) <= {DIAGONAL}")

    print("\nCaveat: the bound is rigorous (terms are non-negative and sum to the")
    print("measured diagonal). A tighter bound needs g's four fixed points, which")
    print("carry plaintext-doublet mass P(b,b) each; that is conditional on which")
    print("runes g fixes and is NOT asserted here.")


if __name__ == "__main__":
    main()
