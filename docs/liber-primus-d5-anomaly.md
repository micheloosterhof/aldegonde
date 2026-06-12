# A Word-Boundary-Aware Statistical Anomaly in the Unsolved Liber Primus

*Shareable summary, 2026-06. Full technical writeup:
`hypotheses/within-word-d5-coincidence.md`. Reproduction:
`experiments/within_word_d5.py`.*

## Claim

In the unsolved Liber Primus ciphertext, runes **five positions apart within
the same word** match each other significantly more often than chance, while
runes five positions apart **across word boundaries** match at exactly the
random rate. This is only the second confirmed deviation from randomness in
the unsolved corpus (after the well-known doublet suppression) — and like the
doublets, it interacts with word structure.

## The numbers

All numbers are on the clean corpus: the **12,956 runes / 2,973 words** of
genuinely unsolved text, excluding the solved AN END page and the plaintext
Parable that are bundled into common transcriptions.

- Within-word pairs (k, k+5): **102 matches / 2,073 pairs = 4.92%** vs the
  1/29 = 3.45% expected of random ciphertext. Exact binomial P = 3e-4.
- Cross-word pairs at the same distance: 377/10,878 = **3.466% — exactly
  random**. The effect exists only inside words.

## Why the p-value can be trusted

Scanning statistics until something fires produces false "anomalies", so the
load-bearing test is a permutation null that keeps the published rune stream
**byte-for-byte intact** — preserving all of its correlations — and only
shuffles where the word boundaries fall (each section's word-length sequence
is shuffled, then the stream is re-cut). 10,000 permutations: null
76.5 ± 7.9 matches, observed 102, **p = 0.0014**.

Running the identical test at every distance d = 1..8, *only d=5 fires*
(next best: d=4 at p = 0.036; correcting for the 7-distance scan still
leaves p ~ 0.01). The effect is positive in 8 of 9 sections and spread
across 91 distinct words — not one section, not a few freak words, not
transcription-file contamination.

## The smoking-gun sub-pattern

Nine words contain a repeated **bigram or trigram at distance exactly 5** —
the shape `XY···XY`:

```
ᛋᛞᛝᚷᛚᛋᛞᛝ     S·D·NG·G·L·S·D·NG        (full trigram repeat)
ᚹᛡᛠᚱᚫᚹᛡᛞᚪᚦ   W·IA·EA·R·AE·W·IA·D·A·TH
ᚾᚪᛠᚩᚪᚾᚪᚦᚷᚩ   N·A·EA·O·A·N·A·TH·G·O
ᛈᛟᛄᚪᛝᛈᚦᛈᚪᛝ   P·OE·J·A·NG·P·TH·P·A·NG  (halves match at 3 of 5 positions)
ᛝᛈᚩᚪᚣᛝᛈᛋ     NG·P·O·A·Y·NG·P·S
ᛠᚣᛈᛟᚦᛋᚣᛈ     EA·Y·P·OE·TH·S·Y·P
ᚢᛈᛋᚦᛁᚳᛈᛋᛁᚹ   U·P·S·TH·I·C·P·S·I·W
ᛖᛋᛇᚦᚦᛖᛋ      E·S·EO·TH·TH·E·S
ᚹᛒᛗᚱᚾᛗᚻᛗᛁᚾᚪᛞ W·B·M·R·N·M·H·M·I·N·A·D  (two isolated matches)
```

Uniform-random expectation: 1.5 such words. Permutation null: 2.8 ± 1.6.
Observed: **9** (p = 0.0019).

## What it could mean

Any position-independent stream cipher (the model the unsolved LP otherwise
perfectly resembles) makes these events vanishingly rare. The natural
reading is that the keystream becomes *locally stationary at distance 5
within a word* — e.g., per-word key material with a length-5 period — so
repeated plaintext fragments ("ing…ing", "th…th") leak through as repeated
ciphertext fragments.

Notably, the naive version (per-word key of half the word's length) is
**excluded**: it predicts the same excess at d = L/2 for every even length,
and d=3/L=6, d=4/L=8, d=6/L=12 are all normal. Whatever the mechanism, it is
specific to distance 5. It must also coexist with everything else we know:
flat unigram distribution, x5.2 doublet suppression, no period, no key reuse
at any alignment, and random autokey split tests in both directions (see
`hypotheses/cryptodiagnostics-page0-58.md`).

## Caveats

This is a verified statistical anomaly (p ~ 1e-3 under a conservative null),
not a break. The honest next steps:

1. Check that an independent transcription reproduces the same 102 pairs
   (transcription-error control).
2. Derive which word-keyed mechanisms quantitatively reproduce both the
   4.92% rate and the doublet suppression together.

## Reproduction

```bash
pip install -e .
python experiments/within_word_d5.py        # every number above
python experiments/lp_cryptodiagnostics.py  # the full battery that surfaced it
```
