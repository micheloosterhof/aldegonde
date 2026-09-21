---
type: observation
---
# Observation: The 2-Rune Word Deficit (one bucket, z ≈ −10, mechanism open)

## Feature

The unsolved corpus contains far fewer 2-rune words than any reference: 15.9%
against ~24%. The departure is confined to **exactly one length class**. Lengths
1, 3, 4 and 6 match both references; length 5 disagrees between them and is
reference noise, not signal.

This is the sharpest boundary-layer anomaly in the corpus and the reason the
2-rune crib surface (`THE` = `ᚦᛖ`) cannot be taken at face value.

## Measurement

`experiments/short_word_reference.py`, `experiments/absorption_model.py`.

| runes | unsolved | English (50k) | solved LP | ratio vs solved | z |
|---|---|---|---|---|---|
| 1 | 3.4% | 4.2% | 4.0% | 0.84 | −1.7 |
| **2** | **15.9%** | **23.7%** | **23.9%** | **0.66** | **−10.2** |
| 3 | 24.8% | 20.2% | 24.1% | 1.03 | +0.9 |
| 4 | 17.6% | 16.8% | 17.5% | 1.00 | +0.1 |
| 5 | 10.9% | 11.0% | 7.6% | 1.43 | +6.7 |
| 6 | 8.6% | 8.0% | 8.7% | 0.98 | −0.3 |

Unsolved n = 2,928 words / 12,956 runes, mean 4.425. Solved n = 698, mean 4.007.

**Two independent references agree**: ratio 0.66 against the solved pages, 0.67
against English, z ≈ −10 either way.

**The transliteration convention is calibrated**, which is what makes the English
reference admissible. A converter contracting digraphs more eagerly than the
scribe would manufacture short words. This is checkable with no decrypted
plaintext, because the solved pages are runeglish in the book's own convention:
the converter's English estimate and the solved rune text agree to **0.26 points
against a standard error of 1.61**.

**Length 5 is reference disagreement, not a finding.** The solved sample sits at
7.6% on 53 words, against 11.0% in English and 10.9% in the LP — the solved pages
are the outlier there. It matters because it is enough to swing model comparisons
(see Mechanism).

## Significance

z ≈ −10 against either reference, present in every section (homogeneity
χ² = 5.91 on 8 df, p = 0.66) and without drift by quarter of the book
(19.0 / 20.2 / 19.4 / 18.4%, τ = −0.008).

Encryption cannot cause it — word lengths pass through any rune-substitution
cipher untouched — so it is a property of the plaintext or of the separator layer.

## What is excluded

- **Transcription omission.** The re-transcription is complete and every
  difference against an independent scan read was visually inspected
  (August 2026). The separators are not missing from the transcription.
  **Consequence: the visible word lengths are the composer's own clock, so the
  walk's clock is sound and the 314M-key Quagmire sweep was correctly clocked.**
- **Transcriber inattention / RANDOM separator loss.** Loss that ignores word
  length cannot hit the observed mean and the observed 2-rune share together: at
  q = 0.09 it reproduces the mean (4.381 vs 4.425) but leaves 2-rune at 21.8%; at
  q = 0.15 it overshoots the mean to 4.611 and still sits at 20.5%. Removing
  separators without regard to length takes words of every length in proportion,
  moving the mean while leaving the shape alone.
- **Line-break merging.** Splitting at every line break — the opposite extreme,
  which manufactures fragments — closes only about a quarter of the gap, leaving
  z = +3.88 (`word-length-keystream-and-boundaries.md` section B).
- **A noisy reference.** The 50,000-word English reference is independent of the
  ~700-word solved sample and lands within 0.26 points of it. Better register data
  will not dissolve this.

## A fourth candidate, and the only one that breaks the key search

**Scribal merging** — the scribe writing two words joined, AFTER encipherment — is
distinct from the three below and is not excluded by anything above. Random loss is
excluded and the transcription is verified, but a transcription can faithfully
record a join the scribe made, and selective joining at short words is exactly the
shape the deficit has.

