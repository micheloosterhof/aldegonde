# ABOUTME: Uses the seam doublet suppression, not a length statistic, to show any block
# ABOUTME: rearrangement happened before enciphering rather than after.
"""The observed block order is the enciphered order. Any transposition came first.

`lengths_cannot_separate_the_readings.py` showed why every block-length statistic has
failed to choose between the surviving readings: transposition destroys word **order** and
keeps the **multiset**, and sentence boundaries carry information about the first and not
the second. Separating anything further needs a channel that is not a length statistic.

The doublet suppression is one. The preventer acts on **adjacent runes, including across a
block boundary** -- `previous` carries over the seam -- so the seam rate records which
blocks were actually neighbours when the cipher ran.

    within-block adjacent doublets    63 / 10,060  = 0.0063
    seam doublets                     23 /  2,895  = 0.0079
    an unrelated pair (sum f^2)                      0.0346

The seam is suppressed by a factor of four. If the blocks had been rearranged **after**
enciphering, the observed seams would be unrelated pairs at 0.0346:

| rearrangement applied after enciphering | seam doublets | z |
|---|---|---|
| the whole body shuffled | 100.1 +- 9.2 | **-8.35** |
| shuffled within each span | 96.6 +- 9.5 | **-7.71** |
| reversed within each span | 89.0 +- 9.4 | **-7.00** |
| **the body as written** | **23** | |

Every post-encipherment rearrangement is excluded at seven sigma or more, including the
within-span shuffle that `the-words-are-transposed-within-sentences.md` proposes. A
within-span shuffle leaves the 172 span-boundary seams intact and randomises the other
2,723, which is why it lands near the whole-body figure rather than anywhere near 23.

## What it settles

**If the words are transposed, the transposition was applied to the plaintext before the
cipher ran.** It is a preparation step, not a rearrangement of finished ciphertext.

That puts it in the same class as the short-unit joining, which is also a property of the
text handed to the cipher (`short-units-are-written-joined.md`), and both change at the
page-15 production break. It also means a solver cannot undo the transposition by moving
ciphertext blocks around: the blocks would have to be deciphered first, and the cipher
state runs through them in the order they appear.

## What it does not settle

Which of the two readings is right. Both "the spans are transposed sentences" and "the
marks are not sentence marks" are consistent with an unrearranged ciphertext -- the second
proposes no rearrangement at all. This closes a family of mechanisms, not a reading.

    python the_transposition_precedes_the_cipher.py
"""

from __future__ import annotations

import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_cipher_restart import ANNOTATION, RUNE, STANDALONE  # noqa: E402
from sentences_do_not_end_long import BODY  # noqa: E402

from aldegonde import c3301  # noqa: E402

INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
MARKS = "④⑬③⑩"
DRAWS = 400


def blocks_and_spans():
    """Blocks as rune indices, and the spans the four-dot marks cut them into."""
    text = "\n".join(
        line
        for line in BODY.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    blocks, spans, current, span = [], [], [], []
    for ch in text:
        if RUNE.match(ch):
            current.append(INDEX[ch])
        elif ch == "\n" or ch in STANDALONE:
            continue
        elif ch in c3301.WORD_BOUNDARY:
            if current:
                blocks.append(current)
                span.append(current)
                current = []
            if ch in MARKS and span:
                spans.append(span)
                span = []
    if current:
        blocks.append(current)
        span.append(current)
    if span:
        spans.append(span)
    return blocks, spans


def doublets(sequence):
    """(within-block, within-block pairs, seam, seam pairs) for a block sequence."""
    win = wtot = seam = stot = 0
    previous = None
    for word in sequence:
        for j, rune in enumerate(word):
            if j:
                wtot += 1
                win += rune == previous
            elif previous is not None:
                stot += 1
                seam += rune == previous
            previous = rune
    return win, wtot, seam, stot


def main() -> None:
    blocks, spans = blocks_and_spans()
    win, wtot, seam, stot = doublets(blocks)
    counts = Counter(r for b in blocks for r in b)
    total = sum(counts.values())
    chance = sum((c / total) ** 2 for c in counts.values())

    print(f"{len(blocks)} blocks in {len(spans)} spans.\n")
    print(f"  within-block adjacent doublets  {win:>4} / {wtot:<7} = {win / wtot:.4f}")
    print(
        f"  seam doublets                   {seam:>4} / {stot:<7} = {seam / stot:.4f}"
    )
    print(f"  an unrelated pair (sum f^2)                    = {chance:.4f}")
    print("\nThe preventer acts across the seam, so the seam rate records which blocks")
    print("were neighbours when the cipher ran.\n")

    rng = random.Random(3301)

    def whole():
        order = list(range(len(blocks)))
        rng.shuffle(order)
        return [blocks[i] for i in order]

    def within_span():
        out = []
        for span in spans:
            t = list(span)
            rng.shuffle(t)
            out += t
        return out

    def reverse_span():
        return [w for span in spans for w in span[::-1]]

    print(
        f"{'rearrangement applied AFTER enciphering':<42}{'seam doublets':>16}{'z':>8}"
    )
    for label, builder, draws in (
        ("the whole body shuffled", whole, DRAWS),
        ("shuffled within each span", within_span, DRAWS),
        ("reversed within each span", reverse_span, 1),
    ):
        values = np.array([doublets(builder())[2] for _ in range(draws)], float)
        mean = float(values.mean())
        sd = float(values.std(ddof=1)) if draws > 1 else math.sqrt(mean)
        print(f"{label:<42}{f'{mean:.1f} +- {sd:.1f}':>16}{(seam - mean) / sd:>+8.2f}")
    print(f"{'the body as written':<42}{seam:>16}")

    print(
        "\nEvery post-encipherment rearrangement is excluded at seven sigma or more,"
        "\nincluding the within-span shuffle the transposition reading proposes. So if the"
        "\nwords are transposed, it was done to the plaintext BEFORE the cipher ran -- a"
        "\npreparation step, like the short-unit joining, not a rearrangement of finished"
        "\nciphertext."
        "\n\nIt follows that a solver cannot undo the transposition by moving ciphertext"
        "\nblocks: they would have to be deciphered first, and the cipher state runs"
        "\nthrough them in the order they appear."
    )


if __name__ == "__main__":
    main()
