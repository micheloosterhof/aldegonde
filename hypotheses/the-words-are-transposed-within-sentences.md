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

## Which permutation: five rules excluded

`which_transposition.py` left every candidate fitting, which was a power problem with two
causes — the longest-block position collapses a span to one number, and the ±4 profile was
computed only on spans of nine blocks or more. Two sharper statistics separate them
(`which_permutation_survives.py`).

**The exact edge cells**, over all 133 spans of three blocks or more, keep the contrast
that binning destroys:

| rule | FIRST z | LAST z | χ²(2) |
|---|---|---|---|
| **identity** | +2.08 | **−4.31** | **22.9** |
| **reverse** | **−3.06** | +1.11 | **10.6** |
| rotate 2 | +0.53 | −0.47 | 0.5 |
| scramble | +0.28 | −1.27 | 1.7 |

**The full ±4 profile** reaches rotations up to k = 3, since a rotation by k parks the
long word at offset −(1+k):

| rule | χ²(8) | P |
|---|---|---|
| identity | 33.3 | **0.0001** |
| reverse | 17.6 | **0.024** |
| rotate 1 | 25.5 | **0.0013** |
| rotate 2 | 29.6 | **0.0002** |
| rotate 3 | 18.1 | **0.021** |
| rotate 6 | 7.9 | 0.447 |
| scramble | 7.6 | 0.472 |

**A deep scan** to offset −12 finds no parked long word anywhere: the largest gap in the
window is +0.37 ± 0.30 at offset −12, which is 2.05σ below the +1.19 a rotation parking
it there would give.

**So: identity, reversal and rotations by 1–3 are excluded, and rotations out to 11 are
disfavoured.** What survives is a permutation that **varies from sentence to sentence**,
or a single rule that moves the final word more than twelve blocks from the end — which
for a median span of 13 blocks is most of them.

That bears on inverting it: a fixed rule would be recoverable from the statistics alone; a
varying one needs a key.

## What it leaves untouched

Everything else that is measured, because the **words themselves are intact**: the
joined-word length fit (P = 0.83), the d5 lag-5 echo (z = −0.47 against ten registers),
the span lengths (CV 0.972 against 0.848 ± 0.120), and the two ordinary independent
blocks either side of a mark.

## What it does not establish, and cannot

Flatness is evidence, not proof: "the marks are not sentence marks" predicts a flat
profile too. The two differ in what a span *is* — a permuted sentence, or a run of words
cut at points unrelated to the syntax — and **no block-length statistic can tell them
apart** (`lengths_cannot_separate_the_readings.py`).

Two attempts, both with no power:

- **Span length against internal word length.** If a span is a sentence, any link between
  its length and the words inside it survives transposition, since the multiset is
  untouched. English has no such link to preserve: r runs −0.130 to +0.154 across ten
  registers, mean 0.034 ± 0.087. The body reads 0.075 (z = +0.33).
- **The longest block in a span.** A sentence holds exactly one sentence-final word; an
  equally long arbitrary run holds a random number. Measured: sentences 9.72, the same
  stream cut at random 9.78 — a difference of **−0.058 ± 0.081**, and matched by span
  length it does not move.

The reason is structural. A sentence and an equally long run of the same text are both
samples of one word-length distribution. Sentence boundaries carry information about
**order** — which word is last — and almost none about the **multiset**. Transposition
destroys exactly the order and keeps exactly the multiset, so it removes the only thing
that distinguished the readings.

That explains why every length statistic tried has failed to separate them: the edge
profile, the longest-block position, the span dispersion, the span shape. Separating them
needs a channel that is not a length statistic — and d5, the only key-free window onto the
plaintext, reads *inside* a block where transposition changes nothing, while cross-block
structure is hidden by the base changing at every block edge.

`separators-are-not-word-boundaries.md` tested 17 route rules and 46,232 keyed columnar
transpositions; none survived cross-validation. **A per-sentence scramble is in neither
family.** With about twenty blocks to a sentence there are 20! orderings, so detecting
the transposition and inverting it are different problems.

## The transposition precedes the cipher

The first result here that is not a length statistic
(`the_transposition_precedes_the_cipher.py`). The preventer acts on adjacent runes
**including across a block boundary** — `previous` carries over the seam — so the seam
doublet rate records which blocks were neighbours when the cipher ran:

| | rate |
|---|---|
| within-block adjacent doublets | 63 / 10,060 = 0.0063 |
| seam doublets | 23 / 2,895 = **0.0079** |
| an unrelated pair (Σf²) | 0.0346 |

The seam is suppressed fourfold. Had the blocks been rearranged **after** enciphering,
the observed seams would be unrelated pairs:

| rearrangement applied after enciphering | seam doublets | z |
|---|---|---|
| the whole body shuffled | 100.1 ± 9.2 | **−8.35** |
| shuffled within each span | 96.6 ± 9.5 | **−7.71** |
| reversed within each span | 89.0 ± 9.4 | **−7.00** |
| **the body as written** | **23** | |

**So if the words are transposed, it was done to the plaintext before the cipher ran** —
a preparation step, like the short-unit joining, and not a rearrangement of finished
ciphertext. Both are properties of the text handed to the cipher, and both change at the
page-15 break.

It follows that a solver cannot undo the transposition by moving ciphertext blocks: they
must be deciphered first, because the cipher state runs through them in the order they
appear.

This closes a family of mechanisms, not a reading — "the marks are not sentence marks"
proposes no rearrangement at all and is untouched.

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
