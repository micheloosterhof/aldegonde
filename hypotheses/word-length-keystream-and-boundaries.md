# Word-Length Keystream & Boundary Authenticity

Two probes of the one confirmed open channel — the word lattice (boundaries
+ lengths), which is transmitted as readable plaintext metadata.
(`experiments/word_lattice.py`, June 2026.)

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

**Status: unresolved.** The unsolved word-length sequence is flatter than
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
pages. (An earlier claim here — "'.'-density varies four-fold across
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
