---
type: observation
---
# Characterization: Within-Word Distance-5 Coincidence Excess

## Claim

Runes **five positions apart inside the same word** match each other
significantly more often than chance (4.92% vs 3.45%), while runes five
positions apart **across word boundaries** match at exactly the random rate.
The excess includes a striking sub-pattern: repeated bigrams/trigrams at
distance exactly 5 within a word (shape `XY···XY`), at ~3.2x the
load-bearing permutation null (9 vs 2.8 ± 1.6; ~6x against the looser
uniform baseline of 1.5).
This is the second confirmed deviation from randomness in the unsolved
corpus, after the doublet suppression — and like the doublet anomaly it is
word-boundary-aware.

## Status

**Status**: plausible (verified anomaly; mechanism unknown)

The observation itself is verified at p ≈ 0.001 under a permutation null
(≈ 0.006 after correcting for the distance scan that found it, and 0.020
family-blind over the full 124-cell battery — see "Does it pass muster").
It is an anomaly characterization, not a cipher mechanism. The length-clocked-walk
family (`length-clocked-walk.md`, `d5-partial-alphabet-leak.md`) now
reproduces it together with the doublet suppression as a period-5
same-alphabet leak — plausible, not confirmed by decryption.

## What was measured

All numbers are on the **clean corpus** (sections 0-9 of `data/page0-58.txt`,
12,956 runes, 2,928 words — sections 10/11 are solved/plaintext, see
`cryptodiagnostics-page0-58.md`). Words tokenized with `- . & %` as
boundaries; `/` and newlines are line wraps.

**Headline**: pairs (k, k+5) within a word: **102 matches / 2,073 pairs =
4.92%** vs 1/29 = 3.45%. Exact binomial P = 3.1e-4 — but that uniform
baseline is looser than it looks: it ignores the corpus's +1.5 sigma
global lag-5 kappa. The permutation null absorbs it and sits at
76.5 +/- 7.9 (3.69%), so quote 102 vs 76.5, p = 0.0014, as the headline.

**Control**: pairs (k, k+5) straddling a word boundary: 377/10,878 = 3.466%
— exactly random (P = 0.47). Global kappa at skip 5 is normal (z = +1.52).
The effect exists *only* inside words.

## The permutation test (the load-bearing evidence)

Naive binomial p-values are not trustworthy here (the cell was found by
scanning). The decisive test keeps the **published rune stream byte-for-byte
intact** — preserving every stream correlation, including any global lag-5
structure and the doublet suppression — and only shuffles each section's
word-length sequence before re-cutting it into "words". This isolates
exactly one question: *do the real word boundaries know where the distance-5
coincidences are?*

10,000 permutations:

| statistic | observed | permutation null | P(>= obs) |
|-----------|----------|------------------|-----------|
| within-word d=5 matches | 102 | 76.5 ± 7.9 | **0.0014** |
| distinct words with >= 1 match | 91 | 72.1 ± 7.3 | **0.0065** |
| bigram repeats at d=5 (`XY···XY`) | 9 | 2.8 ± 1.6 | **0.0019** |

A boundary-rotation null (slide the whole boundary pattern to a random
offset) gives the same answer (p = 0.0015).

**Distance specificity.** The same permutation test at every distance:

| d | obs | null | P(>=) | P(<=) |
|---|-----|------|-------|-------|
| 1 | 63 | 66.6 ± 3.9 | 0.85 | 0.21 |
| 2 | 250 | 245.4 ± 10.2 | 0.35 | — |
| 3 | 179 | 164.4 ± 9.9 | 0.08 | — |
| 4 | 131 | 113.5 ± 9.2 | 0.04 | — |
| **5** | **102** | **76.5 ± 7.9** | **0.0014** | — |
| 6 | 31 | 44.5 ± 6.3 | 0.99 | 0.018 |
| 7 | 30 | 24.4 ± 4.7 | 0.14 | — |
| 8 | 10 | 12.7 ± 3.5 | 0.82 | — |

