# Hypothesis: Word-Boundary-Reset Autokey

## Claim

The cipher uses an autokey that resets its state (primer) at each word
boundary, so each word is encrypted independently.

## Status

**Status**: unresolved

## Mechanism

An autokey cipher where the feedback chain restarts at each word. Each word's
first rune is encrypted with a primer value (which could be fixed, derived from
the previous word's last ciphertext rune, or determined by some other rule).

## Evidence for

- Cross-boundary doublets are extra-suppressed: 27 observed vs ~116 expected
  if doublets were uniformly distributed. This could indicate different autokey
  behavior at word boundaries.
- Word boundaries are clearly preserved, so the cipher is word-aware

## Evidence against

- Within-word doublets (62) and cross-boundary doublets (27) are both
  suppressed relative to random, just at slightly different rates. The
  difference could be explained by word-boundary runes having different
  frequency characteristics in English rather than a cipher mechanism reset.
- Introduces many unknown primer values (one per word), making cryptanalysis
  harder but also making the hypothesis harder to test

## Scripts

- `experiments/lp_deep_analysis.py` — Analyzes within-word vs cross-boundary
  doublet rates.

## Verdict

Unresolved. The cross-boundary doublet suppression is suggestive but not
conclusive. Needs more analysis to determine whether the suppression difference
is statistically significant beyond what English word-boundary letter
frequencies would predict.
