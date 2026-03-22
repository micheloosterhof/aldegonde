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

- **Preceding-rune split disproof**: For fixed C[i-1] = c, C[i] = a*P[i] + b*c
  mod 29, which is an affine transformation of P[i]. Affine transformations are
  permutations and preserve IOC. So each group's IOC should match English IOC.
  Measured: mean IOC 0.0354, indistinguishable from random. See
  `disprove_autokey_split.py`.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Definitive disproof.

## Related

- `ciphertext-autokey.md` — General disproof applies here.

## Verdict

Disproved. Affine autokey is a single-layer ciphertext autokey with a fixed
relationship between C[i-1], P[i], and C[i]. The preceding-rune split test
rules it out.