It matters more than the other three because it is the only one that puts the walk
on a **wrong clock**: two base steps happened where every search models one.
Candidates 1 and 3 below leave the clock intact (under 3 the composer enciphered
the merged unit as one word, so one base covers it).

The test is phi5, the within-word d5 leak fraction, which counts the fraction of
distance-5 pairs lying inside a single true word — see the CLOCK section of
`d5-partial-alphabet-leak.md`. It bounds scribal merging very loosely: every
absorption rate from 0% to 100% of short words sits within 1.6σ of the observed
d5. So the threat is live and unmeasured, not refuted.

## Mechanism: open; the models tried are not separable by these statistics

Three candidates. The two that were modelled (register vs merging) reverse
with the choice of reference base, so THOSE TWO are not separable by the
histogram or the autocorrelation. That is weaker than "no length statistic
can separate them", which was not tested — a different statistic, or a
better-motivated register model, might.

1. **Different register.** The unsolved plaintext uses proportionally fewer
   articles and prepositions than the instructional prose of the solved pages.
2. **The separators mark a non-word unit** — verse, breath, counting group — in
   which case comparing against English *word* lengths is a category error. The
   quotation-mark spans align with the `.` marks (p = 1.5e-7,
   `quote-span-boundaries.md`), so the marks respect something in the plaintext,
   but not necessarily word division.
3. **Deliberate suppression of exposed short units.** 2-rune words are the crib
   surface, so the composer merged or avoided them. This is the only merging story
   consistent with the solved/unsolved asymmetry, since the solved pages were meant
   to be read. It also fits the shape better than a scribal habit would: 1-rune
   words are the easiest to write joined yet are essentially undepleted (ratio
   0.84, z = −1.7), while the crib-bearing 2-rune class is crushed.

**Why merging cannot be established.** Merging must create long units (`2 + L`)
where a register using fewer short words cannot, so the tail ought to
discriminate. It does, in opposite directions depending on the base:

| base | register χ² | merging χ² | winner |
|---|---|---|---|
| solved LP (698 words) | 53 | **27** | merging |
| English (50,000 words) | **21** | 41 | register |

The solved sample's soft length-5 cell is enough to hand merging the tail whenever
the solved pages are the reference. **A paired bootstrap over resampled solved
bases makes merging look robust (48/60, z = +5.3) and is misleading**: resampling
a base captures sampling noise around its shape while preserving that shape's
systematic quirks. Reference-choice error dominates sampling error here, and no
bootstrap of one reference can see it. When a result leans on a reference corpus,
vary the corpus, not the draw.

## Consequences

- **The flat word-length autocorrelation is not a second anomaly.** Reducing the
  solved sequence's 2-rune population by ~39% carries its −/+ signature onto the
  unsolved values at every lag (lag 1: −0.086 → −0.005 ± 0.032 against an observed
  −0.008). Merging and merely dropping those words attenuate identically, so this
  identifies no mechanism — but it collapses two boundary puzzles into one. Only
  the shortage needs explaining.
- **The 2-rune verifier is looking in only part of the right place.** If short
  words are attached rather than absent, `THE` is often a digraph inside a longer
  word, and the published expectation of 75–108 standalone hits
  (`length-clocked-walk.md`) is too high. The generalisation is free because the
  within-word phase does not depend on word length: `c₀ = base_w(p₀)` and
  `c₁ = base_w(g(p₁))` for *any* word, so word-initial digraphs can be scored
  across all 2,928 words instead of 465. Under the attach-to-previous variant
  `THE` lands word-finally at phase `g^((L−2) mod 5)`, `g^((L−1) mod 5)` — still
  computable, just length-dependent. Direction is unsettled, so score both.
- **d5 was tried as a non-length discriminator and fails, twice** (August 2026,
  `d5_unit_model.py`, `d5_clock_check.py`). Both failures are structural rather
  than statistical. On the level: merging raises the plaintext repeat rate (frequent
  letters meet across boundaries) while the straddling pairs go flat, and the two
  effects cancel to 0.0538 vs 0.0540 against an LP error of 0.0048. On the shape: a
  merged unit's straddle fraction FALLS with length, cancelling the rising chance a
  long unit contains a join, so both models predict phi5 flat in length (measured
  slope +0.011 ± 0.137). This extends the file's finding beyond length statistics —
  the first non-length statistic tried also fails to separate them.
