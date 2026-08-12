---
type: observation
---
# Word-Length Keystream & Boundary Authenticity

Probes of the visible metadata channel — word boundaries, word lengths,
and sentence marks. The channel is not established as readable plaintext
metadata: the '.' marks demonstrably do not carry English sentence
semantics (C), and the boundaries' sequential structure is independently
suspicious (B). (`experiments/word_lattice.py`, June 2026.)

## A. Keystream from word-length context — disproved

**Claim tested**: the keystream is a function of the local word-length
pattern (own length, position-in-word, neighbour lengths). This is
attractive because it would key the cipher from plaintext metadata the
solver can also read, and the DJU-BEI repeat's length context (2, [3,3], 2)
matches at both occurrences.

**Method**: bucket every rune by a length-context key; if runes sharing a
bucket share keystream, their within-bucket pairwise coincidence rate rises
from 1/29 toward the plaintext IoC (~0.06+).

| context key | coincidence rate (1/29 = 0.03448) | z |
|-------------|-----------------------------------|---|
| (pos, wlen) | 0.03438 | -0.85 |
| (pos, wlen, prev-len) | 0.03456 | +0.26 |
| (pos, wlen, next-len) | 0.03455 | +0.23 |
| (pos, wlen, prev, next) | 0.03473 | +0.31 |
| (pos, wlen, prev, prev2) | 0.03408 | -0.52 |

**Status: disproved (for LOCAL length-context keys).** Every bucketing
stays exactly at 1/29: the keystream is not a function of the local
word-length context (own length, position-in-word, neighbour lengths).
A schedule driven by the FULL length prefix — e.g. the running product of
`length-clocked-walk.md`, where the base depends on every preceding word
length — changes key at every word and is invisible to this bucketing, so
it is NOT excluded here. (Consistent with the word-transform census and
the J battery: the key varies at rune granularity.)

## B. Boundary authenticity — unresolved (a real but inconclusive tension)

**Question**: are the word boundaries plaintext-faithful, or synthetic? A
synthetic length sequence (placed to mimic an English length *distribution*
without sequential structure) would lack the lag autocorrelation real prose
carries.

**Measurement** (word-length autocorrelation, permutation z, lags 1-6):

| lag | unsolved (n=2953) | solved LP (n=698) | English prose (n=13512) |
|-----|-------------------|-------------------|--------------------------|
| 1 | -0.007 (z=-0.4) | **-0.086 (z=-2.2)** | **+0.056 (z=+6.5)** |
| 2 | +0.018 (z=+1.0) | **+0.092 (z=+2.5)** | **+0.021 (z=+2.4)** |
| 3 | -0.017 (z=-0.9) | +0.015 (z=+0.4) | **+0.062 (z=+7.3)** |
| 4 | +0.012 (z=+0.6) | +0.037 (z=+1.0) | **+0.062 (z=+7.4)** |
| 5 | +0.024 (z=+1.3) | +0.014 (z=+0.4) | **+0.060 (z=+6.0)** |
| 6 | -0.018 (z=-1.0) | +0.002 (z=+0.1) | **+0.049 (z=+5.9)** |

Three distinct signatures. Generic prose is positive at every lag (topic
clustering). The solved LP register shows a short-range -/+ ALTERNATION at
lags 1-2 only (function/content word alternation, no long-range drift).
(The "unsolved" column's n=2953 includes the solved AN END page's ~25
words; the clean corpus has 2,928 — a difference far too small to move
these z-scores.)

The unsolved cipher is flat at all six lags. With 2953 words, the solved
pages' lag-1 autocorrelation would surface at ~4.7 sigma if shared; it
does not. Register-matched joint test on the two informative lags (solved
vs unsolved, lags 1+2): chi2 ~ 6.6 on 2 df, **p ~ 0.036**.

**Why this is NOT yet a finding**: English word-length autocorrelation is
**register-dependent and not even a fixed sign** — generic prose is
positive (+0.06 at every lag), the solved LP koans alternate -/+ at lags
1-2 only. A flat sequence sits between them, so flatness alone cannot
prove synthetic boundaries. The register-matched joint comparison (solved
vs unsolved LP, same author/work, lags 1+2) reaches p ~ 0.036 —
suggestive, not conclusive.

