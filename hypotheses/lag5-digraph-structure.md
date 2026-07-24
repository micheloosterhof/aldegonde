---
type: observation
---
# Finding: Lag-5 Paired-Match Structure

## Claim

The unsolved ciphertext contains a genuine, globally significant excess of
*paired* lag-5 coincidences: positions i with C[i] = C[i+5] occur in pairs
separated by exactly 1 or exactly 4, far more often than chance. Equivalently,
consecutive non-overlapping 5-grams agree in their (1st, 2nd) positions or in
their (1st, 5th) positions more often than they should.

## Status

**Status**: confirmed (characterization)

This is a statistical property of the ciphertext, not a cipher hypothesis.
Any valid cipher hypothesis must now explain it (alongside the constraints in
`README.md`).

## The numbers

Let M[i] = [C[i] == C[i+5]] over the 12,956-rune unsolved corpus.

| Statistic | Observed | Expected | Significance |
|-----------|----------|----------|--------------|
| Sum of M (mono lag-5 matches) | 479 | 446.6 | +1.5 sigma |
| Mono matches outside paired events | 422 | 444.6 | -1.1 sigma |
| Match pairs at separation d=1 | 29 | 17.7 | +2.7 sigma |
| Match pairs at separation d=4 | 28 | 17.7 | +2.4 sigma |
| Match pairs at d=2,3,5..25 | flat | — | all within noise |
| Joint T(5) = d1 + d4 pairs | 57 | 30.7 +/- 6.5 | local z = +4.1 |
| T(5) split-half | 28 + 29 | — | stable |
| Global Monte Carlo, max T(L) over L=2..50 | — | median 45 | **p ~= 0.01** |

The monographic lag-5 excess (+1.5 sigma) is entirely accounted for by the
paired events: outside them, mono matches are at chance. The phenomenon is
purely about pairs.

Plain digraphic kappa (the d=1 component alone, 29 vs 15.4, +3.5 sigma) is
NOT globally significant by itself. (The two expectations for the same
observed 29 are two nulls: 15.4 is the unconditional uniform digraph rate,
12,950/29² — the figure in `README.md` — while the table's 17.7 conditions
on the observed 479 mono matches, 479·478/12,950; both are correct for
their question.) It is also not globally significant — a max over lags 2..150 in null text
reaches +3.47 about 38% of the time, and lag 129 scores +3.78 in the real
text. The significance comes from the joint d=1 + d=4 statistic, which
survives max-over-lags correction at p ~= 0.01 and replicates in both halves.
Caveat: the pattern family (separations {1, L-1}) was chosen after seeing the
data; the d=4 margin was measured after d=1 flagged, but it is an orthogonal
component and landed exactly on the complementary separation 5-1=4.

## Re-assessment (fresh look, family-blind)

A re-examination without the hand-picked pattern family
(`experiments/lag5_freshlook.py`; key numbers below):

- **Family-blind 2D scan**: over ALL 174 cells (lag L = 2..30, separation
  d = 1..6), the top two cells of the entire grid are (5,1) = 29 and
  (5,4) = 28 — both at lag 5. Monte Carlo asking only "does any lag have
  two cells jointly >= (29,28)" gives p ~= 0.033. This is the fairest
  global significance: roughly 1-in-30 of being noise, weaker than the
  earlier family-chosen p ~= 0.01.
- **Cluster decomposition**: maximal clusters of lag-5 matches (gaps <= 4):
  observed sizes {2: 59, 3: 8, 6: 1} vs null {2: 50, 3: 7, 4: 1}.
  Three-clusters are AT CHANCE — earlier remarks about '(1,4) chains' carry
  no significance. The excess is ~20 extra isolated two-match objects at
  separations exactly 1 or 4, plus one extraordinary size-6 cluster (the
  image-verified page-50 SDNG repeat; p ~= 4% alone). Removing that cluster
  leaves d1 = 27, d4 = 26 — the signal is not one passage.
- **Locality**: corpus-wide, not a section-4 artifact: T5 z = +3.67 with
  section 4 excluded, +2.28 with sections 4 and 8 both excluded.
- **Delta-histogram caveat**: at lag 5 the full delta distribution is
  uniform (chi2 24.2, df 28) and delta = 0 (479) TIES with delta = 23 (479)
  with delta = 22 just behind (477). The monographic excess is not even the
  top bin of its own histogram. The anomaly is exclusively the PAIRING of
  matches at separations 1 and 4; every monographic statistic is ordinary.

Bottom line after the fresh look: a modest, corpus-wide, image-verified
pairing anomaly with fair-test significance ~ 1-in-30. Strong enough to
keep on the books, not strong enough to build castles on.