- **The other statistics tried are all functions of word length, and none
  separates the candidates.** That is not the same as the length family being
  exhausted — only that the histogram, the tail, and the autocorrelation do not
  discriminate. The most promising untried direction is the mark geometry:
  the `.` marks align with quoted spans (p = 1.5e-7) while failing English
  sentence semantics (z = +5.86, `word-length-keystream-and-boundaries.md`
  section C), which constrains what unit they delimit without reference to any
  histogram or external corpus.

## Scripts

- `experiments/short_word_reference.py` — the external reference and the
  transliteration-convention calibration.
- `experiments/absorption_model.py` — random vs selective loss, the register/merging
  head-to-head on both bases, the bootstrap caveat, and the autocorrelation check.
- `experiments/d5_unit_model.py` — register vs merging vs blind cutting, on d5.
- `experiments/d5_straddle_prediction.py` — phi5 predicted from the straddle
  fraction with no free parameter.
- `experiments/d5_clock_check.py` — phi5 as a clock test, resolved by unit length.
- `experiments/short_word_deficit.py` — the original anatomy: per-section
  homogeneity, drift, and the segmentation-convention bounds.

## Related

- `word-length-keystream-and-boundaries.md` — the boundary-authenticity question
  this observation sits inside.
- `quote-span-boundaries.md` — the mark alignment that keeps candidate 2 alive.
- `length-clocked-walk.md` — the clock this does not damage, and the 2-rune
  verifier it does.
- `contraction-cribs.md` — runeglish contraction conventions.

## The deficit fits SELECTIVE separator loss, and rules out the uniform kind (September 2026)

If the deficit is transcriptional — separators dropped so that two plaintext words were
read as one — the loss can be modelled with a single parameter. Take the LP's own
plaintext length distribution (`lp-plaintext-register.md`, 486 words of the author's
English), draw a sequence long enough to hold the body's 12,956 runes, merge `m`
adjacent pairs, and compare the result to the body's 2,928 words.

The arithmetic fixes `m` before any fitting: the body's plaintext at the LP's own mean
of 4.04 runes would hold 3,208 words, and it presents 2,928, so **m = 280**.

| model | merges | chi2 (10 df) |
|---|---|---|
| no loss | 0 | 149 |
| uniform loss | 280 | 94 |
| **selective loss, a 2-rune word involved** | **280** | **21** |
| selective loss | 360 | 48 |
| selective loss | 440 | 137 |

**Uniform separator loss does not work.** Merging random adjacent pairs removes words
of every length in proportion and cannot deplete the 2-bucket enough; it leaves the
distribution at chi2 94. Restricting merges to pairs where one member is a 2-rune word
drops that to 21, a 7x improvement on no-loss and 4.5x on uniform loss, and the fitted
`m` lands on the 280 the mean already implied rather than being tuned to it. The
independent estimate of "~300 missing separators" recorded elsewhere agrees.

**What this is not.** chi2 21 on 10 df is p = 0.02, so even the best model is not a
good fit, and more importantly a fit is not a discriminator. Exactly the same
distribution would arise if the body's prose simply uses fewer short words than the
front matter's — which is a live possibility, since the front matter is didactic and
aphoristic and the body is not. This measurement constrains the *shape* any
separator-loss account must have; it does not establish that separators were lost.

**A test I proposed here does NOT discriminate, and is retracted.** The idea was that
a merged "word" carries an internal base change, so a within-word d5 pair spanning it
sees two alphabets and the echo should weaken with word length. Run and then simulated
(`experiments/d5_length_trend.py`): the body does show a length gradient, 1.15x chance
at lengths 6-7 rising to 1.81x at 10+, trend z = +1.68. **But the merge model predicts
no such gradient** — simulating 280 selective merges with the author's own d5 echo
gives a median trend of z = −0.23 and clears z = 1.96 in 2% of runs.

