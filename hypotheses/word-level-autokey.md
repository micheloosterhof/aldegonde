---
type: hypothesis
---
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
- The 6-gram repeat spans aligned word boundaries, suggesting word-level
  structure (now fully characterized in `repeated-phrase-dju-bei.md`:
  p < 0.001, word-initial both times, plus a second aligned repeat
  candidate ᛁ-ᛗᛝᚣᚪ that does not clear chance on its own. The words *preceding* the two occurrences are ᛒᚠ and
  ᚳᛠᛁᛗ|ᚳᛉ — if the line-wrapped word is merged they differ in length,
  weighing against key = previous plaintext word; if line breaks are word
  boundaries, both preceding fragments are 2 runes, which this model would
  predict)
- ~~Cross-word doublets are more suppressed than within-word doublets~~ —
  corrected: measured properly, the within/cross-word doublet split is
  proportional to opportunity and the seam rate (0.0079) is slightly ABOVE
  the within-word rate (0.0063). The suppression is boundary-blind (see
  `cryptodiagnostics-page0-58.md`, `length-clocked-walk.md`)

## Evidence against

- **Additive/affine per-word variants are disproved** by the word transform
  census (`word-transform-census.md`): a constant shift, Beaufort, affine,
  reversal, rotation, or transposition per word would turn the plaintext's
  ~8,000 repeated word pairs into pairs of its transform class; every class
  sits at the doublet-corrected random baseline. Whatever the key schedule,
  the per-word transform cannot be a constant additive/affine map. Only a
  general substitution alphabet per word (or position-varying keys within
  words) survives.
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
  vs observed 0.66% and 0. No ADDITIVE word-level key schedule can suppress
  doublets, because the key is fixed before the word is emitted and an
  additive key cannot bias which plaintext bigrams collide: suppression
  then requires per-rune feedback from the just-emitted ciphertext (see
  `stream-cipher-no-repeat.md`). The additive form of the
  position-dependent loophole (`position-within-word.md`) fails the same
  constraint. The one feedback-free escape — mixed alphabets whose
  adjacent-alphabet relation is tuned to rare plaintext bigrams — is not a
  per-word-constant key and is tracked in `length-clocked-walk.md`.

## Predictions

If word-level autokey with position-within-word dependence: group runes by
(word_key, position_in_word) and check IOC.

## Scripts

None yet.

## Verdict

Disproved. Fixed-transform-per-word variants fail the within-word split
test; letterwise running-key variants fail the doublet fingerprint by 5x;
and the doublet argument holds for any ADDITIVE word-level key schedule:
the key for a word is fixed before its runes are emitted, so it cannot
avoid ciphertext doublets without per-rune output feedback. (Mixed-alphabet
schedules with a bigram-tuned step evade that argument, but those vary the
alphabet per RUNE, not per word — see `length-clocked-walk.md`.)
