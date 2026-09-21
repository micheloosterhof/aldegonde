---
type: observation
---
# Observation: The Unsolved Pages' Marks Do Not Space Like the Solved Pages' Clause Punctuation, and the Glyphs Are Not One Thing

## Feature

Measured in **words between marks**, against the LP's own solved pages as the
reference:

| group | marks | words/mark | mean | cv | p(cv this low) | ≤2 words | p |
|---|---|---|---|---|---|---|---|
| solved pages, `.` (control) | 87 | 8.9 | 8.3 | 0.74 | **0.0026** | 20.7% | 0.12 |
| unsolved, all glyphs | 176 | 18.6 | 13.5 | 0.81 | 0.14 | 11.9% | 0.41 |
| unsolved, 4-dot only | 141 | 23.2 | 14.9 | 0.79 | 0.12 | 5.7% | **0.0115** |
| unsolved, 13-dot only | 31 | 105.7 | 16.5 | 1.12 | 0.9998 | 35.5% | 1.000 |

Three results, in decreasing order of how well they are established.

1. **The solved pages' marks space like punctuation and the unsolved pages' do
   not.** Genuine English clause punctuation in this book is strongly
   under-dispersed against random placement (p = 0.0026). The unsolved pages'
   marks are not (p = 0.14), and this is not a power problem: planting the solved
   pages' own clause-length distribution at the unsolved pages' sparser rate is
   detected at p < 0.05 in **100%** of 120 plants (98% for 4-dot only).

2. **The 4-dot mark avoids short gaps, which is the opposite of punctuation.**
   Only 5.7% of its gaps are ≤ 2 words, significantly *fewer* than random
   placement gives (p = 0.0115), where real clauses in the solved pages run short
   20.7% of the time. English punctuation produces many short clauses; the 4-dot
   mark produces almost none. A minimum-separation rule is machinery-shaped, not
   language-shaped.

3. **The mark glyphs are not one symbol.** The 4-dot and 13-dot marks are not
   exchangeable — short-gap fraction 5.7% (n = 141) against 35.5% (n = 31),
   permutation p = **0.00005** — and the difference tracks the page layout: the
   13-dot mark sits at a line end 51.6% of the time against the 4-dot mark's
   10.6%. The two depart from random placement in *opposite directions*: the 4-dot
   mark is under-dispersed and short-gap-avoiding, the 13-dot mark is
   over-dispersed and clustered (cv 1.12, p = 0.9998; 35.5% short gaps, p = 1.000).
   Pooling them averages a spreading process against a clumping one.

## The word-length signature, split by glyph (the pooled result was already right)

Spacing is one probe. The word-length signature at the boundary is another, and
`word-length-keystream-and-boundaries.md` already ran it properly: it used these same
solved pages as calibration (solved finals 5.56 vs 4.01, z = +7.06, only 2.3% of
finals 1-2 runes against a 27.9% baseline), found the unsolved marks show none of it
(z = -1.21), and reported the contrast at z = +5.86. **That result is not rediscovered
here and no credit for it belongs to this file.**

What is added is only the per-glyph split, which that test did not do. The question it
leaves open is whether pooling a linguistic glyph with a layout glyph hid a signature
in one of them. It did not:

| group | marks | corpus mean | word before | z | word after | z | z if the effect were real |
|---|---|---|---|---|---|---|---|
| solved `.` (calibration) | 86 | 3.62 | 4.95 | **+5.86** | 3.87 | +0.46 | — |
| unsolved, pooled | 173 | 3.90 | 4.14 | +1.65 | 4.05 | +1.01 | +8.3 |
| unsolved, 4-dot | 141 | 3.90 | 4.06 | +1.04 | 4.08 | +1.09 | +7.5 |
| unsolved, 13-dot | 29 | 3.90 | 4.41 | +1.22 | 3.95 | +0.03 | +3.2 |

Genuine clause boundaries in this book lengthen the preceding word by 1.33 runes,
z = +5.86 on only 86 marks (the earlier run's +7.06 on the same pages, under a
slightly different tokenization and denominator — the two agree). The last column
projects that effect onto each group's own sample size: the 4-dot mark, with **more**
data at 141 marks, would have shown z = +7.5 had the effect been there. It shows
+1.04.

So splitting does not rescue the signature. Neither glyph carries it, and the
glyph-pooling defect found above is not the reason the pooled test came back null.