The reasoning behind the prediction was wrong. Merges put a diluted seam into words of
*every* length, not preferentially short ones, and the per-length dilution fractions
cancel against the fact that longer merged words carry more pairs. So the observed
gradient is evidence for neither reading, and anyone re-running this should not expect
it to settle anything.

## Line wraps carry at most ~20 of the 280, which weighs against the transcriptional reading

Layout gives the discriminating test that the d5 gradient could not. A transcription
drops a separator where it is hardest to see, and the overwhelmingly likeliest such
place is a **line break** — the break itself reads as a word gap, so a separator glyph
beside it is easy to miss. Authorial word choice has no reason to track line breaks.

The clean corpus holds 1,338 wraps. Only **454** fall inside a word against 817 ± 15
under random placement (z = −25): the scribe breaks lines at word boundaries, as
expected. The question is whether those 454 "words" are genuine or merges.

A merged word is two words glued, so merges hiding at wraps must inflate their mean
length. The length bias — long words are likelier to contain a wrap — is already in the
null:

| | mean length of a wrap-spanning word |
|---|---|
| observed | 5.75 |
| null | 5.69 ± 0.06 |
| **z** | **+0.95** |

No excess. And the test is sensitive:

| merges hiding there | mean becomes | z |
|---|---|---|
| 10 | 5.81 | +1.9 |
| 20 | 5.87 | +2.8 |
| 40 | 5.98 | +4.6 |
| **280** | **7.36** | **+26.6** |

**So line wraps hold at most ~20 of the 280 separators the model needs, and the full
280 is excluded at 27 sigma.** If separators were lost, they were lost mid-line, with
a visible separator glyph simply overlooked in running text — which is not how
transcription errors are distributed.

That does not close the transcriptional reading, since a mid-line loss mechanism
could exist that nobody has proposed. It does remove its most natural mechanism, and
correspondingly strengthens the plain register explanation: the body's prose uses
fewer short words than the front matter's didactic register does.

## A third line: the body's word lengths are serially independent, the author's are not

In English, adjacent word lengths are not independent — function words cluster, so a
short word tends to follow a long one. Measured as a lag-1 correlation of the length
sequence, which is key-free because per-position ciphers preserve word lengths:

| corpus | words | lag-1 correlation |
|---|---|---|
| the author's own plaintext | 486 | **−0.098** (z = −2.16 against zero) |
| the body | 2,928 | −0.009 (z = −0.46) |

The body shows none of it, on six times the data. The direct comparison is
**z = −1.83** — suggestive, not significant, and limited by the reference being only
486 words.

Merging destroys the dependence, which is consistent with the body's value. Applying
the proportional merge count (42) to the author's own sequence:

| | lag-1 correlation |
|---|---|
| unmerged | −0.098 |
| after 42 selective merges | **+0.015 ± 0.041** |
| after 42 random merges | −0.058 ± 0.040 |
| the body, for comparison | −0.009 |

So the body sits where selective merging would put it. But it is within 1.2 sigma of
the random-merge value too, so this does not separate the two merge models, and it
does not separate merging from register at all.

## Synthesis: if words were merged, the author did it, not the transcriber

Three weak lines now exist and they do not all point the same way. The length
distribution fits selective merging at ~280 sites; the lag-1 dependence is absent as
merging predicts; but line wraps — the only place a transcription plausibly drops a
separator — can host at most ~20 of those 280.

The reading that reconciles them is that **the merging is authorial orthography, not
transcription error**: the body divides words differently from the front matter,
compounding where the didactic pages separate. That produces the 2-rune deficit, the
longer mean word, and the flattened serial dependence, with no lost glyph anywhere and
no mid-line transcription failure to explain.

**This matters for more than bookkeeping.** A transcriptional loss would mean the
ciphertext word boundaries are not the boundaries the cipher used, so every key search
in this project ran on a wrong clock. An authorial difference means the boundaries are
exactly right and the clock is sound; only the plaintext's register differs from the
front matter's. The three measurements above favour the second, and the wrap bound is
the strongest of them.
