# ABOUTME: Measures what the key-free d5 equality pattern can actually identify, using the
# ABOUTME: author's own vocabulary and the solved pages as a positive control.
"""Before using the d5 crib, find out what it can identify.

Within a block `c[j] == c[j+5]` exactly when `p[j] == p[j+5]`, with no key. Every block of
six runes or more therefore carries free plaintext facts: which distance-5 pairs are equal
and which are not. `rubrication_crib_d5.py` uses this to prune candidates for the
rubricated title words, and records its own weakness -- it prunes against a
frequency-ranked **English** dictionary, and notes that an empty list means the true word
is outside that dictionary rather than that the span is invalid.

The author's vocabulary is on disk. `data/register_vocab.txt` holds 332 runeglish words
built from the solved pages, the 2012-13 and 2014 Cicada material and the lore. That is
the list a crib should be pruning against.

Two things have never been measured:

**Coverage.** What share of the author's own words of length >= 6 are in that vocabulary
at all? A crib list that cannot contain the answer is not a lead.

**Power.** Given length and the d5 pattern, how many candidates survive, and how often is
the true word among them? The solved pages answer both, because their plaintext is known.

## The preventer breaks some of the facts

A firing advances the clock by one step, so a distance-5 relation survives only if no
firing falls between the two runes: `(1 - q)^5` with q ~ 0.03, about 86%. **Roughly one
d5 fact in seven is wrong**, so an exact-match prune will sometimes discard the true word.
Everything below is reported at zero and at one allowed mismatch.

## Result: the channel is three to five bits short of naming a word

A d5 pair is equal **0.066** of the time in the author's own vocabulary, so each pair
carries 0.353 bits. A word of length L has L-5 pairs.

| length | pairs | bits supplied | bits needed | short by |
|---|---|---|---|---|
| 6 | 1 | 0.35 | 5.46 | **5.11** |
| 7 | 2 | 0.71 | 5.39 | **4.69** |
| 8 | 3 | 1.06 | 4.39 | **3.33** |
| 9 | 4 | 1.41 | 4.09 | 2.68 |
| 10 | 5 | 1.76 | 2.32 | 0.56 |
| 11 | 6 | 2.12 | 2.32 | 0.21 |
| 12 | 7 | 2.47 | 1.00 | -1.47 |

"Bits needed" is log2 of how many vocabulary words share that length. The surplus at 12
runes and beyond is not identification power: the register vocabulary holds only **two**
words of length 12 and one of length 14, so there is almost nothing to distinguish. Against
a realistic vocabulary the shortfall grows at every length.

Measured directly, pruning the author's own plaintext words:

| allowed mismatches | true word kept | median candidates |
|---|---|---|
| 0 | 66/66 | **36** |
| 1 | 66/66 | **42** |

**Thirty-six candidates out of a 332-word vocabulary.** The pattern is almost always
all-unequal -- 44 words of length 6 share just 2 distinct patterns, 42 words of length 7
share 2 -- so it prunes nothing.

The 100% coverage figure is **circular** and should not be quoted as validation: the
vocabulary was built from the solved pages, so it contains those words by construction.
Coverage on unseen LP text is unmeasured and will be lower.

## Conclusion

**The d5 channel cannot generate cribs.** It supplies 0.35 to 2.5 bits per word where 4 to
5 are needed, and the deficit is structural: d5 equalities are rare, so nearly every word
carries the same uninformative pattern. This puts a number on what
`crib-budget-for-g.md` states qualitatively -- the titles verify and cannot generate.

`rubrication_crib_d5.py` should be read with that in mind. Its candidate lists are not
narrow, and swapping its English dictionary for the author's own vocabulary does not make
them narrow.

One incidental, which is not a hit: the 12-rune title word on page 27 prunes to a single
name, CONSCIAUSNESS. That is 2 candidates reduced to 1, worth one bit, and the length
class is nearly empty. It is a coincidence of vocabulary size, not evidence.

    python how_strong_is_the_d5_crib.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
VOCAB = ROOT / "data" / "register_vocab.txt"
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TITLES = ROOT / "experiments" / "rubricated_titles.json"
PLAIN_PAGES = (3, 8, 9, 10, 11, 14)
MIN_LEN = 6


def vocabulary() -> dict[int, list[tuple[tuple[int, ...], str]]]:
    out: dict[int, list[tuple[tuple[int, ...], str]]] = defaultdict(list)
    for line in VOCAB.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        runes, english = line.split("\t")[:2]
        idx = tuple(IDX[r] for r in runes if r in IDX)
        if idx:
            out[len(idx)].append((idx, english))
    return out


def pattern(word) -> tuple[bool, ...]:
    """The distance-5 equality pattern, which the cipher passes through unchanged."""
    return tuple(word[j] == word[j + 5] for j in range(len(word) - 5))


def survivors(word, vocab, slack=0):
    """Vocabulary entries of the same length whose d5 pattern matches within `slack`."""
    want = pattern(word)
    out = []
    for runes, english in vocab.get(len(word), []):
        got = pattern(runes)
        if sum(a != b for a, b in zip(want, got)) <= slack:
            out.append(english)
    return out


def words_from(pages) -> list[list[int]]:
    chunks = MASTER.read_text().split("%")
    out, cur = [], []
    for n in pages:
        for ch in chunks[n]:
            if RUNE.match(ch):
                cur.append(IDX[ch])
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY and cur:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
            cur = []
    return out


def main() -> None:
    vocab = vocabulary()
    total = sum(len(v) for v in vocab.values())
    long_enough = {k: v for k, v in vocab.items() if k >= MIN_LEN}
    print(
        f"{total} words in the register vocabulary, "
        f"{sum(len(v) for v in long_enough.values())} of them {MIN_LEN} runes or more.\n"
    )
    print(f"{'length':>8}{'in the vocabulary':>20}{'distinct d5 patterns':>24}")
    for k in sorted(long_enough):
        pats = {pattern(r) for r, _ in long_enough[k]}
        print(f"{k:>8}{len(long_enough[k]):>20}{len(pats):>24}")

    plain = [w for w in words_from(PLAIN_PAGES) if len(w) >= MIN_LEN]
    known = {tuple(r) for v in vocab.values() for r, _ in v}
    covered = [w for w in plain if tuple(w) in known]
    print(
        f"\nPositive control: {len(plain)} words of {MIN_LEN}+ runes on the author's"
        f"\nplaintext pages, {len(covered)} of them in the vocabulary"
        f" ({len(covered) / len(plain):.0%} coverage).\n"
    )
    print(f"{'allowed mismatches':<22}{'true word kept':>16}{'median candidates':>20}")
    for slack in (0, 1):
        kept, sizes = 0, []
        for w in covered:
            names = survivors(w, vocab, slack)
            sizes.append(len(names))
            same = [e for r, e in vocab[len(w)] if tuple(r) == tuple(w)]
            kept += any(e in names for e in same)
        print(
            f"{slack:<22}{f'{kept}/{len(covered)}':>16}{np.median(sizes):>20.0f}"
        )

    print("\nThe bit budget: what the pattern supplies against what naming a word needs.\n")
    rate = float(
        np.mean(
            [
                p_
                for v in vocab.values()
                for r, _ in v
                for p_ in pattern(r)
            ]
        )
    )
    h = -(rate * math.log2(rate) + (1 - rate) * math.log2(1 - rate)) if 0 < rate < 1 else 0
    print(f"  a d5 pair is equal {rate:.3f} of the time, worth {h:.3f} bits\n")
    print(f"{'length':>8}{'pairs':>8}{'bits supplied':>16}{'bits needed':>14}{'short by':>11}")
    for k in sorted(long_enough):
        pairs = k - 5
        supplied = pairs * h
        needed = math.log2(len(long_enough[k]))
        print(
            f"{k:>8}{pairs:>8}{supplied:>16.2f}{needed:>14.2f}"
            f"{needed - supplied:>11.2f}"
        )

    print("\nThe rubricated title words of six runes or more.\n")
    chunks = MASTER.read_text().split("%")
    titles = json.loads(TITLES.read_text())
    print(f"{'page':>5}{'runes':>7}{'d5 pattern':>14}{'candidates in the vocabulary':>34}")
    for t in titles:
        a, b = t["word_range"]
        words, cur = [], []
        for ch in chunks[t["chunk"]]:
            if RUNE.match(ch):
                cur.append(IDX[ch])
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY and cur:
                words.append(cur)
                cur = []
        for w in words[a : b + 1]:
            if len(w) < MIN_LEN:
                continue
            names = survivors(w, vocab, 1)
            shown = ", ".join(names[:4]) if names else "none"
            pat = "".join("=" if x else "." for x in pattern(w))
            print(f"{t['page']:>5}{len(w):>7}{pat:>14}{shown:>34}")


if __name__ == "__main__":
    main()