**This is not a second anomaly — it follows from the 2-rune shortage (August
2026, `absorption_model.py`).** Take the solved sequence and reduce its 2-rune
population by the fitted 39%, and its −/+ signature lands on the unsolved values
at every lag:

| lag | solved | merge 39% | drop 39% | unsolved |
|---|---|---|---|---|
| 1 | −0.086 | −0.005 ± 0.032 | −0.015 ± 0.025 | −0.008 |
| 2 | +0.092 | +0.051 ± 0.025 | +0.055 ± 0.021 | +0.017 |
| 3 | +0.015 | −0.010 ± 0.031 | −0.008 ± 0.030 | −0.018 |

Note the two middle columns: **merging short words and simply having fewer of
them attenuate the autocorrelation identically**, so this statistic cannot
distinguish a merging mechanism from a register that uses fewer function words.
The useful consequence is a simplification rather than a mechanism — the flat
autocorrelation and the 2-rune deficit are ONE anomaly, not two, since the
shortage produces the flatness automatically. Only the shortage needs explaining.

**Status: reduced to the 2-rune deficit.** The sequence is flatter than
both the solved pages and generic English at every lag through 6, which
would be expected if the boundaries were placed to match a length
histogram without copying English word *order* — but the register-matched
evidence is ~2 sigma and confounded by the small solved sample.

**Per-section breakdown (July 2026,
`experiments/lattice_by_section.py`)**: the lattice is ONE homogeneous
process — every section tests as drawn from the same distribution as the
rest (KS p = 0.48-1.00), and every section deviates from the solved
register in the SAME directions: mean word length 4.31-4.60 (solved
4.01), short-word (1-2 rune) fraction 18-22% (solved 28%), sentences
14-34 words (solved 8.1), no ordering structure (per-section lag-1
autocorrelation at noise; the sec-2 z=+2.1 is 1-of-9 and positive where
the solved register is negative). No part of the corpus has a more
English-like lattice than any other.

**The short-word deficit, made explicit**: 19.3% of unsolved words are
1-2 runes vs 27.9% in the solved register — z ~ 4.7, present in every
section. Encryption cannot cause this (word lengths pass through any
rune-substitution cipher untouched), so either the plaintext genuinely
lacks a third of its function words relative to the same author's solved
writing (telegraphic/fused composition), or the boundaries are not
plaintext-faithful. This is the hardest single fact in the boundary
question, sharper than the autocorrelation lead.
This is the one assumption-questioning lead worth revisiting with a
register-matched runeglish corpus (philosophical/koan prose with word
boundaries), which the repo does not currently contain.

**Anatomy (August 2026, `experiments/short_word_deficit.py`).** Three facts
narrow what kind of deficit it is.

*It is almost entirely the 2-rune bucket.* Not "short words" in general:

| runes | unsolved | solved | difference |
|---|---|---|---|
| 1 | 3.4% | 3.9% | +0.5% |
| **2** | **15.9%** | **24.2%** | **+8.3%** |
| 3 | 24.8% | 23.7% | -1.1% |
| 4 | 17.6% | 17.8% | +0.2% |
| 5 | 10.9% | 7.5% | -3.3% |
| 7 | 7.3% | 6.3% | -1.0% |
| 8 | 5.4% | 3.4% | -2.1% |

1-rune words match. The whole gap sits at length 2, and the displaced mass
reappears at 3, 5, 7 and 8 (means 4.42 against 4.01; KS D = 0.089,
p = 1.7e-4). **That is the shape MERGING produces** — drop a separator between
a 2-rune and a 3-rune word and you lose two short words and gain one of five.

*It is uniform, not concentrated.* Every section shows it, and homogeneity
across the nine measurable sections gives chi2 = 5.91 on 8 df, **p = 0.66**.

*It does not drift.* By quarter of the book: 19.0% / 20.2% / 19.4% / 18.4%;
rank correlation of shortness with position tau = -0.008, p = 0.62.

*No segmentation convention closes it, including the extreme one.* The
transcription does merge words across line breaks — section D below establishes
that words wrap, and `experiments/boundary_verification.py` finds at least one
line ending with a separator dot the transcription omits. So the current
convention over-merges, and the question is by how much. Splitting at EVERY
line break is the opposite extreme (it cuts wrapped words into fragments, which
is wrong in the other direction) and therefore bounds the effect:

| convention | unsolved 2-rune | solved 2-rune | gap | z |
|---|---|---|---|---|
| merge lines (current) | 15.9% | 24.2% | +8.3% | +4.88 |
| words end only at `- .` | 15.5% | 24.1% | +8.6% | +5.04 |
| split at every line break | 18.7% | 25.2% | **+6.4%** | **+3.88** |

Splitting adds 2.8 points to the unsolved 2-rune rate and 1.0 to the solved —
the unsolved text does gain more, as section D's "far more mid-word page wraps"
predicts — but it closes only about a **quarter** of the gap, and the remainder
stands at z = +3.88. **Merging across line breaks cannot explain the deficit.**
That extends section D's convention-independence result from means to the
2-rune bucket specifically, which is where the whole effect lives.

(The 1-rune rate is the giveaway that the split convention is manufacturing
fragments: it triples, 3.4% to 9.6% unsolved and 3.9% to 10.1% solved, and
stays equal between the two texts. Fragments hit both sides alike.)

What remains: either the plaintext genuinely uses proportionally fewer 2-rune
function words than the solved pages — a register claim, and the 2-rune class
is dominated by THE — or a boundary artifact that is not line-break merging.
Mid-line omissions are not indicated: across 604 lines the reader never found
the transcription carrying MORE separators than the page.

**The noisy-reference caveat is now closed (August 2026,
`experiments/short_word_reference.py`).** The worry was that the solved side is
only ~700 words, so a better register reference might dissolve the gap. It does
not. English carried into runeglish over the 50,000 commonest words, weighted by
token frequency, is an independent reference that never touches the solved
sample:

| runes | unsolved | English (50k) | solved |
|---|---|---|---|
| 1 | 3.4% | 4.2% | 4.0% |
| **2** | **15.9%** | **23.7%** | **23.9%** |
| 3 | 24.8% | 20.2% | 24.1% |
| 4 | 17.6% | 16.8% | 17.5% |

The transliteration-convention objection — a converter that contracts digraphs
more eagerly than the scribe would manufacture short words — is testable without
any decrypted plaintext, because the solved pages are runeglish in the book's own
convention. The converter's English estimate and the solved rune text agree to
**0.26 points against a standard error of 1.61**. With the convention calibrated
the deficit is **z = −9.9** against the large reference, where the solved
comparison gave +4.9.

Note also what the third column shows: English and the solved pages agree at
every length, and the unsolved corpus departs from BOTH at exactly one — length
2. The displaced mass at 3 is not a departure from the solved register (24.8% vs
24.1%); only the 2-rune bucket is anomalous. So the register-corpus job is done
for this question, and it did not help: the reference was never the weak link.

**Which separators are missing: the loss is SELECTIVE (August 2026,
`experiments/absorption_model.py`).** Two one-parameter models, both fitted
against the register- and convention-matched solved pages:

| model | q | chi2 (12 df) | mean | 2-rune |
|---|---|---|---|---|
| observed (target) | — | — | 4.425 | 15.9% |
| no loss | — | 207 | 3.983 | 24.0% |
| H1 loss regardless of length | 0.15 | 106 | 4.611 | 20.5% |
| H2 2-rune word absorbed into next | 0.36 | 40 | 4.343 | 15.4% |
| H2 2-rune word absorbed into prev | 0.39 | **26** | **4.416** | **14.9%** |

**H1 is refuted** — not by chi-square, which base noise makes too permissive, but
because it cannot hit the mean and the 2-rune share together. Tuned to the mean
(q = 0.09) it leaves 2-rune at 21.8%; tuned to chi-square it overshoots the mean
to 4.61 and still sits at 20.5%. Removing separators without regard to length
takes words of every length in proportion, moving the mean while leaving the
shape alone. **This matters because random loss is the shape a transcriber's
oversights would take** — so inattention cannot be the explanation.

**H2 is shape-adequate but the mechanism is NOT IDENTIFIABLE.** Merging must
create long units (2 + L) where a register that simply uses fewer short words
cannot, so the tail ought to discriminate. It does — in opposite directions
depending on which reference supplies the base:

