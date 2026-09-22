# ABOUTME: Searches the body's block-length stream for the author's own known phrases,
# ABOUTME: allowing for the short-unit joining, as a key-free crib attempt.
"""The author's phrases are known. Their length patterns survive encipherment.

The front matter is fully solved, so the author's own words are on hand in plaintext. The
body's cipher is length-preserving, so a phrase he reused would appear in the body's
block-length stream as the same run of lengths -- no key needed to look.

`do_length_patterns_repeat.py` shows the body repeats nothing **internally**: not one
eight-block pattern where the author has nineteen, at forty-seven sigma of power. That
does not rule out the body quoting the front matter, which is a different question and
the one a crib programme actually needs.

## The obstacle, and why it has to be modelled

`short-units-are-written-joined.md` fits the body merging units of two runes or less into
a neighbour at q = 0.40. So an eight-word phrase does not appear as eight blocks -- it
appears as one of many joined variants. Searching raw patterns is guaranteed to fail and
would produce a meaningless null result.

Every mergeable subset is therefore enumerated per phrase, capped to keep the count
finite, and the null carries exactly the same enumeration so the inflated number of
patterns is priced rather than ignored.

## The null

The body's own lengths, shuffled. That keeps the marginal exactly and destroys the order,
so it measures how often these patterns land by coincidence in a stream of this shape.

## Result: nothing, and the sensitivity is the point

| phrase length | patterns searched | hits in the body | in shuffled body | z | genuine quotes needed for 3 sigma |
|---|---|---|---|---|---|
| 6 | 2,172 | 1,034 | 1,006.0 +- 33.1 | +0.85 | 99 |
| 7 | 2,829 | 266 | 264.3 +- 17.1 | +0.10 | 51 |
| 8 | 3,607 | 66 | 59.8 +- 9.9 | +0.63 | 30 |
| 9 | 4,521 | 13 | 12.9 +- 4.3 | +0.03 | 13 |
| 10 | 5,613 | 2 | 2.6 +- 2.0 | -0.31 | **6** |

**No excess at any length.** The z values run -0.31 to +0.85.

The last column is what stops this being an empty null. At n = 6 the body would have to
quote the front matter **ninety-nine times** before the test noticed, because the chance
floor is a thousand hits. Only at n = 10 does it become sharp: **six genuine ten-word
quotes would show at three sigma, and two were found against 2.6 expected.**

So the honest statement is narrow: **the body does not quote the front matter heavily.**
Light quotation -- a handful of phrases -- is invisible to this channel and stays open.

The joining is what costs the sensitivity. Enumerating merge variants turns 698 author
words into thousands of patterns per length, and the null carries that inflation
faithfully rather than hiding it. Without modelling the joining the test would return a
guaranteed and meaningless null instead.

    python do_the_authors_phrases_appear.py
"""

from __future__ import annotations

import random
import re
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from the_gap_depends_on_span_length import body_spans  # noqa: E402

MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
FRONT_MATTER = range(15)
RUNE = re.compile(r"[ᚠ-᛿]")
LENGTHS = (6, 7, 8, 9, 10)
MAX_MERGES = 3
DRAWS = 120


def author_words() -> list[int]:
    """The author's word lengths, read from the transcription's own separators.

    The solved triples store plaintext as an unspaced string, so word boundaries are not
    in them. They do not need to be: the cipher is length-preserving, so the separators
    in the ciphertext give the plaintext's word lengths directly. All fifteen front-matter
    chunks are usable, solved or not.
    """
    out: list[int] = []
    chunks = MASTER.read_text().split("%")
    for n in FRONT_MATTER:
        length = 0
        for ch in chunks[n]:
            if RUNE.match(ch):
                length += 1
            elif ch in "/\n":
                continue
            elif length:
                out.append(length)
                length = 0
        if length:
            out.append(length)
    return out


def variants(pattern, cap=MAX_MERGES):
    """Every way of merging up to `cap` units of two runes or less into the next."""
    spots = [i for i, x in enumerate(pattern[:-1]) if x <= 2]
    seen = {tuple(pattern)}
    for k in range(1, min(cap, len(spots)) + 1):
        for chosen in combinations(spots, k):
            out, skip = [], set()
            merged = list(pattern)
            for i in sorted(chosen, reverse=True):
                merged[i + 1] += merged[i]
                skip.add(i)
            out = [v for i, v in enumerate(merged) if i not in skip]
            if len(out) >= 3:
                seen.add(tuple(out))
    return seen


def phrase_set(words, n):
    """All joined variants of every length-n phrase the author wrote."""
    out = set()
    for i in range(len(words) - n + 1):
        out |= variants(words[i : i + n])
    return out


def hits(stream, patterns):
    by_len: dict[int, set] = {}
    for p in patterns:
        by_len.setdefault(len(p), set()).add(p)
    found = 0
    for k, group in by_len.items():
        for i in range(len(stream) - k + 1):
            if tuple(stream[i : i + k]) in group:
                found += 1
    return found


def main() -> None:
    words = author_words()
    body = [x for s in body_spans() for x in s]
    rng = random.Random(3301)
    print(f"{len(words):,} author plaintext words; {len(body):,} body blocks.\n")
    print(
        f"{'phrase length':>14}{'patterns':>11}{'hits':>8}"
        f"{'in shuffled body':>20}{'z':>8}{'quotes for 3 sigma':>20}"
    )
    for n in LENGTHS:
        patterns = phrase_set(words, n)
        obs = hits(body, patterns)
        null = []
        shuffled = list(body)
        for _ in range(DRAWS):
            rng.shuffle(shuffled)
            null.append(hits(shuffled, patterns))
        null = np.array(null, float)
        sd = null.std(ddof=1)
        z = (obs - null.mean()) / sd if sd > 0 else float("nan")
        print(
            f"{n:>14}{len(patterns):>11,}{obs:>8,}"
            f"{f'{null.mean():,.1f} +- {sd:.1f}':>20}{z:>+8.2f}{3 * sd:>20.0f}"
        )

    print(
        "\nThe null shuffles the body's own lengths, so it prices both the coincidence"
        "\nrate and the pattern inflation the joining variants cause."
    )


if __name__ == "__main__":
    main()