Only d=5 fires (Bonferroni over the 7 scanned distances: ~0.006). d=3 and
d=4 lean mildly high, d=6 mildly **low** — possibly noise, possibly a
shoulder structure worth watching. The d=1 row doubles as a sanity check:
the permutation null already carries the doublet suppression, and the
within-word share of doublets is proportional — consistent with the known
result that doublet suppression ignores word boundaries.

**Robustness.**
- Not contamination: the solved/plaintext sections contribute 2 of the
  original 104 hits; the clean-corpus numbers above stand on their own.
- Not one section: positive in 8 of 9 contributing sections (section 2
  strongest at z = +2.5; sections 8, 7, 0, 4 next).
- Not a few freak words: 91 distinct words carry the 102 hits.

## The repeated-n-gram sub-pattern

Eight words contain a repeated bigram (one a repeated **trigram**) at
distance exactly 5, for nine adjacent-match events in total — the SDNG
trigram word carries two overlapping bigram repeats. (Uniform-random
expectation 1.5 events, permutation null 2.8 ± 1.6.) A ninth word,
listed last, has two isolated matches and no bigram repeat:

```
ᛋᛞᛝᚷᛚᛋᛞᛝ      S·D·NG·G·L·S·D·NG     trigram SDNG ··· SDNG
ᚹᛡᛠᚱᚫᚹᛡᛞᚪᚦ    W·IA·EA·R·AE·W·IA·D·A·TH   WIA ··· WIA
ᚾᚪᛠᚩᚪᚾᚪᚦᚷᚩ    N·A·EA·O·A·N·A·TH·G·O      NA ··· NA
ᛝᛈᚩᚪᚣᛝᛈᛋ      NG·P·O·A·Y·NG·P·S          NG,P ··· NG,P
ᛠᚣᛈᛟᚦᛋᚣᛈ      EA·Y·P·OE·TH·S·Y·P         YP ··· YP
ᚢᛈᛋᚦᛁᚳᛈᛋᛁᚹ    U·P·S·TH·I·C·P·S·I·W       PS ··· PS
ᛖᛋᛇᚦᚦᛖᛋ       E·S·EO·TH·TH·E·S           ES ··· ES
ᛈᛟᛄᚪᛝᛈᚦᛈᚪᛝ    P·OE·J·A·NG·P·TH·P·A·NG    3 of 5 positions match
ᚹᛒᛗᚱᚾᛗᚻᛗᛁᚾᚪᛞ  (two isolated matches)
```

Note the shape: a word that *opens* with `XY`, runs four other runes, and
repeats `XY` at position 5-6. Several of these words are 7-8 runes long, so
the repeat closes the word (`XY????XY`-like). In ciphertext this shape
requires the keystream relation at those two positions to cancel twice in a
row — vanishingly rare under any position-independent stream model.

## Interpretations to test

- **Per-word key of length 5** (or a 5-cycle in per-word key state): would
  make positions k and k+5 share a key element, so matches occur at the
  plaintext coincidence rate (~6-7%) instead of 3.45%, and repeated plaintext
  bigrams (`th···th`, `in···in`, `ed···ed`) leak as ciphertext `XY···XY`.
  Observed within-word rate 4.92% would imply only *part* of the corpus (or
  only some word lengths) behaves this way. But a fixed key length 5 should
  also produce excess at d=10 in 11+ rune words (only 92 such pairs exist —
  too few to test) and arguably interacts with word lengths in ways not yet
  derived.
- **The naive half-length-key variant is already excluded**: key length
  ceil(L/2) per word predicts excess on the d = L/2 diagonal (d=3 at L=6,
  d=4 at L=8, d=6 at L=12); those cells are all normal. The excess at L=10
  (8.2%, exact P = 2.4e-4) is the largest single cell but the effect is not
  confined to it.
- **Plaintext morphology leak**: English has repeated-bigram-at-5 structure
  (e.g. "ing...ing", "tion..tion" alignments). Any cipher that becomes
  *locally key-stationary* at distance 5 within a word would leak it.
- Whatever the mechanism, it must coexist with: flat unigrams, x5.2 doublet
  suppression with normal cross-boundary behavior, no period, no key reuse,
  and random split tests in every direction (see
  `cryptodiagnostics-page0-58.md`).

## Predictions

