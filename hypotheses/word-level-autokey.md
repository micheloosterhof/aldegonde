# Hypothesis: Word-Level Autokey

## Claim

The cipher uses autokey feedback at the WORD level rather than the rune level.
Each word's encryption depends on the previous word (or some function of it),
not the previous rune.

## Status

**Status**: unresolved

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
  structure (now fully characterized in `repeated-phrase-dju-bei.md`:
  p < 0.001, word-initial both times, plus a second aligned repeat
  ᛁ-ᛗᛝᚣᚪ; but note the words *preceding* the two occurrences differ in
  length (2 vs 6 runes), so the key is not simply the previous plaintext
  word verbatim)
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

## Predictions

If word-level autokey with position-within-word dependence: group runes by
(word_key, position_in_word) and check IOC.

## Scripts

None yet.

## Verdict

Unresolved. Simple word-level autokey (fixed transform per word) is ruled
out by the within-word split test. But word-level autokey combined with
position-within-word dependence has not been tested.