**Image-verified**: the highest-value events (the chained page-50 cluster
and the densest pocket-1 events on page 16) were checked glyph-by-glyph
against the source page scans (rtkd/iddqd) and all match the transcription
— see `transcription-verification.md`. The structure is in Cicada's ink,
not transcription noise.

## Spatial distribution

- Per-section lag-5 digraph kappa: section 4 (positions 3612..5506, LP pages
  ~15-22) carries z = +3.84 on its own (8 hits vs 2.2); section 8 is +1.82;
  all others are within noise. Within sections 4+8, lag 5 tops the whole lag
  spectrum (+3.81).
- Two loose pockets inside section 4: positions ~3715-3975 and ~5324-5495
  (sliding-window z up to +4.0). Matches inside pockets are scattered
  (gaps 1..38, no contiguous runs), with several gaps of exactly 29 noted
  but not significant.
- No mod-5 phase preference anywhere: the pattern is translation invariant.
- ~~Events freely cross word boundaries~~ — **corrected, see the
  word-boundary reconciliation below**. All 29 d=1 digraph values are
  distinct; no repeated rune values drive the effect.

## Word-boundary reconciliation (July 2026)

An independent analysis (`within-word-d5-coincidence.md`) found the same
+32 lag-5 match excess concentrated **within words**, contradicting the
boundary-blindness claimed above. The joint test neither analysis had run
(`experiments/lag5_word_boundary.py`) classifies all 479 matches by
(paired at separation 1 or 4 vs isolated) x (within-word vs across-word),
with a per-section word-length permutation null (10,000 shuffles of the
word-length sequence over the byte-identical rune stream):

| matches | within | across | total | within under null | p |
|---------|--------|--------|-------|-------------------|-----|
| paired (in a {1,4} event) | 27 | 79 | 106 | 16.9 ± 4.1 | 0.014 |
| isolated | 75 | 298 | 373 | 59.5 ± 6.8 | 0.018 |
| total | 102 | 377 | 479 | 76.5 ± 7.8 | 0.001 |

Both components are word-boundary-aware; "events freely cross word
boundaries" is **falsified**. Per pair event: 9 of the 29 d1 events are
entire in-word digraph repeats — sitting in the eight `XY···XY` words
listed in `within-word-d5-coincidence.md` (the SDNG trigram word carries
two overlapping events) — vs 2 one-side and 18 outside. For d4
events the both-within cell is structurally near-empty (an event spans 10
positions, longer than almost every word): 1 both-within, 9 one-side, 18
outside. That geometry is why the d4 face genuinely reaches across
boundaries and made the original boundary-blind reading look plausible.

Resolution: the pairing structure and the within-word excess are two faces
of ONE word-aware phenomenon, overlapping in the nine in-word digraph
repeats, not two separate anomalies and not a contradiction. Count-wise
the excess lives inside words (across-word match count is exactly at
chance); placement-wise the {1,4} pairing extends across boundaries.
Mechanism constraint update: whatever produces the lag-5 structure sees
the word boundaries.

## Mechanisms ruled out by the chase

- **Period-5 polyalphabetic (any 5 alphabets)**: would put the mono lag-5
  kappa at plaintext IoC (~1.7 normalized, tens of sigma). Observed 1.073.
- **Plaintext autokey with 5-symbol feedback**: C[i]=P[i]+P[i-5] makes mono
  lag-5 matches equal plaintext lag-10 coincidences (~6%). Observed 3.7%.
- **Ciphertext autokey with depth-L feedback, any tabula recta, L=1..8**:
  splitting C[i] by C[i-L] must yield permuted-plaintext groups with IoC
  ~1.7. Measured mean group nIoC: L1=1.026 (doublet artifact), L2..L8 all
  0.99-1.01, flat. Extends the depth-1/2 disproof in
  `ciphertext-autokey.md` to depth 8.
- **Fixed-grid seriation / columnar structure of width 5**: would impose a
  mod-5 phase on events. None observed.
- **Locally period-5 keystream patches** (key stuck repeating for a
  stretch): would make pocket matches contiguous runs at ~6% density.
  Pocket matches are scattered singletons and pairs.

## The two faces have DIFFERENT origins: d1 is plaintext, d4 is not (July 2026)

An earlier draft here proposed a "walk + copy overlay" composite. That is
**retracted**: a deterministic copy `C[i]=C[i-5]` destroys the information
of the current plaintext rune `P[i]` (the copied position carries zero new
information), so it is not a cipher operation. The only
information-preserving version is a copy that fires exactly where
`P[i]=P[i-5]` — but then it is not a separate mechanism at all: under the
walk's `g^5=id`, positions 5 apart in a word already share the alphabet, so
`P[i]=P[i-5]` gives `C[i]=C[i-5]` automatically. The "copy" IS the echo.