## Status

**Status**: confirmed (measurement) for all three, with the power check run before
the negative was accepted, and and consistent with the
established word-length-signature result, which is re-run per glyph here rather than
reproduced as new evidence. `experiments/mark_clause_lengths.py`,
`experiments/mark_clause_power.py`.

## Why this reference is the right one

The transcription splits cleanly by convention: pages 0–14 write the clause
delimiter as ASCII `.`, pages 15+ write it as the 4/10/13-dot glyphs, and **no page
uses both**. Pages 0–14 are the solved section, where the decryption reads as
English and the marks are known to fall at genuine clause boundaries.

So the control is the same book, the same scribe, the same delimiter convention and
the same transcriber — which is why this comparison is worth more than the
prose-corpus comparisons that have misled this project before
(`battery-register-is-unmatched`, and the register caveat in
`negative-control-battery.md`). The remaining register gap is real and is stated
under Limits.

## Why the earlier gap test missed it

`thirty-symbol-disk.md` reports mark gaps as "near-exponential (cv 0.91)" from
`mark_thirty_symbol.py`, which measures gaps in **runes**. Word lengths in the LP
vary by a factor of several, so rune gaps inherit that variance and are pushed
toward cv 1 whatever the underlying process does. The same quantity measured in
words separates the two readings: the solved control lands at 0.74 and rejects
random placement, which the rune-based measurement could not have shown.

## What it does to the two readings

The two files this sits between could not both be right.

- `quote-span-boundaries.md` measures that quoted spans align to the marks (8 of 14
  edges, p = 1.5e-7) and are depleted inside them — the plaintext respects the
  marks.
- `thirty-symbol-disk.md` reads the marks as machinery, supported by per-section
  homogeneity, uniform rune contexts and near-exponential gaps.

This weighs against the simplest punctuation reading and toward machinery, but it
does **not** settle the conflict, because it does not explain the quote alignment.
What survives is narrower than either file: whatever the marks delimit, it is not
spaced like English clauses, and the 4-dot mark actively avoids the short gaps that
clauses produce.

A reading consistent with all three measurements: the marks delimit a unit the
author used for composition *and* the cipher used for state, so plaintext respects
them without their spacing being linguistic. That is a hypothesis, not a finding,
and nothing here tests it.

## The quote alignment is now isolated, and it is carried entirely by the 4-dot mark

All 8 of the quote-span edges that land on a mark land on the **4-dot** glyph; none
lands on 13-dot or 10-dot (`experiments/quote_span_analysis.py`, re-read per glyph).
That is the direction the rest of this file predicts — 4-dot is the candidate
linguistic glyph, 13-dot the layout one — but it is **not evidence**: 4-dot is 81.8%
of the marks in that corpus, so 8 of 8 has probability 0.818⁸ = 0.20 under random
glyph assignment. Recorded as directional only, and underpowered at n = 8.

So the conflict tightens rather than resolves. Two independent statistics, both
calibrated on this book's own solved pages, say the unsolved marks are not English
clause boundaries. One statistic — the quote-edge alignment at p = 1.5e-7 — still
says the plaintext respects them. The alignment is now the single anomaly, and it
cannot be dismissed as a glyph-pooling artifact.

## The other two pooled statistics, split

`thirty-symbol-disk.md` rests its machinery reading partly on two pooled
measurements. Splitting them by glyph changes one of the two.

**Rune context: unchanged.** The runes immediately before and after a mark are
uniform for every glyph, not just pooled (4-dot n = 139, chi2 28.9 before and 30.6
after on 28 df; 13-dot n = 28). Nothing was hidden by pooling here. With 139 marks
over 29 bins this is underpowered against small deviations and is reported as "no
effect found", not "no effect".

**Per-section rate homogeneity: the pooled result is a mixture.** Pooled, the ten
clean sections are consistent with one Poisson rate (chi2 6.5 on 8 df, p = 0.59),
reproducing the figure that file cites. Split:

| glyph | marks | chi2 | df | p |
|---|---|---|---|---|
| pooled | 168 | 6.5 | 8 | 0.594 |
| 4-dot | 139 | 11.7 | 8 | 0.164 |
| 13-dot | 26 | 24.7 | 8 | **0.002** |

