# Hypothesis: Additive Stream Cipher with No-Repeat Keystream

## Claim

The ciphertext is produced by adding a keystream to the plaintext:
C[i] = P[i] + K[i] mod 29, where the keystream K has the property that
consecutive values are never equal (K[i] != K[i+1]).

## Status

**Status**: unresolved

## Mechanism

A pseudorandom keystream (e.g. LFSR over GF(29), or a de Bruijn sequence) is
generated with the constraint that no two consecutive keystream values are the
same. Adding this keystream to plaintext mod 29 produces ciphertext with
suppressed doublets.

## Evidence for

- An LFSR over GF(29) with a primitive polynomial generates maximum-length
  sequences where consecutive values are never equal
- Produces flat output distribution (additive stream cipher with uniform
  keystream)
- Doublet suppression arises naturally from the keystream constraint

## Evidence against

- The suppression rate depends on the interaction between plaintext statistics
  and the keystream constraint. It is unclear whether this produces the specific
  0.68% doublet rate observed.
- Does not produce the clean "all doublets map to identity element" algebraic
  property seen under autokey models
- Requires knowledge of the specific PRNG to test or break

## Scripts

None yet. Testing would require hypothesizing a specific PRNG construction.

## Verdict

Unresolved. Plausible mechanism but hard to test without knowing the specific
keystream generator. The lack of a clean algebraic signature makes it harder to
confirm or deny than the autokey hypothesis.