- Any candidate decryption should place matching plaintext runes (or a
  shared key relation) at the 102 (k, k+5) pairs, and especially should
  explain the eight `XY···XY` words as repeated plaintext fragments.
- ~~If the mechanism is per-word-key periodicity, words sharing a key state
  should show pairwise correlations beyond d=5 — testable by clustering the
  91 hit-words by section/page position.~~ **Tested negative (July 2026,
  `experiments/followup_checks.py`)**: hit-word pairs within 5/10/25-word
  windows sit exactly on the length-matched permutation null
  (z = −0.19 / +0.62 / +0.04). Hit words do not cluster; no evidence of
  shared key state between nearby words.
- ~~An independent transcription of the same pages should reproduce the
  same 102 pairs (transcription-error check).~~ Settled: the transcription
  is verified ground truth (`transcription-verification.md`); the excess
  is in Cicada's ink.

## Scripts

- `experiments/d5_profile_and_position.py` — the full d1-d12 profile with
  phases, the d10 power calculation, and the position decomposition.
- `experiments/within_word_d5.py` — reproduces every number above
  (exact binomials, all permutation tests, per-section breakdown, the
  word list).
- `experiments/lp_cryptodiagnostics.py` section D8 — the (length x
  distance) heatmap that first surfaced the anomaly.
- `experiments/lag5_word_boundary.py` — the reconciliation with
  `lag5-digraph-structure.md`: joint paired/isolated x within/across
  decomposition, built on the unit-tested
  `aldegonde.analysis.coincidence` boundary functions.

## The full distance profile, and what d10 cannot test

`experiments/d5_profile_and_position.py`, against the structure-free surrogate
of `negative-control-battery.md` (word boundaries and marks held exactly, runes
redrawn at the observed doublet rate, 400 draws).

| d | pairs | matches | rate | surrogate | z | phase |
|---|---|---|---|---|---|---|
| 1 | 10028 | 63 | 0.0063 | 0.0069 | −0.68 | 1 |
| 2 | 7199 | 250 | 0.0347 | 0.0355 | −0.33 | 2 |
| 3 | 4835 | 179 | 0.0370 | 0.0345 | +1.03 | 3 |
| 4 | 3197 | 131 | 0.0410 | 0.0346 | +2.12 | 4 |
| **5** | 2073 | 102 | 0.0492 | 0.0346 | **+3.58** | **0 (echo)** |
| 6 | 1267 | 31 | 0.0245 | 0.0340 | −1.79 | 1 |
| 7 | 713 | 30 | 0.0421 | 0.0345 | +1.11 | 2 |
| 8 | 373 | 10 | 0.0268 | 0.0342 | −0.76 | 3 |
| 9 | 192 | 5 | 0.0260 | 0.0345 | −0.66 | 4 |
| 10 | 88 | 2 | 0.0227 | 0.0332 | −0.54 | 0 (echo) |
| 11 | 35 | 1 | 0.0286 | 0.0366 | −0.26 | 1 |
| 12 | 10 | 0 | 0.0000 | 0.0335 | −0.60 | 2 |

The period-5 phase pattern is visible where there is power: phase 0 carries the
echo, phase 1 (d1 and d6) is suppressed, phases 2-4 sit between. **All of that
rests on d1-d6.** From d7 the pair counts collapse — 713, 373, 192, 88, 35, 10 —
and every cell drifts to zero z regardless of what is true.

**d10 must not be cited either way.** `g^5 = id` predicts the echo recurs at
d10, and the corpus cannot check it. There are 88 pairs and 2 matches; flat
predicts 3.0 matches and a d5-strength echo predicts 4.3. The two hypotheses sit
**0.76 sd apart**, so d10 separates nothing. Reaching 2 sigma would need ~615
pairs against the 88 available — about seven times this book's supply of words
11+ runes long. A flat d10 is not evidence against the model; it is not a
measurement.

## Where the echo sits inside the word

Grouped by the pair's start position. A concentration at one offset would mean
something other than a uniform period-5 leak.

