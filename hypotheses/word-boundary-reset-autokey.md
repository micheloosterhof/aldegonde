---
type: hypothesis
---
# Hypothesis: Word-Boundary-Reset Autokey

## Claim

The cipher uses an autokey that resets its state (primer) at each word
boundary, so each word is encrypted independently.

## Status

**Status**: disproved

## Mechanism

An autokey cipher where the feedback chain restarts at each word. Each word's
first rune is encrypted with a primer value (which could be fixed, derived from
the previous word's last ciphertext rune, or determined by some other rule).

## Evidence for

- ~~Cross-boundary doublets are extra-suppressed~~ — corrected: the old
  "27 vs ~116 expected" compared against the 3.45% chance rate, which just
  restates the GLOBAL suppression at boundary positions. Cross-word
  doublets (23 of the clean corpus's 86) are proportional to opportunity,
  and the seam (0.0079) and within-word (0.0063) figures are statistically
  one rate measured on two tables (z=0.87, p=0.38, pooled 0.0066). The
  suppression is boundary-blind; there is no
  special word-boundary behavior. See `doublet-marker-rune-ea.md` and
  `length-clocked-walk.md`.
- Word boundaries are clearly preserved, so the cipher is word-aware

## Evidence against

- **Within-word split test disproof**: Positions 2+ within each word were
  grouped by their preceding ciphertext rune C[i-1]. Under per-word autokey
  with any fixed TR, each group should have English-like IOC (0.055-0.067).
  Measured: mean IOC 0.0353, random. This rules out per-word autokey with any
  TR, exactly as the continuous autokey split test does.
- **All primer variants random**: Fixed primer (all 29 values), previous word's
  last rune, first rune of word as primer — all produce IOC ~0.035.
- The fundamental issue: any cipher where P[i] = f(C[i-1], C[i]) is killed by
  the split test, whether continuous or per-word.

## Scripts

- `experiments/lp_deep_analysis.py` — Analyzes within-word vs cross-boundary
  doublet rates.

## Verdict

Disproved. The within-word split test shows random IOC (0.0353) for the
non-first positions of each word. Per-word autokey with any standard TR is
eliminated by the same mechanism that kills continuous autokey.