| base | register χ² | merging χ² | winner |
|---|---|---|---|
| solved LP (698 words) | 53 | **27** | merging |
| English (50,000 words) | **21** | 41 | register |

The solved sample sits low at length 5 (7.6% on 53 words, against 11.0% English
and 10.9% LP), which is enough to hand merging the tail whenever the solved pages
are the reference. A paired bootstrap over resampled solved bases makes merging
look robust (48/60, z = +5.3) — **that figure is misleading**, because resampling
a base captures sampling noise around its shape while preserving the shape's
systematic quirks. Reference-choice error dominates sampling error here and no
bootstrap of a single reference can see it.

Also note the solved pages are the control that embarrasses the scribal reading:
the base IS the solved distribution, so H2 asserts ~39% absorption in the
unsolved half and none in the solved half, same book, same hand.

So: the deficit is solid (ratio 0.66 vs solved, 0.67 vs English, z ≈ −10 either
way) and the mechanism is open. Candidates, none excluded by any length statistic:
a different register; separators marking a non-word unit (verse, breath, counting
— which makes the comparison against English WORD lengths a category error); or
deliberate avoidance of exposed 2-rune words, they being the crib surface, the one
merging story that fits the solved/unsolved asymmetry. **Settling it requires a
statistic that is not a function of word length.**

**On the numbers, H2 is adequate.** It hits both targets at once, and the residue is base noise:
resampling the ~700-word solved base from its own words gives chi-square a median
of 70 and a 90% range of 25–120, so **94% of draws that assume the model come out
worse than the fitted 26**. Implied scale: ~300 separators, ~10% of words.
Direction is a weak preference only (26 vs 40); the histogram does not settle
which side the short word attaches to.

Two readings were possible, and the transcription one is **CLOSED**: the
re-transcription is complete and every difference against the independent scan
read was visually inspected (August 2026). The separators are not missing from
the transcription. So:

- **The omissions are in the MANUSCRIPT** — short function words written attached
  to a neighbour, i.e. enclitic writing. The composer wrote the text as we read
  it, so **the visible word lengths ARE the composer's clock and the walk's clock
  is sound.** The "one missing separator corrupts every base after it" worry does
  not apply, and the 314M-key Quagmire sweep was correctly clocked.

What this damages instead is **cribbing on word identity**, and it does so in a
specific, exploitable way. If ~39% of 2-rune words are attached to a neighbour,
then `THE` = `ᚦᛖ` is often NOT a standalone 2-rune word but a digraph inside a
longer one. The 2-rune verifier of `length-clocked-walk.md` — decrypt the 465
2-rune words, count `ᚦᛖ` — is therefore looking in only part of the right place,
and its expected-hit range (75–108) is too high for standalone words and ignores
the attached instances entirely.

The fix is free, because the walk's within-word phase does not depend on word
length: for ANY word, `c₀ = base_w(p₀)` and `c₁ = base_w(g(p₁))`, exactly as for a
2-rune word. So a candidate key can be scored by counting `ᚦᛖ` at the START of
all 2,928 words rather than only among the 465 short ones. If absorption is into
the PREVIOUS word instead, `THE` lands word-FINALLY, where the phase is
`g^((L−2) mod 5)`, `g^((L−1) mod 5)` — still computable, just length-dependent.
Direction is unsettled (chi2 26 vs 40), so both positions should be scored. See
`experiments/the_position_verifier.py`.

