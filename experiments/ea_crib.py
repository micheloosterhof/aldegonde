#!/usr/bin/env python3
# ABOUTME: Cribs Liber Primus doublet-affected words under the assumption that
# ABOUTME: the doublet marker rune is EA, matching against a runeglish dictionary.
"""EA-crib analysis for Liber Primus doublets.

Premise (see hypotheses/doublet-marker-rune-ea.md): each ciphertext doublet
C[i]==C[i+1] marks one position where the plaintext rune is EA (ᛠ). The marker
is the 2nd rune of the doublet under forward keystream, the 1st under reverse.

A polyalphabetic/autokey cipher preserves length, so a ciphertext word of L
runes is a plaintext runeglish word of L runes. Placing EA at the known
position turns each affected word into a partial crib: a length-L word with EA
fixed at position p. We match that against the system dictionary encoded to
runeglish; few matches => strong crib.
"""

from __future__ import annotations

import sys
from collections import Counter

from aldegonde import c3301

DATA = "data/page0-58.txt"
WORDS = "/usr/share/dict/words"
EA = "ᛠ"
RUNES = set(c3301.CICADA_ALPHABET)
WORD_BOUNDARIES = set("-.&$§%")

# Greedy English -> runeglish (Gematria Primus). Digraphs win over singles.
DIGRAPHS = {"TH": "ᚦ", "EO": "ᛇ", "NG": "ᛝ", "OE": "ᛟ", "AE": "ᚫ",
            "IA": "ᛡ", "IO": "ᛡ", "EA": "ᛠ"}
SINGLE = {"F": "ᚠ", "U": "ᚢ", "O": "ᚩ", "R": "ᚱ", "C": "ᚳ", "K": "ᚳ", "G": "ᚷ",
          "W": "ᚹ", "H": "ᚻ", "N": "ᚾ", "I": "ᛁ", "J": "ᛄ", "P": "ᛈ", "X": "ᛉ",
          "S": "ᛋ", "T": "ᛏ", "B": "ᛒ", "E": "ᛖ", "M": "ᛗ", "L": "ᛚ", "D": "ᛞ",
          "A": "ᚪ", "Y": "ᚣ", "Q": "ᚳ", "V": "ᚠ", "Z": "ᛋ"}


def to_runeglish(word: str) -> list[str] | None:
    """Encode an English word to a runeglish rune list, or None if it has a
    character outside the supported set."""
    w = word.upper()
    out: list[str] = []
    i = 0
    while i < len(w):
        dg = w[i:i + 2]
        if dg in DIGRAPHS:
            out.append(DIGRAPHS[dg])
            i += 2
        elif w[i] in SINGLE:
            out.append(SINGLE[w[i]])
            i += 1
        else:
            return None
    return out


def parse_words(text: str) -> list[str]:
    words: list[str] = []
    cur: list[str] = []
    for ch in text:
        if ch in RUNES:
            cur.append(ch)
        elif ch in WORD_BOUNDARIES and cur:
            words.append("".join(cur))
            cur = []
    if cur:
        words.append("".join(cur))
    return words


