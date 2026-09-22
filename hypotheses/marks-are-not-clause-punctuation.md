---
type: observation
---
# Observation: The Unsolved Pages' Marks Do Not Space Like the Solved Pages' Clause Punctuation, and the Glyphs Are Not One Thing

## Correction (2026-09-21, same day): the control was mislabelled and one result does not survive it

This file originally called pages 0-14 "the solved section". That was wrong. The `.`
convention marks pages **transcribed with ASCII delimiters**, which is not the same as
pages that are solved. Scoring each of those 15 pages as runeglish shows only **six**
(3, 8, 9, 10, 11, 14) are plaintext in the transcription -- they read directly as
English, e.g. page 8 "THE LOSS OF DIUINITY THE CIRCUMFERENCE PRACTICES THREE
BEHAUIARS..." -- while nine (0, 1, 2, 4, 5, 6, 7, 12, 13) are still enciphered.
`experiments/solved_page_testbed.py` classifies them.

Re-running the two headline statistics on the pure plaintext set:

| group | marks | cv | p(cv) | ≤2 wd | word before | z |
|---|---|---|---|---|---|---|
| plaintext pages only | 34 | 0.85 | **0.32** | 29.4% | 5.29 | **+3.49** |
| ASCII-convention, still enciphered | 53 | 0.66 | **0.0024** | 15.1% | 4.73 | **+4.74** |
| unsolved, 4-dot | 141 | 0.79 | 0.12 | 5.7% | 4.06 | +1.04 |

**The spacing result does not survive.** The p = 0.0026 reported below as the positive
control came from the pooled ASCII-convention pages, and splitting them shows it is
carried by the *enciphered* subset; the genuine plaintext pages give cv 0.85, p = 0.32.
A control that fails on the one group where the plaintext is readable is not a control.
The spacing argument is withdrawn, and with it the claim that the test had demonstrated
power — `mark_clause_power.py` planted the pooled template's shape, which is now known
to be a mixture.

**The word-length signature survives and is strengthened.** Both ASCII-convention
groups carry it -- plaintext z = +3.49 and enciphered z = +4.74 -- which is what a
length-preserving cipher predicts, since plaintext word lengths pass through
encipherment untouched. The unsolved 4-dot mark does not, at z = +1.04 on the largest
sample of the three. That contrast is now the load-bearing evidence in this file, and
it no longer depends on knowing which pages are solved: it only needs the two
transcription conventions, both of which carry the signature on one side and not the
other.

Everything below is left as written except where it is marked. The 13-dot
identification and the glyph-splitting results are unaffected -- they never used the
control.

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

**Status**: result 1 (spacing) WITHDRAWN by the correction above; results 2 and 3 stand, and the word-length signature stands. Originally recorded as confirmed (measurement) for all three, with the power check run before
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

## What the 13-dot mark is: a paragraph glyph

The transcription carries its own structural delimiter, `&` for paragraph, placed
from the page layout and independent of any cipher reading. The 13-dot mark tracks
it and the 4-dot mark does not:

| glyph | marks | median rune distance to nearest `&` | null | p |
|---|---|---|---|---|
| 4-dot | 17 | 88.0 | 77.0 | 0.73 |
| 13-dot | 26 | **0.0** | 56.5 | **0.0002** |

Sharpened to immediate adjacency in the character stream, where `&` is 0.8% of all
boundaries:

| glyph | beside a `&` | total | rate | expected by chance |
|---|---|---|---|---|
| 4-dot | 0 | 141 | 0% | 1.1 |
| 13-dot | **14** | 31 | **45%** | 0.3 |

Fourteen of the 32 `&` delimiters carry a 13-dot mark. The 4-dot mark touches one
never, and at an expectation of 1.1 that zero is unremarkable on its own — the
identification rests on the 13-dot side, where 14 against 0.3 expected is not a
coincidence.

So the 13-dot glyph is paragraph-associated structural markup, which accounts for
every way it misbehaved above: it clusters (paragraph breaks bunch at headings and
short paragraphs), it sits at line ends half the time (paragraphs end lines), and its
per-section rate is inhomogeneous (paragraph density is a property of the text, not of
a cipher). It is not a clause mark and should be excluded from mark statistics that
are about the clause or cipher system.

It is not simply the same symbol as `&`: 17 of 31 occurrences are not adjacent to one.
"Paragraph-associated" is the claim; "paragraph delimiter" is not established.

That leaves the **4-dot mark as the only candidate for a clause or cipher mark**, and
alone it is homogeneous across sections, uniform in rune context, carries no
clause-final word-length signature, and does not space like clause punctuation.

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
- `experiments/mark_glyph_roles.py` — co-location with the paragraph delimiter, which
  identifies the 13-dot glyph.

