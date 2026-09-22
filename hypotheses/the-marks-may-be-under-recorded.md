---
type: hypothesis
---
# The Body's Marks May Be a Thinned Sample of What the Scribe Wrote

## The claim

One parameter ties together two facts that have sat unconnected: the body's mark **rate**
is 2.3× below the author's, and its mark **spacing** is over-dispersed for sentence ends.
If the transcription records only a fraction p of the marks the scribe wrote, an observed
span is a sum of Geometric(p) true spans, so the mean scales as 1/p and

    CV²(observed) = p·CV²(true) + (1 − p)

**p is fitted from the mean alone.** The dispersion and the distribution shape are then
predictions, not fits.

## What it gets right

Taking the author's own spacing as the truth, the mean gives **p = 0.402**.

| | predicted | observed |
|---|---|---|
| CV of span length | 0.904 | 0.972 ± 0.145 (z = +0.47) |

The CV is a weak test — English at 0.771 and random placement at 0.970 both sit within
about 1.5σ of the observation, so it separates nothing. The **shape** does better.
Mean-normalised, against a reference built from 40 draws of each model:

| model | D from the body |
|---|---|
| the author's spacing, as written | 0.115 |
| **under-recorded at p = 0.40** | **0.059** |
| English (Austen, joined at q = 0.40) | 0.118 |
| marks placed at random | 0.071 |

Closest of the four, with English the furthest. (The accompanying P values are not
comparable across rows — each model's null has its own spread, and the author's 92 spans
resample widely — so the D column is the one to read.)

## What it does not explain, which is the point

If the marks are a thinned sample, then a mark that **is** recorded is still a true
sentence end. The block before it should therefore carry the full English sentence-final
lengthening, whatever p is. `sentences-do-not-end-long.md` measures **−0.21 ± 0.20**
against a joined-English prediction of +0.75.

**Under-recording predicts no dilution of that profile at any p.** It covers the rate and
the spacing and is silent on the thing that actually needs explaining. It is a tidier
account of two secondary facts, not a solution to the anomaly.

The escape — that the lost marks are lost *selectively*, in a way that also flattens the
edge profile — is not falsifiable from this corpus and is not proposed.

## How to falsify

- **The rate is explained by register instead.** If the body's plaintext simply runs
  longer sentences than the front matter's aphoristic pages, no marks are missing and
  p = 1. The block-length evidence says the two share a register
  (`blocks-are-still-words.md`), but sentence length is not word length and nothing
  measures it directly.
- **A second transcription.** `what_the_marks_are.py` shows the master and the marks file
  differ only in how they resolve dot counts, never in whether a mark is present, so both
  would have to have dropped the same marks. That is evidence against under-recording
  being a transcription artifact and for it being the scribe's own inconsistency, if it
  is real at all.

## Status

**Status**: **WITHDRAWN**, one day after it was proposed
(`experiments/sentence_length_across_registers.py`). Both facts it was built to explain
turn out to need no explaining.

Measured across **ten** English registers rather than Austen alone, sentence length in
blocks has CV running **0.645 to 1.068**, mean 0.848 ± 0.120. The body's 0.972 ± 0.145
sits at **z = +0.66**, and one register exceeds it. Its mean span of 19.6 blocks is
ordinary too, against a register range of 16.0 to 32.8.

So the spacing is not over-dispersed and the rate is not low — the *author's* pages are
short because they are aphoristic ("A WARNNG.", "WELCOME.", "SOME WISDOM.") at 7.86
blocks a span. **p = 1.** The falsification route this file named — "the rate is explained
by register instead" — is the one that held.

The machinery below stands as a correct treatment of a thinning process; there is just
nothing here for it to explain.

`experiments/are_the_marks_under_recorded.py`.

## Related

- `sentences-do-not-end-long.md` — the anomaly this does not reach.
- `the-thirteen-dot-closes-a-section.md` — the mark inventory it assumes.
