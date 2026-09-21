---
type: hypothesis
---
# Short Units Are Written Joined, and the Boundary Sits Between Two Runes and Three

## Status

**Status**: the surviving explanation for the block-length anomalies, not a proof. Each
rule is scored against its own parametric null, so the comparison is fair and the errors
carry the 723-word reference.

## What is being explained

The body's block lengths differ from the author's own words in one place: **0.1588 at
length 2 against 0.2420**, z = −4.81. Register across 22 corpora, orthography,
section-to-section variation, line-break transcription and justification are all measured
and all fail (`block-lengths-have-a-hole-at-two.md`).

After that file's retraction, one mechanism survives. Joining about 40% of 2-rune units
to the unit before them is consistent with the length **marginal** at P = 0.79 and with
the **serial order** at 1.2 sigma — one mechanism, not two.

## Which lengths

A rule acting on length 2 but not length 1 would be strange. A rule acting on everything
short is ordinary: in runeglish, two runes or fewer is almost exactly the function-word
class — THE, TO, OF, IS, BE, WE, HE, A, I, AN, OR, DO.

`experiments/which_lengths_merge.py` scores each candidate against a null in which that
rule is true and both a 723-word reference and a 2,928-block body are drawn from it.
Comparing raw χ² across rules would be unfair, since they move the distribution by
different amounts.

| rule | best q | χ² | null, rule true | P |
|---|---|---|---|---|
| **absorb length 2** | 0.40 | 29.5 | 55.2 ± 34.1 | **0.83** |
| **absorb length 1 or 2** | 0.35 | 31.9 | 51.2 ± 29.7 | **0.70** |
| absorb length 1 | 0.25 | 181.7 | 64.2 ± 34.5 | 0.02 |
| absorb length 3 | 0.10 | 187.0 | 56.6 ± 29.2 | **0.00** |
| absorb length 3 or less | 0.15 | 101.9 | 52.6 ± 31.0 | 0.07 |

**The boundary sits between 2 and 3.** Absorbing two-rune units fits, absorbing one- or
two-rune units fits equally, absorbing three-rune units is dead, and absorbing only
one-rune units is rejected. The one- and two-rune versions cannot be separated: the
author's 723 words hold only 29 of length one.

## The rate, and what it predicts

Within the null's own spread the rate is indistinguishable over **q ∈ [0.22, 0.50]**, best
0.40.

| q | plaintext words | joined to a neighbour |
|---|---|---|
| 0.22 | 3,097 | 169 |
| 0.40 | 3,242 | 314 |
| 0.50 | 3,331 | 403 |

**The body's plaintext held somewhere near 3,100 to 3,300 words, of which 170 to 400 were
written joined to their neighbour.** A solved body page tests that directly, and it is the
sharpest prediction this directory has about the plaintext.

## The part that is still strange

The front matter does not do it. Its 2-rune fraction is 0.2420, sitting at the median of
22 English registers, and it is the reference this whole comparison uses. So the
convention differs between the front matter and the body of the same book, written in the
same hand.

Three readings, none tested:

1. **The body's scribe or exemplar differs.** The book escalates its cipher page by page;
   it may escalate its orthography too.
2. **The joining is part of the enciphering**, done when the plaintext was prepared rather
   than when it was composed. That would make it uniform across the body, which it is
   (χ² 3.9 on 8 df over nine sections), and absent from pages enciphered by simpler means,
   which it is.
3. **The 2-rune deficit is not joining at all** but some other process that happens to
   leave the same marginal and the same serial order. Nothing else measured does.

Reading 2 is the one that fits the pattern of the book without needing a second hand.

## Falsification

- A solved body page settles it: count its words against its blocks. The prediction is
  about one joined pair every nine or ten blocks.
- If the joining is orthographic, a solved page shows compounds a reader would recognise
  — THEWORD, TOTHE. If it is a cipher-preparation step, the joins fall where the plaintext
  gives no reason for them.
- The rule must not act on three-rune units. If a solved page shows three-rune words
  joined, the boundary is wrong and the whole fit changes.
- The rate must be uniform. If a solved page shows a joining rate far outside
  [0.22, 0.50], the single-rate model fails.

## Scripts

- `experiments/which_lengths_merge.py`
- `experiments/reference_noise_in_length_tests.py` — the retraction that made this the
  surviving reading.

## Related

- `block-lengths-have-a-hole-at-two.md` — the anomaly and everything that does not
  explain it.
- `separators-are-the-cipher-unit.md`, `blocks-are-still-words.md` — the two readings of
  what a block is; this says blocks are words with the short ones joined.
