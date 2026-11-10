---
type: hypothesis
---
# Hypothesis: The Separators Are Independent Draws, Not Plaintext Word Boundaries

## Claim

The block lengths carry no plaintext. They were laid over the rune stream from one length
marginal, independently, and the four-dot spans hold no sentences. Two forms:

- **N1, decorative.** The separators were placed after encipherment and the cipher never
  saw them.
- **N2, cipher units of independent length.** The cipher does restart its letter clock
  at each separator, but the lengths are independent draws, so there are no words and no
  word order to restore.

Proposed 2026-11-10 as the cheaper reading of the result that adjacent block lengths
inside a span are independent (`the-words-are-transposed-within-sentences.md`, row E11).
That result is what a word permutation leaves, and it is also what independent lengths
leave with no permutation at all.

## Status

**Status**: N1 **disproved**; N2 **unresolved**, and not testable on the lengths.

## Mechanism

N1 needs nothing from the cipher. N2 is any cipher of the surviving class
(`what-any-solution-must-satisfy.md`) run over a plaintext cut into units by a length
sampler rather than by its words. Under N2 the 2-rune hole (E3) is a property of the
sampler, and the joining model (E9) describes nothing.

## Evidence for

- Adjacent block lengths inside a span are independent, z −0.10 against the body's own
  within-span shuffle (E11).
- The lengths depend on no visible variable (E2), and the pre-mark block is a random
  block of its span.
- None of 5,482 rule-based shuffles on 309 unit sets restores an English order.
- "Blocks are words" (E7) rests on a marginal fit with one free parameter and a d5 length
  trend at 1.73σ.

## Evidence against

**N1 is rejected by the lag-5 echo.** `experiments/separators_drawn_independently.py`
keeps the rune stream and re-cuts it with the same block lengths in another order. The
number of within-block pairs at each lag is the same in every draw.

| lag | body | lengths shuffled over the body | z | P | lengths shuffled inside spans | z | P |
|---|---|---|---|---|---|---|---|
| 4 | 131 | 114.4 ± 9.3 | +1.79 | 0.039 | 118.3 ± 9.1 | +1.39 | 0.093 |
| 5 | 104 | 77.9 ± 8.2 | **+3.18** | **0.0015** | 78.9 ± 8.0 | **+3.15** | **0.0005** |
| 6 | 32 | 45.4 ± 6.3 | −2.11 | 0.989 | 43.3 ± 6.0 | −1.89 | 0.977 |

Lag 5 was the one lag named in advance; 4 and 6 move in the directions row D2 records.
The boundaries know where the echo is, so the cipher saw them. This is the same fact as
row D1 (boundaries slid by a fixed offset, +4.17σ) under a different re-cut, and the two
agree. It is counted with join_pages=True (2,896 blocks, 104 lag-5 hits); the default
tokenization gives 102 of 2,073.

**N2 has two facts against it, neither from the lengths.**

- The rubricated titles are contiguous runs of blocks whose rune totals match a title
  (`rubrication-crib-candidates.md`, `permutation_unit_size.py`). A length sampler does
  not know where the red ink is.
- The length marginal is the author's own with short units joined, at P = 0.79 with one
  parameter (E9). A sampler would have had to be fitted to that.

## Predictions

- N2 predicts the spans are random samples of one marginal: no span differs from another
  in composition by more than sampling.
- A sentence reading predicts they differ, as sentences do.

**The test has no power.** The between-span sum of squares of block length over the grand
variance, against all lengths shuffled across spans (every span keeps its block count),
is invariant to order inside a span, so it would separate "sentences, permuted inside"
from independent lengths if sentences differed enough:

| text | spans | blocks | z, block length | z, share of blocks ≤ 2 runes |
|---|---|---|---|---|
| the body | 137 | 2,896 | +0.92 | −1.34 |
| the author's solved pages | 94 | 719 | +1.06 | −0.38 |
| joined prose at the body's span sizes, 8 windows | 137 | 2,894 | +0.6 ± 0.5 | −0.5 ± 0.4 |
| independent lengths planted on the body's spans | 137 | 2,896 | −0.01 ± 1.04 | +0.03 ± 0.97 |

English sentences at the body's span sizes sit 0.53σ from independent lengths. The body
reads +0.92, inside both bands. Sentence-to-sentence composition is not a channel, in
either direction, and the remark in
`the-words-are-transposed-within-sentences.md` that "sentences differ in word-length
composition" holds for a block straddling two sentences in order, not for whole-span
means at this size.

## Scripts

- `experiments/separators_drawn_independently.py` — both tests, about one minute.

## Related

- `the-words-are-transposed-within-sentences.md` — the reading N2 competes with.
- `separators-are-the-cipher-unit.md` — row D1, the slide version of test A.
- `separators-are-not-word-boundaries.md`, `blocks-are-still-words.md` — the earlier
  round of the same question, decided for words on the marginal.
- `the-body-is-machine-made.md` — N2 is what a program with a length sampler would emit.

## Verdict

N1 is out: the separators are inside the cipher. N2 stays open and the lengths cannot
close it. What separates N2 from a word permutation is not statistical: the red-ink
titles and the fitted marginal say the units are words, and N2 has to call both
coincidence or design. For crib work the two readings agree on the one thing that
matters: a crib is a single block, never a phrase.
