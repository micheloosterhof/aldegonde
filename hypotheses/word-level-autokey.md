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
  proportional to opportunity — the within-word rate (0.0063) and the seam
  rate (0.0079) are statistically one rate (z=0.87, p=0.38; pooled 0.0066).
  The suppression is boundary-blind (see
  `cryptodiagnostics-page0-58.md`, `length-clocked-walk.md`)

## Evidence against

- **Additive/affine per-word variants are disproved** by the word transform
  census (`word-transform-census.md`): a constant shift, Beaufort, affine,
  reversal, rotation, or transposition per word would turn the plaintext's
  ~8,000 repeated word pairs into pairs of its transform class; every class
  sits at the doublet-corrected random baseline. Whatever the key schedule,
  the per-word transform cannot be a constant additive/affine map.
- **The general-substitution-per-word survivor is also disproved** by the
  pattern-preservation test in `word-transform-census.md`: any fixed
  per-word substitution, however the key is derived, preserves the
  plaintext's within-word adjacent letter repeats — predicting ~244
  within-word doublets vs 63 observed, an 11.6 sigma deficit. Only
  position-varying keys WITHIN words survive, which is no longer a
  word-level scheme. (The rune-level split test is uninformative here: it
  groups runes by C[i-1], which does not fix a key that varies per word,
  so its random IOC is expected under this variant and disconfirms
  nothing.)
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

- **The seam-keyed BASE is now closed too (August 2026,
  `experiments/seam_keyed_depth.py`).** Everything above kills schemes where
  one substitution covers a whole word. It does not reach the variant that
  survives inside the walk: the key still varies by position through `g^k`,
  and only the per-word **base** is autokeyed on the previous word's last
  rune. That variant is untouched by the transform census (the per-word
  transform is not constant) and by the pattern-preservation test (within-word
  repeats are broken by `g^k`, not by the base).

  It has its own signature. Compare two words at the same position `k`: since
  `c_k = base_w(g^k(p_k))`, two words sharing a base agree exactly when their
  plaintext runes agree, so agreement jumps from the flat 1/29 = 0.0345 to the
  runeglish plaintext coincidence rate of about 0.06. Conditioning on the seam
  rune matching therefore predicts a lift of **+0.0255**.

  | tap | agree, tap matches | tap differs | lift | z |
  |---|---|---|---|---|
  | previous word's last rune | 0.0348 | 0.0344 | **+0.0004** | +1.43 |
  | previous word's first rune | 0.0345 | 0.0344 | +0.0001 | +0.31 |
  | last rune two words back | 0.0342 | 0.0344 | −0.0002 | −0.64 |

  Against a null shuffling the taps across words (2,000 draws, sd 0.0003), the
  predicted +0.0255 sits **93 sigma** away. Three taps were tried so a null
  cannot be blamed on the wrong one.

  The test degrades gracefully, so it also bounds partial keying: the lift is
  at most +0.0009 at 2 sigma, so **the seam rune can determine at most 3.7% of
  the alphabet selection**. This is a much more direct measurement than the
  arguments above — it uses every word pair rather than repeated words only,
  and conditioning on the seam concentrates the signal 29-fold.

## Predictions

~~If word-level autokey with position-within-word dependence: group runes by
(word_key, position_in_word) and check IOC.~~ Mooted: the
pattern-preservation census excludes every fixed per-word substitution
regardless of key derivation, and the additive position-dependent form
fails the doublet constraint, so no variant survives for this grouping to
test.

## Scripts

- `experiments/seam_keyed_depth.py` — conditions word-pair agreement on the
  seam rune, closing the seam-keyed base variant.

## Verdict

Disproved. Additive/affine per-word variants fail the word transform
census, and the general-substitution-per-word survivor fails its
pattern-preservation test (11.6 sigma);
letterwise running-key variants fail the doublet fingerprint by 5x;
and the doublet argument holds for any ADDITIVE word-level key schedule:
the key for a word is fixed before its runes are emitted, so it cannot
avoid ciphertext doublets without per-rune output feedback. (Mixed-alphabet
schedules with a bigram-tuned step evade that argument, but those vary the
alphabet per RUNE, not per word — see `length-clocked-walk.md`.)
