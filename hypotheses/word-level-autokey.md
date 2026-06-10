# Hypothesis: Word-Level Autokey

## Claim

The cipher uses autokey feedback at the WORD level rather than the rune level.
Each word's encryption depends on the previous word (or some function of it),
not the previous rune.

## Status

**Status**: disproved

## Mechanism

Possible forms:
- The key for encrypting word W[i] is derived from the ciphertext of W[i-1]
  (e.g., sum of runes, length, first rune, hash)
- Each word is encrypted with a different shift/permutation determined by
  the previous word
- Within each word, a standard cipher is applied with a per-word key

## Evidence for

- Word boundaries are preserved — the cipher is clearly word-aware
- Defeats the rune-level split test because the key changes per word, not
  per rune
- The 7-gram repeat spans aligned word boundaries, suggesting word-level
  structure
- Cross-word doublets are more suppressed than within-word doublets,
  suggesting different behavior at word boundaries

## Evidence against

- If the per-word key is derived from the previous word's ciphertext, the
  within-word cipher would still be f(word_key, P[i]) for each rune, and
  the word_key is derivable from the ciphertext. So within each word, the
  cipher is a fixed transformation — and the within-word split test should
  show English-like IOC. It doesn't (IOC 0.0353, random).
- Unless the within-word cipher also has position-dependent behavior (e.g.,
  position within the word matters)
- **Doublet fingerprint** (`experiments/mechanism_fingerprint.py`):
  letterwise variants (previous plaintext word or previous ciphertext word
  cycled as running key) simulated on Markov runeglish with the real LP
  word-length sequence give doublet rates of 3.5-3.8% and 12-21 triplets,
  vs observed 0.66% and 0. No word-level key schedule can suppress doublets,
  because the key is fixed before the word is emitted: suppression requires
  per-rune feedback from the just-emitted ciphertext (see
  `stream-cipher-no-repeat.md`). This closes the position-dependent loophole
  too — `position-within-word.md` fails the same constraint.

## Predictions

If word-level autokey with position-within-word dependence: group runes by
(word_key, position_in_word) and check IOC.

## Scripts

None yet.

## Verdict

Disproved. Fixed-transform-per-word variants fail the within-word split
test; letterwise running-key variants fail the doublet fingerprint by 5x;
and the general argument holds for any word-level key schedule: the key for
a word is fixed before its runes are emitted, so it cannot avoid ciphertext
doublets, which requires per-rune output feedback.