## Related

- `thirty-symbol-disk.md` — the machinery reading, whose rune-gap evidence this
  sharpens.
- `quote-span-boundaries.md` — the plaintext-respects-marks result this does not
  explain.
- `mark-glyph-inventory.md` — the glyph collapse whose consequence this measures.
- `word-length-keystream-and-boundaries.md` — the absent sentence-final signature,
  which this agrees with by a different route.

## The 4-dot mark is not a cipher event either (September 2026)

The question this file left open was whether ④ does anything to the key — whether it
consumes a clock step or changes the alphabet. It was recorded as blocked for want of a
key-free test. The orbit theorem supplies one
(`local-channel-is-exactly-coincidence.md`): across any boundary the only base-invariant
statistic is coincidence, so if ④ altered the seam relation, the coincidence profile
across ④ boundaries would differ from ordinary ones.

**The doublet suppression is present at ④ boundaries.** Across the 136 ④ boundaries
there is **1** distance-1 coincidence where chance gives 4.69 — Poisson P(≤1) = 0.052.
Ordinary boundaries give 22/2722 = 0.0081, and ④ gives 1/136 = 0.0074. So whatever
suppresses doublets is still operating across a ④, and ④ does not switch it off.

That is the informative half. A preventer acting on adjacent ciphertext runes predicts
exactly this: it has no way to know a mark is there.

**The relation test is weak and says little.** Pooled over distances 1–7, ④ boundaries
give 52/1867 = 0.0279 against ordinary 1309/40348 = 0.0324, a difference of z = −1.17.
The test resolves a 23% rate change at 2σ, which sounds adequate — but **most seam
relations produce a rate near chance anyway**, so a *changed* relation would usually
look identical. This test has power against a rate change and little against the
hypothesis of interest, and is reported so that its null is not over-read.

**Net:** ④ behaves like an ordinary word boundary as far as the cipher is concerned.
Combined with the earlier results — it carries no clause-final word-length signature,
does not space like clause punctuation, and is homogeneous across sections — the 4-dot
mark now has no established role in either the language or the cipher. The quote-edge
alignment at p = 1.5e-7 remains the single thing about it that wants explaining.

## The spacing argument, redone properly (September 2026)

`experiments/are_the_four_dot_gaps_memoryless.py`

The spacing result above is withdrawn because its control pooled the author's plaintext
pages with still-enciphered ones. This replaces it with a shape test rather than a cv
comparison, in **blocks**, with every reference joined at q = 0.40 so the units match.

| arm | cv | 1-3 | 4-7 | 8-14 | 15-24 | 25-39 | 40+ |
|---|---|---|---|---|---|---|---|
| **the body, 137 gaps** | **1.03** | **9** | 27 | 33 | 28 | 23 | 17 |
| memoryless (geometric) | 0.98 | 18.4 | 20.7 | 27.8 | 26.8 | 22.1 | 21.2 |
| English sentences, joined | 0.82 | 3.7 | 18.5 | 36.4 | 36.8 | 24.7 | 16.9 |
| the LP author's spans | 0.73 | 8.7 | 19.1 | 30.6 | 32.1 | 33.5 | 13.0 |

**cv is the wrong summary and should not be quoted again for this mark.** The body's 1.03
is inflated by its long tail; the short end says the opposite. Nine gaps of three blocks
or less against the 18.4 a constant-rate placement predicts is 2.2σ low, and matches the
author's own 8.7 almost exactly.

Binned log-likelihood: the author's spans −240.52, memoryless −241.08 (ratio 0.571),
English sentences −242.11 (0.203). **1.75 to 1 is not a verdict.** The body sits between
the arms — the author's short-gap deficit with a heavier long tail than either.

The instrument has power: drawing 137 gaps from each arm names the right one 92–98% of the
time, median likelihood ratios 50 to 6,000. The indecision belongs to the corpus.

**Positive content, small but real:** the four-dot is not dropped at a constant rate.
Something avoids placing two close together, which a memoryless process would not do. That
is the first positive statement about the four-dot rather than another absence.

This also explains why `are_the_two_marks_one_system.py` had no power: at cv ≈ 1 the
backward recurrence time matches the gap law, so renewal geometry cannot separate "at a
boundary" from "inside an interval" even though the process is not actually memoryless.

## The four-dot's placement ignores the page

`experiments/is_the_four_dot_placed_per_page.py`

With the thinning reading excluded at 7σ, most four-dots are not sentence ends and
something else sets their spacing. Their gaps are not memoryless — nine of three blocks or
less where a constant-rate process predicts 18.4 — so something keeps them apart, and the
natural candidate needing no reference to the text is a scribe marking off each page.

Counting each glyph per body page against a constant per-rune rate:

