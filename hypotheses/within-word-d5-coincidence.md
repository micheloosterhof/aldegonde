# Characterization: Within-Word Distance-5 Coincidence Excess

## Claim

Runes **five positions apart inside the same word** match each other
significantly more often than chance (4.92% vs 3.45%), while runes five
positions apart **across word boundaries** match at exactly the random rate.
The excess includes a striking sub-pattern: repeated bigrams/trigrams at
distance exactly 5 within a word (shape `XY···XY`), at ~6x the expected rate.
This is the second confirmed deviation from randomness in the unsolved
corpus, after the doublet suppression — and like the doublet anomaly it is
word-boundary-aware.

## Status

**Status**: plausible (verified anomaly; mechanism unknown)

The observation itself is verified at p ≈ 0.001 under a permutation null
(≈ 0.006 after correcting for the distance scan that found it). It is an
anomaly characterization, not a cipher mechanism; no proposed mechanism yet
explains it together with the doublet suppression.

## What was measured

All numbers are on the **clean corpus** (sections 0-9 of `data/page0-58.txt`,
12,956 runes, 2,973 words — sections 10/11 are solved/plaintext, see
`cryptodiagnostics-page0-58.md`). Words tokenized with `- . & %` as
boundaries; `/` and newlines are line wraps.

**Headline**: pairs (k, k+5) within a word: **102 matches / 2,073 pairs =
4.92%** vs 1/29 = 3.45%. Exact binomial P = 3.1e-4.

**Control**: pairs (k, k+5) straddling a word boundary: 377/10,878 = 3.466%
— exactly random (P = 0.47). Global kappa at skip 5 is normal (z = +1.6).
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
shoulder structure worth watching.

**d=6 deficit follow-up (July 2026,
`experiments/within_word_d6_deficit.py`):** the deficit reproduces (31 vs
44.5 ± 6.2, P(<=) = 0.013), is direction-consistent in both corpus halves
(z = -1.9 / -1.2), is spread over sections (8 of 10 at or below null),
and is present in both d5-hit words (0.031) and other words (0.023). On
its own, after look-elsewhere over the 7 scanned distances, it is only
p ~ 0.09 — a watched hint, not a claim. Two mechanical notes: (i) copy
events suppress a few d=6 pairs via the doublet rule (a digraph copy
makes C[k+6] = C[k+1], so a d=6 match would need the doublet C[k]=C[k+1])
but the effect is ~1 match, 10x too small; (ii) the calibrated
word-scoped copy model does NOT produce the deficit (model 42.9 ± 6.6 vs
observed 31, z = -1.8, `experiments/word_scoped_copy_simulator.py`) — if
the deficit is real, it is structure beyond the copy model. The d=1 row doubles as a sanity check:
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

Nine words contain a repeated bigram (one a repeated **trigram**) at
distance exactly 5 — uniform-random expectation 1.5, permutation null
2.8 ± 1.6:

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

## Mechanism discrimination (July 2026): copies, not key sharing

The two live readings of the excess made opposite predictions about the
**full 29-bin histogram of (C[k+5] - C[k]) mod 29 over within-word pairs**:

- key sharing (K[k+5] = K[k] inside words) leaks the plaintext lag-5
  difference distribution Q at the mixture fraction f pinned by the 0 bin
  (f ~= 0.55 given Q(0) ~= 1.8x uniform, measured on two independent
  plaintext controls: Cicada's own solved sections 6.36%, a
  frequency-weighted runeglish lexicon 6.11%);
- literal copies inflate only the 0 bin and leave the other 28 flat.

Result (`experiments/within_word_delta_mixture.py`): the histogram is
**flat off zero** (nonzero bins 0.62-1.18x uniform). A one-parameter copy
model (e = 1.52% of pairs are copies) beats the pinned key-sharing mixture
by 6.4 nats; the optimal projection test rejects pinned key-sharing at
z = +3.6 (observed T = +0.32 vs predicted +1.52 ± 0.33) with ~100% power
at that f. The stream-level generalization agrees: repeated *nonzero*
lag-5 deltas at separations 1/4 are at chance while the zero value is
elevated (`experiments/delta5_generalization.py`). Anatomy
(`experiments/within_word_match_anatomy.py`): matches have no word-edge
anchoring (start z = -0.97, end z = -0.76), the 91 hit words do not
cluster spatially (z = -0.99), and the d=10 tail is 2/88 (key 5-cycle
would predict ~6%). Full write-up: `within-word-key-sharing.md`
(status: disproved).

One sharpening of the word-boundary result falls out of the controls:
plaintext offers lag-5 repeats at ~6.1% *both* within and across words
(the rate is just the runeglish IoC), yet the LP's cross-word pairs match
at exactly 1/29. So the mechanism is not merely passively exposing
plaintext structure — **the copy rule itself is word-scoped**.

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
  explain the nine `XY···XY` words as repeated plaintext fragments.
- If the mechanism is per-word-key periodicity, words sharing a key state
  should show pairwise correlations beyond d=5 — testable by clustering the
  91 hit-words by section/page position.
- An independent transcription of the same pages should reproduce the
  same 102 pairs (transcription-error check).

## Scripts

- `experiments/within_word_d5.py` — reproduces every number above
  (exact binomials, all permutation tests, per-section breakdown, the
  word list).
- `experiments/lp_cryptodiagnostics.py` section D8 — the (length x
  distance) heatmap that first surfaced the anomaly.
- `experiments/lag5_word_boundary.py` — the reconciliation with
  `lag5-digraph-structure.md`: joint paired/isolated x within/across
  decomposition, built on the unit-tested
  `aldegonde.analysis.coincidence` boundary functions.

## Related

- `cryptodiagnostics-page0-58.md` — the full battery this emerged from;
  also documents the word-aligned repeated phrase ᛞᛄᚢ-ᛒᛖᛁ (the other
  word-state lead).
- `position-within-word.md`, `word-level-autokey.md` — the open word-aware
  mechanism families this constrains.
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

## Verdict

Verified anomaly, mechanism now narrowed. The unsolved Liber Primus
ciphertext is not boundary-blind: distance-5 coincidences — and
specifically repeated bigrams/trigrams at distance 5 — cluster inside
words at p ~ 1e-3 under a null that preserves the entire rune stream.
The July 2026 delta-histogram discrimination (see above) rules out the
key-sharing reading: the excess is **literal, word-scoped glyph copying**
(~1.5% of within-word distance-5 pairs; no additive relation, no
positional anchor, no memory), consistent with the nulls / back-reference
/ stutter family of `lag5-back-reference.md` and inconsistent with any
per-word 5-periodic key (`within-word-key-sharing.md`, disproved).
