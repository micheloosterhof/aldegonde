# Hypothesis: Affine Autokey

## Claim

The cipher uses an affine autokey: C[i] = a*P[i] + b*C[i-1] mod 29, where a
and b are constants, adding a multiplicative component to standard autokey.

## Status

**Status**: unresolved

## Mechanism

The standard additive autokey is generalized with a multiplication: both the
plaintext contribution and the feedback are scaled by constants a and b. Since
29 is prime, all non-zero values of a and b have multiplicative inverses, so
the cipher is invertible.

Under this model, C[i] = C[i+1] requires a*(P[i+1] - P[i+2]) = 0 mod 29.
Since 29 is prime and a != 0, this means P[i+1] = P[i+2]: doublets in the
ciphertext correspond to doublets in the plaintext. The doublet suppression
would then reflect the natural English/runeglish plaintext doublet rate.

## Evidence for

- The multiplicative component makes cryptanalysis harder while preserving
  the autokey structure
- 29 being prime ensures clean field arithmetic
- Plaintext doublet rate in runeglish might plausibly be around 0.68%

## Evidence against

- The doublet-causing condition (plaintext doublet) is different from the
  standard autokey identity-element condition. Need to verify whether the
  natural runeglish doublet rate actually matches 0.68%.
- More parameters (a, b) without additional evidence pointing to specific
  values

## Scripts

- Compute the expected doublet rate in runeglish-encoded English text to check
  if ~0.68% is plausible.

## Verdict

Unresolved. An interesting generalization but the key test is whether
runeglish plaintext naturally has a ~0.68% doublet rate.