### The three distance-5 patterns (consolidated)

There are three lag-5 repeat shapes, and each has a different status:

| shape | pattern | scope | ciphertext | plaintext | status |
|-------|---------|-------|-----------|-----------|--------|
| single | `x····x` | within-word | IoC 1.43 | IoC ~1.60 | **match — echo** |
| adjacent bigram | `xy···xy` (d1) | within-word | 29 pairs | 3.7x baseline | **match — morphology** |
| frame | `x···yx···y` (d4) | mostly cross-word | 28 pairs | below chance | **residual — unexplained** |

The single and adjacent-bigram shapes fit inside a word and are the *same*
phenomenon: real runeglish repeats single runes and bigrams at distance 5
(morphemes, affixes), and the walk's `g^5=id` echo passes them through.
(One standing caveat on the echo rows: the echoed runes are S-dominated —
`rune-s-lag5-echo.md`, p=2.4e-6 — which a value-randomizing base would not
produce; "match" here means the rates match, not that the rune-identity
question is closed.) The
frame shape spans 10 positions — longer than almost every word — so it is
inherently cross-word (its both-within cell is structurally near-empty, see the
word-boundary reconciliation above), and it is NOT present in plaintext, so the
echo cannot produce it. Details below.

The MONOGRAPHIC half is already established: the within-word
`P[i]=P[i+5]` coincidence in real runeglish (IoC ~1.60 on Gutenberg prose;
6.0% on solved LP plaintext) matches the LP ciphertext echo (IoC 1.43, CI
[1.15,1.72], contains 1.60) — see `d5-partial-alphabet-leak.md` and
`per-word-related-alphabets.md`. So single-rune lag-5 repeats are known to
be plaintext passing through the walk echo. The open question this test
adds is the PAIRING layer: are the {1,4} pairs present in the runeglish
plaintext's own lag-5 self-matches? Measured on 55k real runeglish words
(`experiments/plaintext_lag5_pairing.py`, within-word, morphology-shuffle
null):

| separation | real plaintext | shuffled null | verdict |
|---|---|---|---|
| d1 (repeated bigram at 5, `XY···XY`) | 1232 (3.7x baseline) | 493 (1.9x) | REAL morphology |
| d4 ((1st,5th)-of-5 frame) | 238 (0.7x baseline) | 187 | ABSENT (below chance) |
| d2/d3/d5 baseline | ~336 | ~262 | — |

So:
- **The d1 face is explained.** Real English/runeglish repeats bigrams at
  distance 5 (morpheme and affix repetition); the walk's echo passes those
  through as `XY···XY` ciphertext with no extra mechanism and no lost
  information. This is the coherent, overlay-free account, and it predicts
  the nine in-word d1 events (eight `XY···XY` words) of
  `within-word-d5-coincidence.md`.
- **The d4 face is NOT a plaintext feature** — real runeglish has d4 *below*
  chance — so the walk echo cannot produce it. The (1st,5th)-of-5 frame
  pairing remains genuinely unexplained.

This is sharper than the retracted composite: it localizes the real
residual anomaly to d4 specifically, and shows d1 needs nothing beyond the
walk. Open caveats: LP's ciphertext has d1 ~= d4 (29 vs 28) whereas
plaintext has d1 >> d4, so the partial leak (`d5-partial-alphabet-leak.md`)
must damp d1 toward d4 while SOMETHING lifts d4 from nothing — the two must
meet in the middle, and only the d1 half has a mechanism. The
cross-word component of the test uses concatenated dictionary words (random
adjacency), so only the within-word rows are load-bearing.

## The d4 anatomy: no wiring equations (July 2026)

The hope that the d4 events could become cross-word key equations under
the walk is closed (`experiments/d4_frame_anatomy.py`). Reading a lag-5
match as an ALPHABET coincidence forces Π(g^(a_v)σ) = g^m across its b
crossed boundaries; per leg:

- b=1 is **impossible** (σ ∉ ⟨g⟩, `sigma-power-step.md`) — and 29 of the
  56 legs (21 of 28 events) cross exactly one boundary, so most of the d4
  face cannot be alphabet-coincidence structure at all.
- b=2 legs carry no free information: geometry forces the relation
  σ g^a σ = g^(a+2) identically (distance 5 makes t = a+2 a tautology —
  do NOT re-derive "σ² = g²" from the event list; only the middle-word
  length class a is data).
