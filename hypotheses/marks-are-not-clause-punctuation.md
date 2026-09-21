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

## Status

**Status**: confirmed (measurement) for all three, with the power check run before
the negative was accepted. `experiments/mark_clause_lengths.py`,
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

## Related

- `thirty-symbol-disk.md` — the machinery reading, whose rune-gap evidence this
  sharpens.
- `quote-span-boundaries.md` — the plaintext-respects-marks result this does not
  explain.
- `mark-glyph-inventory.md` — the glyph collapse whose consequence this measures.
- `word-length-keystream-and-boundaries.md` — the absent sentence-final signature,
  which this agrees with by a different route.