The 4-dot mark is homogeneous; the 13-dot mark is **not**, varying from 0.3 to 7.0
per thousand runes across sections. So "a content-independent process fits cipher
machinery better than authorial punctuation habits" is argued from a statistic that
averages a homogeneous glyph against a section-varying one. The conclusion may still
hold for 4-dot alone — that row is the one to cite — but the pooled version does not
support it.

(Both tests exclude the 9-rune section 3. Including it puts two marks on nine runes
and sends every chi2 to p = 0.000; the published 8 df shows that section was already
being dropped.)

## Readings tested and excluded

**A verse, breath or metrical unit.** If the 4-dot mark closed a metrical unit rather
than a clause, its gaps would concentrate near preferred lengths, which would explain
the short-gap avoidance and the quote alignment at once while predicting no
clause-final word signature. It is refuted by the bulk of the distribution: the 4-dot
mark's gaps measured in runes have cv = 1.02 against 0.66 for the solved pages' real
clause punctuation, so the bulk is exponential and there is no preferred unit length.
A verse structure is the one thing an exponential gap distribution cannot be.

**The quote glyph is another mark glyph, mis-transcribed.** This would dissolve the
quote alignment into a statement about the mark system rather than the plaintext. It
is excluded by the image census in `contraction-cribs.md`: the tick is a raised stroke
of h = 40, w = 12 px against dot marks of 9-10 px, found by connected-component sweep
of the page images, and distinct in both height and vertical placement. The glyphs are
not confusable.

**A refractory minimum separation.** The 4-dot mark's smallest rune gap is 6 and
random placement over rune positions reproduces that only 4 times in 10,000 — but this
is an artifact of the wrong null. Marks sit only at word boundaries, so a rune gap is
at least one word wide by construction. The solved pages' punctuation shows the same
apparent floor at the same significance (min 5, p = 0.00002), which is how the error
surfaced. Nothing is claimed from rune-level floors; the word-boundary-respecting
tests above are the ones that count.

**No control exists for the quote alignment.** All 14 quote ticks fall on unsolved
pages and none on the solved pages, so the natural check — do quotes align to marks in
known LP English? — cannot be run on this corpus.

## Limits

- **Register.** The solved pages are the book's introductory and didactic material
  (warnings, koans); the unsolved pages are its body. Denser punctuation in
  aphoristic prose is an ordinary stylistic difference, so the 2x **rate** gap
  (8.9 vs 18.6 words per mark) is confounded and carries little weight on its own.
  The shape results do not depend on the rate: the permutation null is built at
  each group's own rate, and the power check plants the solved *shape* at the
  unsolved *rate*.
- **Pooling asymmetry.** The solved pages' `.` is a single ASCII character that may
  itself collapse several glyphs (`mark-glyph-inventory.md`). The control is
  therefore a pooled measurement, which is why the headline comparison is against
  the pooled unsolved marks; the per-glyph rows are reported separately.
- The 10-dot mark has n = 4 and nothing is claimed from it.
- None of this touches what the marks do to the key. Whether a mark consumes a
  clock step remains open and is not addressed here.

## What would change the verdict

- A solved-page glyph census. If the scans show the solved pages also use 4-dot and
  13-dot glyphs, the pooling asymmetry can be removed and the control re-run
  per glyph, which is the single largest improvement available.
- If the 13-dot mark is confirmed as a line-end or layout glyph, every pooled mark
  statistic in this directory is a mixture of two processes and should be re-run
  split. `mark-glyph-inventory.md` already records that the transcription collapses
  four glyphs into two characters; this measures a consequence.

## Scripts

- `experiments/mark_clause_lengths.py` — words between marks, solved vs unsolved vs
  random placement, per glyph; decision rule registered in the docstring.
- `experiments/mark_clause_power.py` — the power check, planting the solved pages'
  clause-length shape at the unsolved rate.
- `experiments/mark_word_signature.py` — the word-length signature per glyph, with
  the solved pages calibrating what a real clause boundary does.

## Related

- `thirty-symbol-disk.md` — the machinery reading, whose rune-gap evidence this
  sharpens.
- `quote-span-boundaries.md` — the plaintext-respects-marks result this does not
  explain.
- `mark-glyph-inventory.md` — the glyph collapse whose consequence this measures.
- `word-length-keystream-and-boundaries.md` — the absent sentence-final signature,
  which this agrees with by a different route.