- The direct per-cell test — mono lag-5 match rate by (b, middle-class)
  geometry, far more powerful than the 28 events — shows NO active
  relation: every b=2 cell sits at 1/29 (z = +0.5..+0.8, no
  concentration; the a=0 cell where σ²=g² would predict rate 0.058 is at
  0.0415, z = +0.63), b=1 is at chance as required, and only b=0 shows
  the known echo (+3.7).
- Event geometry matches the random-position null in every dimension
  (b-distribution 11/29/16 vs 8.9/31.7/14.6; both-legs-explainable
  events 7/28 vs 5.4 expected).

Net: the d4 excess has no geometric, mechanical, or key-equation handle.
Given it is also below chance in plaintext and family-blind p ≈ 0.033,
the parsimonious reading is a count excess compatible with scan noise;
it stays on the books as unexplained but is no longer an attack surface.

## What could explain it (open)

The constraint for future hypotheses: a mechanism must generate consecutive
5-grams agreeing in (1st,2nd) or (1st,5th) positions ~85% above chance,
concentrated in (but not exclusive to) section 4, while leaving every other
statistic in `README.md` flat — including doublet suppression and zero
triplets. Tested since via `experiments/mechanism_fingerprint.py`, all
negative:

- Bifid fractionation periods 5/7/10: period 5 couples lag-5 strongly but
  with the wrong shape (all separations d=1..4 elevated, mono kappa 1.45 vs
  observed 1.07) and fails doublets/IoC. See `bifid-fractionation.md`.
- Word-structure correlation: events ignore 5-letter words, word starts,
  and word positions entirely (nulls matched on all four measures).
- Lag-5-tapped lagged-Fibonacci keystreams (taps {1,5}, {4,5}, {2,5}), with
  and without output doublet-avoidance: no d=1/d=4 excess.
- Output-avoidance OTP (the only mechanism matching the base fingerprint):
  no d=1/d=4 excess.
- Reversed text (`experiments/unit5_telex_tests.py`): the d1..d4 counts are
  identical, but this is mathematically forced — equality matches are
  reflection-symmetric and pair separations are preserved — so direction
  tests carry no information about this structure.
- 5-bit telex framing: lag-5 pairs show no Hamming-distance structure under
  the canonical index encoding (all |z| <= 1.5), and the doublet-avoidance
  redraws are Hamming-uniform. No evidence of bitwise mechanics, with the
  caveat that the rune-to-code assignment is unknown.

Note the constant 5 now appears twice independently in the corpus
fingerprint: this lag-5 window coupling, and the doublet acceptance
probability of exactly 1/5 (see `stream-cipher-no-repeat.md`). A mechanism
explaining both with one "5" would be strongly preferred.

Still open:

- Per-word or per-line cipher state where 5-rune-distant positions share key
  material as a side effect of typical word lengths (avg word ~4.4 runes).
- Section 4 having a different (or buggier) cipher than other sections.

## Scripts

- `experiments/lag5_digraph_chase.py` — full reproduction of every number
  in this file.
- `experiments/aligned_kappa_nulls.py` — the original detection.
- `experiments/d4_frame_anatomy.py` — the d4 boundary-geometry anatomy and
  the per-cell σ-relation test (all negative).
- `experiments/lag5_word_boundary.py` — the word-boundary reconciliation
  (joint paired/isolated x within/across decomposition and permutation
  nulls); core statistics live in `aldegonde.analysis.coincidence`
  (`boundary_coincidence`, `boundary_permutation_test`), unit-tested in
  `tests/aldegonde/analysis/test_coincidence.py`.

## Related

- `within-word-d5-coincidence.md` — the word-boundary face of this same
  phenomenon; reconciled above.
- `ciphertext-autokey.md` — depth-L split evidence extended here.
- `bifid-fractionation.md` — the leading untested mechanism family for this
  signature.
- `doublet-spacing-poisson.md` — the other confirmed characterization.

## Verdict

Real pairing structure: family-blind global significance p ~= 0.033 (the
earlier p ~= 0.01 used the hand-picked {1, L-1} family), split-half stable,
word-boundary-aware, in Cicada's ink. After the July 2026 split, the two
faces have different standing: the d1 face (and the single-rune echo) is
accounted for as plaintext morphology passing through a period-5
same-alphabet echo; the d4 frame face is absent from plaintext and remains
the lone unexplained lag-5 count excess — but the July 2026 anatomy shows
it carries no geometric or key-equation structure (most of its legs cannot
be walk alphabet-coincidences, and no σ-relation cell is enriched), so it
is kept as a watch-item compatible with scan noise, not an attack surface.
