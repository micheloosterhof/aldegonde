---
type: observation
---
# Observation: The Four-Dot Counts Words, Not Letters — and the Author's Lengthening Is Mostly Arithmetic

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

## What it costs

The author's marks lengthen by **+1.42** where his own size bias alone predicts **+1.18**.
A verified sentence mark and a letter countdown make the same prediction on his pages, and
the observed value sits 0.7σ from the countdown.

This is a degeneracy, not a claim that he counted letters —
`what_the_authors_mark_means.py` verifies his mark against an English transcription
outside this repository, 26 of 32 at sentence ends. What changes is what his +1.39 may be
quoted for. **It is not evidence that sentence marks lengthen more than an arbitrary
length-proportional mark**, because they do not. Any future use of the author's
lengthening as a sentence signature has to subtract var/mean first.

The body comparison survives because the body shows neither effect.

## How to falsify

- Find a mark class whose preceding blocks average near 5.6 runes; that class is
  rune-clocked and the four-dot is not alone on this axis.
- Show the body's block-length variance is inflated by a parsing error, which would move
  the size-biased prediction; `body_parse.py` verifies at 2,927 blocks / mean 4.43 against
  the canonical 2,928 / 4.42.
- Show a scribe counting letters would mark *before* the block the count falls in rather
  than after it. That model predicts the corpus mean, is indistinguishable from a block
  clock here, and would leave the question open.
