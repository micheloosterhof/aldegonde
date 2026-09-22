---
type: hypothesis
---
# The Body's Sentences Do Not End on a Long Unit

## The claim

In English the last word of a sentence is a content word and runs long. The body's
blocks do not. The block before a circled numeral runs **0.21 runes shorter** than the
body's own interior blocks, where every reference text runs **0.8 to 1.5 runes longer**.

This is the first positional evidence bearing on whether the body's blocks are words.

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

## The marks sit at prose sentence density

New, and nothing had checked it. Units between consecutive marks:

| | units per span | median |
|---|---|---|
| **the LP body** | **17.2** | 13 |
| Austen, joined at q = 0.40 | 17.5 | 14 |
| Austen, raw | 19.2 | 15 |
| the LP author's own pages | 7.9 | 6 |

The body's marks partition it at ordinary prose sentence spacing — **once its own
joining model is applied**, which is the second check that model passes without having
been fitted to it (the first is the interior mean, below). This is the strongest
evidence that the marks are sentence-scale units at all, and it is what makes reading 2
hard to hold.

It also does not match the author's own solved pages at 7.9. Those pages are aphoristic;
the body's marks are spaced like prose.

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

## Confounds measured and cleared

| confound | result |
|---|---|
| marks concentrated on pages with short blocks | page-matched, jackknifed over 54 pages: **−0.21 ± 0.17** |
| marks sitting at line ends, where layout truncates | mark-final blocks are line-final 21% against a 6% base rate, but the gap is the same in both strata (−0.23 mid-line, −0.07 at a line end); line-position-matched: **−0.19 ± 0.18** |
| transcription annotation lines (`3258-3222-…`) clearing the sentence-initial flag | dropped; they carry no runes and sit between a mark and the next block |
| pooling unlike marks | 4-dot carries it (137 blocks, +0.16 ± 0.23 on the two-rune odds); 13-dot is consistent with English at −0.22 ± 0.58 but has only 26 blocks |

## What this leaves

Three readings, none yet eliminated:

1. **The body's plaintext does not lengthen its sentence-final words.** Possible, but
   both available English references do, including the book's own author, and his
   effect is the stronger of the two.
2. **The circled numerals are not sentence marks.** Then the sentence-initial match
   against the author is a coincidence. Hard to hold given that control.
3. **A block adjacent to a mark is not a word** — it is a cipher-cut remainder, or the
   cipher pads to a boundary at a sentence end. This predicts a gap of zero and the
   observation is −0.21 ± 0.18.
4. **The marks open rather than close.** A circled numeral that labels the verse
   *following* it terminates nothing, so the block before it is mid-sentence and flat by
   construction — while the block after it still starts a unit of text, which is why the
   control passes. This explains both cells at once and is the most economical reading
   on the table.

**The profile changes the standing between the readings.** Reading 4 now accounts for
every cell at once: if the mark opens a verse and verses run on grammatically, the unit
before it is mid-span (flat, observed −0.21), the unit after it starts a verse but need
not start a sentence (weak or no dip, observed +0.07), and spans come out at sentence
scale (17.2). Reading 3 fits the −1 and +1 cells equally well. Reading 2 is the one the
span density hurts: arbitrary marks would not land at 17.2 units.

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

**Status**: open. The sentence-final anomaly is 5.0–5.5σ against the joined-English
prediction depending on the baseline, and is the one solid cell. The sentence-initial
control is **equivocal, not passing** — corrected here. The span-density match is new
and independent. `experiments/sentences_do_not_end_long.py`,
`experiments/profile_around_a_mark.py`.

## Related

- `titles-are-just-sentence-initial.md` — established that the marks are sentence marks,
  which is what makes this test possible and supplies its control.
- `block-lengths-have-a-hole-at-two.md` — the joining model and its fitted q.
- `lengths-say-words-not-cuts.md` — the marginal-distribution result this is in tension with.
- `separators-are-the-cipher-unit.md`, `block-lengths-are-detached.md`.
