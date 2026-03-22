# Hypothesis: Monoalphabetic Substitution

## Claim

The unsolved sections use a simple monoalphabetic substitution cipher (one
fixed rune-to-rune mapping for the entire text).

## Status

**Status**: disproved

## Mechanism

Each plaintext rune is replaced by a fixed ciphertext rune according to a
substitution key: C[i] = key[P[i]]. The key is a permutation of the 29-rune
alphabet.

## Evidence for

- Monoalphabetic substitution is the simplest classical cipher and a natural
  first hypothesis
- Word boundaries are preserved, which is consistent with a letter-level
  substitution

## Evidence against

- **Flat distribution**: Monoalphabetic substitution preserves letter
  frequencies. English (even in runeglish encoding) has non-uniform letter
  frequencies, but the ciphertext is perfectly uniform. A monoalphabetic cipher
  cannot flatten the distribution.
- **Single-letter words**: There are 324 single-letter words distributed nearly
  uniformly across all 29 runes. In English, single-letter words are almost
  exclusively "a" and "I". A monoalphabetic cipher would map these to at most 2
  rune values, not 29.
- **IOC**: The observed IOC of 0.0345 matches random (1/29). English runeglish
  text should have a significantly higher IOC under monoalphabetic substitution.

## Scripts

None needed. The statistical properties rule this out directly.

## Verdict

Disproved by multiple independent statistical tests. The uniform distribution
and dispersed single-letter words are each individually sufficient to eliminate
this hypothesis.
