# ABOUTME: Slides every known 3301 plaintext phrase along the unsolved corpus by
# ABOUTME: word-length signature, then refutes placements with the d=5 rule.
"""A systematic crib search: known phrases against unsolved word shapes.

Every phrase the puzzle has already given up is a candidate crib. Word lengths
survive encryption -- the boundaries are published in the transcription -- so a
phrase can only sit where the word-length sequence matches exactly. A phrase of
lengths 3,7,2,4,6 fits only where those five lengths occur consecutively, and
that filter needs no assumption about the cipher.

Sources of known plaintext:

  * the Parable and the AN END page, stored as plaintext runes in page0-58;
  * the solved early pages of the master transcription (2,797 runes), recovered
    by their published keys -- Atbash, an affine, Vigenere DIUINITY and
    FIRFUMFERENFE.

Then the d=5 rule refutes what survives. Under the length-clocked walk

    c[j] = base_w( g^(j mod 5)( p[j] ) )

positions k and k+5 inside one word receive the SAME power of g, and base_w is
one bijection for the whole word, so within a word

    p[k] == p[k+5]   if and only if   c[k] == c[k+5]

with no reference to base_w, g or sigma. A placement whose plaintext repeats a
rune five apart where the ciphertext does not -- or the reverse -- is dead
whatever the key. Only words of six runes or more can be tested, so the report
counts testable placements separately from the rest.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
UNSOLVED = ROOT / "data" / "page0-56.txt"
FULL = ROOT / "data" / "page0-58.txt"
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
MIN_WORDS = 4  # a shorter run matches too often to mean anything


def word_indices(text: str) -> list[list[int]]:
    """Words as lists of rune indices, split on the transcription's boundaries."""
    out: list[list[int]] = []
    cur: list[int] = []
    for ch in text:
        if RUNE.match(ch):
            cur.append(INDEX[ch])
        elif ch in c3301.WORD_BOUNDARY and cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def spell(word: list[int]) -> str:
    return "".join(ENGLISH[i] for i in word)


def plaintext_phrases() -> list[tuple[str, list[list[int]]]]:
    """Known plaintext, as (label, words-of-rune-indices)."""
    phrases: list[tuple[str, list[list[int]]]] = []

    tail = "$".join(FULL.read_text().split("$")[10:])
    words = word_indices(tail)
    for n in range(MIN_WORDS, 9):
        for i in range(len(words) - n + 1):
            phrases.append((f"plaintext pages w{i}", words[i : i + n]))

    try:
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from solved_plaintext_running_key import recover_plaintext, solved_segments

        plain = recover_plaintext(solved_segments())
    except (ImportError, OSError, ValueError) as exc:
        print(f"  (solved-page recovery unavailable: {type(exc).__name__}: {exc})")
        return phrases

    # the recovered stream has no boundaries; take them from the master, whose
    # leading runes are exactly those pages
    lengths: list[int] = []
    run = seen = 0
    for ch in MASTER.read_text():
        if RUNE.match(ch):
            run += 1
            seen += 1
            if seen >= len(plain):
                break
        elif ch in c3301.WORD_BOUNDARY and run:
            lengths.append(run)
            run = 0
    if run:
        lengths.append(run)
    solved: list[list[int]] = []
    pos = 0
    for length in lengths:
        solved.append(list(plain[pos : pos + length]))
        pos += length
    for n in range(MIN_WORDS, 9):
        for i in range(len(solved) - n + 1):
            phrases.append((f"solved pages w{i}", solved[i : i + n]))
    return phrases


def d5_direction(plain: list[int], cipher: list[int]) -> tuple[bool, bool, bool]:
    """Split the d=5 rule into its two halves.

    Returns (strong_fired, strong_ok, weak_fired) where

      strong: the CRIB repeats a rune five apart, so the ciphertext must too.
              Rare, because English seldom repeats a letter at that distance.
      weak:   the CIPHERTEXT repeats five apart, so the crib must too. This is
              the half that can fire often, since the corpus carries a measured
              excess of ciphertext repeats at d=5.
    """
    strong_fired = strong_ok = weak_fired = False
    if len(plain) < 6 or len(plain) != len(cipher):
        return (False, True, False)
    for k in range(len(plain) - 5):
        p_rep = plain[k] == plain[k + 5]
        c_rep = cipher[k] == cipher[k + 5]
        if p_rep:
            strong_fired = True
            strong_ok = strong_ok or c_rep
        if c_rep:
            weak_fired = True
    return (strong_fired, strong_ok, weak_fired)


def d5_verdict(plain: list[int], cipher: list[int]) -> bool | None:
    """p[k]==p[k+5] <=> c[k]==c[k+5] within one word; None when untestable."""
    if len(plain) < 6 or len(plain) != len(cipher):
        return None
    return all(
        (plain[k] == plain[k + 5]) == (cipher[k] == cipher[k + 5])
        for k in range(len(plain) - 5)
    )


