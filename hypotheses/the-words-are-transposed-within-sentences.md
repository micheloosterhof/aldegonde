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

**Superseded, October 2026.** The structural argument below holds for statistics computed inside one span. Adjacency is not one of those, and the adjacency test (closing sections) separates the readings: adjacent block lengths inside a span are independent, z −0.10 against the body's own within-span shuffle, where intact order with the body's joining applied reads +5.1 on the author's pages and +5.8 to +17.1 on prose at the body's size (`experiments/length_adjacency_self_null.py`). The section is kept as the record of why the earlier statistics could not.

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

**Conditional, noted October 2026 (Michel).** This ordering assumes the doublet preventer
is part of the cipher. If the preventer is a separate final pass run after the shuffle, the
seam rate is suppressed under either order and says nothing about whether the shuffle came
before or after the cipher. What then constrains the pipeline is the preventer itself: a
final pass must be invertible by the intended reader, every deterministic local fix is
excluded (`explicit-doublet-avoidance.md`), and what survives is a re-draw that is
statistically the in-cipher dodge except for the clock drift, which the d5 shortfall
favours at about 2σ (`d5-bounds-the-clock-perturbation.md`). So "cipher, then shuffle,
then remover" is live, with a weak lean against it; and if it holds, the chain of bases
runs in the hidden order, not the visible one, which any key search using the visible
block order must allow for.

The ordering also decides which previous-word key is closed: the previous-ciphertext-word closure reads the visible predecessor and holds only under shuffle-then-cipher; the previous-plaintext-word closure reads English bigram recurrence and holds only under cipher-then-shuffle (`word-level-autokey.md`, `the-base-is-not-a-ciphertext-autokey.md`, October 2026).

This closes a family of mechanisms, not a reading — "the marks are not sentence marks"
proposes no rearrangement at all and is untouched here. (It was excluded in October 2026 by
the adjacency test, closing sections.)

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

