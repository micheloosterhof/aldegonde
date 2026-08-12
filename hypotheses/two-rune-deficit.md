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
- **Transcriber inattention / random separator loss.** Loss that ignores word
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

## Mechanism: open, and NOT identifiable from word lengths

Three candidates. No length statistic separates them.

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
- **Settling the mechanism requires a statistic that is not a function of word
  length.** The length family is exhausted. The live lead is the mark geometry:
  the `.` marks align with quoted spans (p = 1.5e-7) while failing English
  sentence semantics (z = +5.86, `word-length-keystream-and-boundaries.md`
  section C), which constrains what unit they delimit without reference to any
  histogram or external corpus.

## Scripts

- `experiments/short_word_reference.py` — the external reference and the
  transliteration-convention calibration.
- `experiments/absorption_model.py` — random vs selective loss, the register/merging
  head-to-head on both bases, the bootstrap caveat, and the autocorrelation check.
- `experiments/short_word_deficit.py` — the original anatomy: per-section
  homogeneity, drift, and the segmentation-convention bounds.

## Related

- `word-length-keystream-and-boundaries.md` — the boundary-authenticity question
  this observation sits inside.
- `quote-span-boundaries.md` — the mark alignment that keeps candidate 2 alive.
- `length-clocked-walk.md` — the clock this does not damage, and the 2-rune
  verifier it does.
- `contraction-cribs.md` — runeglish contraction conventions.
