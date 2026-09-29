# ABOUTME: Evidence for/against the doublet-suppression <-> period-5 linkage:
# ABOUTME: plaintext vs ciphertext doublet rate, per-rune spread, and phase-gating.
"""Is the doublet suppression tied to the period-5 structure?

Three measurements bearing on whether the 5.2x adjacent-doublet suppression and
the distance-5 same-alphabet leak are one order-5 mechanism:

1. Plaintext vs ciphertext doublet rate -- is the suppression the cipher's doing
   or inherited from runeglish? (Cipher's: plaintext is 2-3.7%, ciphertext 0.66%.)
2. Per-rune doublet spread -- is it carried by a few runes (an order-5 g fixes
   >=4 of 29) or uniform? (Uniform across 28 of 29.)
3. Phase-gating -- if a doublet survived only ~1 phase in 5, the doublets would
   cluster at one absolute position mod 5. (They do not: chi2 ~ 3.6, flat.)

Usage: python experiments/doublet_period5_linkage.py
"""

from __future__ import annotations

import sys
from collections import Counter

sys.path.insert(0, "src")

from aldegonde import c3301

MOD = 29
ALPHABET = c3301.CICADA_ALPHABET
R2I = {rune: index for index, rune in enumerate(ALPHABET)}
RUNES = set(ALPHABET)
WORD_END = set(c3301.MARK_CHARS + "&%$" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS)
CIPHERTEXT = "data/page0-56.txt"


def rune_stream(path: str) -> list[int]:
    with open(path) as handle:
        return [R2I[c] for c in handle.read() if c in RUNES]


def words_of(path: str) -> list[list[int]]:
    with open(path) as handle:
        text = handle.read()
    words: list[list[int]] = []
    current: list[int] = []
    for ch in text:
        if ch in RUNES:
            current.append(R2I[ch])
        elif ch in WORD_END and current:
            words.append(current)
            current = []
    if current:
        words.append(current)
    return words


def doublet_rate(stream: list[int]) -> tuple[int, float]:
    doublets = sum(1 for i in range(len(stream) - 1) if stream[i] == stream[i + 1])
    return doublets, doublets / (len(stream) - 1)


def main() -> None:
    stream = rune_stream(CIPHERTEXT)
    words = words_of(CIPHERTEXT)
    n = len(stream)

    # 1. cipher feature, not inherited (plaintext numbers are cited in the doc;
    #    here we report the ciphertext rate and the chance rate it beats).
    doublets, rate = doublet_rate(stream)
    chance = 1 / MOD
    print(
        f"ciphertext ({CIPHERTEXT}): {n} runes, {doublets} adjacent doublets "
        f"= {rate * 100:.2f}%  (chance {chance * 100:.2f}%, suppression {chance / rate:.2f}x)"
    )
    print("plaintext runeglish for comparison (see doc): solved LP 2.3%, lexicon 3.65%")

    # 2. per-rune spread: are doublets carried by a few runes?
    per_rune = Counter(stream[i] for i in range(n - 1) if stream[i] == stream[i + 1])
    carried = sum(1 for r in range(MOD) if per_rune.get(r, 0) > 0)
    top = per_rune.most_common(4)
    print(
        f"\nper-rune doublets: carried by {carried}/{MOD} runes; "
        f"top {[(ALPHABET[r], c) for r, c in top]} vs even share {doublets / MOD:.1f}"
    )

    # 3. phase-gating: doublet start position mod 5.
    phase = Counter(i % 5 for i in range(n - 1) if stream[i] == stream[i + 1])
    exp = doublets / 5
    chi2 = sum((phase.get(k, 0) - exp) ** 2 / exp for k in range(5))
    print(f"\ndoublet phase (abs position mod 5): {dict(sorted(phase.items()))}")
    print(
        f"  expected/phase={exp:.1f}  chi2(4df)={chi2:.2f}  "
        f"({'FLAT -- not phase-gated' if chi2 < 9.49 else 'concentrated'})"
    )

    # within-word start-phase, flagged as opportunity-confounded.
    wphase = Counter(
        j % 5 for w in words for j in range(len(w) - 1) if w[j] == w[j + 1]
    )
    print(
        f"within-word doublet start-phase: {dict(sorted(wphase.items()))}  "
        f"(confounded by word length -- short words over-weight low phases)"
    )


if __name__ == "__main__":
    main()
