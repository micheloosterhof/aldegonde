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

## An independent check — weaker than first reported

**Corrected.** The first version of this file tested the longest-block position against a
*uniform* null and reported the body at P = 0.65, reading that as support for scrambling.
Uniform is the wrong null: the position is i/(n−1), so pooling across span lengths is
lumpy even under a random permutation — applied to English, a scramble gives D = 0.051
against uniform (P = 4×10⁻⁶⁵), not 0. And 122 spans can only resolve D above 0.123, so
that test was never going to reject anything.

Compared against what each rule actually produces (`which_transposition.py`):

| rule | longest-block position | | sentence-final gap |
|---|---|---|---|
| | KS D | P | z vs the body |
| **identity** | **0.128** | **0.034** | **−4.42** |
| reverse | 0.077 | 0.445 | +1.36 |
| rotate 1 | 0.105 | 0.130 | +1.36 |
| rotate 3 | 0.083 | 0.356 | −0.82 |
| scramble | 0.080 | 0.393 | −0.99 |

**Both statistics reject the identity and nothing else.** The second statistic does
support "not the original order" — at P = 0.034, not P = 0.65 — but it does **not** pick
scrambling over reversal or rotation.

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

- **A residual order.** If the permutation is a rule rather than a scramble — a reversal,
  a rotation, an interleave — the block-length sequence inside spans should carry a trace.
  Reversal **within each sentence** gives the same mirrored profile as reversal of the
  whole text, so it is covered: χ² 17.6 on 8 df, P = 0.024, driven by the offset +1 cell
  where reversal predicts +1.19 and the body reads +0.22. But on the single final-block
  cell reversal *fits* (z = +1.36), so the cells disagree and P = 0.024 is a lean rather
  than an exclusion. **Rotation and scrambling are not separated at all.**
- **The author's pages.** His spans are not scrambled (longest block at 0.579, P = 0.01
  against uniform), so whatever does this starts at the page-15 break with the joining,
  the mark rate and the line measure (`one-production-break-at-page-fifteen.md`).
- **d5 across a block boundary.** Transposition moves whole words, so cross-block
  plaintext structure should be destroyed while within-block structure survives. The base
  changes every block, so this is not currently measurable.

## Status

**Status**: open. What is established is that the word order inside a span is **not** the
order English would give — the identity is rejected by the offset profile (χ² 33.3 on
8 df, P = 0.0001) and by the longest-block position (P = 0.034). **Which** permutation is
undetermined: reversal, rotation and scrambling all fit, and reversal is disfavoured only
by the full profile at P = 0.024.
`experiments/are_the_words_transposed.py`.

## Related

- `sentences-do-not-end-long.md` — the anomaly.
- `separators-are-not-word-boundaries.md` — the older anomaly this unifies with, and the
  transposition families already excluded.
