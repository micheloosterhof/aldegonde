# Characterization: Word-Level Transform Census (Per-Word Keyed Ciphers Excluded)

## Claim

For every classical transform family T, the number of cipher word pairs
related by a member of T is at the doublet-corrected random baseline. Since
English-like plaintext repeats words heavily, this **excludes every cipher
that enciphers each word with one transform from these families**, no matter
how the per-word key is scheduled:

| per-word cipher | repeated plaintext words become | observed excess | expected if true |
|-----------------|----------------------------------|------------------|------------------|
| monoalphabetic / codebook (any fixed map) | identical cipher words | +6 ± 3.6 | ~8,000 |
| constant additive shift per word (Vigenere-like, any key schedule) | shift pairs (w2 = w1 + c) | +11 ± 19 | ~8,000 |
| constant Beaufort per word (w -> c - w) | beaufort pairs | -33 ± 16 | ~8,000 |
| affine per word (w -> m*w + c) | affine-class pairs | +87 ± 124 | ~8,000 |
| reversal (+shift) per word | reversal pairs | +45 ± 17 | ~thousands |
| rotation per word | rotation pairs | +4 ± 5 | ~thousands |
| transposition per word | anagram pairs | -7 ± 8 | ~thousands |

The only per-word scheme the pairwise census cannot see is a **general
substitution per word** (29! possibilities) — but that survivor is excluded
separately by pattern preservation: any per-word substitution preserves the
plaintext's within-word adjacent letter repeats. The solved pages (the LP
author's own plaintext, mostly monoalphabetic so repeats are preserved)
double letters within words at **2.43%** (51/2,099 adjacencies), which
predicts ~245 within-word doublets in the cipher; observed: **64** — an
11.6 sigma deficit. Robustness: the runeglish corpus bigram table gives a
3.23% doubling rate (predicting ~326, a 14.5 sigma deficit), and every
individual solved section lies between 1.67% and 3.34% — even the most
conservative section-level baseline (1.67%, possibly Vigenere-diluted)
predicts ~168 vs 64 observed, an 8 sigma deficit. The cipher's ABA rate
(3.46%) also matches random (3.33%), not the plaintext (3.92%).

**Net result: no cipher that applies one fixed transformation per word —
additive, affine, reversal, transposition, or arbitrary substitution —
survives. The cipher state varies within words, at rune granularity.**

## Status

**Status**: confirmed (characterization)

## Method

All 2,953 cipher words (merged line-wrap convention, parable excluded),
grouped by length (3-10). For each length, count word pairs related by each
transform via canonical signatures:

- shift class: equal first-difference sequences
- beaufort: difference sequence equals the other's negated differences
- affine: differences normalized by the inverse of the first nonzero delta
- reversal+shift: differences equal the other's reversed negated differences
- rotation: minimal cyclic rotation of the word
- anagram: sorted rune multiset

Null model: 80 Monte Carlo samples of a doublet-suppressed Markov stream
(p_doublet = 0.00675) re-segmented into the real word-length structure. This
correction matters: the suppressed delta-zero probability inflates all
delta-matching classes by ~2.3% per rune, which produces spurious 4-5 sigma
flags against a naive uniform null.

## The plaintext repetition baseline

The solved pages (first 2,797 runes of the master transcription, mostly
monoalphabetic, which preserves word repetition) contain **445 repeated
identical word pairs of length >= 3 among only 698 words** (random
expectation: 0.6). The top word repeats 13 times. Scaled to the cipher's
corpus size (x17.9), LP-style plaintext implies roughly **8,000 repeated
word pairs**. Any of the per-word ciphers above would transport essentially
all of them into its class. Every class sits within ~2.6 sigma of the null.
The kill margin is two to three orders of magnitude.

## Caveats

- Assumes the unsolved plaintext repeats words like ordinary prose and that
  cipher word boundaries correspond to plaintext words 1:1. The word-length
  distribution being English-like supports both.
- A fixed Hill matrix applied per word is also excluded (it preserves word
  identity for repeated plaintext words -> identity class). A per-word
  VARYING matrix is not covered (general linear relations are a larger
  family than the scalar affine class tested).
- A general (non-additive) substitution alphabet per word is excluded by
  the doublet-preservation argument above, not by the pairwise census
  itself.

## Scripts

- `experiments/word_transform_census.py` — the census with analytic
  baselines (use the MC-corrected totals; the analytic affine/reversal
  baselines are biased by doublet suppression as described above).

## Related

- `repeated-phrase-dju-bei.md` — the one place where identical ciphertext
  DOES recur; under this census's result, that recurrence cannot come from
  a per-word additive scheme hiding word repeats (those would recur ~8,000
  times); it must be a rare state collision.
- `word-level-autokey.md` — additive per-word variants are now disproved;
  only general-substitution-per-word variants survive.
- `monoalphabetic-substitution.md`, `hill-cipher-per-word.md`.

## Verdict

Confirmed characterization. The ciphertext contains no excess of word pairs
related by shift, Beaufort, affine, reversal, rotation, or anagram
transforms. Combined with English word-repetition rates, this excludes the
entire family of per-word constant-transform ciphers (for these families)
regardless of key schedule — a large bite out of the remaining hypothesis
space. The cipher state must vary WITHIN words.