| runes | pairs | matches | rate | surrogate | z |
|---|---|---|---|---|---|
| 1 & 6 | 806 | 35 | 0.0434 | 0.0347 | +1.32 |
| 2 & 7 | 554 | 27 | 0.0487 | 0.0342 | +1.93 |
| 3 & 8 | 340 | 18 | 0.0529 | 0.0343 | +1.88 |
| 4 & 9 | 181 | 10 | 0.0552 | 0.0345 | +1.58 |
| 5 & 10 | 104 | 7 | 0.0673 | 0.0364 | +1.68 |
| 6 & 11 | 53 | 2 | 0.0377 | 0.0360 | +0.07 |
| 7 & 12 | 25 | 3 | 0.1200 | 0.0378 | +2.14 |

**No preference: it is all of them, evenly.** Homogeneity across start
positions gives chi2 = 4.89 on 8 df, **p = 0.77** — one uniform rate fits. This
reproduces the decomposition in `d5-partial-alphabet-leak.md`
(0.043/0.049/0.053/0.059, p = 0.70) under a different null.

Two consequences worth keeping straight:

- **No single position is individually significant.** The best real cells reach
  z ≈ +1.3 to +1.9. The dramatic-looking 7&12 at 0.12 is 3 matches out of 25,
  one of nine cells scanned. The d5 signal exists only in aggregate — which is
  the correct way to read a uniform leak, but it means there is no hot spot to
  attack.
- **There is no drift.** Base drift inside a word would make the echo *decay*
  as the pair starts later, since more drift accumulates between i and i+5. The
  slope is if anything positive: +0.00485 per position against a surrogate
  +0.00024 ± 0.00294, **z = +1.57** — not significant, and tested only after
  the rise was noticed in the table, so discount it further. The surrogate
  carries the same word-length structure, so the obvious confound (later
  positions exist only in longer words) is controlled and contributes nothing.

## Scope note

This file covers the two distance-5 shapes that fit inside a word — the
single-rune echo (`x····x`) and the adjacent-bigram repeat (`xy···xy`, the
eight `XY···XY` words / nine d1 events). Both are consistent with real
runeglish morphology passing through the walk's `g^5=id` echo (plaintext
~1.60 IoC / 3.7x baseline matching the ciphertext) — see the plaintext test
and the consolidated three-pattern table in `lag5-digraph-structure.md`.
(An earlier caveat here — the S-dominance of the echoed runes as possible
evidence against a value-randomizing base — is resolved: under
base-scrambling the concentration is expected-level, P ≈ 0.08-0.15; see
`rune-s-lag5-echo.md`.) The THIRD shape, the frame
`x···yx···y` (d4), spans 10 positions and is mostly cross-word, is absent from
plaintext, and remains the lone lag-5 residual — it is documented there, not
here.

## Related

- `lag5-digraph-structure.md` — the consolidated three-pattern table
  (`x····x` / `xy···xy` / `x···yx···y`) and the d4 residual.
- `within-word-key-sharing.md` — disproves ADDITIVE key-sharing for this
  excess (delta histogram flat off zero, 3.63σ): the excess is equality-only,
  consistent with the walk's mixed-alphabet echo, not an additive per-word key.
- `rune-s-lag5-echo.md` — the d=5 excess is not rune-agnostic: the rune S
  carries ~22% of it (11 vs 1.75, p=2.4e-6, Bonferroni-clean,
  distance-5-specific, within-word only).
- `cryptodiagnostics-page0-58.md` — the full battery this emerged from;
  also documents the word-aligned repeated phrase ᛞᛄᚢ-ᛒᛖᛁ (the other
  word-state lead).
- `position-within-word.md`, `word-level-autokey.md` — word-aware
  mechanism families this excess helped constrain; both are disproved,
  and the surviving word-aware family is the walk
  (`length-clocked-walk.md`).
