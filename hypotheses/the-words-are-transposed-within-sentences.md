---
type: hypothesis
---
# The Words Are Transposed Within Each Sentence

## The claim

Michel's proposal, September 2026. The four-dot **is** a full stop and the spans between
marks **are** real sentences. What is missing is the word order inside them.

This is the first reading that accounts for both long-standing anomalies with one
mechanism.

## The two anomalies it joins

1. **`separators-are-not-word-boundaries.md`**: "the body's block lengths have the
   marginal of running text and none of running text's order. That is the anomaly in its
   sharpest form, and it is what any reading has to produce."
2. **`sentences-do-not-end-long.md`**: the block before a mark does not lengthen —
   −0.29 ± 0.20 against a ten-register English +1.19 ± 0.28.

A within-sentence transposition keeps the multiset of word lengths and destroys their
sequence. That is (1) exactly, and it flattens the sentence edges, which is (2).

## The test

Scramble the words inside each English sentence, keep the sentence boundaries, and
compare the body's whole offset profile (`are_the_words_transposed.py`):

| | χ² on 8 df | P |
|---|---|---|
| body vs English **as written** | 33.3 | **0.0001** |
| body vs English **mirrored** (the reversal reading) | 17.6 | 0.024 |
| body vs English **scrambled** | **8.7** | **0.37** |

Every offset is within 1.7σ of scrambled English. The −1 cell moves from −4.42 against
English as written to −1.05 against English scrambled.

## An independent check that is not just flatness

A flat profile is consistent with several readings, so this second test carries the
weight: **where the longest block sits inside a span.** English puts it late; scrambling
puts it anywhere.

| | spans | mean position | KS against uniform |
|---|---|---|---|
| ten registers pooled | 28,551 | 0.547 | **P = 2×10⁻²⁶⁴** |
| the LP author | 60 | 0.579 | P = 0.01 |
| **the LP body** | 122 | **0.482** | **P = 0.65** |

The author behaves like English. The body is indistinguishable from uniform and 2.30σ
from the register spread.

## What it leaves untouched

Everything else that is measured, because the **words themselves are intact**: the
joined-word length fit (P = 0.83), the d5 lag-5 echo (z = −0.47 against ten registers),
the span lengths (CV 0.972 against 0.848 ± 0.120), and the two ordinary independent
blocks either side of a mark.

## What it does not establish

Flatness is evidence, not proof: "the marks are not sentence marks" predicts a flat
profile too. What separates them is that under transposition the spans are *genuine
sentences*, and their lengths do match English sentence lengths — consistent, not
decisive.

`separators-are-not-word-boundaries.md` tested 17 route rules and 46,232 keyed columnar
transpositions; none survived cross-validation. **A per-sentence scramble is in neither
family.** With about twenty blocks to a sentence there are 20! orderings, so detecting
the transposition and inverting it are different problems.

## How to falsify

- **A residual order.** If the permutation is a rule rather than a scramble — a reversal
  within the sentence, a rotation, an interleave — the block-length sequence inside spans
  should carry a trace. Reversal within the whole text is already rejected (χ² 17.6,
  z = −2.70 at offset +1); reversal *within each sentence* is not yet tested and is the
  obvious next candidate.
- **The author's pages.** His spans are not scrambled (longest block at 0.579, P = 0.01
  against uniform), so whatever does this starts at the page-15 break with the joining,
  the mark rate and the line measure (`one-production-break-at-page-fifteen.md`).
- **d5 across a block boundary.** Transposition moves whole words, so cross-block
  plaintext structure should be destroyed while within-block structure survives. The base
  changes every block, so this is not currently measurable.

## Status

**Status**: open, and the best-fitting reading of the sentence-edge result. Two
independent statistics support it; neither is decisive alone.
`experiments/are_the_words_transposed.py`.

## Related

- `sentences-do-not-end-long.md` — the anomaly.
- `separators-are-not-word-boundaries.md` — the older anomaly this unifies with, and the
  transposition families already excluded.
