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

## Related

- `cryptodiagnostics-page0-58.md` — the full battery this emerged from;
  also documents the word-aligned repeated phrase ᛞᛄᚢ-ᛒᛖᛁ (the other
  word-state lead).
- `position-within-word.md`, `word-level-autokey.md` — the open word-aware
  mechanism families this constrains.
- `doublet-spacing-poisson.md` — the other confirmed anomaly.

## Verdict

Verified anomaly. The unsolved Liber Primus ciphertext is not
boundary-blind: distance-5 coincidences — and specifically repeated
bigrams/trigrams at distance 5 — cluster inside words at p ~ 1e-3 under a
null that preserves the entire rune stream. Together with the word-aligned
repeated phrase, this is direct statistical evidence that the cipher carries
**word-scoped key state with a distance-5 (or 5-periodic) regularity**. The
next steps are out-of-sample checks (independent transcription, the d=10
tail) and deriving which word-keyed mechanisms quantitatively reproduce
both the 4.92% rate and the doublet suppression.
