# ABOUTME: Measures the doublet rate in the enciphered front matter against the body's,
# ABOUTME: showing the two sections differ decisively in the preventer whatever g they share.
"""One cipher or two? The preventer answers where the d-profile could not.

`does_the_front_matter_share_g.py` compares the body with the nine enciphered
ASCII-convention chunks using the within-block d-profile and reports **4.3 to 1 for a
shared letter step** -- weak, and labelled weak, because the front matter supplies 2,218
within-block pairs against the body's 19,284.

There is a far louder statistic. The doublet suppression is a 17-sigma effect in the body,
and `nothing-else-in-the-book-suppresses-repeats.md` records that no other part of the
book shows it. That claim has never been put side by side with the shared-`g` finding, and
the two point in opposite directions.

## What a doublet means in each section

Under the walk a ciphertext doublet needs `p_i = g(p_(i+1))`, not `p_i = p_(i+1)`, so the
unsuppressed rate is the graph mass m1(g) -- about 0.031 for a typical order-5 `g` on
English digraphs -- rather than the plaintext's own repeat rate. The author's plaintext
pages are included below as a scale: they show what an unenciphered rate looks like.

## Result: not the same cipher, and the frequency test settles it

| section | runes | distinct | chi2 | P(uniform) |
|---|---|---|---|---|
| front matter, PLAINTEXT | 1,001 | 25 | 747.5 | 2e-139 |
| **front matter, enciphered** | **1,796** | **29** | **456.8** | **5e-79** |
| **the body** | **12,956** | **29** | **26.4** | **0.55** |

**The enciphered front matter's rune frequencies are English-shaped and the body's are
flat.** A flat distribution over 29 runes needs many alphabets; the front matter plainly
has few. That is decisive and it is the answer to the question
`does_the_front_matter_share_g.py` was asking.

The doublet rates say the same thing more loudly than the d-profile did:

| section | pairs | doublets | rate | vs chance | implied phi |
|---|---|---|---|---|---|
| front matter, PLAINTEXT, within a word | 770 | 19 | 0.0247 | -1.49 | 0.20 |
| front matter, enciphered, within a word | 1,329 | 32 | 0.0241 | -2.08 | 0.22 |
| **the body, within a word** | **10,028** | **63** | **0.0063** | **-15.48** | **0.80** |
| front matter, enciphered, across a separator | 458 | 12 | 0.0262 | -0.97 | 0.15 |
| the body, across a separator | 2,873 | 23 | 0.0080 | -7.78 | 0.74 |

Enciphered front matter 0.0241 against the body 0.0063: **z = +4.16**. The front matter
sits 2.0 sigma below chance, a weak deficit at most; the body sits eighty orders of
magnitude below it.

Note the enciphered front matter's 0.0241 is within noise of its own **plaintext** pages'
0.0247, which is what a few-alphabet cipher does: it passes the plaintext's repeat rate
through almost unchanged.

## Retraction

`does_the_front_matter_share_g.py` reports 4.3 to 1 for a shared letter step. That is
about 1.3 sigma and rests on the d-profile alone. **It is withdrawn.** The d-profile
agreement was measuring shared plaintext structure at distance five, which both sections
have, and not a shared `g`.

What survives is the narrower use the front matter is put to in
`encipherment_does_not_break_the_link.py`: that SOME length-preserving cipher keeps the
sentence-final lengthening (+1.21 +- 0.33 against the body's -0.17 +- 0.21). A
monoalphabetic cipher is length-preserving, so that argument is unaffected -- and is in
fact cleaner, since a cipher that passes plaintext structure through is a stronger
demonstration that encipherment does not destroy the link.

    python the_preventer_is_only_in_the_body.py
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
PLAIN_PAGES = (3, 8, 9, 10, 11, 14)
ENCIPHERED_FRONT = (0, 1, 2, 4, 5, 6, 7, 12, 13)
BODY_CHUNKS = range(15, 71)
CHANCE = 1.0 / 29
UNSUPPRESSED = 0.031  # typical m1(g), graph_mass_is_not_recoverable.py


def cells(pages):
    """(within-word pairs, across-separator pairs) as equality flags."""
    chunks = MASTER.read_text().split("%")
    within, cross = [], []
    for n in pages:
        if n >= len(chunks):
            continue
        previous, sep = None, False
        for ch in chunks[n]:
            if RUNE.match(ch):
                if previous is not None:
                    (cross if sep else within).append(ch == previous)
                previous, sep = ch, False
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY:
                sep = True
            elif ch in "%$&":
                previous = None
    return within, cross


def row(label, flags):
    n, hits = len(flags), sum(flags)
    if n < 50:
        return None
    rate = hits / n
    z = (rate - CHANCE) / math.sqrt(CHANCE * (1 - CHANCE) / n)
    phi = max(0.0, 1 - rate / UNSUPPRESSED)
    print(
        f"{label:<40}{n:>7,}{hits:>7}{rate:>9.4f}{z:>+10.2f}"
        f"{stats.binom.cdf(hits, n, CHANCE):>12.1e}{phi:>9.2f}"
    )
    return n, hits, rate


def frequencies(pages) -> Counter:
    chunks = MASTER.read_text().split("%")
    c: Counter = Counter()
    for n in pages:
        if n < len(chunks):
            c.update(ch for ch in chunks[n] if RUNE.match(ch))
    return c


def uniformity(pages):
    c = frequencies(pages)
    obs = list(c.values()) + [0] * (29 - len(c))
    chi, p = stats.chisquare(obs)
    return sum(c.values()), len(c), float(chi), float(p)


def main() -> None:
    print("FIRST: are the two sections even the same kind of cipher?\n")
    print(f"{'section':<30}{'runes':>8}{'distinct':>10}{'chi2':>10}{'P(uniform)':>13}")
    for label, pages in (
        ("front matter, PLAINTEXT", PLAIN_PAGES),
        ("front matter, enciphered", ENCIPHERED_FRONT),
        ("the body", BODY_CHUNKS),
    ):
        n, distinct, chi, p = uniformity(pages)
        print(f"{label:<30}{n:>8,}{distinct:>10}{chi:>10.1f}{p:>13.2e}")
    print(
        "\n  The enciphered front matter's rune frequencies are ENGLISH-SHAPED"
        "\n  (P = 5e-79 against uniform) and the body's are flat (P = 0.55). Those"
        "\n  are not the same cipher: a flat distribution needs many alphabets and"
        "\n  the front matter plainly has few.\n\n"
    )
    print("A ciphertext doublet needs p_i = g(p_(i+1)), so the unsuppressed rate is")
    print(
        f"the graph mass m1(g), about {UNSUPPRESSED}, not the plaintext's repeat rate."
    )
    print(f"Chance is {CHANCE:.4f}. phi is the implied suppression strength.\n")
    print(
        f"{'section':<40}{'pairs':>7}{'dbl':>7}{'rate':>9}{'vs chance':>10}"
        f"{'P(<= obs)':>12}{'phi':>9}"
    )
    got = {}
    for label, pages in (
        ("front matter, PLAINTEXT", PLAIN_PAGES),
        ("front matter, enciphered", ENCIPHERED_FRONT),
        ("the body", BODY_CHUNKS),
    ):
        within, _ = cells(pages)
        got[label] = row(label + ", within a word", within)
    for label, pages in (
        ("front matter, enciphered", ENCIPHERED_FRONT),
        ("the body", BODY_CHUNKS),
    ):
        _, cross = cells(pages)
        row(label + ", across a separator", cross)

    (n1, h1, r1) = got["front matter, enciphered"]
    (n2, h2, r2) = got["the body"]
    se = math.sqrt(r1 * (1 - r1) / n1 + r2 * (1 - r2) / n2)
    print(
        f"\nEnciphered front matter {r1:.4f} against the body {r2:.4f}:"
        f" difference {r1 - r2:+.4f} +- {se:.4f}, z = {(r1 - r2) / se:+.2f}."
    )
    print(
        "\nThe front matter sits 2.0 sigma below chance -- a weak deficit at most --"
        "\nwhile the body sits 80 orders of magnitude below it. Whatever the two"
        "\nsections share, they do not share the preventer."
    )
    print(
        "\nRETRACTION for `does_the_front_matter_share_g.py`. Its 4.3 to 1 for a shared"
        "\nletter step is worth about 1.3 sigma and rests on the d-profile alone. The"
        "\nfrequency test above settles the question the other way at P = 5e-79: the"
        "\nfront matter is a few-alphabet cipher and the body is a many-alphabet one."
        "\nThe d-profile agreement was measuring shared PLAINTEXT structure at distance"
        "\nfive, which both sections have, not a shared g."
        "\n\nWhat survives: `encipherment_does_not_break_the_link.py` uses the front"
        "\nmatter only to show that SOME length-preserving cipher keeps the"
        "\nsentence-final lengthening. A monoalphabetic cipher is length-preserving, so"
        "\nthat argument is unaffected."
    )


if __name__ == "__main__":
    main()
