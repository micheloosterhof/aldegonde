---
type: hypothesis
---
# The Body's Sentences Do Not End on a Long Unit

## The claim

**Revised 2026-09-22 and materially narrowed.** The anomaly is real but confined to the
spans where both texts have data, and the pooled figure that carried it was substantially
a composition effect.

The author's mark and the body's are the same glyph class (below). Comparing them
pooled gives the author +1.63 ± 0.25 runes of final-block lengthening against the body's
−0.33 ± 0.20, a difference of −6.1σ. **Most of that is not evidence.** The gap depends
strongly on the length of the span the mark closes, and the two texts close very
different spans.

| stratum | share: author / body | author | the body | difference |
|---|---|---|---|---|
| 1–2 blocks | 20.2% / 2.9% | +2.78 ± 0.61 | −1.49 ± 0.71 | n = 4, ignore |
| 3–6 | 31.9% / 18.2% | +2.20 ± 0.42 | −0.81 ± 0.33 | **−5.66σ** |
| 7–14 | 38.3% / 29.2% | +0.90 ± 0.34 | −0.19 ± 0.36 | **−2.19σ** |
| 15+ | 9.6% / 49.6% | +0.20 ± 0.53 | −0.17 ± 0.30 | **−0.61σ** |

So: real at short and medium spans, and **apparently absent in the stratum holding half
the body's spans**.

**That last reading is withdrawn, September 2026.** It rests on the author's 15+ cell,
which holds **nine spans**. Against ten English registers
(`final_lengthening_across_registers.py`) the same stratum reads:

| stratum | the body | ten registers | z |
|---|---|---|---|
| 3-6 | −0.81 ± 0.33 | +0.87 ± 0.63 | **−2.35** |
| 7-14 | −0.19 ± 0.36 | +1.20 ± 0.32 | **−2.90** |
| **15+** | **−0.17 ± 0.30** | **+1.25 ± 0.22** | **−3.80** |
| all | −0.29 ± 0.20 | +1.19 ± 0.28 | **−4.38** |

All ten registers lengthen (none below +0.78) and all ten **rise** with span length. The
anomaly is present in every stratum and is *strongest* at 15+, not absent. What survives
from the stratified reading is only that the pooled figure against the author was
inflated by composition. The author has only 9 spans at 15+, so that cell settles nothing by itself — but
it is where the body mostly lives, and the pooled number leans on the author closing
short units five times as often.

Reading the solved pages with their plaintext spliced into their own separator layout
shows what those short units are: the mark is a period, and it closes titles and
exclamations as readily as sentences — `A WARNNG.`, `WELCOME.`, `SOME WISDOM.`, whose
final word is necessarily a content word. That is where +2.78 comes from.

`experiments/the_gap_depends_on_span_length.py`.

## The measurement

`experiments/sentences_do_not_end_long.py`. Mean unit length in each cell, measured
against that same text's own interior, so register cancels.

| text | sentence-initial | sentence-final |
|---|---|---|
| Pride and Prejudice, 5,361 sentences | −0.37 ± 0.03 | **+1.00 ± 0.04** |
| the LP author, 16 solved pages | −0.33 ± 0.24 | **+1.51 ± 0.25** |
| the LP body, 4-dot and 13-dot marks | −0.07 ± 0.21 | **−0.21 ± 0.18** |

The two-rune odds say the same thing more sharply at one point: the author has **0 of
85** sentence-final words at length 2, against 27% of interior words. The body has 27
of 166.

**The sentence-initial column was called a passing control here and that was
overstated.** It rested on comparing the body against the *author's* 85 words, where the
error bar is ±0.24 and nothing resolves. Against Austen's 5,361 sentences the body's
sentence-initial contrast is **+0.07 ± 0.21 where −0.30 ± 0.03 is predicted** — the
wrong sign, at 1.67σ. It does not fail, but it does not pass: it is equivocal.
See `profile_around_a_mark.py` and the profile section below.

## The profile: English marks a sentence with three units, the body with none

`experiments/profile_around_a_mark.py` widens the single cell to a profile over offsets
from a mark, each against that text's own span interior. Both references agree on a
three-point shape, and it is the shape English grammar predicts:

| offset | what it is | Austen | joined q=0.40 | the LP author | **the LP body** |
|---|---|---|---|---|---|
| −2 | penultimate, usually a function word | −0.41 | −0.26 | −0.53 | **−0.01 ± 0.20** |
| **−1** | **final, a content word** | **+0.97** | **+0.75** | **+1.28** | **−0.21 ± 0.19** |
| +1 | initial, usually a function word | −0.40 | −0.30 | −0.29 | **+0.07 ± 0.21** |

All three body cells lean away from English, but **only −1 is individually decisive**
(z = −5.03 against joined Austen); −2 and +1 sit at 1.25σ and 1.67σ, which 156 spans
cannot resolve. Joint χ² over the three pre-specified offsets is 29.7 on 3 df and is
dominated by −1. Treat this as one strong cell inside a consistent shape, not as three
independent results.

A fourth cell, **+2, came out at +0.37 ± 0.21 against a predicted −0.14, z = +2.45**. It
was noticed in the data, not predicted, and is excluded from the joint test. It needs an
independent replication before it means anything.

## The marks' spacing: mechanical is dead, sentences are in doubt

**This section previously claimed the opposite and the claim is withdrawn.** It reported
that the marks "partition the body at ordinary prose sentence density — 17.2 units a
span against 17.5 for joined Austen" and called that the strongest evidence the marks
are sentence-scale. It is not evidence at all: random placement matches **any** mean by
construction, since the density is its one free parameter. Only the shape discriminates.

`experiments/what_the_marks_space_like.py` measures the shape. Dispersion of the gap
between marks:

| | spans | mean | CV |
|---|---|---|---|
| **the LP body** | 148 | 19.6 | **0.972 ± 0.145** |
| the LP author's own pages | 92 | 7.9 | 0.738 ± 0.049 |
| Pride and Prejudice, joined q = 0.40 | 5,361 | 17.4 | 0.771 ± 0.010 |
| marks placed at random | 148 | 19.6 | 0.970 ± 0.071 |
| mechanical, every 19.6 blocks | — | 19.6 | 0 |

**Mechanical placement is dead** at 6.7σ. That much is settled, and it was worth
checking: a counting device would have dissolved the whole anomaly.

Between sentence ends and a memoryless process the body sits **exactly on memoryless**
and 1.4σ from English. On the mean-normalised shape, scored under both models rather
than one:

| reference | P(D ≥ body) under it | under random | ratio |
|---|---|---|---|
| Pride and Prejudice, 5,361 sentences | 0.028 | 0.938 | **33 : 1 for random** |
| the LP author's own 92 sentences | 0.793 | 0.915 | **1.2 : 1 — no power** |

So the honest range is **3:1 to 33:1 leaning to random**, and the loud number depends on
Austen standing in for the LP's register.

**Tested, September 2026, and it does not stand in.** Across ten English registers
(`sentence_length_across_registers.py`) the sentence-length CV runs **0.645 to 1.068**,
mean 0.848 ± 0.120. The body's 0.972 is **z = +0.66** — ordinary — and its mean span of
19.6 blocks sits inside a register range of 16.0 to 32.8. On the mean-normalised shape,
the body against all ten pooled gives **D = 0.095, P = 0.134**, so English is **not
rejected**; random placement gives D = 0.064, P = 0.580. The ratio is nearer 4:1 than
33:1, and the dispersion evidence is gone entirely. The register-matched control cannot confirm it
— 92 sentences resolve nothing — though it does support the reference *value*, since the
author's own dispersion (0.738) agrees with Austen's (0.771).

A section mixture would inflate dispersion innocently and does not: 9.2% of variance is
between the nine sections, and the within-section CV is 0.956 against the pooled 0.972.
The 13 short spans driving it are spread over 7 sections and 13 pages, not clustered.

## Austen is a poor model for this register — a second retraction

Every "predicted +0.75" in this file is Austen's pooled figure with the body's joining
model applied. Stratifying shows Austen's profile runs the **opposite way** to the
author's:

| stratum | Austen | the LP author |
|---|---|---|
| 3–6 | +0.35 ± 0.08 | +2.20 ± 0.42 |
| 7–14 | +0.67 ± 0.06 | +0.90 ± 0.34 |
| 15+ | **+1.08 ± 0.05** | **+0.20 ± 0.53** |