**Boundary verification against the scans is inconclusive so far**
(`experiments/boundary_verification.py`). The merging shape makes a
transcription artifact worth testing directly, and the scans allow it: 491 of
604 lines (81.3%) carry exactly the transcribed separators. But 92 of the 113
mismatches are the reader merging touching runes, and of the 21 clean
disagreements — all at line edges, 19 with the image carrying MORE separators
and 0 the transcription — spot-checking two found one real omission and one
piece of marginal artwork misread as a dot. The caveat above ("cannot be fully
excluded without the page scans") is now half-answered: most lines verify, and
settling the rest needs a tighter per-page text block and a rune segmenter that
does not merge glyphs.

**If confirmed**, it would matter a lot: it would mean the boundaries are a
separate synthetic layer, the "English-like word lengths" are a histogram
match rather than real word structure, and cribbing on word identity is
futile. **If refuted**, boundaries are real and the lattice remains the
best crib surface.

## C. Sentence-mark channel fails English semantics — confirmed (~5.9 sigma)

The sharpest authenticity result (`experiments/sentence_forensics.py`).
English sentences end on content words, almost never on 1-2 letter
function words. The solved pages show this signature overwhelmingly; the
unsolved '.' marks show NONE of it:

| | sentence-final mean | overall mean | permutation z | finals 1-2 runes |
|---|---|---|---|---|
| solved LP pages (n=86 finals) | **5.56** | 4.01 | **+7.06** | **2.3%** (vs 27.9% baseline) |
| unsolved cipher (n=149 finals) | 4.19 | 4.42 | -1.21 | 20.8% (vs 19.4% baseline) |

Contrast between the two effects: **z = +5.86**. The words before '.' in
the unsolved section are statistically indistinguishable from words at
random positions — consistent across every section with >= 8 marks
(per-section final means 3.91-4.91, none elevated). Supporting facts:
"sentences" average 19.7 words (median 14, max 182) vs 8.9 in the solved
pages. (Denominator convention: the corpus has 168 '.' marks but only 149
carry a qualifying sentence-final word; 19.7 is words per qualifying
sentence, while README's 17.3-vs-8.0 figures are words per mark — same
signal, different denominator.) (An earlier claim here — "'.'-density varies four-fold across
sections and two sections have no marks" — does not hold at the
`$`-section level: all ten clean sections have marks at rates consistent
with one homogeneous Poisson process, chi2 ~ 6 on 8 df; see
`thirty-symbol-disk.md`. The variation was an artifact of smaller
counting units.)

**Conclusion: the '.' marks in the unsolved section do not mark English
sentence ends.** Either the marks are synthetic/decorative, they denote a
different unit (verse, breath, counting), or the visible segmentation is
not aligned with plaintext semantics. Unlike the autocorrelation lead in
B, this is not register-fragile: avoiding 1-2 letter sentence-final words
is near-universal in English, and the same author's solved register shows
the effect at z=+7.

**Narrowed (August 2026): the first branch is now much harder.** The
quotation marks recovered from the page scans align to these same '.' marks
— 8 of 14 quoted-span edges land on one against 0.7 expected (p = 1.5e-7,
robust to a layout confound 6.1x stronger than any on record), and '.' is
depleted strictly inside spans (1 versus 4.2, p = 0.071). Quoted speech
opens on them, closes on them, and avoids crossing them, so the marks
delimit something the plaintext respects and are not synthetic/decorative or
semantically inert. The conclusion above is unchanged — they are still not
English sentence ends — but of the three branches offered here, "a different
unit (verse, breath, counting)" is now the live one. See
`quote-span-boundaries.md`. The mixture proposal below predicts that
quote-adjacent marks are the genuine sentence ends; their final-word means
do not bear that out (4.14 versus 4.23), at n=7.

**Direction-independent (July 2026).** If the text read right-to-left, the
word AFTER each mark in file order would be the reading-order
sentence-final word and should carry the signature instead. It does not
(`experiments/mark_direction_test.py`, harness validated by reproducing
the solved-pages finals exactly, 5.56 / z=+7.0):

| | before-mark | after-mark |
|---|---|---|
| unsolved (168 marks) | 4.23, z=-1.15 | 4.38, z=-0.24 |
| solved (86 marks) | 5.56, z=+7.03 | 3.93, z=-0.34 (short 37.2% vs 27.9% baseline — the English sentence-INITIAL lean) |

Both sides of the unsolved marks look like random words, so the
no-English-semantics conclusion holds in both reading directions, closing
the "text reads backwards" loophole for this channel. (The other
statistical anomalies — doublets, lag-5, length histogram,
autocorrelation — are reflection-symmetric and carry no direction
information; reversed autokey and reversed running keys are separately
excluded.)

This materially weakens the foundational reading of the metadata channel:
of the three visible plaintext-metadata structures (word boundaries, word
lengths, sentence marks), the sentence marks now demonstrably do NOT carry
English sentence semantics, and the word-boundary sequential structure (B)
is independently suspicious at ~2 sigma. The word-length HISTOGRAM remains
English-like — exactly what a cosmetic segmentation designed to look like
language would preserve.

### What the marks ARE: layout-coupled (`experiments/mark_forensics.py`)

The '.' marks cluster strongly at line ends — **19.9% sit exactly at a
line end vs the 3.7% baseline** for '-' word marks (z = +11.3). The solved
pages show the same typographic habit (26.7% vs 5.5%, z = +8.6). Combined
with the sentence-final result this yields a sharp dissociation:

| | layout coupling ('.' at line end) | language coupling (final-word signature) |
|---|---|---|
| solved pages | present (z=+8.6) | present (z=+7.1) |
| unsolved | present (z=+11.3) | **absent** (z=-1.2) |

The unsolved marks inherit the book's typographic behavior but not the
linguistic content. Splitting the final-word test by mark position
sharpens this into a possible MIXTURE:

- **mid-line marks (n=120)**: final mean 4.03 vs 4.42 overall, z=-1.85,
  23.3% short finals — definitively no English signature (if anything the
  words before them are short);
- **line-end marks (n=29)**: final mean 4.86, only 10.3% short finals,
  z=+1.05 — weakly English-ward but underpowered.

So the marks may be two populations: a minority of genuine sentence ends
that the typesetting aligned with line ends (as in the solved pages,
where 26.7% of real sentence marks sit at line ends), plus a majority of
mid-line marks that are not linguistic punctuation. A transcription
artifact (dots conjured at visually ambiguous line ends) cannot be fully
excluded without the page scans, but it is the mid-line majority — where
dots are visually unambiguous — that carries the anomaly.

The rest of the mark process is structureless: inter-mark gaps are
roughly exponential (cv=1.11) with no autocorrelation; no prime bias in
gaps (z=-1.3), sentence word-counts (z=+1.5), or mark positions (18
prime vs 18.1 expected); block checksums uniform (rune sums mod 29
p=0.19, GP sums mod 29 p=0.70, GP-sum primality z=+0.6); doublets per
block consistent with opportunity.

## Other negatives from the same battery

- Near-repeats: zero pairs of length >= 11 with <= 2 mismatches anywhere
  (null expectation ~0). The DJU-BEI repeat is exact and unique; there is
  no population of "almost-depths" from a drifting state.
- Doublet-deleted stream: repeat census unchanged (no repeats rejoined by
  removing doublets).

## D. Convention check: mid-word PAGE breaks

Line breaks (`/`) are not word breaks — words wrap across lines — and the
same holds for **page breaks**: 46 of 57 `%` page breaks in the unsolved
file are mid-word (plus 3 of 19 `&` and 1 of 11 `$`). The correct word
segmentation ends words ONLY at `-` and `.`. Under this full merge,
applied consistently to both texts:

| convention | unsolved | solved | KS p |
|------------|----------|--------|------|
| split at line breaks | 3,344 words, mean 3.90 | 772, mean 3.62 | 9e-3 |
| merge lines only | 2,953 words, mean 4.42 | 698, mean 4.01 | 5e-4 |
| full merge (lines+pages+&) | **2,921 words, mean 4.47** | **694, mean 4.03** | **2e-4** |

Merging does NOT close the unsolved-vs-solved word-length gap — it widens
it slightly (the unsolved text has far more mid-word page wraps). The
~0.4 rune/word gap is convention-independent; the Parable (4.75) keeps it
within the author's stylistic range. All conclusions in this file are
robust under the full merge: the word-length autocorrelation stays flat
(lags 1-3, |z| <= 1.2), and the sentence-final null stays null (finals
4.20 vs overall 4.46, permutation z = -1.52, vs solved +7 sigma).

NB: `experiments/anomaly_scan.py::parse()` splits words at page breaks;
its word stats (2,953 words, mean 4.42) differ immaterially (~50 words of
2,953) from the full-merge values. No earlier z-score moves materially.

## Other checks (null)

- Doublet-containing words: length distribution matches the per-length
  doublet *opportunity* (L-1 adjacencies) — no excess at any length.
- Adjacent short-short word clustering: unsolved at chance (z=+0.18).

## Scripts

- `experiments/word_lattice.py` — all three probes.

## Related

- `repeated-phrase-dju-bei.md` — the length-context match that motivated A.
- `word-transform-census.md`, `autokey-plus-substitution.md` — rune-level
  key variation, consistent with A's negative.
