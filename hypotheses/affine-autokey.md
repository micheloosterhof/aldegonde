---
type: hypothesis
---
# Hypothesis: Affine Autokey

## Claim

The cipher uses an affine autokey: C[i] = a*P[i] + b*C[i-1] mod 29, where a
and b are constants, adding a multiplicative component to standard autokey.

## Status

**Status**: disproved

## Mechanism

The standard additive autokey is generalized with a multiplication: both the
plaintext contribution and the feedback are scaled by constants a and b. Since
29 is prime, all non-zero values of a and b have multiplicative inverses, so
the cipher is invertible.

Under this model, C[i+1] = C[i] requires a*P[i+1] + b*C[i] = C[i], i.e.
P[i+1] = a^-1 * (1 - b) * C[i] mod 29: a ciphertext doublet forces ONE
specific plaintext value determined by the history, with no correspondence
to plaintext doublets. (P[i+1] = P[i+2] is only forced conditional on a
preceding doublet — it characterizes triplets, not doublets.) For any
fixed (a, b) the forced value is hit at roughly the average letter
frequency, ~1/29 = 3.45%.

## Evidence for

- The multiplicative component makes cryptanalysis harder while preserving
  the autokey structure
- 29 being prime ensures clean field arithmetic

## Evidence against

- **Preceding-rune split disproof**: For fixed C[i-1] = c, C[i] = a*P[i] + b*c
  mod 29, which is an affine transformation of P[i]. Affine transformations are
  permutations and preserve IOC. So each group's IOC should match English IOC.
  Measured: mean IOC 0.0354, indistinguishable from random. See
  `disprove_autokey_split.py`.
- **Doublet rate disproof**: a doublet requires P[i+1] to hit the single
  forced value a^-1 * (1 - b) * C[i], predicting a doublet rate of
  ~1/29 = 3.45% for an untuned key. Observed: 0.66% — a ~5x deficit,
  independent of the split test.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Definitive disproof.

## Related

- `ciphertext-autokey.md` — General disproof applies here.

## Verdict

Disproved. Affine autokey is a single-layer ciphertext autokey with a fixed
relationship between C[i-1], P[i], and C[i]. The preceding-rune split test
rules it out, and the doublet rate rules it out independently (predicted
~3.45%, observed 0.66%).
