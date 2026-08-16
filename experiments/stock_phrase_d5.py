# ABOUTME: Slides 3301 STOCK phrases (register, not just recovered plaintext) across
# ABOUTME: the unsolved corpus and filters by the key-free d=5 repeat rule.
"""Do Cicada's recurring stock phrases fit anywhere in the unsolved corpus?

3301 reuses stock phrases (DIVINITY WITHIN, THE LOSS OF DIVINITY, THE PRIMES ARE
SACRED, ...). `crib_phrase_search.py` slides only phrases it already HAS as
plaintext (Parable, AN END, solved pages); it never tried the register's stock
phrases. This does, using the same key-free filter: within a word

    p[k] == p[k+5]   <=>   c[k] == c[k+5]

The discriminating half is the d5 REPEAT -- a stock phrase whose plaintext
repeats a rune five apart (STRONG fire) can sit only where the ciphertext repeats
there too, which is rare. A placement matching the word-length signature and
never violating the d5 rule on any testable (>= 6 rune) word is a candidate
location. A STRONG survivor -- one that carries a plaintext d5 repeat matched by
the ciphertext -- is the real lead.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from crib_phrase_search import (  # noqa: E402, I001
    INDEX,
    UNSOLVED,
    d5_direction,
    d5_verdict,
    spell,
    word_indices,
)
from runeglish_frequency import english_to_runeglish  # noqa: E402

# Cicada 3301 stock phrases and register fragments (2+ words; long words carry d5).
STOCK = [
    "DIVINITY WITHIN",
    "THE LOSS OF DIVINITY",
    "FIND THE DIVINITY WITHIN",
    "AN INSTRUCTION",
    "SOME WISDOM",
    "THE PRIMES ARE SACRED",
    "THE TOTIENT FUNCTION IS SACRED",
    "A WARNING",
    "BELIEVE NOTHING FROM THIS BOOK",
    "WELCOME PILGRIM",
    "THE GREAT JOURNEY",
    "TOWARD THE END OF ALL THINGS",
    "THE END OF ALL THINGS",
    "WITHIN THE DEEP WEB",
    "SHED YOUR CIRCUMFERENCES",
    "WE MUST SHED OUR OWN CIRCUMFERENCES",
    "LIKE THE INSTAR",
    "TUNNELING TO THE SURFACE",
    "THE INSTAR EMERGENCE",
    "ALL THINGS ARE ENCRYPTED",
    "KNOW THIS",
    "THE PATH",
    "THE SEEKER",
    "THE PILGRIMS",
    "THE DECEPTION",
    "CONSUMPTION",
    "PRESERVATION",
    "REALITY IS AN ILLUSION",
    "THE UNIVERSE IS A HOLOGRAM",
    "BUY GOLD",
]


def phrase_words(phrase: str) -> list[list[int]]:
    return [
        [INDEX[c] for c in english_to_runeglish(w.upper()) if c in INDEX]
        for w in phrase.split()
    ]


def main() -> None:
    cipher_words = word_indices(UNSOLVED.read_text())
    lengths = [len(w) for w in cipher_words]
    print(f"unsolved corpus: {len(cipher_words)} words; {len(STOCK)} stock phrases\n")

    placements = testable = 0
    survivors: list[tuple[str, int, bool]] = []  # (phrase, word index, strong?)
    for phrase in STOCK:
        words = phrase_words(phrase)
        sig = [len(w) for w in words]
        n = len(sig)
        if n < 2:
            continue
        for i in range(len(lengths) - n + 1):
            if lengths[i : i + n] != sig:
                continue
            placements += 1
            verdicts = [d5_verdict(p, cipher_words[i + j]) for j, p in enumerate(words)]
            if all(v is None for v in verdicts):
                continue
            testable += 1
            if any(v is False for v in verdicts):
                continue
            # strong: some word's plaintext repeats a rune 5 apart and the cipher agrees
            strong = any(
                d5_direction(p, cipher_words[i + j])[0]
                for j, p in enumerate(words)
            )
            survivors.append((phrase, i, strong))

    print("=== results")
    print(f"  placements matching a word-length signature : {placements}")
    print(f"  testable by the d=5 rule                    : {testable}")
    print(f"  surviving the d=5 rule                      : {len(survivors)}")
    strong = [s for s in survivors if s[2]]
    print(f"  of those, STRONG (a d5 repeat matched)      : {len(strong)}\n")
    for phrase, i, is_strong in sorted(survivors, key=lambda s: (not s[2], s[0])):
        n = len(phrase_words(phrase))
        shown = " ".join(spell(w) for w in cipher_words[i : i + n])
        tag = "STRONG" if is_strong else "weak  "
        print(f"  [{tag}] {phrase!r} @ word {i}: cipher '{shown}'")


if __name__ == "__main__":
    main()
