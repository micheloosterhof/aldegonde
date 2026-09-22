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

   *Tested, weak support at best.* A different hand should show in more than word
   lengths. Two scribal features are in the transcription — line measure and which marks
   end a block — and both are confounded.

   **Line measure** has an encipherment confound that must be handled first: enciphered
   text has no word shapes to break on, so a scribe fills to a measure while plaintext
   breaks at sentence ends. Paragraph-final lines dropped:

   | group | lines | runes per line |
   |---|---|---|
   | front: plaintext | 49 | 18.59 ± **6.49** |
   | front: monoalphabetic | 46 | 19.52 ± **3.17** |
   | front: interrupted Vigenère | 37 | 20.32 ± **2.60** |
   | **the body** | 539 | **21.92 ± 2.32** |

   The spread tightens monotonically, which is the confound doing its work. Against the
   right comparison — the *enciphered* front matter — the body's lines are 1.6 runes
   longer, about 8%, at z = +6.02. Real, but far smaller than the raw front-against-body
   gap of +2.5 suggests, and an 8% line measure is not obviously a different hand.

   **Mark inventory cannot be read at all.** The front matter uses `.` and never a
   circled numeral; the body uses circled numerals and never `.`. Those are the same
   manuscript feature under two *transcription* conventions — the circled numeral records
   a dot count the `.` does not (`marks-are-not-one-glyph`). Comparing them measures the
   transcriber. What is comparable is the rate: 12.5% of front-matter blocks end in a dot
   mark against 5.7% in the body, which is ordinary for short instructional paragraphs
   against continuous text.
2. **The joining is part of the enciphering**, done when the plaintext was prepared rather
   than when it was composed. That would make it uniform across the body, which it is
   (χ² 3.9 on 8 df over nine sections), and absent from pages enciphered by simpler means,
   which it is.

   ***Tested and dead.*** If joining were preparation it should track how hard the page's
   cipher is. `experiments/joining_is_not_preparation.py` finds no gradient at all:

   | cipher | pages | words | fraction at 2 | z vs the body |
   |---|---|---|---|---|
   | plaintext (no cipher) | 6 | 231 | 0.2597 | −3.41 |
   | monoalphabetic | 5 | 255 | 0.2196 | −2.27 |
   | interrupted Vigenère | 4 | 212 | 0.2406 | −2.71 |
   | prime running key | 1 | 25 | 0.3200 | −1.72 |
   | **all enciphered pages** | | 492 | **0.2337** | **−3.70** |
   | **the body** | | 2,928 | **0.1588** | |

   All four groups sit between 0.22 and 0.32, within each other's errors and around the
   0.2422 median of twenty-two English registers. The AN END page — the hardest cipher
   the author ever solved — reads the *highest* of any group at 0.320, though on 25 words
   it cannot carry the argument alone.

   **Being enciphered is not what distinguishes the body.**
3. **The 2-rune deficit is not joining at all** but some other process that happens to
   leave the same marginal and the same serial order. Nothing else measured does.

Reading 2 was the one that fitted the pattern of the book without needing a second hand.
It is now dead, so what survives is reading 1 — the body's scribe or exemplar differs —
or reading 3, that the deficit is not joining at all. Nothing else measured produces the
same marginal and the same serial order, which is what keeps reading 3 unattractive
rather than excluded.

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