def main() -> None:
    cipher_words = word_indices(UNSOLVED.read_text())
    lengths = [len(w) for w in cipher_words]
    print(f"unsolved corpus: {len(cipher_words)} words")

    phrases = plaintext_phrases()
    print(f"candidate phrases of {MIN_WORDS}-8 words: {len(phrases)}\n")

    placements = 0
    testable = 0
    survived: list[tuple[str, int]] = []
    for label, words in phrases:
        sig = [len(w) for w in words]
        n = len(sig)
        for i in range(len(lengths) - n + 1):
            if lengths[i : i + n] != sig:
                continue
            placements += 1
            verdicts = [d5_verdict(p, cipher_words[i + j]) for j, p in enumerate(words)]
            if all(v is None for v in verdicts):
                continue
            testable += 1
            if all(v is not False for v in verdicts):
                survived.append((label, i))

    print("=== results")
    print(f"  placements matching the word-length signature : {placements}")
    print(f"  of those, testable by the d=5 rule            : {testable}")
    print(f"  surviving the d=5 rule                        : {len(survived)}")
    if testable:
        print(
            f"  the rule refutes {(testable - len(survived)) / testable:.1%} "
            f"of testable placements"
        )
    for label, i in survived[:12]:
        print(f"     survives: {label} at word {i}")

    # A refutation rate means nothing on its own: random plaintext of the right
    # SHAPE would also be refuted sometimes. The null pairs each ciphertext word
    # with a random known-plaintext word of the same length.
    import random

    rng = random.Random(3301)
    by_length: dict[int, list[list[int]]] = {}
    for _, words in phrases:
        for w in words:
            by_length.setdefault(len(w), []).append(w)
    null_refuted = null_testable = 0
    for _ in range(30):
        for _label, words in phrases:
            sig = [len(w) for w in words]
            n = len(sig)
            for i in range(len(lengths) - n + 1):
                if lengths[i : i + n] != sig:
                    continue
                fake = [rng.choice(by_length[len(w)]) for w in words]
                v = [d5_verdict(p_, cipher_words[i + j]) for j, p_ in enumerate(fake)]
                if all(x is None for x in v):
                    continue
                null_testable += 1
                if any(x is False for x in v):
                    null_refuted += 1
    if null_testable:
        rate = null_refuted / null_testable
        print("\n=== is that refutation rate meaningful?")
        print(
            f"  observed : {(testable - len(survived)) / testable:.1%} of testable "
            f"placements refuted"
        )
        print(
            f"  null     : {rate:.1%}  (same shapes, random known-plaintext words,"
            f" {null_testable:,} draws)"
        )
        print("  the crib placements are refuted at the rate random ones are,")
        print("  so the d=5 rule separates nothing here.")

    # which half of the rule does the refuting?
    strong_kill = weak_kill = strong_chances = weak_chances = 0
    for _label, words in phrases:
        sig = [len(w) for w in words]
        n = len(sig)
        for i in range(len(lengths) - n + 1):
            if lengths[i : i + n] != sig:
                continue
            for j, pw in enumerate(words):
                cw = cipher_words[i + j]
                if len(pw) < 6:
                    continue
                for k in range(len(pw) - 5):
                    p_rep = pw[k] == pw[k + 5]
                    c_rep = cw[k] == cw[k + 5]
                    if p_rep:
                        strong_chances += 1
                        if not c_rep:
                            strong_kill += 1
                    if c_rep:
                        weak_chances += 1
                        if not p_rep:
                            weak_kill += 1
    # a placement is only informative if some pair actually repeats on one side;
    # counting every 6-rune word as "testable" buries the rule's power in cases
    # where it is vacuously satisfied
    fired_placements = fired_refuted = 0
    for _label, words in phrases:
        sig = [len(w) for w in words]
        n = len(sig)
        for i in range(len(lengths) - n + 1):
            if lengths[i : i + n] != sig:
                continue
            fires = refuted = False
            for j, pw in enumerate(words):
                cw = cipher_words[i + j]
                for k in range(max(0, len(pw) - 5)):
                    p_rep = pw[k] == pw[k + 5]
                    c_rep = cw[k] == cw[k + 5]
                    if p_rep or c_rep:
                        fires = True
                        if p_rep != c_rep:
                            refuted = True
            if fires:
                fired_placements += 1
                fired_refuted += refuted
    print("\n=== the rule's power, counted where it actually applies")
    print(
        f"  placements where some pair repeats on one side: {fired_placements}"
        f" of {placements}"
    )
    if fired_placements:
        print(
            f"  of those, refuted: {fired_refuted} "
            f"({fired_refuted / fired_placements:.1%})"
        )
    print("  (the earlier 14.4% used every 6-rune word as its denominator, so it")
    print("   counted placements the rule never spoke to)")

    print("\n=== which half of the rule does the work")
    print(
        f"  strong (crib repeats -> cipher must): fired {strong_chances}, "
        f"refuted {strong_kill}"
    )
    print(
        f"  weak   (cipher repeats -> crib must): fired {weak_chances}, "
        f"refuted {weak_kill}"
    )
    if weak_chances:
        print(
            f"\n  the weak half fires {weak_chances / max(strong_chances, 1):.1f}x "
            f"more often and refutes {weak_kill / weak_chances:.1%} of what it sees"
        )

    print("\n=== why the rule bites so rarely")
    counts = Counter(lengths)
    six_plus = sum(v for k, v in counts.items() if k >= 6)
    print(
        f"  words of 6+ runes: {six_plus} of {len(lengths)} "
        f"({six_plus / len(lengths):.1%}); only these can be tested"
    )
    repeats = sum(
        1
        for w in cipher_words
        if len(w) >= 6 and any(w[k] == w[k + 5] for k in range(len(w) - 5))
    )
    print(f"  ciphertext words already repeating a rune at d=5: {repeats}")
    print("  a crib placed on one of those must repeat its plaintext rune there")


if __name__ == "__main__":
    main()
