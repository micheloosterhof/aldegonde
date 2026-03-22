# Hypothesis: First-Difference Cipher

## Claim

The ciphertext encodes the first differences of the plaintext:
C[i] = P[i+1] - P[i] mod 29.

## Status

**Status**: unresolved

## Mechanism

Each ciphertext rune represents the difference between consecutive plaintext
runes. Decryption recovers plaintext by computing the running cumulative sum:
P[i] = (sum of C[0..i-1] + P[0]) mod 29, where P[0] is an unknown starting
value.

A doublet (C[i] = C[i+1]) requires P[i+2] - P[i+1] = P[i+1] - P[i], meaning
three consecutive plaintext values in arithmetic progression. This is rarer
than random, naturally suppressing doublets.

## Evidence for

- Produces flat output distributions from structured input (differencing
  removes trends)
- Naturally suppresses doublets through the arithmetic-progression requirement
- Simple and elegant mechanism
- Decryption (cumulative sum) is straightforward

## Evidence against

- Does not produce the specific "all doublets map to one identity element"
  property that autokey does. Under differencing, doublets occur whenever three
  plaintext values form an arithmetic progression, regardless of which specific
  values are involved.
- The doublet suppression rate depends on plaintext statistics in a complex way
  that has not been quantified for runeglish

## Scripts

- Try decrypting by computing cumulative sums with each possible starting
  value (0-28) and check resulting text for English-like statistics.

## Verdict

Unresolved. A clean alternative to autokey that deserves computational testing.
The key distinguishing test: under autokey, doublets always decrypt to a single
specific rune; under differencing, they do not.