Austen rises with span length; the author falls — **and ten registers show the rise is
the English norm.** All ten rise from +0.87 at 3-6 blocks to +1.25 at 15+, so it is the
*author* who is atypical, and his fall rests on nine spans at 15+ (1.8σ below the register
mean). **This retraction is itself withdrawn**: Austen's shape was never the problem, one
book's worth of it was.
Austen's composition happens to match the body's (46.7% vs 49.6% at 15+) while its shape
does not match the author's, so the pooled benchmark looked more authoritative than it
was. Every Austen-based sigma in this file should be read with that discount; the
author-versus-body strata above are the load-bearing comparison.

## Why joining does not explain it



This was the first thing to rule out and it needed measuring rather than asserting.
The body joins units of ≤2 runes at q ≈ 0.40 (`short-units-are-written-joined.md`).
Joining is **not** neutral for this statistic: it removes short units, the interior cell
holds more of them, so it lifts the interior mean further and shrinks the gap.

Running the joining model forward on Austen at its fitted rate:

| | interior mean | final gap |
|---|---|---|
| Austen, untouched | 4.16 | +1.00 ± 0.04 |
| joined, q = 0.40 | 4.60 | **+0.79 ± 0.04** |
| joined, q = 0.70 | 4.95 | +0.59 ± 0.04 |
| **the LP body** | **4.49** | **−0.21 ± 0.18** |

Joining at the fitted rate reproduces the body's interior mean (4.60 against 4.49) — a
check the model was never fitted to pass — and still predicts +0.79. The observation sits
**5.5σ** below that. A rate of 0.70, far above fitted, does not reach it either.

## The two marks are the same glyph, which the transcription hid

The author's mark is written `.` and the body's ④, and the changeover falls exactly at
the solved section's edge — pages 0–14 carry 87 `.` and no circled numeral, pages 15–72
carry 182 circled numerals and no `.`. That looked like it might be a convention change
masquerading as a finding, so `experiments/what_the_marks_are.py` audits it against the
repository's second transcription.

The two files are identical except for this one mark. **All 46 disagreements are clean
④ ↔ `.` swaps**, ④ plus `.` totals 228 in both, and ⑬, ③, ⑩ agree exactly everywhere. So
`.` means "a dot mark whose count was not recorded" and ④ means "confirmed four dots";
page 55 carries both in the same file, which rules out `.` being a pooled rendering.

This makes the comparison **stronger, not weaker**. Pages 0–14 carry 87 marks of the ④
class and not one ⑬, ③ or ⑩, so the author reference is pure four-dot rather than a
mixture, and the body's ④ row is the exact like-for-like test:

| | marks | gap vs interior |
|---|---|---|
| the author, ④ class | 87 | **+1.28 ± 0.28** |
| the body, before a ④ | 136 | **−0.32 ± 0.20** |
| | | **z = −4.65** |

Within the body the glyphs disagree, as earlier work on the dot-counts predicted: ④ carries
the anomaly at −5.34σ against the joined-English prediction, ⑬ reads +0.05 ± 0.39 on 25
blocks. That was recorded here as an underpowered cell; **it is the wrong population.**
`the-thirteen-dot-closes-a-section.md` shows ⑬ is a structural mark sitting at section
breaks (median 9 runes to the nearest `$`, against 429 for ④) and standing immediately
before the `&` marker 15 times in 31, where ④ does so 0 times in 141. The two are
different kinds of mark, so ⑬ was never a counter-example to a sentence-level result.

**The mark rate differs 2.3×**, needing no reference text: one mark every 32.1 runes on
pages 0–14 against every 72.2 in the body, z = +5.02. Consistent with longer sentences
and equally consistent with the mark meaning something else there, so it decides nothing
alone.

## The long block is not displaced — it is absent

One of the surviving readings says the marks sit somewhere other than the true sentence
end. If they are merely **displaced**, English's long final block should still be there
at a different offset. `experiments/the_long_block_is_nowhere.py` searches the whole
neighbourhood:

| offset | ten registers | the LP body | z |
|---|---|---|---|
| −4 | +0.01 ± 0.07 | +0.11 ± 0.26 | +0.36 |
| −3 | −0.02 ± 0.11 | −0.20 ± 0.22 | −0.72 |
| −2 | −0.24 ± 0.07 | −0.14 ± 0.22 | +0.45 |
| **−1** | **+1.19 ± 0.23** | **−0.27 ± 0.24** | **−4.42** |
| +1 | −0.71 ± 0.23 | +0.22 ± 0.27 | +2.64 |
| +2 | −0.14 ± 0.18 | +0.30 ± 0.25 | +1.44 |
| +3 | −0.06 ± 0.12 | +0.44 ± 0.26 | +1.78 |
| +4 | −0.01 ± 0.08 | −0.23 ± 0.24 | −0.86 |

The body's **largest** value anywhere is +0.44 at offset +3, against +1.19. Every
displacement variant scored against that lengthening fails: at the sentence end −4.42,
one block early −2.70, one late −4.14, two late −4.35, two early −2.63.

**So the long block is absent from the neighbourhood, not moved within it.** The three
surviving readings now say one thing between them: *no sentence ends at or near a mark.*

That sits oddly beside the spacing, which is ordinary prose-sentence scale — mean 19.6
blocks, CV 0.972, both inside a ten-register range. Units of sentence size whose edges
are not sentence edges.

The +1 cell's z = +2.64 is **not** an anomaly: English dips there on short opening
function words, the LP register does not dip at all, and the author is flat there too
(`which_edge_is_anomalous.py`).

*Scope*: the profile needs spans of nine blocks or more for the offsets to stay distinct,
leaving 97 of the body's 148 marks. The −1 cell over all spans reads −0.29 ± 0.20 and
agrees.

## Confounds measured and cleared

| confound | result |
|---|---|
| marks concentrated on pages with short blocks | page-matched, jackknifed over 54 pages: **−0.21 ± 0.17** |
| marks sitting at line ends, where layout truncates | mark-final blocks are line-final 21% against a 6% base rate, but the gap is the same in both strata (−0.23 mid-line, −0.07 at a line end); line-position-matched: **−0.19 ± 0.18** |
| transcription annotation lines (`3258-3222-…`) clearing the sentence-initial flag | dropped; they carry no runes and sit between a mark and the next block |
| pooling unlike marks | 4-dot carries it (137 blocks, +0.16 ± 0.23 on the two-rune odds); 13-dot is consistent with English at −0.22 ± 0.58 but has only 26 blocks |

## Encipherment is not what severs the link

The tidiest account of the anomaly would be that the body's marks were added to text
nobody could read. `the-scribe-ignored-the-blocks.md` shows the copyist worked
mechanically — he keeps words whole when ruling lines on plaintext (z = +5.60) and not at
all on ciphertext — so a scribe punctuating enciphered runes at arbitrary intervals would
produce exactly what the body shows.

**The book tests it and refutes it.** Ten of the author's sixteen solved pages are
enciphered, and their plaintext is known:

| group | spans | gap vs interior |
|---|---|---|
| plaintext pages | 26 | +1.48 ± 0.44 |
| enciphered: monoalphabetic | 30 | +1.31 ± 0.37 |
| enciphered: interrupted Vigenère | 18 | +1.11 ± 0.67 |
| **all enciphered** | **49** | **+1.21 ± 0.33** |
| ten English registers | | +1.19 ± 0.28 |
| **the body** | 133 | **−0.29 ± 0.20** |

The enciphered pages keep the link — their +1.21 sits on top of the plaintext pages' +1.48
and the ten-register +1.19, and **3.89σ above the body**. So whoever marked the author's
enciphered pages knew where the sentences were: the marks went in before or during
enciphering, not afterwards by someone reading runes.

That removes the mechanism that made reading 2 comfortable. It survives, but it can no
longer lean on the marks having been added blind to ciphertext, because the same book
does the opposite on pages of the same kind.

It also joins a pattern: `joining_is_not_preparation.py` found the short-unit joining does
not track cipher difficulty either. Two independent conventions change at page 15 and
neither tracks encipherment — which is what `one-production-break-at-page-fifteen.md`
concluded from the line measure.