def load_ea_dictionary() -> list[tuple[str, int, tuple[int, ...]]]:
    """Return (word, runeglish_length, ea_positions_1based) for dict words
    whose runeglish form contains EA."""
    out = []
    with open(WORDS, encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if not w or not w.isalpha():
                continue
            rg = to_runeglish(w)
            if rg is None or EA not in rg:
                continue
            pos = tuple(j + 1 for j, r in enumerate(rg) if r == EA)
            out.append((w.lower(), len(rg), pos))
    return out


def candidates(ea_dict, length: int, p: int, limit: int = 8) -> tuple[int, list[str]]:
    hits = [w for (w, L, pos) in ea_dict if length == L and p in pos]
    # dedupe preserving order
    seen: dict[str, None] = {}
    for w in hits:
        seen.setdefault(w, None)
    uniq = list(seen)
    return len(uniq), uniq[:limit]


def report(label: str, cribs: list[tuple], ea_dict) -> None:
    print("\n" + "=" * 72)
    print(label)
    print("=" * 72)
    # cribs: list of (rune_word, length, marker_pos, doublet_kind)
    scored = []
    for w, L, p, kind in cribs:
        cnt, examples = candidates(ea_dict, L, p)
        scored.append((cnt, w, L, p, kind, examples))
    scored.sort(key=lambda x: (x[0], x[2]))
    nz = [s for s in scored if s[0] > 0]
    print(f"affected words: {len(scored)}   with >=1 dictionary match: {len(nz)}   "
          f"no match: {len(scored) - len(nz)}")
    sizes = Counter(min(s[0], 50) for s in scored)
    print(f"candidate-set sizes: unique(1)={sizes[1]}  2-5="
          f"{sum(v for k, v in sizes.items() if 2 <= k <= 5)}  "
          f"6-20={sum(v for k, v in sizes.items() if 6 <= k <= 20)}  "
          f">20={sum(v for k, v in sizes.items() if k > 20)}  none={sizes[0]}")
    print("\nStrongest cribs (fewest candidates first):")
    print(f"  {'cipher word':<18} {'L':>2} {'EA@':>3} {'kind':<6} {'#cand':>5}  examples")
    for cnt, w, L, p, kind, ex in scored[:24]:
        marker = w[:p - 1] + f"[{EA}]" + w[p:]
        print(f"  {marker:<24} {L:>2} {p:>3} {kind:<6} {cnt:>5}  {', '.join(ex) if ex else '(none)'}")


def main() -> None:
    with open(DATA, encoding="utf-8") as f:
        text = f.read()
    words = parse_words(text)

    # stream with word metadata
    stream: list[str] = []
    wid: list[int] = []
    pos1: list[int] = []
    wlen: list[int] = []
    for i, w in enumerate(words):
        for p, r in enumerate(w, start=1):
            stream.append(r)
            wid.append(i)
            pos1.append(p)
            wlen.append(len(w))
    n = len(stream)
    doublets = [i for i in range(n - 1) if stream[i] == stream[i + 1]]

    print(f"Source {DATA}: {len(words)} words, {n} runes, {len(doublets)} doublets.")
    lone = sum(1 for i in doublets if wlen[i] == 1 or wlen[i + 1] == 1)
    print(f"Doublets touching a 1-rune word: {lone}  "
          f"(consistency: EA is never a standalone word, so this should be 0)")
    print("Building runeglish dictionary (this reads /usr/share/dict/words)...")
    ea_dict = load_ea_dictionary()
    print(f"  dictionary words whose runeglish contains EA: {len(ea_dict)}")

    # EA = 2nd rune of the doublet (forward keystream)
    cribs_2nd = [(words[wid[i + 1]], wlen[i + 1], pos1[i + 1],
                  "cross" if wid[i] != wid[i + 1] else "in") for i in doublets]
    report("EA = 2nd rune of each doublet (forward keystream)", cribs_2nd, ea_dict)

    # EA = 1st rune of the doublet (reverse keystream)
    cribs_1st = [(words[wid[i]], wlen[i], pos1[i],
                  "cross" if wid[i] != wid[i + 1] else "in") for i in doublets]
    report("EA = 1st rune of each doublet (reverse keystream)", cribs_1st, ea_dict)

    # Multi-EA words: a single word carrying two distinct marker positions is a
    # far stronger crib (both EAs fixed). Count distinct markers per word.
    for label, marker_of in (("forward (EA=2nd rune)", lambda i: (wid[i + 1], pos1[i + 1])),
                             ("reverse (EA=1st rune)", lambda i: (wid[i], pos1[i]))):
        per_word: dict[int, set[int]] = {}
        for i in doublets:
            w, p = marker_of(i)
            per_word.setdefault(w, set()).add(p)
        multi = {w: ps for w, ps in per_word.items() if len(ps) >= 2}
        print("\n" + "=" * 72)
        print(f"MULTI-EA words, {label}: {len(multi)} word(s) with >=2 fixed EA positions")
        print("=" * 72)
        for w, ps in sorted(multi.items()):
            rw, L = words[w], len(words[w])
            ps_sorted = sorted(ps)
            hits = [d for (d, dl, dpos) in ea_dict
                    if dl == L and all(p in dpos for p in ps_sorted)]
            seen: dict[str, None] = {}
            for h in hits:
                seen.setdefault(h, None)
            uniq = list(seen)
            marked = "".join(f"[{EA}]" if (j + 1) in ps else r for j, r in enumerate(rw))
            print(f"  {marked}  L={L} EA@{ps_sorted}  #cand={len(uniq)}: "
                  f"{', '.join(uniq[:10]) if uniq else '(NONE - tension with EA assumption)'}")


if __name__ == "__main__":
    sys.exit(main())
