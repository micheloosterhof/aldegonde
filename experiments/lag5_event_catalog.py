#!/usr/bin/env python3
"""Emit a machine-readable catalog of every lag-5 event in the corpus.

Under the surviving copy-semantics family (`lag5-back-reference.md`), the
lag-5 events are the only plaintext-correlated marks in the unsolved
corpus besides the doublets. This catalog fixes their coordinates once,
so any future key-search can consume the conditional constraints
(P[i] = P[i-5] at event positions under the back-reference branch, or
"skip C[i]" under the nulls branch) without re-deriving them.

Output: hypotheses/lag5-event-catalog.json

    corpus     : "clean unsolved corpus" = sections 0-9 of
                 data/page0-58.txt, runes only, 12,956 symbols;
                 index = 0-based offset into that stream
    matches    : every i with C[i] == C[i+5]; classification
                 (paired-d1 / paired-d4 / isolated), word info
    d1_events  : i with M[i] and M[i+1] (digraph copy candidates)
    d4_events  : i with M[i] and M[i+4] (frame copy candidates)
    doublets   : every i with C[i] == C[i+1]
    words      : index of first rune of each word (for cross-reference)

Usage: python experiments/lag5_event_catalog.py
"""

from __future__ import annotations

import json

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
WORD_BOUNDARIES = set("-.&%")
OUT = "hypotheses/lag5-event-catalog.json"
D = 5


def parse() -> tuple[list[int], list[int], list[int]]:
    """stream, section id per position, word id per position."""
    with open(DATA) as f:
        text = f.read()
    stream: list[int] = []
    sec_of: list[int] = []
    word_of: list[int] = []
    sec = 0
    word = 0
    in_word = False
    for ch in text:
        if ch in R2I:
            stream.append(R2I[ch])
            sec_of.append(sec)
            word_of.append(word)
            in_word = True
        elif ch == "$":
            if in_word:
                word += 1
                in_word = False
            sec += 1
        elif ch in WORD_BOUNDARIES and in_word:
            word += 1
            in_word = False
    # keep sections 0-9 only (10 = solved AN END, 11 = plaintext Parable)
    keep = [i for i, s in enumerate(sec_of) if s < 10]
    assert len(keep) == 12956, len(keep)
    return ([stream[i] for i in keep], [sec_of[i] for i in keep],
            [word_of[i] for i in keep])


def main() -> None:
    c, sec_of, word_of = parse()
    n = len(c)
    m = [c[i] == c[i + D] for i in range(n - D)]

    d1 = [i for i in range(len(m) - 1) if m[i] and m[i + 1]]
    d4 = [i for i in range(len(m) - 4) if m[i] and m[i + 4]]
    paired = set()
    for i in d1:
        paired.update((i, i + 1))
    for i in d4:
        paired.update((i, i + 4))

    # word start offsets
    word_start: dict[int, int] = {}
    for i, w in enumerate(word_of):
        word_start.setdefault(w, i)

    matches = []
    for i in range(len(m)):
        if not m[i]:
            continue
        within = word_of[i] == word_of[i + D]
        cls = ("paired-d1" if (i in paired and
                               ((i in d1) or (i - 1 in d1)))
               else "paired-d4" if i in paired else "isolated")
        matches.append({
            "i": i,
            "rune": RUNES[c[i]],
            "class": cls,
            "section": sec_of[i],
            "word": word_of[i],
            "within_word": within,
            "pos_in_word": i - word_start[word_of[i]],
        })

    doublets = [i for i in range(n - 1) if c[i] == c[i + 1]]

    catalog = {
        "corpus": {
            "source": "data/page0-58.txt sections 0-9 (runes only)",
            "length": n,
            "note": "index = 0-based offset into the clean rune stream; "
                    "a match at i means C[i] == C[i+5]; under the "
                    "back-reference branch the plaintext satisfies "
                    "P[i+5] = P[i] at marked events; under the nulls "
                    "branch C[i+5] is skipped on decryption",
        },
        "counts": {
            "matches": len(matches),
            "d1_events": len(d1),
            "d4_events": len(d4),
            "within_word_matches": sum(1 for x in matches
                                       if x["within_word"]),
            "doublets": len(doublets),
        },
        "d1_events": d1,
        "d4_events": d4,
        "doublets": doublets,
        "matches": matches,
    }
    with open(OUT, "w") as f:
        json.dump(catalog, f, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}")
    print(json.dumps(catalog["counts"], indent=2))


if __name__ == "__main__":
    main()
