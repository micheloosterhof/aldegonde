# Hypothesis: Hill Cipher per Word

## Claim

Each word is encrypted independently using matrix multiplication in GF(29).
The word's plaintext runes form a vector, multiplied by a key matrix to
produce the ciphertext runes.

## Status

**Status**: unresolved

## Mechanism

For a word of length k: C_vec = M_k * P_vec mod 29, where M_k is a k×k
invertible matrix over GF(29). Different word lengths could use different
matrices, or words could be padded to a fixed length.

Since 29 is prime, GF(29) is a field and matrix arithmetic works cleanly.

## Evidence for

- Preserves word boundaries naturally (each word encrypted as a unit)
- Creates dependencies within each word — plaintext at position i depends on
  all ciphertext runes in the word, not just adjacent ones
- Defeats the split test: C[i] depends on all P[j] in the word, not just
  a small window
- GF(29) is a field, so matrix inverses exist for all non-singular matrices
- Produces flat output if the key matrix is well-chosen

## Evidence against

- **Many key matrices needed**: Words range from 1 to 14 runes. Each length
  needs its own matrix. A 14×14 matrix has 196 entries — too many to search.
- **Single-rune words**: 324 single-rune words are encrypted as C = M_1 * P
  mod 29, which is just a monoalphabetic substitution. Single-rune words
  should concentrate on 2-3 rune values (for "a", "I"). They don't — they're
  uniformly distributed. This is problematic unless M_1 varies.
- **Doublet suppression**: A Hill cipher doesn't naturally suppress doublets.
  Adjacent runes in the ciphertext are deterministic functions of the
  plaintext vector, and there's no obvious mechanism for doublet avoidance.

## Predictions

If Hill cipher, the mapping within each word is linear over GF(29). Pairs
of words with the same ciphertext should have plaintext that's related by
the inverse matrix. Repeated ciphertext words would decrypt to the same
plaintext.

## Scripts

None yet.

## Verdict

Unresolved. The uniform distribution of single-rune words is a significant
concern — it suggests the cipher at the single-rune level is not a fixed
monoalphabetic map. The Hill cipher hypothesis may need modification
(e.g., word-position-dependent matrices).