## Three channels say the plaintext is ordinary English

The register escape is closed from three independent directions, which is what makes the
anomaly hard rather than merely odd:

| channel | result |
|---|---|
| **word lengths** | the author's own distribution with a third of the short units merged fits at P = 0.83; smooth cutting laws are rejected with two free parameters (`blocks-are-still-words.md`) |
| **function-word content** | depletion — a list or invocation register — fits at χ² 63.9 against joining's 20.2 (`does_the_author_ever_join.py`) |
| **lag-5 structure** | the body's 0.0494 ± 0.0047 against a ten-register plaintext 0.0558 ± 0.0054, attenuated by the preventer: predicted 0.0525, **z = −0.47** (`d5_across_registers.py`) |

d5 is the only key-free window onto the plaintext — two positions five apart inside a
block share alphabet and base, so they coincide exactly when the plaintext does — and it
says English prose. The earlier version of that test used a single book; ten registers
give 0.0558 ± 0.0054 and the verdict is unchanged at every plausible skip rate.

So the body is English prose with a normal complement of short function words, and its
sentence-final words still do not lengthen at the marks.

## What this leaves

Three readings, none yet eliminated:

1. ~~**The body's plaintext does not lengthen its sentence-final words.**~~ **EXCLUDED,
   September 2026** (`which_edge_is_anomalous.py`). This is the register escape, and the
   book closes it. The LP author's own sentence-final lengthening is **+1.32 ± 0.26**,
   sitting on top of a ten-register English mean of **+1.17 ± 0.27** (z = +0.42). So a
   register explanation needs the body to be a different register from the front matter,
   which the block-length evidence denies
   (`blocks-are-still-words.md`, `short-units-are-written-joined.md`).

   The same comparison settles the **other** edge in the opposite direction. Ten registers
   show a sentence-initial dip of −0.66 ± 0.26; the body reads +0.07 ± 0.23 — but **so does
   the author**, at −0.01 ± 0.27. The missing initial dip is an LP-register property, not a
   body anomaly: English's dip comes from sentences opening on short function words, and
   the LP opens on imperatives — `BELIEUE NOTHNG`, `TEST THE CNOWLEDGE`, `FIND YOUR TRUTH`.
   This also means the initial edge cannot discriminate whether the marks open or close,
   since there is no dip there for either arrangement to disturb.
2. **The circled numerals are not sentence marks.** Then the sentence-initial match
   against the author is a coincidence. Hard to hold given that control.
3. **A block adjacent to a mark is not a word** — it is a cipher-cut remainder, or the
   cipher pads to a boundary at a sentence end. This predicts a gap of zero and the
   observation is −0.21 ± 0.18.

   *The LOCAL form is excluded, September 2026* (`does_a_mark_split_a_unit.py`). If a mark
   falls inside a unit and splits it, the blocks either side are two halves of one thing:

   | | splitting | independence | observed |
   |---|---|---|---|
   | mean of (before + after) | ≈ 4.5 | ≈ 8.9 | **8.71 ± 0.25** (z = **+17** vs split) |
   | var(sum) / 2·var(block) | ≈ 0.5 | 1.0 | **0.904 ± 0.099** (z = **+4.07** vs split) |
   | correlation across the mark | strongly − | 0 | **−0.097, P = 0.21** |

   All three say two ordinary independent blocks, and blocks two apart across a mark give
   r = −0.048 (P = 0.54), so nothing is cut across a wider span either. What survives is
   only the **global** form — that no block anywhere is a word — which is not a claim
   about marks and belongs to `blocks-are-still-words.md`, where smooth cutting laws are
   rejected with two free parameters and joined words fit with one.
4. **The marks open rather than close.** A circled numeral that labels the verse
   *following* it terminates nothing, so the block before it is mid-sentence and flat by
   construction — while the block after it still starts a unit of text, which is why the
   control passes. This explains both cells at once and is the most economical reading
   on the table.