**Status**: supported on the order question, open on the unit. The word order inside a
span is **not** English's, established three ways: the identity is rejected by the offset
profile (χ² 33.3 on 8 df, P = 0.0001), the pre-mark block is a random block of its span
(z −0.86 against the body's own shuffle), and — October 2026, the decisive one — adjacent
block lengths inside a span are independent (z −0.10 against the body's own within-span
shuffle) where intact order gives +5.1 on the author's joined pages at a fifth of the
body's size and +5.8 to +17.1 on joined prose at the body's size. **Which** permutation is
undetermined (reversal and rotations 1–3 excluded; nothing beats a plain shuffle), and
the unit is bounded above by the span (the rubricated titles are contiguous runs of red
blocks, so no word left its span) and below only weakly (order as written excluded at
−2.6σ on the author and −6.6σ on prose; two-word units at −2.2σ on prose; three-word
units and larger not separated from a whole-span shuffle by the pre-mark block,
`experiments/permutation_unit_size.py`); the quote-edge alignment (P = 1.5e-7) and the
sentence-shaped gap law are what make the span, rather than a clause, the unit. `experiments/are_the_words_transposed.py`,
`experiments/is_there_any_order_inside_a_span.py`,
`experiments/length_adjacency_self_null.py`.

## Related

- `sentences-do-not-end-long.md` — the anomaly.
- `separators-are-not-word-boundaries.md` — the older anomaly this unifies with, and the
  transposition families already excluded.

## The order channel forks the readings but cannot reach them

**Superseded, October 2026.** It reaches them with the right statistic; see "Adjacency under the body's own shuffle" below. Kept as the record of the Pearson attempt and of the joining-rate side-finding, which stands.

`experiments/order_survives_in_the_lengths.py`

`lengths_cannot_separate_the_readings.py` concluded that no block-length statistic can
separate this reading from "the marks are not sentence marks". Its argument was about
what a span *contains*: a sentence and an equally long run of the same text hold the same
multiset of word lengths, and transposition keeps the multiset. Every statistic it tried
was computed inside one span.

The **lag-1 serial correlation of the length stream** escapes that argument. It is a
property of the order, not the multiset, and the two readings predict opposite things
about it — transposition destroys within-span order, arbitrary marks leave it untouched.
So the blanket claim was drawn too wide.

Measured, the fork exists and is too small:

| lag | order intact | transposed | the body |
|---|---|---|---|
| 1 | −0.031 ± 0.029 | −0.005 ± 0.042 | −0.009 ± 0.019 |
| 2 | +0.028 ± 0.031 | +0.008 ± 0.047 | +0.023 ± 0.020 |
| 3 | +0.000 ± 0.040 | +0.002 ± 0.051 | −0.018 ± 0.020 |

**+0.64σ from order intact, −0.08σ from transposed.** The body leans to this reading and
the lean means nothing. The arms are 0.026 apart at lag 1; the body's own sampling error
is 0.019 and the reference adds 0.029 because the solved pages are only 719 blocks.
Three-sigma separation needs about 13,000 pairs, **4.7× the corpus**.

**The reference is the whole difficulty, and it produced a false positive twice.**

- **Unmatched short-word population.** Lag-1 here is driven by the fraction of blocks two
  runes long: English alternates short and long words, joining removes the short ones, and
  both quantities slide together. The body carries 15.5%, raw Gutenberg prose 25.5%.
  Compared directly the body reads **+3.2σ** from order intact — a difference in joining
  read as a difference in order.
- **Unmatched register.** Matching the fraction is not enough. At the same 15.9%
  two-rune share the ten registers read −0.082 and the author's joined pages read −0.028:
  **the two references disagree by three times the effect.** The curves are parallel, so
  the slope is shared and the level is a register property. Only the author's own solved
  pages match on both.

So the lengths still cannot separate the two readings, but not for the reason previously
given: the surviving statistic is throttled by the joining nuisance the corpus has already
spent, not excluded by a structural argument.

**Side-finding, independent of all of this.** The joining rate that brings the author's
two-rune share onto the body's is **q = 0.40**, the rate `short-units-are-written-joined.md`
fitted from the length histogram. Two unrelated statistics, the same rate.

## The titles: a non-length channel, and it leans the wrong way for English order (October 2026)

`experiments/title_word_order.py`

The rubricated titles are the one place where plaintext order is partly known without a
key. The author's own titles put an article or preposition first — A WARNING, A KOAN,
THE LOSS OF DIVINITY, AN INSTRUCTION, AN END: in runes A is one and THE, OF, AN are two —
so a one- or two-rune block in a title span is almost certainly such a word, and where it
sits is an order statistic that no length *distribution* argument can neutralise. Under a
per-span shuffle it lands in a uniformly random slot.

The seventeen spans' shapes (from the master transcription):

| page | shape | short word first? |
|---|---|---|
| 0 | (8, 5) | — crib, matched by this shape, not counted |
| 3 | (2, 11, 3) | yes |
| 3 | (3) | — |
| 6 | (4, 1, 4, 2) | **no** |
| 7 | (2, 4, 3, 2, 3) | yes |
| 8 | (4, 8) | — |
| 15 | (4, 5, 4, 2, 5) | **no** |
| 23 | (2, 6, 3, 5) | yes |
| 27 | (3, 12, 4) | — |
| 33 | (2, 8) | yes |
| 33 | (3, 5) | — |
| 39, 40, 54 | (3), (3, 5), (1) | — |
| 53 | (5, 4, 4, 11, 2, 3, 2, 6, 5, 5, 2, 2) | **no** |
| 56, 57 | (2, 3) AN END, (7) PARABLE | yes, — : outside the body |

Seven body spans carry the test; the short word opens **4 of 7**. A shuffle expects 2.52
(exact Poisson-binomial over the spans' own sizes), P(≥ 4) = 0.21. The author's titles
read 5 of 5. Likelihood of 4 of 7 against the shuffle's 0.153:

| in-order rate r | P(4 of 7) | ratio to shuffle |
|---|---|---|
| 0.95 (the author's own titles) | 0.004 | 0.02 |
| 0.85 | 0.062 | 0.40 |
| 0.70 | 0.227 | 1.5 |
| 0.50 | 0.273 | 1.8 |

**Read plainly: the body's titles do not behave like the author's titles in order** —
three of seven have their short word interior (pages 6, 15 and the twelve-word span on
53), where his five have none. Against a shuffle they are an ordinary draw (P = 0.21).
The result leans toward "not in the author's order" at about 40:1 against his own rate,
and at nothing against a looser English-title rate where interior articles are common.

What it does not settle. Seven spans are seven; a one-rune block interior to page 6's
(4, 1, 4, 2) may be an A inside an ordinary English phrase; page 53's twelve words may be
an epigraph rather than a heading; and a short word moved inward by a shuffle can be
joined to its predecessor and vanish, which would make the shuffle arm read *higher* than
2.52 and the body less unlike it. The two spans outside the body (AN END, PARABLE) are in
order, as their decryptions already showed — the body is bracketed by in-order text on
both sides.

So the titles give the first non-length reading on the question and it does not rescue
English order; it is consistent with a per-span permutation and with "the marks are not
sentence marks" alike, and the fork stood until the adjacency test below. Reading the titles' plaintext — which needs
the key — would settle it in one page.

## Adjacency under the body's own shuffle: the order is not intact (October 2026)

`experiments/length_adjacency_self_null.py`

The section above left the order channel "forked but unreachable": a Pearson lag-1 of
−0.031 for intact order against −0.005 for a shuffle, with the body between them and the
reference's own error larger than the gap. Two things were wrong with that reading, and
fixing them decides the question.

**The statistic.** Pearson lag-1 sees only linear dependence. The dependence English
word lengths carry is not linear: after a two-rune block the next is rarely two runes,
after a long block the next is often short, and the middle classes are nearly flat. A
transition table over five length classes (1–2, 3, 4, 5–6, 7+; 25 cells) sees this where
Pearson does not. On the same 636 blocks of the author's joined pages, Pearson reads
z = +0.05 and the table reads z = +5.14.

**The null.** The comparison is each corpus against its **own within-span shuffle**, the
device of `is_there_any_order_inside_a_span.py`: every span's multiset of lengths is kept
exactly and only adjacency is destroyed, so no reference enters the body's reading. The
chi-square of the observed table against the shuffle's cell means and sds is scored on
the null distribution of the same statistic from a second set of shuffles. The reference
is used only to calibrate what intact order would read, and it is calibrated on both
available references: the author's solved pages and five Gutenberg registers, each with
the body's joining applied (units of two runes or fewer joined forward at q = 0.40) and
the prose cut into windows of the body's own block count.

| corpus | blocks | pairs | χ² | shuffle null | z | P |
|---|---|---|---|---|---|---|
| the author, raw | 713 | 625 | 77.2 | 25.6 ± 8.1 | **+6.38** | 0.000 |
| the author, joined q = 0.40 | 636 | 552 | 67.5 | 25.3 ± 8.2 | **+5.14** | 0.000 |
| joined prose, 28 windows at the body's size | ≈2,900 | ≈2,750 | 80–164 | ≈25 ± 9 | **+9.5 ± 3.0** (min +5.8) | 0.000 |
| the author, joined, then shuffled (control) | 636 | 552 | 31.2 | 25.3 ± 8.2 | +0.72 | 0.21 |
| **the body, four-dot spans** | 2,896 | 2,759 | 25.2 | 26.0 ± 8.7 | **−0.10** | 0.52 |
| the body, cut at sections only | 2,928 | 2,918 | 24.8 | 24.8 ± 9.0 | 0.00 | 0.44 |
| the body, cut at every cluster mark | 2,925 | 2,760 | 24.9 | 24.8 ± 8.7 | +0.01 | 0.46 |

The body's table sits on its own shuffle to the decimal. Its largest cells are
4 → 5–6 at +1.9σ and 4 → 1–2 at −1.6σ, ordinary for 25 cells.

**Robustness.** The result does not depend on the class edges or on the cut, and it
cannot be the joining:

| classes | author joined | one prose window | the body |
|---|---|---|---|
| 1–2 / 3 / 4 / 5–6 / 7+ | +4.79 | +13.43 | +0.06 |
| 1 / 2 / 3 / 4–5 / 6+ | +3.91 | +12.73 | −0.19 |
| 1–2 / 3–4 / 5–6 / 7+ | +4.21 | +9.84 | −0.59 |
| 1–3 / 4–5 / 6–8 / 9+ | +1.05 | +15.74 | +2.70 |
| **both blocks 3+**, 3 / 4 / 5–6 / 7+ | +3.02 | +10.35 | +0.19 |

The last row counts only pairs whose blocks are both three runes or longer. The joining
model touches units of two runes or fewer, so no pair in that row was created or moved by
joining, and intact order still reads +3.0 on the author and +10.4 on prose there. The
body reads +0.19. Whatever removed the body's adjacency structure is not the joining.

The one cell to be honest about: the 1–3 / 4–5 / 6–8 / 9+ cut reads +2.70 on the body
(+2.1 to +2.3 on three further seeds, P 0.02–0.035), one of five cuts times three
span definitions. Its driving cells are 4–5 → 1–3 at −2.7 and 6–8 → 6–8 at −2.7, which
is a *deficit* of long-then-short, the opposite of English's alternation; the body's
Pearson lag-1 is −0.009 (z −0.77 against its shuffle). A 2σ cell in a scan of fifteen,
pointing the wrong way, is not order.

**What this settles.** Under "the marks are not sentence marks and the order is intact",
the body's block lengths are English word lengths in English order with the joining
applied, and that reads between +5 and +17 here. The body reads zero under three cuts and
five classings. **The words are not in their English order.** That reading is out. Two
earlier verdicts are superseded by this one and the reason is the same for both:
`short-units-are-written-joined.md`'s "joining explains the serial order at 1.2σ" and the
section above's "4.7× the corpus needed" were both Pearson lag-1 against an errored
reference, and the table against the self-null has about a hundred times the power.
The September result in `separators-are-not-word-boundaries.md` (excess G² per
transition 0.0039 ± 0.0025 against 0.0397 for the author) was right, and it is now
reference-free.

**What it does not settle.** The unit of permutation. A shuffle within sections or within
pages destroys adjacency just as a shuffle within spans does, and all three cuts of the
body read zero, so this test says the unit is *at least* a span and nothing more. The
things that make the four-dot span the unit are elsewhere: the gap law has English
sentence-length shape, the quote edges land on marks at P = 1.5e-7, and the marks arrive
with the joining and the line measure at page 15. Nor does it say which permutation; it
says only that no adjacency survives, which a plain shuffle gives and which a rotation or
reversal would not (both keep adjacency and are excluded on their own already).

**Consequence for the crib program.** A span is a bag of words. A phrase crib (a title, a
quotation) constrains a span's multiset of block lengths, not its sequence, and the crib
verifier must place the crib's words into blocks of matching length in any order. The
transposition is a key: a different permutation per sentence, with 20! orderings for a
twenty-word sentence, so recovering it is a separate problem after the cipher is off.

**Order of operations with the joining (October 2026).** Whether the short units were
joined before or after the permutation is not readable from the lengths: all three models
fit the marginal at P 0.55–0.70 and differ by two percent in the share of short blocks,
under reference error of ±21–34 χ² units. `short-units-are-written-joined.md`,
`experiments/joining_before_or_after_the_shuffle.py`.

**The permutation is not the doublet avoider (October 2026).** Doublets per four-dot
span are binomial (dispersion 121 on 145 df against 145 ± 30; 93/35/11/7 spans with
0/1/2/3+ against 91/36/12/7 expected; rate flat across span length), where choosing each
span's order for few doublets would clear the short spans and leave the long ones at
chance. `doublet-suppression-requires-design.md`, `experiments/doublets_per_span.py`.

## The unit of the permutation: bounded above by the red ink, weakly from below (October 2026)

`experiments/permutation_unit_size.py`

**From above.** The rubricated titles (`rubricated_titles.json`, read off the page scans
independently of the glyph stream) are each a contiguous run of blocks whose rune total
matches the title, and the thirteen-dot sits on their edges
(`do_the_marks_bound_the_titles.py`). A permutation within sections or pages would have
scattered a title's words through the section and the red runes with them. They are
contiguous, and the title spans are themselves scrambled (short word interior in 3 of 7).
So no word left its span: the unit is at most the span.

**From below.** If the words were permuted within consecutive units of k words, the
sentence's long final word stays in the last unit and the pre-mark block keeps part of
the sentence-final lift. Planted on the author's joined sentences and on joined prose
length-matched to the body's spans (6+ blocks; units counted from the end), the last
block's excess over its span's mean:

| unit k | author planted | z (body) | prose planted | z (body) |
|---|---|---|---|---|
| 1 (as written) | +0.43 | **−2.59** | +1.25 | **−6.56** |
| 2 | +0.04 ± 0.22 | −0.51 | +0.51 ± 0.18 | **−2.24** |
| 3 | −0.03 ± 0.24 | −0.28 | +0.28 ± 0.21 | −1.34 |
| 4 | +0.10 ± 0.29 | −0.61 | +0.14 ± 0.21 | −0.87 |
| 5–15 | ≈ +0.02 ± 0.29 | −0.3 to −0.4 | +0.16 to −0.01 | −0.9 to −0.3 |
| whole span | +0.01 ± 0.33 | −0.32 | +0.01 ± 0.20 | −0.41 |

The body reads −0.11 ± 0.21. Order as written is excluded again by this statistic; pairs
are disfavoured at 2.2σ against prose and not at all against the author (whose joined
6+-block sentences number 50 and lift only +0.42); three-word units and larger are not
separated from a whole-span shuffle. The lower bound is weak because even a two-word unit
puts the final word last only half the time, and the author's reference is small.

So: the unit is no larger than a span and no smaller than a pair, with everything from a
clause to the whole sentence open on the lengths. The span is the unit by parsimony and by
the non-length channels — the quote edges on the marks and the sentence-shaped gap law —
not by this bound.

## Which permutation: no fixed geometry among sixteen, and no fixed row count (October 2026)

The lag-1 table excludes a permutation that keeps neighbours together (reversal,
rotation). A transposition with a fixed geometry escapes it: a columnar transposition of a
span's words with R rows puts English neighbours R positions apart in the output, so the
same table at lag R carries the intact-order signal. `which_permutation_lag_scan.py` runs
two scans against the within-span shuffle, which keeps every span's multiset:

- the **lag scan**, the table over pairs (i, i + lag) for lags 1 to 12, family P for the
  largest z over lags 2 to 12 from the same shuffle draws;
- the **inversion scan**, each of sixteen geometries (columnar with 2 to 6 rows, columnar
  with 2 to 8 columns, rail fence with 2 to 4 rails, reversal) undone on every span and
  the lag-1 table scored, family P over the sixteen.

Calibration on a joined prose window of 2,916 blocks, the body's size:

| planted | lag scan, largest z (lag) | inversion scan, best geometry |
|---|---|---|
| intact | +13.1 at lag 1 | reversal +12.5 (its inverse is itself; the transpose table scores too) |
| columnar, 3 rows | +10.8 at lag 3 | columnar 3 rows +12.1 |
| columnar, 5 rows | +7.3 at lag 5 | columnar 5 rows +13.5 |
| columnar, 4 columns | +2.2, family P 0.24 (a fixed width smears the lag) | columnar 4 columns +11.8 |
| rail fence, 3 rails | +1.3, family P 0.70 | rail fence 3 rails +13.1 |
| shuffled | +0.7, family P 0.96 | +0.7, family P 0.98 |

On the author's joined pages (634 blocks) neither scan has power: a planted 3-row
columnar reads +1.3 in the lag scan and +2.6 (family P 0.05) in the inversion scan, and
this joining draw's intact lag-1 reads +3.0 where the earlier draw read +5.1.

**The body**, 137 four-dot spans of two or more blocks, 2,896 blocks:

| scan | largest z | family P |
|---|---|---|
| lag scan, lags 2 to 12 | +2.14 (lag 7) | 0.29 |
| inversion scan, 16 geometries | +1.88 (columnar, 4 columns) | 0.49 |

**Negative.** No geometry of the sixteen restores the order, and no fixed row count puts
the order at a fixed lag. Where a planted geometry reads +7 to +13, the body reads under
+2.2 at the chance rate of a scan. What survives is a permutation without a fixed
geometry: a random shuffle, a keyed transposition whose geometry changes per span, or a
geometry outside the sixteen. For a solver that is the same thing: the permutation is
not invertible from the lengths, and any key search has to treat the order within a span
as unknown.

## The catalogue of rule-based sentence shuffles: none of 5,482 fits (October 2026)

Michel's framing: a shuffle a reader can undo must be a rule that works at every sentence
length, and there are not many. `catalogue_of_sentence_shuffles.py` enumerates them and
tests each by undoing it on every four-dot span and scoring the lag-1 length-class table
against the body's own within-span shuffle, with one family P for the whole catalogue
from the same shuffle draws scored under every rule.

The catalogue, each rule followed by its inverse, 5,482 in all:

- columnar with a fixed width 2 to 10, the columns read in every order up to width 6 and
  forward or reversed above, each column read down, up or alternating;
- columnar with a fixed number of rows 2 to 10, columns forward or reversed, the same
  three read directions;
- rail fence with 2 to 6 rails at every starting offset;
- reversal, rotations by 1 to 3 either way, swapped halves, reversed halves, middle-out and
  ends-in in both parities, reversed blocks of 2 to 5 words.

Calibration on a joined prose window at the body's size (2,912 blocks):

| window | best rule | z | family P |
|---|---|---|---|
| intact | rotation by 3 (keeps the order) | +8.7 | 0.000 |
| planted keyed columnar, width 5, columns (3, 0, 4, 1, 2), up | the planted rule | +7.7 | 0.000 |
| planted rail fence, 4 rails, offset 3 | the planted rule | +7.7 | 0.000 |
| planted ends-in | the planted rule | +8.9 | 0.000 |
| shuffled | a width-6 columnar | +4.4 | 0.65 |

The scan's own maximum under the null is 4.6 ± 0.6, set by the 1,440 keyed width-6
orders. A planted rule clears it by 3 to 4 sigma and is named exactly.

**The body**, 137 spans of two or more blocks:

| | best rule | z | family P |
|---|---|---|---|
| whole body | columnar width 6, columns (3, 5, 1, 4, 2, 0), alternating | +5.11 | 0.175 |

Held out, selecting the best rule on one half of the spans and reading it on the other:

| split | selected on | rule | z there | z on the other half |
|---|---|---|---|---|
| odd / even | odd | width 6, (0, 4, 5, 2, 1, 3), down | +6.43 | +0.59 |
| odd / even | even | width 6, (4, 5, 2, 1, 0, 3), up | +5.10 | −1.10 |
| first / second | first | width 6, (5, 4, 2, 3, 0, 1), down | +5.61 | −0.35 |
| first / second | second | width 6, (3, 5, 1, 4, 2, 0), alternating | +5.38 | +2.12 |

Four different winners, none carrying to the other half. **This check has no power and
is withdrawn as evidence (review, 28 October 2026).** A rule reading +5.1 on the whole
body reads about +2.6 on a half, and even a planted rule at +7.7 to +8.9 reads about +4,
below the scan's null maximum of 4.6 ± 0.6; so the rule selected on a half is a noise
winner whether or not a real rule exists, and its failure to carry over is what both
cases produce.

**Sorted after encipherment?** A shuffle that sorts the ciphertext words by a visible
key would leave ascending runs. Ascending adjacent pairs inside spans, against the shuffle:
first rune z +0.78, last rune +0.53, Gematria sum −0.22, rune order −0.05, length +0.05.
Not sorted. A sort on the plaintext (alphabetical) is invisible to this test and stays
open; so does a keyed rule whose key changes per span, and a random draw.

**Corrected reading (28 October 2026).** The scan is evidence against a catalogue rule,
not an exclusion. A true rule would restore intact order, which reads 9.5 ± 3.0 on
joined prose windows at the body's size (`length_adjacency_self_null.py`, 28 windows,
range +5.8 to +17.1). The body's best is +5.11: 7% of intact windows read that low, and
the scan's null maximum is 4.59 ± 0.61, so the likelihood ratio at +5.11 is about 10 : 1
for no rule in the catalogue against a rule. The ciphertext words are not sorted by any
visible key. Still open at 10 : 1: a catalogue rule whose restored order happens to sit
in the weak tail; and untouched: a sort on the plaintext, a keyed rule whose key changes
per span, and a random draw. For a solver the within-span order is unknown in every case.
An independent channel can sharpen the 10 : 1 without a new scan: under the whole-body
winner's inversion the sentence-final long block should return (prose +1.28 ± 0.24, the
author +0.42 ± 0.29, the body as written −0.11 ± 0.21); that statistic was not used in the
selection.
