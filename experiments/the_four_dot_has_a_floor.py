# ABOUTME: Shows the body never places two four-dots one block apart, a hard floor the
# ABOUTME: author's own sentence marks do not have.
"""Something keeps the four-dots apart -- but not as strongly as this file claims.

**CORRECTED. The P = 0.00015 headline below is withdrawn.** Its "author's own
convention" arm applies his raw one-block sentence rate to a corpus whose gaps are 2.7
times longer than his sentences. Scale-matched by thinning -- the relationship the gap
law itself fits -- the price is P = 0.055, not 0.00015. See
`the_floor_needs_a_scale_matched_reference.py`. The counts measured here are correct;
the conclusions drawn from them in the last three sections are not.

`is_the_four_dot_placed_per_page.py` closes the production explanation for the four-dot's
spacing -- its count per page sits exactly on a constant per-rune rate, so the page is
invisible to it. What remains unexplained is the short-gap deficit: nine gaps of three
blocks or less where a memoryless process predicts 18.4.

The deficit has a sharp shape. **There is not one gap of a single block in the whole
body**, where a constant-rate process predicts 6.8.

## The comparison that matters

The author marks sentences, verified against an English transcription outside the
transcription itself (`what_the_authors_mark_means.py`). His sentences have no floor: six
of his ninety-four are a single block. If the body's four-dot marked sentences on the same
convention, about nine of its 138 gaps would be one block long.

## A filter artifact to avoid

`register_spans` drops sentences shorter than three words, twice -- before and after
joining. English sentence lengths taken from it therefore cannot be 1 or 2 by
construction, and comparing the body's small gaps against that reference shows English
"never" having short sentences, which is the filter speaking. This file builds its English
reference without the filter.

## Result: a floor at two blocks, which nothing else in the book has

| | n | mean | min | counts at 1..5 |
|---|---|---|---|---|
| the body, four-dot gaps | 138 | 20.4 | **2** | **0**, 4, 6, 7, 8 |
| the author, sentences | 94 | 7.6 | **1** | **6**, 13, 7, 8, 6 |
| English, sentences, unfiltered | 13,439 | 18.4 | **1** | **444**, 495, 377, 437, 492 |

| gaps of a single block predicted by | rate | expected | P(0 or fewer) |
|---|---|---|---|
| a memoryless process | 0.0491 | 6.8 | 0.00115 |
| **the author's own convention** | 0.0638 | **8.8** | **0.00015** |
| English sentences | 0.0330 | 4.6 | 0.01047 |

**Observed in the body: zero.**

The author's sentences have no floor -- six of his ninety-four are a single block -- and
neither does English, where 3.3% of sentences are one word after joining. The body's
four-dots have a floor and it is absolute.

## What it adds

The short-gap deficit is not a soft tendency to spread the marks out. It is a **rule**: no
two four-dots are ever one block apart. Whatever places them enforces a minimum unit of
two blocks.

That is the first positive structural statement about the four-dot in this directory.
Everything else established about it is a negation -- not a sentence mark, not a clause
mark, not a paragraph mark, not a cipher boundary, not a page artifact.

## What it does not show

Why the floor is at two rather than anywhere else, and whether the remaining spread above
the floor carries any structure. The four gaps of exactly two blocks are consistent with a
floor at two and nothing tighter.

    python the_four_dot_has_a_floor.py
"""

from __future__ import annotations

import random
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, blocks  # noqa: E402
from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

JOIN_RATE = 0.40
SMALL = 6
REGISTER_COUNT = 3


def body_gaps():
    """Blocks between consecutive four-dots."""
    out, count = [], 0
    for _, glyph, _ in blocks(BODY):
        count += 1
        if glyph == "④":
            out.append(count)
            count = 0
    return out[1:]


def english_sentences(rng):
    """Sentence lengths in blocks, with NO minimum-length filter."""
    out = []
    for number in REGISTERS[:REGISTER_COUNT]:
        path = fetch(number)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        trim = len(text) // 10
        for sentence in re.split(r"[.!?]+", text[trim : len(text) - trim]):
            words = [
                len([c for c in to_runeglish(w.upper()) if c in IDX_ENG])
                for w in re.findall(r"[A-Za-z']+", sentence)
            ]
            words = [n for n in words if n]
            if words:
                out.append(len(join(words, JOIN_RATE, rng, forward=True)))
    return out


def show(label, lengths):
    counts = Counter(lengths)
    small = {k: counts.get(k, 0) for k in range(1, SMALL)}
    print(
        f"{label:<34}{len(lengths):>7}{np.mean(lengths):>9.1f}{min(lengths):>6}"
        f"   {small}"
    )
    return counts


def main() -> None:
    rng = random.Random(3301)
    gaps = body_gaps()
    author = [len(s) for s in author_spans()]
    english = english_sentences(rng)

    print(f"{'':<34}{'n':>7}{'mean':>9}{'min':>6}   counts at 1..5")
    body_counts = show("the body, four-dot gaps", gaps)
    author_counts = show("the author, sentences", author)
    show("English, sentences, unfiltered", english)

    print("\nGaps of a single block.\n")
    print(f"{'predicted by':<36}{'rate':>9}{'expected':>10}{'P(0 or fewer)':>16}")
    for label, rate in (
        ("a memoryless process", 1 / np.mean(gaps)),
        ("the author's own convention", author_counts.get(1, 0) / len(author)),
        ("English sentences", Counter(english).get(1, 0) / len(english)),
    ):
        expected = rate * len(gaps)
        print(
            f"{label:<36}{rate:>9.4f}{expected:>10.1f}"
            f"{stats.poisson.cdf(body_counts.get(1, 0), expected):>16.5f}"
        )
    print(f"\n  observed in the body: {body_counts.get(1, 0)}")
    print(
        "\n  The author's sentences have no floor -- six of ninety-four are one block."
        "\n  WITHDRAWN: his rate cannot be applied here, his sentences being 2.7x"
        "\n  shorter than these gaps. Scale-matched, P = 0.055. See"
        "\n  the_floor_needs_a_scale_matched_reference.py."
    )


if __name__ == "__main__":
    main()