**The profile changes the standing between the readings.** Reading 4 now accounts for
every cell at once: if the mark opens a verse and verses run on grammatically, the unit
before it is mid-span (flat, observed −0.21), the unit after it starts a verse but need
not start a sentence (weak or no dip, observed +0.07), and spans come out at sentence
scale. Reading 3 fits the −1 and +1 cells equally well. **Reading 2 is now the one the spacing
favours**, reversing what this file said before: the gaps between marks are
over-dispersed for sentence ends and sit exactly on a memoryless process. If the marks
are not at sentence ends, nothing about the plaintext needs to lengthen before them and
the whole anomaly dissolves.

Reading 4 has a problem the others do not: the inventory. If these were verse numbers
there would be many distinct numerals, spread. There are four, and 4-dot alone is 139 of
174. That is the shape of punctuation, not of numbering. It also predicts a *diluted*
sentence-initial effect rather than a full one, since a verse need not start a sentence —
and the body's initial cell is indeed weaker than the author's (−0.07 ± 0.21 against
−0.33 ± 0.24), though at z = +0.83 that is not evidence.

Reading 3 sits against `blocks-are-still-words.md`, which read the marginal length
distribution as words rather than cuts. The two are compatible more easily than they
look: that file is explicit that what it excludes is a **natural cutting rule**, not cuts
in general, and rests its case on parsimony. A rule that is word-shaped in its marginal
but mechanical at a sentence edge is exactly the unnatural rule it declines to exclude.
So this result does not overturn it — it names the kind of rule that would have to hold.

## How to falsify this

- **Find a register that behaves like the body.** Any English corpus whose
  sentence-final gap is ≤ 0 after joining kills reading 3 and rescues reading 1. Austen
  is one book; a wider sweep is cheap and has not been run. Liturgical and aphoristic
  registers are the ones to try, since the LP's own author is aphoristic — though note
  he runs *stronger* than Austen, not weaker, which is the wrong direction for this
  escape.
- **More marks.** 166 final blocks give ±0.18. The full book beyond page 56 adds few.
  Going below ±0.10 would need a source of sentence marks this transcription does not
  have.
- **Replicate the +2 cell.** It is the only unexplained positive in the profile and it
  is currently post-hoc. Page 57 onward and the marks-file transcription are the places
  to look for independent spans.
- **Predict the final block's length distribution under reading 3.** If final blocks are
  remainders of a cutting rule, their lengths should be *exactly* the interior
  distribution, with no residual shape. The full distribution is already close
  (mean 4.28 against 4.49) but a shape test has not been run.

## Status

**Status**: open, narrowed to three readings. Reading 1 — the register escape — is
**excluded**: the author's own sentence-final lengthening (+1.32 ± 0.26) matches ten
English registers (+1.17 ± 0.27) while the body reads −0.29 ± 0.20. The anomaly is
present in every span-length stratum at −2.3σ to −4.4σ. Pooled, the author-versus-body difference is −6.1σ, but
stratifying by the span length the mark closes shows it is **−5.7σ at 3–6 blocks, −2.2σ
at 7–14, and −0.6σ at 15+** — absent in the stratum holding half the body's spans. The
Austen benchmark is retracted as a register model: its profile runs opposite to the
author's. The mark spacing excludes mechanical placement at 6.7σ. It is **not** over-dispersed —
across ten English registers the sentence-length CV runs 0.645–1.068 and the body's 0.972
is z = +0.66 — and on shape English is not rejected (P = 0.134 pooled), so the earlier
3:1-to-33:1 lean against the marks falling at sentence ends narrows to about 4:1. `sentences_do_not_end_long.py`,
`profile_around_a_mark.py`, `what_the_marks_space_like.py`, `what_the_marks_are.py`, `sentence_length_across_registers.py`,
`the_gap_depends_on_span_length.py`.

## Related

- `block-lengths-have-a-hole-at-two.md` — records the withdrawn rubricated-titles lead
  and, in its place, the finding that the heavy marks do fall at sentence-initial
  positions. That is what made this test possible.
- `short-units-are-written-joined.md` — the joining model and its fitted q = 0.40.
- `blocks-are-still-words.md` — the marginal-distribution result, and the source of the
  "natural cutting rule" qualification this leans on.
- `the-cipher-does-not-restart.md` — the marks mean nothing to the cipher, so whatever
  they are, they are the scribe's.
- `separators-are-the-cipher-unit.md`, `separators-are-not-word-boundaries.md`.
