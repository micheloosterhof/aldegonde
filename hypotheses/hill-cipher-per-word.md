---
type: hypothesis
---
# Hypothesis: Hill Cipher per Word

## Claim

Each word is encrypted independently using matrix multiplication in GF(29).
The word's plaintext runes form a vector, multiplied by a key matrix to
produce the ciphertext runes.

## Status

**Status**: disproved (fixed matrices by the census; per-word varying
matrices by the doublet hyperplane argument — see Verdict)

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
- **Single-rune words**: ~100 single-rune words are encrypted as C = M_1 * P
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

## Related

- `word-transform-census.md` — the identity-class census that excludes
  fixed per-word transforms, including fixed Hill matrices.

## Verdict

Disproved for the stated claim (fixed matrices, one per word length): a
fixed M_k maps repeated plaintext words of the same length to identical
ciphertext words, so the plaintext's ~8,000 repeated word pairs would
surface as identical cipher-word pairs. The identity class sits at the
random baseline and there are zero repeated cipher words of length >= 4
(`word-transform-census.md`, `cryptodiagnostics-page0-58.md`). The
uniformly distributed single-rune words (M_1 is monoalphabetic) and the
missing doublet-suppression mechanism fail independently.

Per-word VARYING matrices — the remainder the census cannot see — are
closed by the doublet argument (July 2026): a within-word doublet under
C_w = M_w·P_w is the hyperplane condition (row_i − row_{i+1})·P_w = 0,
hit at ~1/29 per adjacency for any matrix chosen independently of the
plaintext, no matter how M_w varies per word. Simulation with random
invertible matrices on the author's register gives a 3.3% within-word
doublet rate vs the observed 0.63% (`experiments/varying_hill_closure.py`).
Escaping requires matrices tuned to the plaintext bigram distribution,
which collapses the family into the known escape of README structural
constraint 1 (bigram-tuned alphabet relations — the walk family), not a
Hill cipher in any meaningful sense.
