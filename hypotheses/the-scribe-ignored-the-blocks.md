---
type: observation
---
# The Scribe Broke Lines at Word Boundaries Only Where He Could Read the Text

## The claim

Line breaks in the body fall at block boundaries no more often than chance: **0.236
against 0.224**, z = +0.76 on 593 breaks. Three lines in four end inside a block.

On the pages the scribe could **read** — the plaintext front matter — the same
measurement reads **0.558 against 0.231, z = +5.60**. So the test detects
boundary-respecting layout when it is there, and the body's null is a real absence.

## Why the obvious version of this test is invalid

`line_layout_and_the_hole.py` records the trap: its null holds the line lengths fixed and
shuffles the blocks, but a scribe chooses where to break a line to fit what is on it, so
line length and content are not independent. That null breaks the coupling as well as the
hypothesis and manufactures an effect. The separators-per-line test built on it reads
z ≈ −8 for the body and **z ≈ −21 for the book's own plaintext**, which is how it was
caught.

The fix is to stop shuffling and **generate** the layout, letting the model produce the
line lengths instead of holding them fixed.

## The models

| model | aligned | runes per line |
|---|---|---|
| fill to measure, break wherever | 0.225 ± 0.017 | 21.82 ± 2.57 |
| seek a boundary within 1 rune | 0.436 ± 0.016 | 21.60 ± 2.60 |
| seek a boundary within 2 | 0.625 ± 0.020 | 21.15 ± 2.70 |
| seek a boundary within 3 | 0.748 ± 0.017 | 20.53 ± 2.82 |
| **the body** | **0.236** | **21.81 ± 2.61** |

The plain scribe reproduces the body exactly. Every boundary-seeking tolerance
overshoots — even one rune of tolerance nearly doubles the alignment rate.

The target jitter is fitted so the plain model matches the observed line spread, so the
spread is not an independent check; the **alignment rate is**, and it is what separates
the models.

## The gradient

| text | breaks | at a boundary | chance | z |
|---|---|---|---|---|
| front matter, **plaintext** | 52 | **0.558** | 0.231 | **+5.60** |
| front matter, enciphered | 92 | 0.337 | 0.262 | +1.65 |
| the body, enciphered | 432 | 0.252 | 0.227 | +1.28 |

Readable text: words kept whole at more than twice chance. Enciphered text: nothing,
in the front matter and in the body alike. That is the expected thing — ciphertext has no
word shapes to protect — and it is a clean internal control, same book and same hand.

## What it settles and what it does not

**Settles**: the block boundaries were not salient to whoever ruled these lines. He filled
to about 21.8 runes and broke where he landed. Any reading in which the scribe treated
blocks as units to keep intact is out.

**Does not settle** whether blocks are words. A scribe copying ciphertext cannot see word
shapes whatever the blocks are, so this measurement cannot distinguish the readings in
`blocks-are-still-words.md`. It rules out one *scribal* story, not a cipher one.

## How to falsify

- **A page whose layout does respect blocks.** The measurement is per-page; a section
  with a high alignment rate would mean a different hand or a different exemplar, and
  would bear on `short-units-are-written-joined.md`'s reading 1.
- **The enciphered front matter is the ambiguous cell** at z = +1.65 on 92 breaks. If it
  is real, the body and the front matter differ in layout as well as in joining. More
  enciphered front matter does not exist, so this one cannot be resolved.

## Status

**Status**: confirmed, with a positive control in the same book.
`experiments/did_the_scribe_break_at_blocks.py`.

## Related

- `line_layout_and_the_hole.py` — the invalid shuffle null this avoids.
- `short-units-are-written-joined.md` — the different-hand reading this bears on.
- `blocks-are-still-words.md` — which this does **not** settle.