| glyph | total | per page | χ² | df | P | reading |
|---|---|---|---|---|---|---|
| **④** | 139 | 2.53 | 55.8 | 54 | **0.406** | Poisson at a constant rate |
| ⑬ | 26 | 0.47 | 82.8 | 54 | **0.007** | over-dispersed, clustered |
| ① | 2,722 | 49.49 | 13.9 | 54 | **1.000** | under-dispersed, near-determined |

**The two controls land where they must** — the section mark clusters (titles are bounded
by a pair a few words apart), the word separator is nearly fixed by a page's rune count —
so the test discriminates and the four-dot's cell is readable.

**It sits exactly on a constant per-rune rate: the page is invisible to it.** That closes
the production explanation for its spacing, and matches what the doublet preventer says
from a different direction (`the-preventer-is-in-the-stream.md`) — the mechanisms in this
book do not see the layout.

It does not explain the short-gap deficit itself. Something spaces the four-dots more
evenly than chance; this only says where not to look.

## The four-dot has a hard floor of two blocks

`experiments/the_four_dot_has_a_floor.py`

The short-gap deficit has a sharp shape: **there is not one gap of a single block in the
whole body.**

| | n | mean | min | counts at 1..5 |
|---|---|---|---|---|
| the body, four-dot gaps | 138 | 20.4 | **2** | **0**, 4, 6, 7, 8 |
| the author, sentences | 94 | 7.6 | **1** | **6**, 13, 7, 8, 6 |
| English, sentences, unfiltered | 13,439 | 18.4 | **1** | **444**, 495, 377, 437, 492 |

| gaps of one block predicted by | expected | P(0 or fewer) |
|---|---|---|
| a memoryless process | 6.8 | 0.00115 |
| **the author's own convention** | **8.8** | **0.00015** |
| English sentences | 4.6 | 0.01047 |

The author's sentences have no floor — six of ninety-four are a single block — and neither
does English. **The body's four-dots have one and it is absolute.**

So the spacing is a *rule*, not a tendency: whatever places the four-dots enforces a
minimum unit of two blocks. That is the first **positive** structural statement about the
mark here; everything else established is a negation.

**A filter artifact worth avoiding.** `register_spans` drops sentences under three words,
twice — before and after joining — so English lengths taken from it cannot be 1 or 2 by
construction. Comparing the body's small gaps against that reference shows English
"never" having short sentences, which is the filter speaking. The English row above is
built without it.

### What the floor counts is unresolved

`experiments/does_the_floor_count_blocks_or_runes.py`

The floor could be a word count (≥2 blocks) or a letter count (≥6 runes). Both hold in the
body — the smallest gaps are (2 blocks, 6 runes), (2, 7), (2, 7), (4, 7), (3, 8) — and
they are distinguishable in principle, because each permits what the other forbids: a
block floor allows a two-block gap of four or five runes, and a rune floor allows a
one-block gap when that block is six runes or longer.

Placing 138 marks at random in the body's own block sequence under one floor and counting
violations of the other:

| rule simulated | one-block gaps | sub-6-rune gaps | P(the body's zero) |
|---|---|---|---|
| a block floor alone | 0.00 | **1.06** | 0.35 |
| a rune floor alone | **1.86** | 0.00 | 0.16 |
| both floors | 0.00 | 0.00 | — |
| **the body** | **0** | **0** | |

**Neither single floor is excluded.** The preference for both is 3:1 and 6:1 — real but
not a demonstration.

This is the sharpest open question about the four-dot. If the unit is a **word count**, the
mark divides the text by syntax however loosely; if a **rune count**, it divides by length
and the text is not involved at all. Those are different objects, and the question turns on
one or two expected violations, so it needs more marks rather than a better statistic.

### The floor is the four-dot's, not the medium's

`experiments/the_floor_belongs_to_the_four_dot.py`

The floor rests on an unchecked premise: that a one-block gap between marks is possible at
all. If the transcription, the hand or the page never permits two marks that close, the
floor is a property of the medium rather than the mark.

| pair kind | n | min blocks | min runes |
|---|---|---|---|
| four-dot to four-dot | 123 | **2** | **6** |
| every other pair | 47 | **1** | **3** |

**Two thirteen-dots sit one block and three runes apart, twice.** So the alternative was
physically available and the four-dot never takes it.

The direct glyph comparison is confounded and reaches only **Fisher P = 0.075** — both
one-block cases are a *one-word rubricated title* bounded by its pair of section marks,
which is a distinct structure rather than a scribe placing two marks close together. That
number should not be quoted as the floor's evidence.

The floor stands on its own comparisons — 0 against 6.8 expected under a memoryless
process and 8.8 under the author's convention. What this adds is the premise they rest on.
