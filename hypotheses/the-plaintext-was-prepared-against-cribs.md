---
type: hypothesis
---
# Hypothesis: The Plaintext Was Prepared Against Cribbing Before Encipherment

## Claim

The early pages fell to cribs: `A WARNING`, `WELCOME`, the Parable's opening. The body's
plaintext was therefore processed first: **short function words were attached to the word
that follows them**, and **the words inside each sentence were shuffled, the first word
kept in place**. The cipher then enciphered a text with no phrase a cribber could slide.
This reads the whole plaintext-side anomaly as one deliberate design rather than as
accidents of transcription.

## Status

**Status**: unresolved, a framing of measured facts rather than a new measurement.
Proposed 2026-10-25.

## Mechanism

Two steps before encipherment, both reversible by the reader of a decryption:

1. join: a 2-rune unit is written onto its successor at rate q ≈ 0.40
   (`short-units-are-written-joined.md`, P = 0.79 for the marginal; the serial-order fit was
   withdrawn in October 2026), producing the hole at length 2 and the 3,100–3,300 plaintext words the fit
   implies;
2. shuffle: the words after the first are permuted uniformly within the sentence
   (`the-rearrangement-is-not-a-simple-rule.md`: no structured rule beats a shuffle;
   "keep first, shuffle rest" fits at P = 0.17 and a full shuffle at 0.39, and the span's
   first block carries the author's sentence-initial signature cell for cell).

## Evidence for

- E1/E2/E3/E9 and D15 are all consequences of these two steps, and no other single
  reading in this directory produces all five.
- The body's last block in a span is not a sentence-final word (31.7 on four degrees of
  freedom against identity), while its first block is sentence-initial: exactly what
  "keep the first word" leaves.
- Motive is documented in the book itself: every solved page was broken by a crib.
- October 2026: the shuffle step is measured, not inferred — adjacent block lengths inside a span are independent, z −0.10 against the body's own within-span shuffle, where intact order with the body's joining applied reads +5.1 on the author's pages and +5.8 to +17.1 on prose at the body's size (`experiments/length_adjacency_self_null.py`). Whether the join came before or after the shuffle is unreadable from the marginal (`joining_before_or_after_the_shuffle.py`), and the shuffle did not make the doublet deficit (`doublets_per_span.py`).

## Evidence against

- The joining does not happen in the front matter (E9 notes it), so the author applied
  it to the body only; a design decision, but an undocumented one.
- A framing cannot be killed by the statistics it was built from; only a decryption or a
  structured rule found later can.

## Predictions

1. The joined units are function words: OF, TO, IN, IS, IT, AN, BE, AT, AS, WE, HE. A
   crib dictionary should carry them attached to their commonest successors (OFTHE,
   TOTHE, INTHE, ITIS, TOBE), as `docs/new-directions.md` 3.6 already asks.
2. The span-initial block is a sentence-initial word. A crib programme on those 137
   blocks alone, with the sentence-initial vocabulary of the author's own pages, has a
   much higher prior per block than one over the whole body.
3. Phrase cribs (two adjacent words) are void everywhere except at span starts; the
   DJU-BEI phrase is a state return of the cipher and says nothing about plaintext
   adjacency.

## Scripts

- `experiments/which_structured_permutation.py`, `experiments/short_word_deficit.py`
  and the E9 fit — the measurements this reads together. Nothing new to run until a
  carrier is fixed.

## Related

- `the-words-are-transposed-within-sentences.md`, `short-units-are-written-joined.md`,
  `sentences-do-not-end-long.md`, `block-lengths-have-a-hole-at-two.md`.
- `the-body-is-a-scrambled-copy-of-published-text.md` — the same shuffle with a known
  source.

## Verdict

Open as a design reading. Its value is the crib strategy it dictates: words, not phrases;
span-initial blocks first; joined function words in the dictionary.
