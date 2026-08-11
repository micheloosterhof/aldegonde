# ABOUTME: Matches known plaintext SENTENCES against unsolved sentences, whole
# ABOUTME: unit to whole unit, then applies the d=5 rule where it can fire.
"""Sentence-level cribbing: one boundary to the next, not a sliding window.

A sliding window ignores what the transcription already tells us. The cluster
marks and the quotation marks divide the text into units, and a known sentence
must occupy a whole unit -- same word count, same word lengths in order, and it
should end on the same kind of mark. That is far stronger than finding the same
length sequence somewhere in the middle of a longer unit.

The d=5 rule then applies to whatever survives. Under the length-clocked walk,
positions k and k+5 inside a word take the same power of g through one bijection,
so within a word

    p[k] == p[k+5]   if and only if   c[k] == c[k+5]

and it has two halves that fire in different circumstances:

  strong  the CRIB repeats a rune five apart, so the ciphertext must too
  weak    the CIPHERTEXT repeats, so the crib must too

Both are near-certain killers when they fire, and both are silent otherwise --
which is the whole difficulty. Counting every long word as "tested" hides that:
the rule speaks only where one side actually repeats.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
RUNE = re.compile(r"[ᚠ-᛿]")
INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
# a sentence closes at a cluster mark or a quotation mark, not at a word separator
ENDERS = c3301.CLUSTER_MARKS | c3301.QUOTES

Unit = tuple[list[list[int]], str]


def units(text: str, plain: list[int] | None = None) -> list[Unit]:
    """Sentence units as (words of rune indices, closing mark)."""
    out: list[Unit] = []
    cur: list[list[int]] = []
    word: list[int] = []
    n = 0
    for ch in text:
        if RUNE.match(ch):
            word.append(plain[n] if plain is not None else INDEX[ch])
            n += 1
        elif ch in c3301.WORD_BOUNDARY:
            if word:
                cur.append(word)
                word = []
            if ch in ENDERS and cur:
                out.append((cur, ch))
                cur = []
    if word:
        cur.append(word)
    if cur:
        out.append((cur, ""))
    return out


def spell(word: list[int]) -> str:
    return "".join(ENGLISH[i] for i in word)


def known_units() -> list[tuple[str, Unit]]:
    """Every known plaintext sentence, labelled by source."""
    out: list[tuple[str, Unit]] = []
    tail = "$".join((ROOT / "data" / "page0-58.txt").read_text().split("$")[10:])
    for u in units(tail):
        out.append(("plaintext pages", u))

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from solved_plaintext_running_key import recover_plaintext, solved_segments

        plain = recover_plaintext(solved_segments())
    except (ImportError, OSError, ValueError) as exc:
        print(f"  (solved pages unavailable: {type(exc).__name__}: {exc})")
        return out
    master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text()
    # the recovered stream is exactly the master's leading runes, so the master's
    # own marks supply the sentence boundaries
    cut = []
    seen = 0
    for ch in master:
        cut.append(ch)
        if RUNE.match(ch):
            seen += 1
            if seen >= len(plain):
                break
    for u in units("".join(cut), plain):
        out.append(("solved pages", u))
    return out


def d5(plain: list[int], cipher: list[int]) -> tuple[bool, bool]:
    """(the rule fired, the placement is refuted) for one word."""
    fired = refuted = False
    for k in range(max(0, len(plain) - 5)):
        p_rep = plain[k] == plain[k + 5]
        c_rep = cipher[k] == cipher[k + 5]
        if p_rep or c_rep:
            fired = True
            if p_rep != c_rep:
                refuted = True
    return fired, refuted


def main() -> None:
    cipher_units = units((ROOT / "data" / "page0-56.txt").read_text())
    known = known_units()
    print(f"\nunsolved sentence units : {len(cipher_units)}")
    print(f"known plaintext sentences: {len(known)}\n")

    shape_hits = mark_hits = fired = refuted = 0
    survivors: list[str] = []
    for label, (pwords, pmark) in known:
        psig = [len(w) for w in pwords]
        for cwords, cmark in cipher_units:
            if [len(w) for w in cwords] != psig:
                continue
            shape_hits += 1
            same_mark = pmark == cmark
            mark_hits += same_mark
            f = r = False
            for pw, cw in zip(pwords, cwords):
                a, b = d5(pw, cw)
                f |= a
                r |= b
            fired += f
            refuted += r
            if not r:
                text = " ".join(spell(w) for w in pwords)
                survivors.append(
                    f"{label}: {len(psig)} words {psig}"
                    f"{' (same closing mark)' if same_mark else ''}  {text[:60]}"
                )

    print("=== whole-sentence placements")
    print(f"  units matching word count and every word length : {shape_hits}")
    print(f"  of those, also closing on the same mark         : {mark_hits}")
    print(f"  where the d=5 rule fires at all                 : {fired}")
    print(f"  refuted by it                                   : {refuted}")
    if fired:
        print(
            f"  refutation rate where it speaks                 : {refuted / fired:.1%}"
        )
    print(f"\n  surviving placements: {len(survivors)}")
    for s in survivors[:15]:
        print(f"     {s}")


if __name__ == "__main__":
    main()