- `doublet-spacing-poisson.md` — the other confirmed anomaly.
- `lag5-digraph-structure.md`, `docs/lag5-phenomenon.md` — an independent
  characterization of the same +32 lag-5 excess as paired events at
  separations {1,4}. **Reconciled (July 2026)** by the joint test
  (`experiments/lag5_word_boundary.py`): the two are faces of ONE
  word-aware phenomenon. Paired matches sit within words above the
  boundary-permutation null (27 vs 16.9 ± 4.1, p = 0.014) — the other
  analysis's boundary-blindness claim is falsified — and 9 of its 29 d1
  pair events are exactly the nine `XY···XY` words listed above. Isolated
  matches are boundary-aware too (75 vs 59.5 ± 6.8, p = 0.018). One
  refinement in the other direction: "the effect exists only inside
  words" is true for match COUNTS (across-word count is at chance) but
  the {1,4} pairing structure itself extends across boundaries (18 of 29
  d1 and 18 of 28 d4 events have neither match within a word; a d4 event
  spans 10 positions and cannot usually fit inside a word).

## Does it pass muster — the honest calibration (Aug 2026)

Yes, but as a **~2–3σ effect, not a high-sigma certainty**, and the exact
significance depends on how wide the multiple-testing net is cast:

- the d5 cell alone, word-length permutation null: **p = 0.0014**
- corrected for the 7 distances scanned: **~0.006**
- family-blind over the full 124-cell negative-control battery
  (`negative-control-battery.md`): **p = 0.020** — d5 is the *one* cell
  that survives everything asked of it

So the load-bearing significance is ~2.3–3σ. Three things raise it above
"marginal":

1. **Word-anchored via an internal control that needs no external
   reference:** within-word d5 = 0.0492 vs cross-word d5 = 0.0347 (exactly
   chance), a **+2.87σ** gap at the *same distance*. The cross-word cell is
   the cleanest control there is.
2. **The profile shape carries it, not the d5 magnitude.** Against flat
   chance d5 is only +3.1σ. What discriminates is the plaintext (prose)
   reference: d3 and d4 sit **5.5σ and 3.5σ below plaintext** (scrambled,
   not leaking) while d5 is only 1.4σ below (leaks) — d3/d4 are internal
   "scrambled" controls (`d5-partial-alphabet-leak.md`).
3. **Not a few freak words:** 102 matches in 91 distinct words, max 3/word.

The caveats that keep it from being a slam dunk:

- **Magnitude-limited.** Separating 102 from ~114 (plaintext) against ~71
  (chance) needs ~4× the corpus. "Period-5 confirmed" overstates it; "the
  best-supported structure in the corpus, surviving every test at 2–3σ" is
  the accurate calibration.
- **Reference-dependent.** The profile discrimination leans on the prose
  reference; d3/d4 being far below plaintext is register-robust, but the
  exact d5 reading is not reference-free.
- **Contingent on word-boundary authenticity.** The within/cross split is
  *defined* by boundaries, so synthetic boundaries could engineer the
  within-word concentration. Boundary authenticity is separately supported
  (`quote-span-boundaries.md`) but is the standing open question.

**Null-choice trap (a fifth face of the doublet-suppression trap,
`bigram-ioc.md`).** Do NOT test this with a within-word rune *shuffle*. That
preserves each ciphertext word's composition, which is *sub-random* (the
doublet suppression flattens repeats), so the shuffle baseline sits at
0.026–0.029 and makes d2/d3/d4/d5 read +4 to +5.6σ *all at once* — a
manufactured "leak at every distance." The valid nulls keep the rune stream
intact and shuffle word LENGTHS (the permutation test above), or use the
plaintext reference; both isolate the boundary/period question without the
composition confound.

## Verdict

Verified anomaly, at a calibrated ~2–3σ (see the calibration section:
p = 0.0014 for the cell, 0.020 family-blind over 124 cells). The unsolved
Liber Primus ciphertext is not boundary-blind: distance-5 coincidences —
and specifically repeated bigrams/trigrams at distance 5 — cluster inside
words under a null that preserves the entire rune stream. Together with the word-aligned
repeated phrase, this is direct statistical evidence that the cipher carries
**word-scoped key state with a distance-5 (or 5-periodic) regularity**. The
next steps are the d6 suppression (the echo's period-5 partner, see
`d5-partial-alphabet-leak.md`) and deriving which walk-family mechanisms
quantitatively reproduce both the 4.92% rate and the doublet suppression.
(The transcription is settled ground truth, and the d=10 tail is
unmeasurable at ~88-92 eligible pairs, so neither is an available check.)
