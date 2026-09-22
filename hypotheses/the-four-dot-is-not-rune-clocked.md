---
type: observation
---
# Observation: The Four-Dot Counts Words, Not Letters

## Question

Every statement about the four-dot's spacing has assumed a clock without testing which
one. `is_the_four_dot_placed_per_page.py` fits its count per page to a constant rate **per
rune**; `the_four_dot_has_a_floor.py` counts its gaps **in blocks**. The two models are
separable from the corpus alone, with no reference text.

`experiments/what_the_four_dot_counts.py`

## The prediction

A **rune clock** drops a mark when a letter countdown expires. A scribe counting letters
cannot mark mid-word, so the mark goes at the end of the block the count falls inside —
and that block is drawn in proportion to its length. Its mean therefore exceeds the corpus
mean by var/mean:

| | blocks | mean | var | size-biased mean |
|---|---|---|---|---|
| the body | 2,927 | 4.426 | 5.347 | **5.634** |
| the author | 719 | 4.008 | 4.744 | **5.19** |

A **block clock** drops a mark at a block boundary at a constant rate per boundary. It
samples blocks uniformly, so the block before a mark has the corpus mean.

The two differ by 1.21 runes in the body, which 139 four-dots resolve to 0.19. This is the
same cell as the sentence-final lengthening statistic, read against a model that has
nothing to do with language.

## Result

| corpus | observed | rune clock | block clock |
|---|---|---|---|
| the body's four-dot | 4.165 ± 0.187 | 5.631, **z = −4.9** | 4.428, z = −1.0 |
| the author's marks | 5.426 ± 0.239 | 5.182, z = +0.7 | 4.012, **z = +4.5** |

**The four-dot is not rune-clocked.** It is consistent with a block clock, sitting 1.0σ
below it — the short-block lean already recorded as the −0.24 gap.

## What it removes

The body's missing lengthening now excludes two models with one number. It was read only
as "the four-dot is not a sentence mark". It also says the mark is not placed by any rule
that samples blocks in proportion to their length: letter counts, line measures, column
widths, or anything else that counts glyphs rather than words. That was the last reading
in which the four-dot is a production quantity measured off the page, and
`is_the_four_dot_placed_per_page.py` had left it open by fitting a per-rune rate and
finding it adequate — a per-page test cannot separate runes from blocks, because the two
are nearly proportional per page.

## What it does not cost

The author's marks lengthen by **+1.42** where a length-proportional mark on his pages
would give **+1.18**. A verified sentence mark and a letter countdown therefore make
almost the same prediction there, and his cell sits 0.7σ from the countdown.

That is a statement about **discrimination**, and an earlier version of this file
overstated it into a statement about **magnitude**. It said his +1.39 "has to subtract
var/mean first" before being quoted as a sentence signature. That is wrong. Size bias is
what a *length-proportional* placement would produce; a sentence mark is placed by syntax
and samples blocks uniformly, so under the sentence model — which
`what_the_authors_mark_means.py` verifies from outside this repository, 26 of 32 at
sentence ends — the whole +1.42 is the linguistic effect, measured against his own uniform
interior at z = +4.5.

What the degeneracy does mean, exactly:

- the author's lengthening **cannot tell** a sentence mark from a rune clock;
- it remains the full measure of the sentence effect under the model already verified for
  him;
- the body-against-author comparison at −4.65σ is unaffected, because both sides are
  measured against their own corpus's uniform interior.

## How to falsify

- Find a mark class whose preceding blocks average near 5.6 runes; that class is
  rune-clocked and the four-dot is not alone on this axis.
- Show the body's block-length variance is inflated by a parsing error, which would move
  the size-biased prediction; `body_parse.py` verifies at 2,927 blocks / mean 4.43 against
  the canonical 2,928 / 4.42.
- Show a scribe counting letters would mark *before* the block the count falls in rather
  than after it. That model predicts the corpus mean, is indistinguishable from a block
  clock here, and would leave the question open.

## The detector was calibrated after the fact, and it works

`experiments/does_the_size_bias_detector_work.py`

A null result from an untested detector proves nothing. The same statistic was run on
boundaries whose clock is physical rather than editorial — a line holds a fixed width of
runes, so the block a line break falls inside is drawn in proportion to its length.

| class | n | mean | uniform | z | size-biased | z |
|---|---|---|---|---|---|---|
| blocks a line break falls inside | 419 | 5.909 | 4.428 | **+9.2** | 5.635 | +1.9 |
| blocks a page break falls inside | 34 | 6.676 | 4.428 | **+3.7** | 5.631 | +1.6 |
| four-dot | 139 | 4.165 | 4.428 | −1.0 | 5.630 | **−4.9** |
| thirteen-dot | 26 | 4.462 | 4.420 | +0.1 | 5.640 | −1.9 |
| three-dot | 4 | 5.000 | 4.445 | +0.2 | 5.629 | −0.3 |
| one-dot separator | 2,722 | 4.442 | 4.427 | +0.3 | 5.634 | −24.9 |

The detector separates the two clocks at **9.2σ on 419 blocks**, so the four-dot's
negative is a measurement and not a missing sensitivity. Both physical classes read at or
slightly above the size-biased prediction, which is expected — a scribe avoids breaking a
short word, so the real selection is steeper than proportional.

**No mark class in the book is rune-clocked.** The one-dot row is definitional: it is the
block delimiter, and it fixes the uniform column. The thirteen-dot leans with the four-dot
on a quarter of the sample and is unresolved alone.

